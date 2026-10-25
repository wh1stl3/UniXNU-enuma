"""Bind packaged RAM driver, active compiler macros and boot-v3 FAT bytes."""
import argparse
import hashlib
import json
import re
import shutil
import struct
import sys
from pathlib import Path
from audit_display_handoff import named_pe
from package_enuma_boot import verify

ROOT = Path(__file__).resolve().parents[1]


def sha(blob): return hashlib.sha256(blob).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-path', type=Path)
    p.add_argument('--image', type=Path, default=ROOT / 'out/full-boot/transport/enuma-system-transport-v3.img')
    a = p.parse_args()
    if a.tool_path: sys.path.insert(0, str(a.tool_path.resolve()))
    import capstone
    import pefile
    build = json.loads((ROOT / 'reports/enuma-firmware-build.json').read_text())
    pin = json.loads((ROOT / 'config/uefi-source.lock.json').read_text())
    contract = json.loads((ROOT / 'reports/enuma-ram-payload-contract.json').read_text())
    if build['complete'] is not True or build['uefi_source_commit'] != pin['commit']:
        raise ValueError('incomplete/stale firmware build')
    fd = (ROOT / build['fd']).read_bytes()
    if sha(fd) != build['fd_sha256']:
        raise ValueError('FD changed')
    base = ROOT / 'out/firmware-build/uefi'
    output = base / 'Build/enumaPkg/DEBUG_CLANGPDB/AARCH64'
    defs = build['firmware_configuration']['defines']
    required = {'ENUMA_RAM_PAYLOAD': '1', 'ENUMA_DIAG_STAGE': '0', 'ENUMA_DIAG_SIMPLEFB': '0',
                'ENUMA_DIAG_DISPATCH_FALLBACK': '0', 'ENUMA_DIAG_GOP_QUERY': '0',
                'ENUMA_DIAG_GOP_STEP': '0', 'ENUMA_VALUE_SOURCE': '0', 'ENUMA_DIAG_PIXEL_PREVIEW': '0'}
    modules = {}
    archive_files = {}
    driver_pe = None
    for name, relative in [('EnumaRamPayloadDxe', 'Drivers'), ('EnumaProbe', 'Application')]:
        folder = output / f'enumaPkg/{relative}/{name}/{name}'
        # Application path is named EnumaProbe; driver folder matches module name.
        make = (folder / 'GNUmakefile').read_bytes()
        for key, value in required.items():
            matches = re.findall(rb'-D' + key.encode() + rb'=([^\s]+)', make)
            if defs.get(key) != value or not matches or set(matches) != {value.encode()}:
                raise ValueError(name + ': actual compiler flags differ: ' + key)
        blob = (folder / ('OUTPUT/' + name + '.efi')).read_bytes()
        packaged = named_pe(fd, name, sha(blob))
        pe = pefile.PE(data=packaged)
        if pe.FILE_HEADER.Machine != 0xaa64:
            raise ValueError('not AARCH64: ' + name)
        modules[name] = dict(bytes=len(blob), sha256=sha(blob), compiler_sha256=sha(make),
                             flags=required, packaged_equal=True)
        archive_files[name + '.efi'] = folder / ('OUTPUT/' + name + '.efi')
        archive_files[name + '.map'] = folder / ('OUTPUT/' + name + '.map')
        archive_files[name + '.GNUmakefile'] = folder / 'GNUmakefile'
        if name == 'EnumaRamPayloadDxe': driver_pe = pe
        else:
            if 'PHOTO NOW; UNIXNU MENU IN 60 SECONDS'.encode('utf-16-le') in blob:
                raise ValueError('old diagnostic hold still present in payload application')
            for label in ['MAP', 'FDT', 'INITRD', 'PREFIX', 'BPB', 'FAT CRC', 'BLOCKIO', 'CONNECT', 'SFS', 'KERNEL', 'ADT', 'TRUST', 'CONFIG']:
                if (label + '\0').encode('utf-16-le') not in blob:
                    raise ValueError('batch output label missing: ' + label)
    driver_dir = base / 'Platforms/Xiaomi/enumaPkg/Drivers/EnumaRamPayloadDxe'
    header = driver_dir / 'PayloadContract.h'
    if sha(header.read_bytes()) != contract['header_sha256']:
        raise ValueError('generated contract header changed')
    for name in ['EnumaRamPayload.c', 'TransportBounds.h', 'TransportReport.h']:
        if (driver_dir / name).read_bytes() != (ROOT / 'firmware/Platforms/Xiaomi/enumaPkg/Drivers/EnumaRamPayloadDxe' / name).read_bytes():
            raise ValueError('staged source differs: ' + name)
        archive_files[name] = driver_dir / name
    archive_files['PayloadContract.h'] = header
    map_text = archive_files['EnumaRamPayloadDxe.map'].read_text()
    symbols = {m[2]: int(m[1], 16) for m in re.finditer(r'^([0-9a-fA-F]{8,16})\s+[0-9a-fA-F]+\s+0\s+(\S+)\s*$', map_text, re.M)}
    for name, fmt, expected in [('CheckFiles.Sizes', '<4Q', [e['bytes'] for e in contract['files']]),
                                 ('CheckFiles.Crcs', '<4I', [e['head_crc32'] for e in contract['files']])]:
        if list(struct.unpack(fmt, driver_pe.get_data(symbols[name], struct.calcsize(fmt)))) != expected:
            raise ValueError('actual PE constant array differs: ' + name)
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_LITTLE_ENDIAN)
    start = symbols['RamWrite']; end = min(v for v in symbols.values() if v > start)
    instructions = [(i.mnemonic, i.op_str) for i in md.disasm(driver_pe.get_data(start, end - start), start)]
    if instructions != [('mov', 'x0, #8'), ('movk', 'x0, #0x8000, lsl #48'), ('ret', '')]:
        raise ValueError('actual RamWrite does not return EFI_WRITE_PROTECTED')
    image = a.image.resolve()
    if not image.is_relative_to((ROOT / 'out').resolve()):
        raise ValueError('candidate must stay inside out/')
    kernel = ROOT / 'out/boot-candidate/enuma-uefi.raw'
    fat = ROOT / 'out/full-boot/payload/payload.img'
    packaging = verify(image.read_bytes(), kernel.read_bytes(), fat.read_bytes())
    if sha(fat.read_bytes()) != contract['fat_sha256'] or kernel.read_bytes()[192:] != fd:
        raise ValueError('boot image FD/FAT identity differs')
    archive = ROOT / ('out/full-boot/transport/qualified-' + pin['commit'][:7])
    if archive.exists(): raise ValueError('refuse to overwrite qualification archive')
    archive.mkdir()
    archive_files.update({'SILICIUM_UEFI.fd': ROOT / build['fd'], 'enuma-uefi.raw': kernel,
                          'enuma-system-transport-v3.img': image, 'firmware-build.json': ROOT / 'reports/enuma-firmware-build.json',
                          'payload-contract.json': ROOT / 'reports/enuma-ram-payload-contract.json',
                          'host-checks.json': ROOT / 'reports/enuma-ram-payload-host.json',
                          'abl-concat.json': ROOT / 'reports/enuma-abl-v3-concat.json'})
    manifest = {}
    for name, path in archive_files.items():
        shutil.copyfile(path, archive / name)
        blob = (archive / name).read_bytes()
        manifest[name] = dict(bytes=len(blob), sha256=sha(blob))
    report = dict(scope='offline actual PE/compiler/boot packaging qualification, no device execution',
                  firmware_commit=pin['commit'], fd_sha256=sha(fd), modules=modules,
                  ram_write_instructions=instructions, constant_arrays_match=True,
                  packaging=packaging, image_sha256=sha(image.read_bytes()), image_bytes=image.stat().st_size,
                  image=image.relative_to(ROOT).as_posix(),
                  archive=archive.relative_to(ROOT).as_posix(), files=manifest,
                  hardware_tested=False, runtime_fdt_sfs_observed=False,
                  full_boot_ready=False, new_memory_mapping=False)
    (archive / 'qualification.json').write_text(json.dumps(report, indent=2) + '\n')
    (ROOT / 'reports/enuma-ram-payload-qualification.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: actual driver/probe PE, active flags, constant arrays, write-protection code, FD/FAT boot-v3 identity and immutable archive')


if __name__ == '__main__':
    main()
