#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Replay the pinned r15 candidate with only kern_exec.o replaced (WSL root)."""
import json
import os
import re
import runpy
import shutil
import struct
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True
R = runpy.run_path(str(Path(__file__).with_name('build-enuma-r15-shared-region-probe.py')))
BASE, DEVICE, R13, R14, R15, PIN, RESULT = (R[k] for k in ('BASE', 'DEVICE', 'R13', 'R14', 'R15', 'PIN', 'RESULT'))
sha, describe, write_json, artifact_path = (R[k] for k in ('sha', 'describe', 'write_json', 'artifact_path'))
R16 = R15.with_name(R15.name.removesuffix('15') + '16')
OLD, NEW = (root / 'self-check/build-final' for root in (R15, R16))
SOURCE = Path('source/bsd/kern/kern_exec.c')
OBJECT = Path('objects/kern_exec.o')
RECIPE = 'run_packaging.py'
WRAPPER = 'r7-payload-wrapper.py'
TRUSTCACHE = Path('self-check-package/extracted/kernel.macho.trustcache')
FORMATS = (b'enuma-cpu: memcpy %u ns=%llu mbps=%llu\n\0', b'enuma-cpu: loop %u ns=%llu mops=%llu\n\0')


def run(tag, argv, cwd, env):
    proc = subprocess.run(list(map(str, argv)), cwd=cwd, env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log = NEW / 'logs' / f'{tag}.log'
    log.write_text(proc.stdout)
    if proc.returncode:
        first = next((s for s in proc.stdout.splitlines() if 'error:' in s.lower()),
                     proc.stdout.partition('\n')[0])
        raise SystemExit(f'{tag}: {first} (exit {proc.returncode}; {log})')
    print(tag, flush=True)
    return proc.stdout


def baseline():
    assert subprocess.check_output(['git', '-C', BASE, 'rev-parse', 'HEAD'], text=True).strip() == PIN
    data = json.loads((OLD / RESULT).read_text())
    manifest = json.loads((R15 / 'candidate-manifest.json').read_text())
    assert manifest['artifacts']['boot.img']['sha256'] == \
        '4224d84cef09f59f85f1cf795b1b112236445b19ec84a75bd18ca710fd5a2083'
    for name, info in manifest['artifacts'].items():
        assert describe(R15 / artifact_path(name)) == info, name
    assert sha(OLD / 'native.macho') == data['diff_vs_r4']['new_sha256']
    assert describe(OLD / 'prelink.macho') == manifest['artifacts']['self-check/kernel.macho']
    assert sha(R15 / RECIPE) == '84e767c46cd7f5f92d6a3cf5afadddee081a73dd3370911d4f6bcf2d752adbdd'
    assert sha(R15 / WRAPPER) == '2db5b7f1a215cdabf9394d0d47a2b03a23c6874d9de45bba38d884d36c21867a'
    names = [R15 / artifact_path(name) for name in manifest['artifacts']]
    names += [R15 / n for n in ('candidate-manifest.json', 'delta-vs-r14.json', RECIPE, WRAPPER, TRUSTCACHE)]
    names += [OLD / n for n in ('native.macho', 'prelink.macho', 'link.filelist', RESULT, 'seed-inspection.json')]
    names += sorted((OLD / 'objects').iterdir())
    return data, manifest, {str(p.relative_to(R15)): sha(p) for p in names}


def link_inputs(data):
    filelist = list(map(Path, (OLD / 'link.filelist').read_text().splitlines()))
    inputs = {Path(k): v for k, v in data['r13_delta']['unchanged_explicit_link_inputs'].items()}
    old_vm, = [p for p in filelist if p.name == 'vm_unix.o']
    original_vm, = [p for p in inputs if p.name == 'vm_unix.o']
    assert old_vm == OLD / 'objects/vm_unix.o'
    assert inputs.pop(original_vm) == data['r15_delta']['old_object']['sha256']
    inputs[old_vm] = data['r15_delta']['new_object']['sha256']
    old_obj = R14 / 'self-check/build-final' / OBJECT
    assert old_obj not in inputs and filelist.count(old_obj) == 1
    inputs[old_obj] = data['macros']['kern_exec.o']['object_sha256']
    assert inputs[old_obj] == '9c8a1211e2d9c3722f5512519d3dc942164ad56ff0dfe7f94bd811ca0bd6793c'
    assert sha(OLD / OBJECT) == inputs[old_obj]
    assert all(p in inputs for p in filelist)
    assert all(sha(p) == h for p, h in inputs.items())
    return filelist, inputs, old_obj


def audit(old_obj, new_obj, env):
    counts = {}
    for root, link, obj, expected in ((R15, OLD, old_obj, 0), (R16, NEW, new_obj, 1)):
        for path in (obj, link / 'native.macho', link / 'prelink.macho'):
            blob = path.read_bytes()
            formats = [blob.count(fmt) for fmt in FORMATS]
            assert formats == [expected, expected] and blob.count(b'enuma-cpu:') == 2 * expected, path
            for fmt in R['FORMATS']:
                assert blob.count(fmt) == (0 if path.suffix == '.o' else 1), path
            evidence = counts[f'{root.name[-3:]}/{path.name}'] = {'format_strings': formats}
            if path.suffix == '.o':
                continue
            tag = f'{root.name[-3:]}-{path.stem}'
            assert not run(f'undefined-{tag}', ['llvm-nm', '-u', path], NEW, env).strip()

            def asm(symbol):
                return run(f'disasm-{tag}-{symbol}', ['llvm-objdump', '-d',
                           f'--disassemble-symbols={symbol}', path], NEW, env)

            def branches(instructions):
                return re.findall(r'\b(?:b|bl)\s+\S+\s+<(_\w+)>', instructions)

            caller = branches(asm('_load_init_program'))
            assert caller.count('_enuma_cpu_probe') == expected
            evidence['load_init_program->enuma_cpu_probe'] = expected
            if expected:
                assert caller.count('_enuma_console_probe') == 1
                assert caller.index('_enuma_cpu_probe') == caller.index('_enuma_console_probe') + 1
                body = asm('_enuma_cpu_probe')
                calls = branches(body)
                # XNU's arm64 memcpy and memmove share a symbol address.
                nm = run(f'symbols-{tag}', ['llvm-nm', path], NEW, env)
                symbols = dict((name, addr) for addr, name in
                               re.findall(r'^([0-9a-f]+) \w (_\w+)$', nm, re.M))
                assert symbols['_memcpy'] == symbols['_memmove']
                expected_calls = (['_secure_memset'] * 2 + ['_mach_absolute_time', '_memmove'] +
                                  ['_mach_absolute_time'] * 3 + ['_absolutetime_to_nanoseconds'] * 2 +
                                  ['_printf'] * 2)
                assert calls == expected_calls, (path, calls)
                loop = re.search(r'\bmov\s+(w\d+), #57600\b.*\n'
                                 r'.*\bmovk\s+\1, #1525, lsl #16\b.*\n'
                                 r'([0-9a-f]+):.*\badd\s+(x\d+), \3, #1\b.*\n'
                                 r'.*\bror\s+\3, \3, #7\b.*\n'
                                 r'.*\bsubs\s+\1, \1, #1\b.*\n'
                                 r'.*\bb\.ne\s+0x\2\b', body)
                assert loop, path
                evidence['loop_iterations'] = 57600 + (1525 << 16)
                assert evidence['loop_iterations'] == 10**8
                evidence['enuma_cpu_probe_calls_in_order'] = calls
                src, dst = (int(symbols['_enuma_cpu_' + n], 16) for n in ('src', 'dst'))
                assert abs(src - dst) >= 2**23 and (src | dst) % 64 == 0
                segment = layout(path)['__DATA']
                va = int(segment['va'], 16)
                assert va + segment['file_bytes'] <= min(src, dst)
                assert max(src, dst) + 2**23 <= va + segment['vm_bytes']
                evidence['zero_fill_buffers'] = dict(src=hex(src), dst=hex(dst), bytes_each=2**23)
    return counts


def layout(path):
    blob = path.read_bytes()
    magic, _, _, _, count = struct.unpack_from('<5I', blob)
    assert magic == 0xfeedfacf
    at = 32
    segments = {}
    for _ in range(count):
        cmd, size = struct.unpack_from('<2I', blob, at)
        if cmd == 0x19:
            name, va, vm, off, files = struct.unpack_from('<16s4Q', blob, at + 8)
            segments[name.rstrip(b'\0').decode()] = dict(va=hex(va), vm_bytes=vm, file_offset=off, file_bytes=files)
        at += size
    return segments


def kernel():
    assert len(f'enuma-cpu: memcpy {2**23} ns={2**64-1} mbps={1000*2**23}\n') < 80
    assert len(f'enuma-cpu: loop {10**8} ns={2**64-1} mops={2000*10**8}\n') < 80
    data, _, frozen = baseline()
    filelist, inputs, old_obj = link_inputs(data)
    commands = {s['tag']: s for s in data['r13_delta']['steps']}
    cc = commands['compile-kern_exec.o']
    old_source = R14 / 'self-check/build-final' / SOURCE
    assert sha(old_source) == data['macros']['kern_exec.o']['source_sha256'] == \
        '0bd9beaf03d2db942777d5eaa7326b22559a53eac40e655f3b5c10db192f592a'

    (NEW / 'logs').mkdir(parents=True)
    (NEW / 'tmp').mkdir()
    (NEW / 'objects').mkdir()
    source, new_obj = NEW / SOURCE, NEW / OBJECT
    shutil.copytree(old_source.parent, source.parent, symlinks=True)
    sys.path.insert(0, str(BASE / 'scripts'))
    from unixnu.kernel import linux_env
    env = dict(os.environ)
    env.update(linux_env(SimpleNamespace(tree=Path(commands['link']['cwd']).parents[3])))
    env.update(PATH='/home/wh1stl3/.local/bin:' + env['PATH'],
               TMPDIR=str(NEW / 'tmp'), PYTHONDONTWRITEBYTECODE='1')

    patch = DEVICE / 'patches/xnu/enuma-r16-cpu-calibration.patch'
    patch_args = ['patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i', patch]
    for tag, args in (('patch-dry-run', patch_args + ['--dry-run']), ('patch', patch_args)):
        output = run(tag, args, NEW / 'source', env)
        assert 'offset' not in output and 'fuzz' not in output, output
    argv = list(cc['argv'])
    assert argv[1:5] == ['-xc', str(R13 / 'self-check/build-final' / SOURCE), '-o',
                         str(R13 / 'self-check/build-final' / OBJECT)]
    argv[2], argv[4] = str(source), str(new_obj)
    run('compile-kern_exec.o', argv, cc['cwd'], env)
    assert sha(new_obj) != inputs[old_obj]
    (NEW / 'link.filelist').write_text('\n'.join(str(new_obj if p == old_obj else p) for p in filelist) + '\n')
    for tag in ('link', 'prelink'):
        entry = commands[tag]
        args = list(entry['argv'])
        for name in ('link.filelist', 'native.macho', 'native-link.map', 'prelink.macho'):
            original = R13 / 'self-check/build-final' / name
            args = [a.replace(str(original), str(NEW / name)) for a in args]
        run(tag, args, NEW if tag == 'prelink' else entry['cwd'], env)
    for path in sorted((OLD / 'objects').iterdir()):
        if path.name != OBJECT.name:
            shutil.copyfile(path, NEW / 'objects' / path.name)
            assert sha(NEW / 'objects' / path.name) == sha(path), path
    assert all(sha(p) == h for p, h in inputs.items())
    assert baseline()[2] == frozen
    counts = audit(old_obj, new_obj, env)
    data['diff_vs_r4'].update(new_sha256=sha(NEW / 'native.macho'),
                             prelink_sha256=sha(NEW / 'prelink.macho'),
                             prelink_bytes=(NEW / 'prelink.macho').stat().st_size)
    data['diff_vs_r5']['native_bytes_delta'] += (
        (NEW / 'native.macho').stat().st_size - (OLD / 'native.macho').stat().st_size)
    data['r16_delta'] = dict(old_object=describe(old_obj), new_object=describe(new_obj), compile_argv=argv,
        compile_cwd=cc['cwd'], source_before=describe(old_source), source_after=describe(source),
        unchanged_filelist_entries=len(filelist) - 1,
        unchanged_explicit_link_inputs={str(p): h for p, h in inputs.items() if p != old_obj},
        unchanged_saved_objects={p.name: sha(p) for p in sorted((OLD / 'objects').iterdir())
                                 if p.suffix in ('.o', '.cpo') and p.name != OBJECT.name},
        counts=counts, frozen_r15=frozen,
        segments={f'{root.name[-3:]}/{name}': layout(folder / name)
                  for root, folder in ((R15, OLD), (R16, NEW)) for name in ('native.macho', 'prelink.macho')})
    write_json(NEW / RESULT, data)
    shutil.copyfile(OLD / 'seed-inspection.json', NEW / 'seed-inspection.json')


def package():
    old_data, prior, frozen = baseline()
    data = json.loads((NEW / RESULT).read_text())
    assert data['r16_delta']['frozen_r15'] == frozen
    shutil.copyfile(R15 / WRAPPER, R16 / WRAPPER)
    label = 'r15 shared-region syscall probe; not deployed'
    text = (R15 / RECIPE).read_text()
    assert text.count(label) == 1
    (R16 / RECIPE).write_text(text.replace(label, 'r16 CPU calibration; not deployed'))
    feeds = R15 / 'self-check-package/packaging/out/feeds'
    assert feeds.is_dir()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    run('package', [sys.executable, '-B', R16 / RECIPE, '--seed-feeds-from', feeds], R16, env)
    now = json.loads((R16 / 'candidate-manifest.json').read_text())
    for key in prior['package_audit'].keys() - {'payload_content_bytes'}:
        assert prior['package_audit'][key] == now['package_audit'][key], key
    assert prior['artifacts'].keys() == now['artifacts'].keys()
    assert {k for k, v in prior['artifacts'].items() if v != now['artifacts'][k]} == {
        'boot.img', 'payload.img', 'self-check/kernel.macho'}
    for name, info in now['artifacts'].items():
        assert describe(R16 / artifact_path(name)) == info, name
    extracted = R16 / TRUSTCACHE.parent
    assert describe(extracted / 'kernel.macho') == describe(NEW / 'prelink.macho')
    trustcache = describe(R16 / TRUSTCACHE)
    assert trustcache == describe(R15 / TRUSTCACHE)
    output = run('root-match', [sys.executable, '-B', DEVICE / 'scripts/check-enuma-root-match.py',
                 '--build-dir', extracted.parent / 'packaging', '--macho', extracted / 'kernel.macho'], R16, env)
    assert output.startswith('OK:'), output
    link_inputs(old_data)
    assert baseline()[2] == frozen
    write_json(R16 / 'delta-vs-r15.json', dict(before=prior['artifacts'], after=now['artifacts'],
               package_before=prior['package_audit'], package_after=now['package_audit'],
               trustcache=trustcache, native_before=describe(OLD / 'native.macho'),
               native_after=describe(NEW / 'native.macho'), **data['r16_delta']))


if __name__ == '__main__':
    commands = {'kernel': kernel, 'package': package}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        raise SystemExit(f'usage: {Path(__file__).name} {{kernel|package}}')
    commands[sys.argv[1]]()
