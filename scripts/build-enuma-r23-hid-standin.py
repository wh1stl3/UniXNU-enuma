#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Replay the r22 link and package, adding only a software HID stand-in (WSL)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import struct
import subprocess
import sys
import tomllib
from types import SimpleNamespace

sys.dont_write_bytecode = True
R = runpy.run_path(str(Path(__file__).with_name('build-enuma-r22-memory-window.py')))
DEVICE, BASE, R21, BASE_PIN = (R[k] for k in ('DEVICE', 'BASE', 'R21', 'BASE_PIN'))
R22 = R['NEW']
INPUT = R21 / 'self-check/build-final'
R19 = R21.with_name(R21.name.removesuffix('21') + '19') / 'self-check/build-final'
OUT = DEVICE / 'out'
HID_PIN = '71a40e76daeae1bb4127546f96ffa7339c7a06ff'
HID_HASH = '7e4c5104814f2e773d5be13d092dec53ee44ba5a61a81264b229780406e86b72'
TOKEN = 'sheng-touch-hid=1'
ROOTS = ['com.apple.iokit.IOHIDFamily', 'com.apple.iokit.IOHIDEventDriver']
SYMBOLS = ['_enuma_hid_standin_start', '_native_hid_input_allocate',
           '_native_hid_live_checkpoint', '_native_touch_set_sink',
           '__GLOBAL__sub_I_NativeHidInput.cpp', '__ZTV14NativeHidInput']
STRINGS = ['enuma HID stand-in: IOHIDFamily=%d IOHIDEventDriver=%d\n',
           'enuma HID stand-in: IOHIDResource=%s\n',
           'enuma HID stand-in: init=%d attach=%d start=%d\n',
           'enuma HID stand-in: digitizer properties=%d\n',
           'Offline HID input probe', 'sheng-touch-hid']

sys.path[:0] = [str(BASE / 'scripts'), str(BASE / 'kits/XnuPrelink')]
from native_prelink import backed_offset, exports, macho
from unixnu import bootimg, payload as payload_step
from unixnu.cli import parser
from unixnu.config import Context
from unixnu.kernel import linux_env


def json_file(path):
    return json.loads(path.read_text())


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def artifact(path):
    return {'bytes': path.stat().st_size, 'sha256': R['digest'](path)}


def run(argv, cwd, env, log):
    result = subprocess.run(list(map(str, argv)), cwd=cwd, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log.write_text(result.stdout)
    if result.returncode:
        first = next((s for s in result.stdout.splitlines() if 'error:' in s.lower()),
                     result.stdout.partition('\n')[0])
        raise SystemExit(f'{log.name}: {first} (exit {result.returncode}; {log})')
    print(log.stem, flush=True)
    return result.stdout


def sections(image):
    return [s for segment in image['segments'] for s in segment['sections']]


def symbols(blob, image):
    cmd = next(at for kind, at, _ in image['commands'] if kind == 2)
    table, count, strings, _ = struct.unpack_from('<4I', blob, cmd + 8)
    result = []
    for i in range(count):
        ix, kind, section, _, va = struct.unpack_from('<IBBHQ', blob, table + i * 16)
        name = blob[strings + ix:blob.index(b'\0', strings + ix)].decode()
        result.append((name, kind, section, va))
    return table, result


def view(blob, image):
    def read(va, length):
        offset = backed_offset(image['segments'], va, length, len(blob))
        return blob[offset:offset + length]
    return read


def check_donor(path, plan):
    # ABI gates from UniXNU build-sheng-hid-input.py, also used by Orange Pi 5.
    blob = path.read_bytes()
    assert sha(blob) == plan['candidate_sha256']
    assert ROOTS[0] in plan['components'] and ROOTS[1] in plan['codeless_components']
    image = macho(blob)
    read = view(blob, image)
    names = {name: va for va, ns in exports(blob, image).items() for name in ns}
    extent, = [x for x in plan['extents'] if x['module'] == ROOTS[0] and x['segment'] == '__TEXT_EXEC']
    assert sha(read(extent['va'], extent['size'])) == plan['original_executable_sha256'][ROOTS[0]] == HID_HASH
    vptr = 0xfffffff005d045c0
    methods = struct.unpack('<207Q', read(vptr, 207 * 8))
    base = struct.unpack('<168Q', read(names['__ZTV9IOService'] + 16, 168 * 8))
    assert [i for i in range(168) if methods[i] != base[i]] == [
        0, 1, 7, 12, 14, 21, 23, 76, 81, 82, 86, 87, 91, 92, 93, 101, 132, 140]
    assert all(methods) and [i for i, va in enumerate(methods) if va == names['___cxa_pure_virtual']] == [180]
    assert read(vptr + 207 * 8, 24) == bytes(24)
    assert read(0xfffffff004ad94f8, 0x20).hex() == 'fd7bbfa9fd0300912bd90094489100f008011791080000f9fd7bc1a8c0035fd6'
    assert struct.unpack('<2Q', read(0xfffffff005d00f10, 16)) == (
        names['__ZN9IOServiceC2EPK11OSMetaClass'], names['__ZN9IOServiceD2Ev'])
    assert read(0xfffffff004ad9aec, 0x34).hex() == (
        '680240f908a142f9e00313aae10314aa00013fd6680240f9603d003608d142f9e1630091e00313aa00013fd6a02d0035e00f40f9')
    assert methods[181] == 0xfffffff004add0c4
    assert read(0xfffffff004add110, 28).hex() == '680240f9081543f9e00313aae20316aae30315aae40314aa00013fd6'
    fixed = {'__ZN11IOHIDDeviceC2EPK11OSMetaClass': 0xfffffff004ad94f8,
             '__ZN11IOHIDDeviceD2Ev': 0xfffffff004ad9518,
             '__ZN11IOHIDDevice10gMetaClassE': 0xfffffff006ae6fa0,
             '__ZTV11IOHIDDevice': vptr - 16}
    return names, methods, fixed, read


def abi_header():
    # Same 208-byte IOHIDDevice contract as build-sheng-hid-input.py.
    header = '''// Generated from the qualified original image; opaque private storage only.
#pragma once
#include <IOKit/IOService.h>
#include <IOKit/IOMemoryDescriptor.h>
class IOHIDDevice : public IOService {
 OSDeclareAbstractStructors(IOHIDDevice)
 unsigned char originalPrivate[0xd0-sizeof(IOService)];
public:
 using IOService::setProperty;
 IOReturn Dispatch(IORPC) override;
 void free() override;
 bool init(OSDictionary *properties=nullptr) override;
 bool setProperty(const OSSymbol *,OSObject *) override;
 bool willTerminate(IOService *,IOOptionBits) override;
 IOReturn configureReport(IOReportChannelList *,IOReportConfigureAction,void *,void *) override;
 IOReturn updateReport(IOReportChannelList *,IOReportUpdateAction,void *,void *) override;
 bool start(IOService *) override;
 void stop(IOService *) override;
 bool handleOpen(IOService *,IOOptionBits,void *) override;
 void handleClose(IOService *,IOOptionBits) override;
 bool handleIsOpen(const IOService *) const override;
 bool matchPropertyTable(OSDictionary *,SInt32 *) override;
 IOReturn message(UInt32,IOService *,void *) override;
 IOReturn newUserClient(task_t,void *,UInt32,OSDictionary *,IOUserClient **) override;
'''
    declarations = {
        171: 'OSString *newTransportString() const',
        173: 'OSString *newProductString() const',
        180: 'IOReturn newReportDescriptor(IOMemoryDescriptor **) const=0',
        181: 'IOReturn handleReport(IOMemoryDescriptor *,unsigned,IOOptionBits)',
    }
    for slot in range(168, 207):
        header += f' virtual {declarations.get(slot, f"void opaque{slot}()")};\n'
    return header + '};\nstatic_assert(sizeof(IOHIDDevice)==0xd0,"Original device instance size");\n'


def check_object(raw, donor):
    image = macho(raw)
    _, syms = symbols(raw, image)
    vt, = [va for name, _, _, va in syms if name == '__ZTV14NativeHidInput']
    sec, = [s for s in sections(image) if s['va'] <= vt < s['va'] + s['size']]
    rels = {}
    start, count = struct.unpack_from('<2I', raw, sec['command_offset'] + 56)
    for i in range(count):
        offset, bits = struct.unpack_from('<2I', raw, start + 8 * i)
        if bits >> 27 & 1 and bits >> 28 == 0 and bits >> 25 & 3 == 3:
            rels[sec['va'] + offset] = syms[bits & 0xffffff][0]
    table = [rels[vt + 16 + i * 8] for i in range(207)]
    assert vt + 16 + 207 * 8 not in rels
    names, methods, fixed, _ = donor
    bindings, owned = dict(fixed), []
    for slot, name in enumerate(table):
        if name.startswith(('__ZN14NativeHidInput', '__ZNK14NativeHidInput')):
            owned.append(slot)
        elif '11IOHIDDevice' in name:
            bindings[name] = methods[slot]
        else:
            assert slot < 168 and names[name] == methods[slot], slot
    assert owned == [0, 1, 7, 14, 86, 87, 111, 171, 173, 180]
    assert {name for name, kind, _, _ in syms if kind == 1 and '11IOHIDDevice' in name} == bindings.keys()
    return bindings, table, owned


def late_init(path):
    # Linux llvm-objcopy cannot globalize Mach-O symbols. Like the Orange Pi
    # builder, keep DYSYMTAB ranges and external relocation indexes coherent.
    blob = bytearray(path.read_bytes())
    image = macho(blob)
    table, entries = symbols(blob, image)
    dys = next(at for kind, at, _ in image['commands'] if kind == 0xb)
    local, count, ext, next_, _, _ = struct.unpack_from('<6I', blob, dys + 8)
    i, = [i for i, (name, _, _, _) in enumerate(entries) if name == SYMBOLS[4]]
    last = local + count - 1
    assert local <= i <= last and ext == last + 1 and entries[i][1] == 0x0e
    a, b = table + 16 * i, table + 16 * last
    if i != last:
        blob[a:a+16], blob[b:b+16] = blob[b:b+16], blob[a:a+16]
        remap = {i: last, last: i}
        for section in sections(image):
            start, n = struct.unpack_from('<2I', blob, section['command_offset'] + 56)
            for at in range(start, start + 8 * n, 8):
                offset, bits = struct.unpack_from('<2I', blob, at)
                assert not offset >> 31
                if bits >> 27 & 1 and (index := bits & 0xffffff) in remap:
                    struct.pack_into('<I', blob, at + 4, bits & ~0xffffff | remap[index])
        start, n = struct.unpack_from('<2I', blob, dys + 56)
        for at in range(start, start + 4 * n, 4):
            index, = struct.unpack_from('<I', blob, at)
            if index in remap:
                struct.pack_into('<I', blob, at, remap[index])
    blob[b + 4] |= 1
    struct.pack_into('<4I', blob, dys + 8, local, count - 1, last, next_ + 1)
    assert not any(s['name'] == '__mod_init_func' for s in sections(image))
    path.write_bytes(blob)


def compile_cxx(record, src, obj, objdir, call):
    args = iter(record['arguments'])
    cmd = []
    for arg in args:
        if arg == record['file']:
            cmd.append(src)
        elif arg == '-o':
            next(args)
            cmd.extend((arg, obj))
        elif arg in ('-MF', '-MQ', '-MT', '-MJ'):
            next(args)
        elif arg not in ('-MD', '-MMD', '-MP') and (not arg.startswith('-W') or arg.startswith('-Wno-')):
            cmd.append(arg)
    assert '--target=arm64-apple-ios17.0' in cmd
    cmd.extend(('-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter',
                '-Wno-unnecessary-virtual-specifier', '-Wno-c99-designator',
                '-Wno-reorder-init-list', '-Wno-deprecated-enum-enum-conversion', '-I', objdir))
    call(obj.stem, cmd, record['directory'])


def build(out, hid_source, dtb):
    before = json_file(R22 / 'candidate-manifest.json')
    assert before['artifacts']['boot.img']['sha256'] == '646e7d8dd2d1d3e4ae25d02c9b34cced7e1a1e7f20f34506cc9437b34fb360e7'
    assert all(artifact(R22 / n) == info for n, info in before['artifacts'].items())
    assert artifact(R22 / Path(R['ADT']).name) == before['fat_members'][R['ADT']]
    assert subprocess.check_output(['git', '-C', BASE, 'rev-parse', 'HEAD'], text=True).strip() == BASE_PIN
    assert subprocess.check_output(['git', '-C', hid_source, 'rev-parse', 'HEAD'], text=True).strip() == HID_PIN
    source_bytes = subprocess.check_output(['git', '-C', hid_source, 'show', HID_PIN + ':NativeHidInput.cpp'])
    assert source_bytes.startswith(b'// SPDX-License-Identifier: BSD-2-Clause-Patent\n')
    frozen_paths = [p for p in R22.rglob('*') if p.is_file()]
    frozen_paths += [INPUT / 'native.macho', INPUT / 'prelink.macho',
                     INPUT / 'source/bsd/kern/kern_exec.c', INPUT / 'link.filelist']
    frozen = R['snapshot'](frozen_paths)
    for rel in ('native.macho', 'prelink.macho'):
        assert frozen[str(INPUT / rel)] == before['r21_pins_unchanged']['self-check/build-final/' + rel]
    pins = {Path(line.split('  ', 1)[1]): line.split('  ', 1)[0]
            for line in (R22 / 'r21-link-inputs.sha256').read_text().splitlines()}
    assert R['snapshot'](pins) == {str(path): digest for path, digest in pins.items()}
    r22_plan = json_file(INPUT / 'prelink.json')
    donor = check_donor(INPUT / 'prelink.macho', r22_plan)
    old_kernel = json_file(INPUT / 'kernel-build-result.json')
    steps = {entry['tag']: entry for entry in old_kernel['r13_delta']['steps']}
    tree = Path(steps['link']['cwd']).parents[3]
    record = json.loads((Path(steps['link']['cwd']) /
                         'iokit/DEVELOPMENT/IOPlatformExpert.cpo.json').read_text().strip().rstrip(','))
    env = {**os.environ, **linux_env(SimpleNamespace(tree=tree)),
           'PYTHONDONTWRITEBYTECODE': '1'}
    env.update(PATH='/home/wh1stl3/.local/bin:' + env['PATH'], TMPDIR=str(out / 'tmp'))
    for n in ('objects', 'logs', 'tmp', 'source/bsd/kern', 'device'):
        (out / n).mkdir(parents=True, exist_ok=True)

    def call(tag, argv, cwd=out):
        return run(argv, cwd, env, out / 'logs' / (tag + '.log'))

    objdir = out / 'objects'
    source = out / 'source/NativeHidInput.cpp'
    source.write_bytes(source_bytes)
    (out / 'source/LICENSE.ShengHidInput').write_bytes(
        subprocess.check_output(['git', '-C', hid_source, 'show', HID_PIN + ':LICENSE']))
    (objdir / 'OriginalHidDeviceABI.h').write_text(abi_header())
    obj, late = [objdir / n for n in ('NativeHidInput.o', 'NativeHidInput.late.o')]
    publisher, binding_obj = [objdir / n for n in ('EnumaHidStandin.o', 'hid-original-bindings.o')]
    compile_cxx(record, source, obj, objdir, call)
    compile_cxx(record, DEVICE / 'package/EnumaHidStandin.cpp', publisher, objdir, call)
    raw = obj.read_bytes()
    bindings, vtable, owned = check_object(raw, donor)
    asm = objdir / 'original-bindings.S'
    asm.write_text(''.join(f'.globl {name}\n.set {name}, {va:#x}\n' for name, va in sorted(bindings.items())))
    call('bindings', [record['arguments'][0], '--target=arm64-apple-ios17.0', '-c', asm, '-o', binding_obj])
    call('remove-auto-init', ['llvm-objcopy', '--remove-section=__DATA,__mod_init_func', obj, late])
    late_init(late)
    linked = late.read_bytes()
    assert check_object(linked, donor) == (bindings, vtable, owned)

    def text(blob):
        s, = [s for s in sections(macho(blob)) if s['name'] == '__text']
        return blob[s['fileoff']:s['fileoff'] + s['size']]

    assert text(linked) == text(raw)
    archive = objdir / 'libShengHidInputStandin.a'
    call('archive', ['llvm-ar', 'rcsD', archive, late, binding_obj, publisher])
    assert call('archive-members', ['llvm-ar', 't', archive]).splitlines() == [p.name for p in (late, binding_obj, publisher)]
    original = (INPUT / 'source/bsd/kern/kern_exec.c').read_bytes()
    anchor = b'\t(void) sheng_boot_watchdog_policy(p, (uint64_t)scratch_addr);\n'
    assert original.count(anchor) == 1 and b'\nload_init_program(proc_t p)' in original[:original.index(anchor)]
    exec_source = out / 'source/bsd/kern/kern_exec.c'
    exec_source.write_bytes(original.replace(anchor, anchor +
        b'\textern void enuma_hid_standin_start(void);\n\tenuma_hid_standin_start();\n'))
    for local in (INPUT / 'source/bsd/kern').iterdir():
        if local == INPUT / 'source/bsd/kern/kern_exec.c':
            continue
        if local.is_file():
            shutil.copyfile(local, exec_source.parent / local.name)
    cc = steps['compile-kern_exec.o']
    argv = list(cc['argv'])
    assert argv[1] == '-xc' and Path(argv[2]).name == 'kern_exec.c' and argv[3] == '-o'
    exec_obj = objdir / 'kern_exec.o'
    argv[2], argv[4] = exec_source, exec_obj
    call('kern_exec', argv, cc['cwd'])
    paths = [Path(line) for line in (INPUT / 'link.filelist').read_text().splitlines()]
    replaced, = [path for path in paths if path.name == 'kern_exec.o']
    assert all(path in pins for path in paths)
    (out / 'link.filelist').write_text('\n'.join(str(exec_obj if path == replaced else path) for path in paths) + '\n')
    watch_archive = R19 / 'objects/libEnumaBootWatchdogPolicy.a'
    assert R['digest'](watch_archive) == pins[INPUT / 'objects' / watch_archive.name]
    for tag in ('link', 'prelink'):
        step = steps[tag]
        origin = Path(steps['prelink']['cwd'])
        argv = step['argv']
        for name in ('link.filelist', 'native.macho', 'native-link.map', 'prelink.macho'):
            argv = [arg.replace(str(origin / name), str(out / name)) for arg in argv]
        if tag == 'link':
            argv += [f'-Wl,-force_load,{path}' for path in (watch_archive, archive)]
        call(tag, argv, out if tag == 'prelink' else step['cwd'])
    final = {}
    for name in ('native.macho', 'prelink.macho'):
        path = out / name
        assert not call('undefined-' + name, ['llvm-nm', '-u', path]).strip()
        blob = path.read_bytes()
        image = macho(blob)
        _, syms = symbols(blob, image)
        syms = [sym for sym in syms if not sym[1] & 0xe0]  # Exclude N_STAB debug entries.
        assert not [sym for sym in syms if sym[1] & 0x0e == 0], 'Undefined Mach-O symbol, including weak'
        assert all(sum(n == s for n, _, _, _ in syms) == 1 for s in SYMBOLS)
        meta_sec, = [sec for n, _, sec, _ in syms if n == '__ZN14NativeHidInput10gMetaClassE']
        assert sections(image)[meta_sec - 1]['name'] in ('__bss', '__data', '__common')
        counts = {s: blob.count(s.encode() + b'\0') for s in STRINGS}
        assert all(counts.values())
        dump = call('call-' + name, ['llvm-objdump', '-d', '--disassemble-symbols=_load_init_program', path])
        assert len(re.findall(r'\bbl\s+[^\n]*<_enuma_hid_standin_start>', dump)) == 1
        assert dump.index('<_sheng_boot_watchdog_policy>') < dump.index('<_enuma_hid_standin_start>')
        final[name] = {'old': artifact(INPUT / name), 'new': artifact(path), 'format_counts': counts,
                       'symbols_once': SYMBOLS, 'undefined_including_weak': 0, 'post_watchdog_calls': 1}
    plan = json_file(out / 'prelink.json')
    assert plan['components'] == r22_plan['components']
    assert plan['codeless_components'] == r22_plan['codeless_components']
    assert plan['original_executable_sha256'] == r22_plan['original_executable_sha256']
    names, methods, new_fixed, read = check_donor(out / 'prelink.macho', plan)
    assert all(names[name] == va for name, va in new_fixed.items())
    assert all(names[name] == va for name, va in bindings.items())
    definitions = {n: va for n, _, _, va in syms}
    actual = struct.unpack('<207Q', read(names['__ZTV14NativeHidInput'] + 16, 207 * 8))
    assert all(entry == (definitions[name] if slot in owned else methods[slot])
               for slot, (entry, name) in enumerate(zip(actual, vtable)))

    result = package(out, before, dtb)
    assert frozen == R['snapshot'](map(Path, frozen)), 'r22 artifact or r21 kernel input changed'
    assert R['snapshot'](pins) == {str(path): digest for path, digest in pins.items()}
    assert subprocess.check_output(['git', '-C', BASE, 'rev-parse', 'HEAD'], text=True).strip() == BASE_PIN
    result.update(status='self-checked; host only', base=BASE_PIN, hid_revision=HID_PIN,
                  hid_source=artifact(source), hid_text_hash=HID_HASH, abi_slots=len(vtable), binding_count=len(bindings),
                  owned_slots=owned, r22_files_untouched=len(frozen_paths) - 4, r21_link_inputs_untouched=len(pins),
                  opt_in=TOKEN, outputs=final,
                  kern_exec_old=artifact(replaced), kern_exec_new=artifact(exec_obj),
                  unchanged_filelist_entries=len(paths)-1,
                  archive_and_objects={p.name: artifact(p) for p in (archive, publisher, obj, late, binding_obj)})
    write_json(out / 'candidate-manifest.json', result)
    print(json.dumps(result, indent=2))


def package(out, before, dtb):
    # r22 already ran the official ADT generator. Keep its output byte for byte.
    board = (R22 / 'device/board.toml').read_bytes()
    original_args = tomllib.loads(board.decode())['payload']['kernel_args']
    old = (R22 / 'payload.img')
    fat = R['fat_tree'](old)
    old_config = R['read_member'](old, 'unixnu.toml')
    actual, = [e for e in tomllib.loads(old_config.decode())['entry'] if e['id'] == 'xnu']
    assert actual['args'].split() == original_args and TOKEN not in original_args
    arg_text = actual['args'].encode() + b'"'
    assert old_config.count(arg_text) == 1
    config = out / 'unixnu.toml'
    config.write_bytes(old_config.replace(arg_text, arg_text[:-1] + b' ' + TOKEN.encode() + b'"'))
    assert board.count(b'"sheng-lite=1"]') == 1
    (out / 'device/board.toml').write_bytes(
        board.replace(b'"sheng-lite=1"]', b'"sheng-lite=1", "' + TOKEN.encode() + b'"]'))
    payload = out / 'payload.img'
    shutil.copyfile(old, payload)
    env = dict(os.environ, MTOOLS_SKIP_CHECK='1', TZ='UTC')
    for source, member in ((config, 'unixnu.toml'), (out / 'prelink.macho', R['MEMBERS'][0])):
        os.utime(source, (payload_step.EPOCH, payload_step.EPOCH))
        subprocess.run(['mcopy', '-o', '-m', '-i', payload, source, '::/EFI/UniXNU/' + member], check=True, env=env)
    assert payload.stat().st_size == old.stat().st_size and R['fat_tree'](payload) == fat
    after = {n: R['read_member'](payload, n) for n in R['MEMBERS']}
    readback = {n: {'bytes': len(data), 'sha256': sha(data)} for n, data in after.items()}
    changed = [n for n in readback if readback[n] != before['fat_members'][n]]
    assert set(changed) == {R['MEMBERS'][0], 'unixnu.toml'}
    assert readback[R['MEMBERS'][0]] == artifact(out / 'prelink.macho')
    assert after['unixnu.toml'] == config.read_bytes()
    assert after[R['ADT']] == (R22 / 'kernel.macho.adt').read_bytes()
    adt = R['read_properties'](after[R['ADT']])
    assert adt[R['SIZE_KEY']] == struct.pack('<Q', 0xaa000000) and adt[R['SLEEP_KEY']] == struct.pack('<I', 1)
    local = R21 / 'self-check-package/packaging/local-build.toml'
    uefi = DEVICE.parent / 'uefi-enuma'
    fd = uefi / 'Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd'
    ref = json_file(R21 / 'self-check-package/boot.json')
    assert R['digest'](fd) == ref['fd_sha256'] and R['digest'](dtb) == ref['dtb_sha256']
    ctx = Context(parser().parse_args([
        'bootimg', '-D', str(out / 'device'), '--out', str(out / 'work'), '--config', str(local),
        '--local-module', 'soc:sm8250=' + str(DEVICE.parent / 'UniXNU-sm8250-common'),
    ]))
    boot = out / 'boot.img'
    bootimg.build(ctx, uefi, fd, dtb, payload, boot)
    offset = before['boot_payload_offset']
    with boot.open('rb') as new, (R22 / 'boot.img').open('rb') as prior:
        a, b = new.read(offset), prior.read(offset)
        assert a[:576] == b[:576] and a[596:] == b[596:] and a[576:596] != b[576:596]
        assert hashlib.file_digest(new, 'sha256').hexdigest() == R['digest'](payload)
    assert boot.stat().st_size == (R22 / 'boot.img').stat().st_size
    return dict(old_artifacts=before['artifacts'], artifacts={p.name: artifact(p) for p in (boot, payload)},
                fat_members=readback, changed_fat_members=changed, boot_payload_offset=offset,
                adt_r22_byte_identical=True, memory_size_from_payload='0xaa000000', sleep_disabled_from_payload=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=OUT / 'ufs-sm8250-launchd-hid-20261122-r23')
    ap.add_argument('--hid-source', required=True, type=Path, help='ShengHidInput Git checkout at the catalog pin')
    ap.add_argument('--dtb', required=True, type=Path, help='same Android boot DTB as r22')
    args = ap.parse_args()
    out = args.out.resolve()
    assert OUT in out.parents and not out.exists()
    build(out, args.hid_source.resolve(), args.dtb.resolve())


if __name__ == '__main__':
    main()
