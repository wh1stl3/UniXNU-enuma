#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
# Adapted from UniXNU contributors' build-sheng-platform-power.py at
# 6bc0ce1e8c3a3733110a80dd80ddfb2a1ca46555; see package/PMGR-NOTICE.md.
"""Build a guarded PMGR archive using explicit, hash-bound Linux inputs."""
import argparse
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('pmgr_contract', HERE / 'audit-enuma-pmgr-contract.py')
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def run(command, **kwargs):
    return subprocess.check_output([str(v) for v in command], timeout=120, **kwargs)


def build(args):
    out = args.tree / 'build/sheng-platform-power'
    out.mkdir(parents=True, exist_ok=True)
    args.output = out / 'contract'
    contract.audit(args)
    sys.path.insert(0, str(args.base / 'kits/XnuPrelink'))
    from native_prelink import macho, backed_offset, exports
    sys.path.insert(0, str(args.base / 'scripts'))
    from kernel_target import DEPLOYMENT, TRIPLE, check_object
    header = '''// Generated storage/slot ABI; private fields stay opaque.
#pragma once
#include <IOKit/IOPMGR.h>
class ApplePMGR : public IOPMGR {
 OSDeclareAbstractStructors(ApplePMGR)
 unsigned char originalPrivate[0x4b8a8-sizeof(IOPMGR)];
public:
'''
    guards = ''
    for slot in range(177, 340):
        if slot == 320:
            header += ' virtual uint32_t readAon();\n'
        elif slot == 321:
            header += ' virtual void writeAon(uint64_t);\n'
        else:
            header += f' virtual void opaque{slot}() = 0;\n'
            guards += f' void opaque{slot}() override {{ unavailable({slot}); }}\n'
    header += '};\nstatic_assert(sizeof(ApplePMGR)==0x4b8a8,"Original provider storage");\n'
    (out / 'OriginalPMGRABI.h').write_text(header)
    (out / 'GuardedPMGRSlots.inc').write_text(guards)
    source = args.source
    record = json.loads(args.compile_record.read_text().strip().rstrip(','))
    require(Path(record['file']).name == 'IOPlatformExpert.cpp', 'Require actual IOPlatformExpert record')
    obj = out / 'ShengPlatformPower.o'
    arguments = record['arguments']
    command, i = [], 0
    while i < len(arguments):
        arg = arguments[i]
        if arg == record['file']:
            command.append(source)
        elif arg == '-o':
            command += ['-o', obj]
            i += 1
        elif arg in ('-MF', '-MT', '-MQ', '-MJ'):
            i += 1  # Do not overwrite the original compile/dependency records.
        elif arg in ('-MD', '-MMD', '-MP'):
            pass
        elif arg.startswith('-W') and not arg.startswith('-Wno-'):
            pass  # Keep Linux header suppressions, not XNU's -Weverything.
        else:
            command.append(arg)
        i += 1
    require('--target=arm64-apple-ios17.0' in command or '--target=arm64-apple-ios17.0.0' in command,
            'Require actual arm64 iOS17 compile target')
    command += ['-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter', '-Wno-c99-designator',
                '-Wno-reorder-init-list', '-Wno-deprecated-enum-enum-conversion',
                '-Wno-unnecessary-virtual-specifier', '-I', out, '-I', args.tree / '.cache/xnu-work/osfmk']
    command += [arg for arg in arguments if arg.startswith('-Wno-')]
    run(command, cwd=record['directory'])
    raw = obj.read_bytes()
    check_object(raw, 'PMGR provider')
    info = macho(raw)
    sym_at = next(at for cmd, at, _ in info['commands'] if cmd == 2)
    at, count, strings, _ = struct.unpack_from('<4I', raw, sym_at + 8)
    symbols = []
    for i in range(count):
        ix, kind, section, _, address = struct.unpack_from('<IBBHQ', raw, at + i * 16)
        symbols.append((raw[strings + ix:raw.index(b'\0', strings + ix)].decode(), address, kind, section))
    vtable = next(va for name, va, _, _ in symbols if name == '__ZTV18ShengPlatformPower')
    relocations = {}
    sections = [s for seg in info['segments'] for s in seg['sections']]
    for section in sections:
        if section['va'] <= vtable < section['va'] + section['size']:
            at, count = struct.unpack_from('<2I', raw, section['command_offset'] + 56)
            for i in range(count):
                offset, bits = struct.unpack_from('<2I', raw, at + i * 8)
                if bits >> 27 & 1 and bits >> 28 == 0 and bits >> 25 & 3 == 3:
                    relocations[section['va'] + offset] = symbols[bits & 0xffffff][0]
    entries = [relocations.get(vtable + 16 + i * 8) for i in range(340)]
    require(all(entries) and vtable + 16 + 340 * 8 not in relocations, 'Exact 340-entry provider table required')
    candidate = args.candidate.read_bytes()
    meta = macho(candidate)
    native = {n: va for va, names in exports(candidate, meta).items() for n in names}

    def pointer(va):
        return struct.unpack_from('<Q', candidate, backed_offset(meta['segments'], va, 8, len(candidate)))[0]

    bindings = {'__ZN9ApplePMGRC2EPK11OSMetaClass': 0xfffffff0049f003c,
                '__ZN9ApplePMGRD2Ev': 0xfffffff0049f019c,
                '__ZN9ApplePMGR10gMetaClassE': 0xfffffff006adf490}
    for slot, name in enumerate(entries):
        if slot in (0, 1, 7) or 168 <= slot < 340 and slot not in (320, 321):
            require('18ShengPlatformPower' in name, f'Own lifecycle/guard required at slot {slot}')
        elif slot in (320, 321):
            require('9ApplePMGR' in name, f'Original AON required at slot {slot}')
            bindings[name] = pointer(0xfffffff005ce26d8 + slot * 8)
        else:
            require(native.get(name) == pointer(native['__ZTV6IOPMGR'] + 16 + slot * 8),
                    f'Native IOPMGR slot {slot} differs')
    undefined = {n for n, _, kind, _ in symbols if kind == 1 and 'ApplePMGR' in n}
    require(undefined == set(bindings), 'All and only original base imports must be bound')
    bindings.update({'_sheng_original_pmgr_nub_create': 0xfffffff004a22568,
                     '_sheng_original_pmgr_nub_read': 0xfffffff004a24adc,
                     '_sheng_original_pmgr_nub_write': 0xfffffff004a230ec})
    asm = out / 'original-bindings.S'
    asm.write_text(''.join(f'.globl {name}\n.set {name}, {va:#x}\n' for name, va in bindings.items()))
    run([arguments[0], '-target', TRIPLE, '-c', asm, '-o', out / 'original-bindings.o'])
    late = out / 'ShengPlatformPower.late.o'
    require(sum(s['name'] == '__mod_init_func' for s in sections) == 1, 'Exactly one object initializer section required')
    run(['llvm-objcopy', '--remove-section=__DATA,__mod_init_func', obj, late])
    # Linux llvm-objcopy cannot globalize Mach-O symbols. Change only N_EXT
    # on this object's named initializer, after section removal.
    converted = late.read_bytes()
    converted_info = macho(converted)
    sym_cmd = next(at for cmd, at, _ in converted_info['commands'] if cmd == 2)
    sym_off, sym_count, str_off, _ = struct.unpack_from('<4I', converted, sym_cmd + 8)
    targets = []
    for index in range(sym_count):
        entry = sym_off + index * 16
        string = struct.unpack_from('<I', converted, entry)[0] + str_off
        if converted[string:converted.index(b'\0', string)] == b'__GLOBAL__sub_I_ShengPlatformPower.cpp':
            targets.append(entry + 4)
    require(len(targets) == 1, 'Exactly one manual initializer symbol required')
    patched = bytearray(converted)
    require(patched[targets[0]] & 0x0e == 0x0e, 'Initializer must be section-defined')
    patched[targets[0]] |= 1
    require([i for i, (a, b) in enumerate(zip(converted, patched)) if a != b] == targets,
            'Initializer globalization must change only its N_EXT bit')
    late.write_bytes(patched)
    late_raw = late.read_bytes()
    late_info = macho(late_raw)
    check_object(late_raw, 'Late PMGR provider')
    late_sections = [s for seg in late_info['segments'] for s in seg['sections']]
    require(not any(s['name'] == '__mod_init_func' for s in late_sections), 'Automatic initializer remains')
    for section in sections:
        if section['name'] == '__text':
            other, = [s for s in late_sections if s['name'] == '__text']
            require(raw[section['fileoff']:section['fileoff'] + section['size']] ==
                    late_raw[other['fileoff']:other['fileoff'] + other['size']], 'Late conversion changed code')
    meta_section = next(sec for n, _, _, sec in symbols if n == '__ZN18ShengPlatformPower10gMetaClassE')
    require(sections[meta_section - 1]['name'] in ('__bss', '__data', '__common'), 'Late metaclass not in writable storage')
    archive = out / 'libShengPlatformPower.a'
    archive.unlink(missing_ok=True)
    run(['llvm-ar', 'rcs', archive, late, out / 'original-bindings.o'])
    report = {'status': 'self-checked', 'virtual_entries': entries,
              'bindings': {n: hex(va) for n, va in bindings.items()},
              'all_undefined_imports': [n for n, _, kind, _ in symbols if kind == 1],
              'source_sha256': contract.sha256(source), 'archive_sha256': contract.sha256(archive),
              'compile_record_sha256': contract.sha256(args.compile_record),
              'compile_command': [str(x) for x in command], 'deployment': DEPLOYMENT,
              'ownership_closure_qualified': False, 'runtime_qualified': False,
              'final_prelink_audited': False, 'release_allowed': False}
    (out / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('self-checked: guarded archive built; ownership/final prelink/review gates still required')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, help='Explicit local JSON object with every path and input SHA256')
    for name in ('tree', 'base', 'source', 'compile-record', 'donor', 'candidate', 'manifest'):
        parser.add_argument('--' + name, type=Path)
    for name in ('donor', 'candidate', 'manifest'):
        parser.add_argument('--' + name + '-sha256')
    args = parser.parse_args()
    if args.inputs:
        values = json.loads(args.inputs.read_text())
        require(set(values) == set(vars(args)) - {'inputs'}, 'Explicit input file must supply all and only builder inputs')
        for name, value in values.items():
            require(getattr(args, name) is None, f'Duplicate input: {name}')
            setattr(args, name, value if name.endswith('_sha256') else Path(value))
    for name, value in vars(args).items():
        if name != 'inputs' and value is None:
            parser.error(f'explicit {name} required; no fallback permitted')
    for name, value in vars(args).items():
        if isinstance(value, Path):
            setattr(args, name, value.resolve())
    try:
        build(args)
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f'PMGR build rejected: {error}\n')


if __name__ == '__main__':
    main()
