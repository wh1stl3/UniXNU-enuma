"""Archive one offline DisplayDxe pre-entry/return candidate; never boot it."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
GUID = '4138022f-06c7-4f79-9c94-7e33b511a4e7'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def qualify(image, target, point, *, payload_fat=None, completion_fallback=True):
    from audit_display_handoff import firmware_files
    import capstone
    import pefile
    image = image.resolve()
    target = target.resolve()
    if not image.is_relative_to(ROOT / 'out') or not target.is_relative_to(ROOT / 'out'):
        raise ValueError('Artifacts must stay in out/')
    if target.exists():
        raise ValueError('Refuse to overwrite archive')
    build_path = ROOT / 'reports/enuma-firmware-build.json'
    audit_path = ROOT / 'reports/enuma-fd-audit.json'
    payload_path = ROOT / 'reports/enuma-boot-payload.json'
    build, audit, payload, package = [json.loads(p.read_text()) for p in
                                     [build_path, audit_path, payload_path, image.with_suffix('.json')]]
    required = {'complete': True, 'diagnostic_stop_stage': 13, 'diagnostic_delay_seconds': 2,
                'diagnostic_dispatch_ordinal': 1, 'diagnostic_detail_point': point,
                'diagnostic_dispatch_guid': GUID, 'diagnostic_dispatch_guid_only': True,
                'diagnostic_dispatch_completion_fallback': completion_fallback, 'diagnostic_gop_query': 0,
                'diagnostic_gop_step': 0, 'diagnostic_pixel_preview': False,
                'diagnostic_omitted_oem_modules': ['UFSDxe']}
    if any(build.get(key) != value for key, value in required.items()):
        raise ValueError('Build profile mismatch')
    lock = json.loads((ROOT / 'config/uefi-source.lock.json').read_text())
    if build['uefi_source_commit'] != lock['commit'] or build['value_probe']['source'] != 'off':
        raise ValueError('Source or value profile mismatch')
    fd = (ROOT / build['fd']).read_bytes()
    raw = (ROOT / 'out/boot-candidate/enuma-uefi.raw').read_bytes()
    blob = image.read_bytes()
    if not (sha(fd) == build['fd_sha256'] == audit['fd_sha256'] == payload['fd_sha256']):
        raise ValueError('FD ownership mismatch')
    if sha(raw) != payload['raw_sha256'] or raw[192:] != fd:
        raise ValueError('Raw payload ownership mismatch')
    if sha(blob) != package['image_sha256'] or package['kernel_sha256'] != sha(raw):
        raise ValueError('Packaged image ownership mismatch')
    if blob[:8] != b'ANDROID!' or struct.unpack_from('<I', blob, 40)[0] != 3:
        raise ValueError('Not boot v3')
    size, ramdisk = struct.unpack_from('<II', blob, 8)
    if size != len(raw) or blob[4096:4096 + size] != raw:
        raise ValueError('Unexpected boot content')
    fat_sha = None
    if payload_fat is None:
        if ramdisk or build['firmware_configuration']['defines'].get('ENUMA_RAM_PAYLOAD', '0') != '0':
            raise ValueError('legacy boundary profile must have empty ramdisk and RAM payload disabled')
    else:
        from package_enuma_boot import verify
        payload_fat = payload_fat.resolve()
        if not payload_fat.is_relative_to(ROOT / 'out'):
            raise ValueError('FAT must stay in out/')
        fat = payload_fat.read_bytes()
        approved = json.loads((ROOT / 'reports/enuma-full-payload.json').read_text())
        if sha(fat) != approved['payload_sha256'] or ramdisk != len(fat):
            raise ValueError('full-input boundary FAT differs from system-input report')
        verify(blob, raw, fat)
        fat_sha = sha(fat)
    make = ROOT / 'out/firmware-build/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64/MdeModulePkg/Core/Dxe/DxeMain/GNUmakefile'
    text = make.read_text()
    low, high = struct.unpack('<QQ', uuid.UUID(GUID).bytes_le)
    expected = {'ENUMA_DIAG_STAGE': 13, 'ENUMA_DIAG_DETAIL_POINT': point,
                'ENUMA_DIAG_DELAY_US': 2000000, 'ENUMA_DIAG_DISPATCH_ORDINAL': 1,
                'ENUMA_DIAG_GUID_ENABLED': 1, 'ENUMA_DIAG_GUID_ONLY': 1,
                'ENUMA_DIAG_GUID_LOW64': low, 'ENUMA_DIAG_GUID_HIGH64': high,
                'ENUMA_DIAG_DISPATCH_FALLBACK': int(completion_fallback), 'ENUMA_DIAG_GOP_QUERY': 0}
    if payload_fat is not None:
        expected['ENUMA_RAM_PAYLOAD'] = 1
    for key, wanted in expected.items():
        values = re.findall(r'-D' + key + r'=([^\s]+)', text)
        if not values or any(int(re.sub('[uUlL]+$', '', value), 0) != wanted for value in values):
            raise ValueError('Actual compiler macro mismatch: ' + key)
    modules = list(firmware_files(fd))
    if any(m['name'] in ['SimpleFbDxe', 'UFSDxe'] for m in modules):
        raise ValueError('Unexpected provider/UFS packaged')
    if not {'DisplayDxe', 'CPRDxe'}.issubset({m['name'] for m in modules}):
        raise ValueError('Native display modules missing')
    source_pe = next(m['data'] for m in modules if m['name'] == 'DisplayDxe')
    if sha(source_pe) != '6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425':
        raise ValueError('OEM DisplayDxe changed')
    core = [m for m in modules if m['guid'] == 'd6a2cb7f-6a18-4e2f-b43b-9920a733700a']
    # The PI core GUID is stable; reject missing/ambiguous core instead of using
    # a possibly stale build-output PE with the same UI name.
    if len(core) != 1:
        raise ValueError('Packaged DXE Core missing/ambiguous')
    core_pe = pefile.PE(data=core[0]['data'])
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_LITTLE_ENDIAN)
    md.detail = True
    md.skipdata = True
    found = {value: [] for value in [low, high, 2000000] + ([7000000] if completion_fallback else [])}
    for section in core_pe.sections:
        if not section.Characteristics & 0x20000000:
            continue
        registers = {}
        for ins in md.disasm(section.get_data()[:section.Misc_VirtualSize], section.VirtualAddress):
            if not ins.id:
                registers.clear()
                continue
            operands = ins.operands
            if ins.mnemonic in ['mov', 'movk'] and len(operands) == 2 and operands[1].type == capstone.arm64.ARM64_OP_IMM:
                reg = ins.reg_name(operands[0].reg)
                key = reg[1:]
                shift = operands[1].shift.value
                value = operands[1].imm
                if ins.mnemonic == 'mov':
                    registers[key] = value & ((1 << (32 if reg.startswith('w') else 64)) - 1)
                elif key in registers:
                    registers[key] = (registers[key] & ~(0xffff << shift)) | ((value & 0xffff) << shift)
                if registers.get(key) in found:
                    found[registers[key]].append(hex(ins.address))
                continue
            for reg_id in ins.regs_access()[1]:
                registers.pop(ins.reg_name(reg_id)[1:], None)
            if ins.mnemonic in ['bl', 'blr', 'ret']:
                registers.clear()
    semantic_delay = None
    if not completion_fallback and not found[2000000]:
        from audit_display_boundary_core import code_review
        map_path = make.parent / 'OUTPUT/DxeCore.map'
        semantic_delay = code_review(core[0]['data'], map_path.read_text(), point)['delay_contract']
        if semantic_delay.get('mode') != 'constant_specialized_2x1s':
            raise ValueError('Missing delay constant without exact specialized callee proof')
    if any(not addresses for value, addresses in found.items() if value != 2000000 or semantic_delay is None):
        raise ValueError('GUID halves/target or fallback delay absent from packaged Core code')
    target.mkdir(parents=True)
    artifacts = {'candidate.img': image, 'build.json': build_path, 'audit.json': audit_path,
                 'payload.json': payload_path, 'package.json': image.with_suffix('.json'),
                 'DxeCore.GNUmakefile': make,
                 'DxeCore.map': make.parent / 'OUTPUT/DxeCore.map'}
    for name, path in artifacts.items():
        shutil.copyfile(path, target / name)
    for name, data in [('candidate.fd', fd), ('candidate.raw', raw), ('DxeCore.efi', core[0]['data'])]:
        (target / name).write_bytes(data)
    report = {'scope': 'offline artifact, compiler and FD qualification; no execution',
              'detail_point': point, 'target_guid': GUID, 'firmware_commit': lock['commit'],
              'image': image.relative_to(ROOT).as_posix(), 'image_sha256': sha(blob),
              'image_bytes': len(blob), 'archive': target.relative_to(ROOT).as_posix(),
              'compiler_defines': {key: hex(value) for key, value in expected.items()},
              'ram_payload_sha256': fat_sha, 'ram_payload_bytes': ramdisk,
              'completion_fallback_enabled': completion_fallback,
              'semantic_delay_review': semantic_delay,
              'core_materialized_constants': {hex(value): addresses for value, addresses in found.items()},
              'files': {p.name: {'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size}
                        for p in sorted(target.iterdir())},
              'limits': ['constant construction and compiler flags do not prove complete runtime control flow',
                         'no current device identity/recovery checks or hardware authorization evaluation',
                         ('completion fallback is not a watchdog' if completion_fallback else 'completion fallback disabled; absence of return does not prove the selected driver was reached'),
                         'preceding drivers can run hardware writes']}
    (target / 'qualification.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--point', type=int, choices=[13, 15, 20, 21], required=True)
    parser.add_argument('--tool-path', type=Path)
    parser.add_argument('--ram-payload', type=Path, help='explicit exact system FAT; legacy default still requires empty ramdisk')
    parser.add_argument('--no-completion-fallback', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.tool_path:
        sys.path.insert(0, str(args.tool_path.resolve()))
    report = qualify(args.image, args.archive, args.point, payload_fat=args.ram_payload,
                     completion_fallback=not args.no_completion_fallback)
    if args.output:
        output = args.output.resolve()
        if not any(output.is_relative_to(ROOT / name) for name in ['out', 'reports']):
            raise ValueError('Output must stay in out/ or reports/')
        output.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: immutable offline candidate archive; image ' + report['files']['candidate.img']['sha256'])


if __name__ == '__main__':
    main()
