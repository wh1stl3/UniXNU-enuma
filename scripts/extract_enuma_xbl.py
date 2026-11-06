"""Extract this enuma's OEM inputs locally; never write device partitions."""
import argparse
import hashlib
import json
import re
import struct
import uuid
from pathlib import Path
from uefi_firmware.uefi import FirmwareVolume, FirmwareFile

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = '7ac67cbf4c7870a972cb4ffd9cc09d5db1c96b7f4a5abc7a80c0da9cabc65057'
# Hardware services only. Keep the new Mu core/BDS/console, not OEM equivalents.
SELECT = set('EnvDxe SmemDxe DALSys HWIODxeDriver ChipInfo PlatformInfoDxeDriver HALIOMMU ULogDxe CmdDbDxe PwrUtilsDxe NpaDxe RpmhDxe PdcDxe VcsDxe ClockDxe SPMI ShmBridgeDxe ScmDxe TzDxe DALTLMM ResetRuntimeDxe PmicDxe DDRInfoDxe UFSDxe GpiDxe SPI I2C HashDxe CipherDxe MacDxe RngDxe'.split())
SELECT.update(('DisplayDxe', 'CPRDxe'))
RAW = ('Panel_K81_42_02_0a_dualdsi_cphy_lcd_vid.xml', 'Panel_K81_35_02_0b_dualdsi_cphy_lcd_vid.xml')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dependencies(data):
    """Decode PI dependency opcodes for inventory, not protocol-provider proof."""
    result = []; offset = 0; depth = 0
    while offset < len(data):
        op = data[offset]; offset += 1
        if op in (0, 1, 2):
            if offset + 16 > len(data): raise ValueError('truncated DEPEX GUID')
            result.append({'op': ('BEFORE', 'AFTER', 'PUSH')[op],
                           'guid': str(uuid.UUID(bytes_le=data[offset:offset + 16]))})
            offset += 16
            if op == 2: depth += 1
        elif op in (3, 4):
            if depth < 2: raise ValueError('DEPEX stack underflow')
            depth -= 1; result.append({'op': 'AND' if op == 3 else 'OR'})
        elif op == 5:
            if depth < 1: raise ValueError('DEPEX NOT underflow')
            result.append({'op': 'NOT'})
        elif op in (6, 7):
            depth += 1; result.append({'op': 'TRUE' if op == 6 else 'FALSE'})
        elif op == 8:
            result.append({'op': 'END'})
            if offset != len(data): raise ValueError('trailing DEPEX')
            return result
        elif op == 9: result.append({'op': 'SOR'})
        else: raise ValueError(f'unsupported DEPEX opcode {op}')
    raise ValueError('DEPEX missing END')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--xbl', type=Path, default=ROOT / 'out/device/xbl_a.bin')
    args = parser.parse_args()
    blob = args.xbl.read_bytes()
    if sha(blob) != EXPECTED: raise ValueError('XBL differs from captured enuma; review new input')
    offset = 0x888b0
    length = struct.unpack_from('<Q', blob, offset + 32)[0]
    header = struct.unpack_from('<H', blob, offset + 48)[0]
    if offset + length > len(blob) or header % 2: raise ValueError('FV bounds')
    if sum(struct.unpack('<' + 'H' * (header // 2), blob[offset:offset + header])) & 0xffff:
        raise ValueError('FV header checksum')
    volume = FirmwareVolume(blob[offset:offset + length])
    if not volume.process(): raise ValueError('FV decoding failed')
    out = ROOT / 'out/firmware-vendor'; out.mkdir(parents=True, exist_ok=True)
    raw = out / 'raw'; raw.mkdir(exist_ok=True)
    queue = [volume]; files = {}; apriori = []
    while queue:
        obj = queue.pop(0); queue.extend(getattr(obj, 'objects', []))
        if not isinstance(obj, FirmwareFile) or obj.type == 0xf0: continue
        guid = str(uuid.UUID(bytes_le=obj.guid))
        sections = obj.objects
        names = [s.data.decode('utf-16-le').rstrip('\0') for s in sections if s.type == 0x15]
        name = names[0] if names else guid
        if name in files: raise ValueError('duplicate OEM UI name')
        files[name] = (guid, obj, sections)
        if guid == 'fc510ee7-ffdc-11d4-bd41-0080c73c8881':
            value = next(s.data for s in sections if s.type == 0x19)
            if len(value) % 16: raise ValueError('APRIORI size')
            apriori = [str(uuid.UUID(bytes_le=value[i:i+16])) for i in range(0, len(value), 16)]
        if name in ('uefiplat.cfg', *RAW):
            value = next(s.data for s in sections if s.type == 0x19)
            (raw / name).write_bytes(value)
    missing = SELECT - files.keys()
    if missing: raise ValueError(f'missing native modules: {sorted(missing)}')
    modules = []
    for name in sorted(SELECT):
        guid, obj, sections = files[name]
        pe = [s for s in sections if s.type == 0x10]
        depex = [s for s in sections if s.type == 0x13]
        if len(pe) != 1 or len(depex) > 1: raise ValueError(f'unsupported sections: {name}')
        image = pe[0].data; dep = depex[0].data if depex else None
        if image[:2] != b'MZ': raise ValueError(f'not PE: {name}')
        peoff = struct.unpack_from('<I', image, 60)[0]
        if image[peoff:peoff+4] != b'PE\0\0' or struct.unpack_from('<H', image, peoff+4)[0] != 0xaa64:
            raise ValueError(f'not AArch64 PE: {name}')
        subsystem = struct.unpack_from('<H', image, peoff + 24 + 68)[0]
        if subsystem not in (11, 12): raise ValueError(f'not EFI driver: {name}')
        module_type = 'DXE_RUNTIME_DRIVER' if subsystem == 12 else 'DXE_DRIVER'
        directory = out / 'Binaries/enuma' / name; directory.mkdir(parents=True, exist_ok=True)
        (directory / (name + '.efi')).write_bytes(image)
        if dep is not None: (directory / (name + '.depex')).write_bytes(dep)
        inf = f'[Defines]\n  INF_VERSION = 0x00010005\n  BASE_NAME = {name}\n  FILE_GUID = {guid}\n  MODULE_TYPE = {module_type}\n  VERSION_STRING = 1.0\n\n[Binaries.AARCH64]\n  PE32|{name}.efi|*\n'
        if dep is not None: inf += f'  DXE_DEPEX|{name}.depex|*\n'
        (directory / (name + '.inf')).write_text(inf)
        modules.append({'name': name, 'guid': guid, 'module_type': module_type,
                        'inf': f'Binaries/enuma/{name}/{name}.inf', 'pe_bytes': len(image),
                        'pe_sha256': sha(image), 'depex_sha256': sha(dep) if dep is not None else None,
                        'depex': dependencies(dep) if dep is not None else None})
    by_guid = {m['guid']: m for m in modules}
    ordered = [by_guid[g] for g in apriori if g in by_guid]
    remaining = [m for m in modules if m['guid'] not in apriori]
    (out / 'Vendor.dsc.inc').write_text('[Components]\n' + ''.join('  ' + m['inf'] + '\n' for m in modules))
    (out / 'Vendor.fdf.inc').write_text(''.join('  INF ' + m['inf'] + '\n' for m in modules))
    (out / 'Vendor.apriori.inc').write_text(''.join('  INF ' + m['inf'] + '\n' for m in ordered))
    resources = ''
    for name in RAW:
        guid = files[name][0]
        resources += f'  FILE FREEFORM = {guid} {{\n    SECTION UI = "{name}"\n    SECTION RAW = raw/{name}\n  }}\n'
    (out / 'Vendor.raw.fdf.inc').write_text(resources)
    report = {'scope': 'own-device OEM module reuse; dependency expressions preserved, provider/runtime closure not proven',
              'xbl_sha256': EXPECTED, 'extractor': 'uefi_firmware==1.16', 'fv_offset': offset,
              'oem_file_count': len(files), 'oem_apriori_count': len(apriori),
              'selected_modules': modules, 'selected_without_apriori': [m['name'] for m in remaining],
              'raw_inputs': {p.name: sha(p.read_bytes()) for p in raw.iterdir()},
              'closure_gaps': ['DEPEX GUID providers must be checked against new Mu core plus selected modules',
                               'OEM config/SMEM/SCM protocol ABI and dispatch need runtime validation',
                               'UEFI USB/storage and reset behavior not executed']}
    (ROOT / 'reports/enuma-oem-modules.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: {len(modules)} enuma AArch64 drivers and original DEPEX extracted; no device writes')


if __name__ == '__main__': main()
