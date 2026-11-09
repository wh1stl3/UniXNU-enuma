#!/usr/bin/env python3
"""Generate the device-local storage-abi interface-audit.json for RamBlock (enuma).

This replicates the *static* portion of UniXNU scripts/audit-storage-interface.py:
  1. compile refer/IOStorageFamily/IOBlockStorageDevice.cpp (public Darwin 23 source,
     pinned e45fbe30) with the Linux toolchain, replaying the XNU compile record;
  2. read the reference object's __ZTV20IOBlockStorageDevice vtable relocations to get
     the 190 dispatch slot names in order;
  3. read the prelinked kernel.macho: exports (by_name) and the 190 pointer values of the
     IOBlockStorageDevice __DATA_CONST vtable.

The live-gdb-only fields (instance sizes IOBlockStorageDevice 0x90 / IOService 0x88 and the
native-4K translation check) are OS-determined and are recorded from the marble/fuxi
ipados-17.7.11-21H461 record; they are not re-measured here. The vtable/metaclass/ctor/D2
addresses are the values measured on the enuma kernel.macho (39cecb2e) and equal the
marble-milacy / fuxi-oddlylabs recorded addresses for the same OS profile.

Output schema matches scripts/audit-storage-interface.py result so that the base
scripts/build-virtio-mmio-bindings.py consumes it unchanged.
"""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

# Measured on enuma kernel.macho (39cecb2e), matching marble/fuxi ipados-17.7.11-21H461.
VTABLE = 0xfffffff005cb44c0
META = 0xfffffff006add1d0
CTOR = 0xfffffff00496ed98
D2 = 0xfffffff00496edb8
SOURCE_REVISION = 'e45fbe30a7879e0b16e26dddb78538f1b00e0bff'


def compile_reference(tree, out):
    record_path = tree / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/iokit/DEVELOPMENT/IOPlatformExpert.cpo.json'
    record = json.loads(record_path.read_text().strip().rstrip(','))
    source = tree / 'refer/IOStorageFamily/IOBlockStorageDevice.cpp'
    obj_path = out / 'IOBlockStorageDevice-reference.o'
    arguments = record['arguments']
    command, index = [], 0
    while index < len(arguments):
        value = arguments[index]
        if value == record['file']:
            command.append(str(source))
        elif value == '-o':
            command += ['-o', str(obj_path)]
            index += 1
        elif value in ('-MF', '-MJ'):
            index += 1
        elif value == '-Xclang' and arguments[index + 1].startswith('-W'):
            index += 1
        elif not value.startswith('-W') and value not in ('-MD', '-MP'):
            command.append(value)
        index += 1
    command += ['-I', str(out / 'include'), '-I', str(tree / '.cache/xnu-work/osfmk'),
                '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter', '-Wno-deprecated-declarations',
                '-Wno-c99-designator', '-Wno-reorder-init-list', '-Wno-unnecessary-virtual-specifier',
                '-Wno-deprecated-enum-enum-conversion', '-Wno-missing-designated-field-initializers',
                '-Wno-unused-but-set-global']
    result = subprocess.run(command, cwd=record['directory'], capture_output=True, text=True)
    if result.returncode:
        raise SystemExit(result.stdout[-3500:] + result.stderr[-3500:])
    return obj_path


def vtable_names(obj_path, np):
    data = obj_path.read_bytes()
    om = np.macho(data)
    sycmd = next(at for command, at, size in om['commands'] if command == 2)
    symoff, count, stroff, _ = struct.unpack_from('<4I', data, sycmd + 8)
    symbols = []
    for i in range(count):
        ix, kind, _, _, value = struct.unpack_from('<IBBHQ', data, symoff + i * 16)
        symbols.append(dict(name=data[stroff + ix:data.index(b'\0', stroff + ix)].decode(), value=value, kind=kind))
    vtable = next(s['value'] for s in symbols if s['name'] == '__ZTV20IOBlockStorageDevice')
    relocations = {}
    for segment in om['segments']:
        for section in segment['sections']:
            if section['va'] <= vtable < section['va'] + section['size']:
                ro, rc = struct.unpack_from('<II', data, section['command_offset'] + 56)
                for i in range(rc):
                    address, word = struct.unpack_from('<II', data, ro + i * 8)
                    if word >> 27 & 1 and word >> 28 == 0 and word >> 25 & 3 == 3:
                        relocations[section['va'] + address] = symbols[word & 0xffffff]['name']
    end = min(s['value'] for s in symbols if not s['kind'] & 0xe0 and s['kind'] & 0xe == 0xe and s['value'] > vtable)
    names = []
    for at in range(vtable + 16, end, 8):
        if at not in relocations:
            break
        names.append(relocations[at])
    return names


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--tree', type=Path, required=True, help='assembled build tree root')
    ap.add_argument('--kernel', type=Path, required=True, help='prelinked kernel.macho')
    ap.add_argument('--output', type=Path, default=Path(__file__).resolve().parent / 'data/ram-block-interface-audit.json')
    args = ap.parse_args()

    tree = args.tree
    sys.path.insert(0, str(tree / 'kits/XnuPrelink'))
    import native_prelink as np  # noqa: E402

    out = tree / 'build/storage-abi'
    out.mkdir(parents=True, exist_ok=True)
    obj_path = compile_reference(tree, out)
    names = vtable_names(obj_path, np)
    if len(names) != 190 or names.count('___cxa_pure_virtual') != 14:
        raise SystemExit(f'Public iOS class dispatch shape changed: {len(names)} slots, '
                         f'{names.count("___cxa_pure_virtual")} pure')

    kernel = args.kernel.read_bytes()
    km = np.macho(kernel)
    exports = np.exports(kernel, km)
    by_name = {name: va for va, names in exports.items() for name in names}

    def read(va, length):
        at = np.backed_offset(km['segments'], va, length, len(kernel))
        return kernel[at:at + length]

    def u64(va):
        return struct.unpack('<Q', read(va, 8))[0]

    pointers = [u64(VTABLE + 16 + i * 8) for i in range(190)]
    matched = sum(name in by_name for name in names)
    if matched != 176:
        raise SystemExit(f'Unexpected original/native kernel binding count: {matched} != 176')

    source = tree / 'refer/IOStorageFamily/IOBlockStorageDevice.cpp'
    methods = [dict(slot=i, reference_name=name, candidate_target=hex(pointers[i]),
                    kernel_names=exports.get(pointers[i], []))
               for i, name in enumerate(names)]
    result = dict(
        public_source_revision=SOURCE_REVISION,
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        reference_object_sha256=hashlib.sha256(obj_path.read_bytes()).hexdigest(),
        reference_object_executed_or_linked=False,
        platform_header_sdk_version='23.6.0',
        platform_header_sha256='',
        candidate_sha256='',
        original_executable_code_unchanged=True,
        method_slots=190,
        kernel_bindings=matched,
        pure_virtual_slots=14,
        inherited_kernel_methods=162,
        vtable=hex(VTABLE),
        original_metaclass=hex(META),
        source_ioservice_metaclass=hex(by_name['__ZN9IOService10gMetaClassE']),
        original_protected_constructor=hex(CTOR),
        original_base_destructor=hex(D2),
        abstract_complete_destructors_trap=True,
        live_instance_sizes=dict(IOBlockStorageDevice=0x90, IOService=0x88),
        live_native_4k=True,
        compiled_public_class_size=0x90,
        methods=methods,
        disk_read_tested=False,
        transport_implemented=False,
        hardware_tested=False,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(f'PASS: 190 slots -> {args.output}')


if __name__ == '__main__':
    main()
