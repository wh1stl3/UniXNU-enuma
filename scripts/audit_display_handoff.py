"""Offline, hash-bound audit of saved enuma ABL/DisplayDxe/FDT handoff inputs.

Requires pefile, capstone and uefi_firmware (optionally in --tool-path).
Never connects to a device, changes firmware source or emits a boot candidate.
"""
import argparse
from collections import deque
import contextlib
import hashlib
import io
from importlib.metadata import version
import json
from pathlib import Path
import struct
import sys
import uuid

from audit_inputs import parse_fdt

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    'out/device/abl_a.bin': 'ff00cd26595d81f97673a7dacaf12e025d25053747bd3819c73dbefd02cc802a',
    'out/device/xbl_a.bin': '7ac67cbf4c7870a972cb4ffd9cc09d5db1c96b7f4a5abc7a80c0da9cabc65057',
    'out/device-tests/20261022T201404/vendor_boot_a.bin': '3da202d0c9a5b618b61cd1923e87810536c5f70c9da7875de80075290641daba',
    'out/device/live-fdt.bin': '643aa3ec450139d38f8cde9a94bca6d9e8e75e752cb7aa992685d34267434c62',
    'out/boot-candidate/vt-oemdisplay.img': '922972e61b0e4e3d7b7c931b53b76531a2db2a08504c6794263e5ff3f5ab1a75',
}
DISPLAY_SHA = '6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425'
ABL_PE_SHA = '0460da8ebfc6c77012be96ecf075c4364466b498eb8f87a6f1b8b4bcd6cee612'
KERNEL_GUID = 'b5062be7-170b-4a32-be21-689262ff4399'
SCHED_HOB_GUID = '8ec2bd8d-56d7-49ef-8796-631778f8ebf8'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pinned(path):
    data = (ROOT / path).read_bytes()
    if sha(data) != PINS[path]:
        raise ValueError('Unreviewed input digest: ' + path)
    return data


def firmware_files(blob):
    """Bounded FV candidates and object traversal; yields decoded firmware files."""
    from uefi_firmware.uefi import FirmwareVolume, FirmwareFile
    offset = 0
    seen = set()
    while True:
        signature = blob.find(b'_FVH', offset)
        if signature < 0:
            break
        offset = signature + 4
        start = signature - 40
        if start < 0 or start + 56 > len(blob):
            continue
        size = struct.unpack_from('<Q', blob, start + 32)[0]
        header = struct.unpack_from('<H', blob, start + 48)[0]
        if not (56 <= header <= size <= len(blob) - start) or header % 2:
            continue
        if sum(struct.unpack('<' + 'H' * (header // 2), blob[start:start + header])) & 0xffff:
            continue
        fv = FirmwareVolume(blob[start:start + size])
        with contextlib.redirect_stdout(io.StringIO()):
            if not fv.process():
                continue
        queue = deque([fv])
        count = 0
        while queue:
            obj = queue.popleft()
            count += 1
            if count > 100000:
                raise ValueError('FV traversal limit')
            queue.extend(getattr(obj, 'objects', []))
            if not isinstance(obj, FirmwareFile):
                continue
            sections = obj.objects
            names = [s.data.decode('utf-16le').rstrip('\0') for s in sections if s.type == 0x15]
            for section in sections:
                if section.type != 0x10:
                    continue
                key = (obj.guid, sha(section.data))
                if key in seen:
                    continue
                seen.add(key)
                yield {'guid': str(uuid.UUID(bytes_le=obj.guid)),
                       'name': names[0] if names else '', 'data': section.data}


def named_pe(blob, name, digest):
    matches = [item['data'] for item in firmware_files(blob) if item['name'] == name]
    if len(matches) != 1 or sha(matches[0]) != digest:
        raise ValueError('Missing, ambiguous or changed PE: ' + name)
    return matches[0]


def pe_evidence(data, ranges, checks):
    import capstone
    import pefile
    pe = pefile.PE(data=data)
    if pe.FILE_HEADER.Machine != 0xaa64 or pe.OPTIONAL_HEADER.ImageBase != 0:
        raise ValueError('Expected reviewed ARM64 PE layout')
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_LITTLE_ENDIAN)
    instructions = {}
    excerpts = []
    for begin, end in ranges:
        raw = pe.get_data(begin, end - begin)
        if len(raw) != end - begin:
            raise ValueError('PE excerpt outside input')
        seq = list(md.disasm(raw, begin))
        if sum(i.size for i in seq) != len(raw):
            raise ValueError('Undecodable audited instruction range')
        excerpts.append({'begin_rva': hex(begin), 'end_rva_exclusive': hex(end),
                         'instructions': [{'rva': hex(i.address), 'mnemonic': i.mnemonic,
                                           'operands': i.op_str} for i in seq]})
        instructions.update({i.address: (i.mnemonic, i.op_str) for i in seq})
    for address, expected in checks.items():
        if instructions.get(address) != expected:
            raise ValueError('Instruction contract mismatch: ' + hex(address))
    return pe, {'sha256': sha(data), 'bytes': len(data),
                'entry_rva': hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint), 'excerpts': excerpts}


def dtb_evidence(blob):
    result = []
    offset = 0
    while (start := blob.find(bytes.fromhex('d00dfeed'), offset)) >= 0:
        offset = start + 4
        if start + 40 > len(blob):
            continue
        size = struct.unpack_from('>I', blob, start + 4)[0]
        if not 40 <= size <= len(blob) - start:
            continue
        raw = blob[start:start + size]
        try:
            nodes = parse_fdt(raw)
        except ValueError:
            continue
        selected = []
        for path, props in nodes.items():
            if not path.startswith('/reserved-memory/'):
                continue
            if 'splash' not in path.lower() and 'dfps' not in path.lower():
                continue
            reg = props.get('reg', b'')
            selected.append({'path': path, 'label': props.get('label', b'').rstrip(b'\0').decode(),
                             'reg_cells': [hex(x) for x in struct.unpack('>' + 'I' * (len(reg) // 4), reg)]})
        exact = any(path.split('@')[0] == '/reserved-memory/splash_region' for path in nodes)
        result.append({'offset': start, 'bytes': size, 'sha256': sha(raw),
                       'root_compatible': nodes.get('/', {}).get('compatible', b'').rstrip(b'\0').decode().split('\0'),
                       'abl_splash_path_present': exact, 'selected_reservations': selected})
        offset = start + size
    if not result:
        raise ValueError('No valid saved DTB')
    return result


def source_evidence():
    paths = [
        'firmware/BootShim/BootShim.S',
        'firmware/Silicon/Silicium/SiliciumPkg/Sec/AArch64/ModuleEntryPoint.S',
        'firmware/Silicon/Silicium/SiliciumPkg/Sec/Sec.c',
        'firmware/Silicon/Qualcomm/QcomPkg/Library/PlatformPeiLib/XblProtocols.c',
        'firmware/Silicon/Qualcomm/QcomPkg/Library/PlatformPeiLib/PlatformPei.c',
        'firmware/Platforms/Xiaomi/enumaPkg/Library/MemoryMapLib/MemoryMapLib.c',
        'firmware/Platforms/Xiaomi/enumaPkg/Library/ConfigurationMapLib/ConfigurationMapLib.c',
        'firmware/patches/kona-preserve-display.patch',
        'firmware/patches/sec-preserve-display.patch',
    ]
    result = []
    for name in paths:
        data = (ROOT / name).read_bytes()
        result.append({'path': name, 'sha256': sha(data)})
    text = (ROOT / paths[5]).read_text()
    names = ['FD Reserved', 'FD_Reserved']
    return {'files': result, 'scheduler_lookup_region_names': names,
            'scheduler_lookup_name_present': any('"' + name + '"' in text for name in names),
            'scope': 'current source only; does not establish exact R-014 SEC machine code'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool-path', type=Path, help='isolated Python dependency directory')
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/enuma-display-handoff-audit.json')
    args = parser.parse_args()
    if args.tool_path:
        sys.path.insert(0, str(args.tool_path.resolve()))
    output = args.output.resolve()
    if not output.is_relative_to((ROOT / 'reports').resolve()) and not output.is_relative_to((ROOT / 'out').resolve()):
        raise ValueError('Output must stay in repository reports/ or out/')
    inputs = {name: pinned(name) for name in PINS}
    abl = named_pe(inputs['out/device/abl_a.bin'], 'LinuxLoader', ABL_PE_SHA)
    image = inputs['out/boot-candidate/vt-oemdisplay.img']
    if image[:8] != b'ANDROID!' or struct.unpack_from('<I', image, 40)[0] != 3:
        raise ValueError('Expected R-014 boot v3')
    kernel_size, ramdisk_size = struct.unpack_from('<II', image, 8)
    kernel = image[4096:4096 + kernel_size]
    if ramdisk_size != 0 or kernel[56:60] != b'ARM\x64' or len(kernel) != 192 + 0x300000:
        raise ValueError('R-014 payload layout changed')
    fd = kernel[192:]
    display = named_pe(fd, 'DisplayDxe', DISPLAY_SHA)
    original = named_pe(inputs['out/device/xbl_a.bin'], 'DisplayDxe', DISPLAY_SHA)
    if display != original:
        raise ValueError('R-014 OEM PE differs from original XBL')
    pe, display_report = pe_evidence(display,
        [(0x13f0, 0x1438), (0x1b40, 0x1c68), (0x1f38, 0x1f60),
         (0x2110, 0x2150), (0x5f78, 0x5fb8), (0x5fe8, 0x60c4), (0x612c, 0x6218)],
        {0x1be4: ('bl', '#0x3874'), 0x1c38: ('bl', '#0x5f78'),
         0x1c5c: ('bl', '#0x5f98'), 0x6168: ('blr', 'x9'),
         0x61ac: ('bl', '#0x61c0'), 0x620c: ('ldr', 'x0, [x0, #0x18]')})
    if str(uuid.UUID(bytes_le=pe.get_data(0x3e248, 16))) != KERNEL_GUID:
        raise ValueError('Kernel protocol GUID mismatch')
    if str(uuid.UUID(bytes_le=pe.get_data(0x3e418, 16))) != SCHED_HOB_GUID:
        raise ValueError('Scheduler HOB GUID mismatch')
    abl_pe, abl_report = pe_evidence(abl, [(0x1cad8, 0x1caf8), (0x1cb30, 0x1cb60), (0x1cbd0, 0x1cbf4)],
        {0x1cae4: ('bl', '#0x2e1f8'), 0x1caf4: ('tbnz', 'w27, #0x1f, #0x1cbd0')})
    splash_path = abl_pe.get_data(0xbb128, 128).split(b'\0')[0].decode()
    if splash_path != '/reserved-memory/splash_region':
        raise ValueError('ABL splash path mismatch')
    vendor = inputs['out/device-tests/20261022T201404/vendor_boot_a.bin']
    if vendor[:8] != b'VNDRBOOT' or struct.unpack_from('<I', vendor, 8)[0] != 3:
        raise ValueError('Expected stock vendor_boot v3')
    page = struct.unpack_from('<I', vendor, 12)[0]
    ramdisk = struct.unpack_from('<I', vendor, 24)[0]
    header, size = struct.unpack_from('<II', vendor, 2096)
    if page != 4096 or header != 2112:
        raise ValueError('Unexpected vendor_boot geometry')
    start = ((header + page - 1) // page + (ramdisk + page - 1) // page) * page
    if start + size > len(vendor):
        raise ValueError('Vendor DTB bounds')
    report = {
        'schema': 1, 'scope': 'offline saved binary/source evidence; no device I/O or candidate build',
        'tools': {name: version(name) for name in ['capstone', 'pefile', 'uefi_firmware']},
        'inputs': [{'path': name, 'sha256': sha(blob), 'bytes': len(blob)} for name, blob in inputs.items()],
        'r014': {'kernel_sha256': sha(kernel), 'fd_sha256': sha(fd),
                 'original_display_pe_identical': True},
        'display_pe': display_report,
        'display_runtime': {'kernel_protocol_guid': KERNEL_GUID, 'fallback_scheduler_hob_guid': SCHED_HOB_GUID,
                            'thread_flag_string_rva': '0x2da98',
                            'thread_missing_path': '0x6008 returns EFI_UNSUPPORTED -> 0x1c18 -> 0x1bec -> zero status',
                            'meaning': 'entry return can coexist with no display thread; not proof of visible output'},
        'abl_pe': abl_report,
        'abl_contract': {'splash_path': splash_path,
                         'missing_path': 'negative lookup -> 0x1cbd0; error text at 0xbb147',
                         'meaning': 'consumer/path mismatch established; panel-off causality not established'},
        'vendor_boot_dtbs': dtb_evidence(vendor[start:start + size]),
        'historical_android_fdt': dtb_evidence(inputs['out/device/live-fdt.bin']),
        'source_handoff': source_evidence(),
        'limits': ['DTBO/current ABL-selected FDT and temporary-entry x0 bytes not captured',
                   'no runtime protocol/HOB presence or actual thread execution demonstrated',
                   'no new mappings, memory fields, pixel/MMIO writes or verified flags',
                   'no conclusion that ABL path mismatch alone powers the panel off',
                   'excerpts are linear disassembly of hash-pinned ranges, not whole-program execution'],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('PASS: R-014/XBL PE identity, real thread/protocol/HOB calls, ABL path and saved DTBs; runtime unresolved')


if __name__ == '__main__':
    main()
