"""Audit packaged native modules and loader interfaces in the built FD; no boot."""
import argparse
import hashlib
import json
import uuid
from pathlib import Path
from uefi_firmware.uefi import FirmwareVolume, FirmwareFile

ROOT = Path(__file__).resolve().parents[1]


def digest(data): return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fd', type=Path, default=ROOT / 'out/firmware-build/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd')
    args = parser.parse_args()
    blob = args.fd.read_bytes()
    if len(blob) != 0x300000 or blob[40:44] != b'_FVH': raise ValueError('unexpected FD envelope')
    volume = FirmwareVolume(blob)
    if not volume.process(): raise ValueError('cannot decode built FD')
    queue = [volume]; files = {}; pe_payloads = {}
    while queue:
        obj = queue.pop(0); queue.extend(getattr(obj, 'objects', []))
        if not isinstance(obj, FirmwareFile) or obj.type == 0xf0: continue
        guid = str(uuid.UUID(bytes_le=obj.guid))
        if guid in files: raise ValueError('duplicate firmware file GUID: ' + guid)
        sections = obj.objects
        names = [s.data.decode('utf-16-le').rstrip('\0') for s in sections if s.type == 0x15]
        files[guid] = {'name': names[0] if names else guid,
                       'pe': [digest(s.data) for s in sections if s.type == 0x10],
                       'depex': [digest(s.data) for s in sections if s.type == 0x13]}
        pe_payloads[files[guid]['name']] = [s.data for s in sections if s.type == 0x10]
    inventory = json.loads((ROOT / 'reports/enuma-oem-modules.json').read_text())
    matched = []
    for module in inventory['selected_modules']:
        packaged = files.get(module['guid'])
        if not packaged or packaged['pe'] != [module['pe_sha256']]:
            raise ValueError('OEM PE bytes changed/missing: ' + module['name'])
        expected = [module['depex_sha256']] if module['depex_sha256'] else []
        if packaged['depex'] != expected: raise ValueError('OEM DEPEX changed: ' + module['name'])
        matched.append(module['name'])
    names = {item['name'] for item in files.values()}
    for required in ('EnumaProbe', 'UniXNU', 'UniXNUDxe', 'DarwinBoot', 'DisplayDxe', 'DDRInfoDxe', 'EnvDxe'):
        if required not in names: raise ValueError('required module missing: ' + required)
    if 'SimpleFbDxe' in names: raise ValueError('unqualified framebuffer provider included')
    probe_guid = 'aef8c196-230e-4e19-a306-d62e21e3d780'
    if probe_guid not in files or uuid.UUID(probe_guid).bytes_le not in b''.join(pe_payloads['UniXNUDxe']):
        raise ValueError('UniXNUDxe does not contain the packaged EnumaProbe boot target')
    report = {'scope': 'built FD structure and byte identity; no firmware execution',
              'fd_sha256': digest(blob), 'fd_bytes': len(blob), 'file_count': len(files),
              'matched_oem_modules': matched, 'packaged_names': sorted(names),
              'probe_boot_target_guid': probe_guid,
              'runtime_protocol_closure': 'pending hardware dispatch', 'hardware_execution': False}
    (ROOT / 'reports/enuma-fd-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: {len(matched)} native PE/DEPEX payloads unchanged; UniXNU loader modules packaged')


if __name__ == '__main__': main()
