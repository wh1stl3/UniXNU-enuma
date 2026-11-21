#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Replay frozen r17 with one post-Data launch-policy hook (WSL root)."""
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
R = runpy.run_path(str(Path(__file__).with_name('build-enuma-r17-exit-probe.py')))
BASE, DEVICE, PIN, R13, R17, RESULT = (R[k] for k in (
    'BASE', 'DEVICE', 'PIN', 'R13', 'R17', 'RESULT'))
sha, describe, write_json, artifact_path, layout = (R[k] for k in (
    'sha', 'describe', 'write_json', 'artifact_path', 'layout'))
OLD, R19 = R['NEW'], R17.with_name(R17.name.removesuffix('17') + '19')
NEW = R19 / 'self-check/build-final'
RECIPE, WRAPPER, TRUSTCACHE = (R[k] for k in ('RECIPE', 'WRAPPER', 'TRUSTCACHE'))
SOURCE, OBJECT = (R['R'][k] for k in ('SOURCE', 'OBJECT'))
POLICY = DEVICE / 'package/BootWatchdogPolicy.c'
TOKENS = ['sheng-disable-watchdogd=1', 'sheng-lite=1']
SYMBOL = '_sheng_boot_watchdog_policy'
STRINGS = [s.split('=')[0] for s in TOKENS] + [
    'enuma launch policy: watchdogd=%d lite=%d errno=%d\n']


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
    prior = json.loads((R17 / 'candidate-manifest.json').read_text())
    assert prior['artifacts']['boot.img']['sha256'] == \
        '4fed789b186b0ef478f1f040f5a2b95e3db37c6c7c8f1fed83339d6f3dcc9d2a'
    names = {R17 / artifact_path(n) for n in prior['artifacts']}
    for n, d in prior['artifacts'].items():
        assert describe(R17 / artifact_path(n)) == d, n
    assert describe(OLD / 'prelink.macho') == prior['artifacts']['self-check/kernel.macho']
    assert sha(OLD / 'native.macho') == data['diff_vs_r4']['new_sha256']
    names.update(R17 / n for n in (RECIPE, WRAPPER, TRUSTCACHE, 'candidate-manifest.json',
                                   'delta-vs-r16.json'))
    names.update(OLD / n for n in (RESULT, 'native.macho', 'prelink.macho',
                                   'link.filelist', 'seed-inspection.json'))
    names.update((OLD / 'objects').iterdir())
    delta = data['r17_delta']
    filelist = list(map(Path, (OLD / 'link.filelist').read_text().splitlines()))
    inputs = {Path(p): h for p, h in delta['unchanged_explicit_link_inputs'].items()}
    for name, pair in delta['objects'].items():
        path, = [p for p in filelist if p.name == name]
        assert path == OLD / 'objects' / name and describe(path) == pair['after']
        inputs[path] = pair['after']['sha256']
    assert all(p in inputs for p in filelist)
    assert all(sha(p) == h for p, h in inputs.items())
    return data, prior, filelist, inputs, {str(p.relative_to(R17)): sha(p) for p in sorted(names)}


def kernel():
    data, _, filelist, inputs, frozen = baseline()
    commands = {s['tag']: s for s in data['r13_delta']['steps']}
    cc = commands['compile-kern_exec.o']
    old_source = R['R']['R14'] / 'self-check/build-final' / SOURCE
    assert sha(old_source) == data['r16_delta']['source_before']['sha256'] == \
        '0bd9beaf03d2db942777d5eaa7326b22559a53eac40e655f3b5c10db192f592a'
    original = old_source.read_bytes()
    anchor = b'\tif (data_error) panic("offline scratch Data mount failed: %d", data_error);\n'
    hook = (b'\textern int sheng_boot_watchdog_policy(void *, uint64_t);\n'
            b'\t(void) sheng_boot_watchdog_policy(p, (uint64_t)scratch_addr);\n')
    assert original.count(anchor) == 1
    assert original.index(b'\nload_init_program(proc_t p)') < original.index(anchor)
    assert original[original.index(anchor) + len(anchor):].startswith(b'#endif\n')
    for n in ('logs', 'tmp', 'objects'):
        (NEW / n).mkdir(parents=True)
    source = NEW / SOURCE
    shutil.copytree(old_source.parent, source.parent, symlinks=True,
                    ignore=shutil.ignore_patterns(old_source.name))
    source.write_bytes(original.replace(anchor, anchor + hook))
    sys.path.insert(0, str(BASE / 'scripts'))
    from unixnu.kernel import linux_env
    env = dict(os.environ)
    env.update(linux_env(SimpleNamespace(tree=Path(commands['link']['cwd']).parents[3])))
    env.update(PATH='/home/wh1stl3/.local/bin:' + env['PATH'],
               TMPDIR=str(NEW / 'tmp'), PYTHONDONTWRITEBYTECODE='1')
    argv = list(cc['argv'])
    assert argv[1:5] == ['-xc', str(R13 / 'self-check/build-final' / SOURCE),
                         '-o', str(R13 / 'self-check/build-final' / OBJECT)]
    obj, policy_obj = NEW / OBJECT, NEW / 'objects/BootWatchdogPolicy.o'
    argv[2], argv[4] = str(source), str(obj)
    run('compile-kern_exec.o', argv, cc['cwd'], env)
    macros = list(argv)
    macros[4] = str(obj.with_suffix('.o.i'))
    macros[macros.index('-c'):macros.index('-c') + 1] = ['-E', '-dM']
    run('macros-kern_exec', macros, cc['cwd'], env)
    defines = obj.with_suffix('.o.i').read_text().splitlines()
    for macro in ('XNU_OWNER_DATA_MOUNT 1', 'XNU_BOOT_PROGRESS 0', 'XNU_ENUMA_PATH_PROBE 1'):
        assert '#define ' + macro in defines, macro
    policy_argv = list(argv)
    policy_argv[2], policy_argv[4] = str(POLICY), str(policy_obj)
    run('compile-BootWatchdogPolicy.o', policy_argv + ['-mgeneral-regs-only'], cc['cwd'], env)
    archive = NEW / 'objects/libEnumaBootWatchdogPolicy.a'
    run('archive', ['llvm-ar', 'rcsD', archive, policy_obj], NEW, env)
    assert run('archive-members', ['llvm-ar', 't', archive], NEW, env).splitlines() == [policy_obj.name]
    old_obj = OLD / OBJECT
    assert filelist.count(old_obj) == 1 and sha(obj) != inputs[old_obj]
    (NEW / 'link.filelist').write_text('\n'.join(str(obj if p == old_obj else p) for p in filelist) + '\n')
    for tag in ('link', 'prelink'):
        entry = commands[tag]
        args = list(entry['argv'])
        for name in ('link.filelist', 'native.macho', 'native-link.map', 'prelink.macho'):
            before = R13 / 'self-check/build-final' / name
            args = [a.replace(str(before), str(NEW / name)) for a in args]
        if tag == 'link':
            args.append(f'-Wl,-force_load,{archive}')
        run(tag, args, NEW if tag == 'prelink' else entry['cwd'], env)
    for path in (OLD / 'objects').iterdir():
        if path.name not in (obj.name, obj.with_suffix('.o.i').name):
            shutil.copyfile(path, NEW / 'objects' / path.name)
    counts = {}
    for name in ('native.macho', 'prelink.macho'):
        path = NEW / name
        assert not run(f'undefined-{name}', ['llvm-nm', '-u', path], NEW, env).strip()
        symbols = run(f'symbols-{name}', ['llvm-nm', path], NEW, env)
        assert sum(s.split()[-1:] == [SYMBOL] for s in symbols.splitlines()) == 1
        blob = path.read_bytes()
        counts[name] = {s: blob.count(s.encode() + b'\0') for s in STRINGS}
        assert set(counts[name].values()) == {1}
        assert blob.count(R['FORMAT']) == 1
        asm = run(f'call-{name}', ['llvm-objdump', '-d',
                  '--disassemble-symbols=_load_init_program', path], NEW, env)
        assert len(re.findall(r'\bbl\s+[^\n]*<' + SYMBOL + r'>', asm)) == 1
    assert baseline()[4] == frozen
    data['diff_vs_r4'].update(new_sha256=sha(NEW / 'native.macho'),
                              prelink_sha256=sha(NEW / 'prelink.macho'),
                              prelink_bytes=(NEW / 'prelink.macho').stat().st_size)
    data['diff_vs_r5']['native_bytes_delta'] += (
        (NEW / 'native.macho').stat().st_size - (OLD / 'native.macho').stat().st_size)
    data['r19_delta'] = dict(frozen_r17=frozen, source_before=describe(old_source),
        source_after=describe(source), policy_source=describe(POLICY), archive=describe(archive),
        policy_object=describe(policy_obj), exec_object_before=describe(old_obj),
        exec_object_after=describe(obj), unchanged_filelist_entries=len(filelist) - 1,
        unchanged_explicit_link_inputs=len(inputs) - 1, counts=counts, zero_undefined=True,
        segments={f'{folder.parents[1].name[-3:]}/{n}': layout(folder / n)
                  for folder in (OLD, NEW) for n in ('native.macho', 'prelink.macho')})
    write_json(NEW / RESULT, data)
    shutil.copyfile(OLD / 'seed-inspection.json', NEW / 'seed-inspection.json')


def package():
    _, prior, _, _, frozen = baseline()
    delta = json.loads((NEW / RESULT).read_text())['r19_delta']
    assert delta['frozen_r17'] == frozen
    shutil.copyfile(R17 / WRAPPER, R19 / WRAPPER)
    recipe = (R17 / RECIPE).read_text()
    for before, after in (
        ("EXPECTED_ARGS = R4_ARGS + DISPLAY_ARGS + ['sheng-aks=1']",
         f"EXPECTED_ARGS = R4_ARGS + DISPLAY_ARGS + ['sheng-aks=1'] + {TOKENS!r}"),
        ('r17 BSD exit probe; not deployed', 'r19 watchdogd and lite policy; not deployed'),
    ):
        assert recipe.count(before) == 1
        recipe = recipe.replace(before, after)
    (R19 / RECIPE).write_text(recipe)
    feeds = R17 / 'self-check-package/packaging/out/feeds'
    assert feeds.is_dir()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    run('package', [sys.executable, '-B', R19 / RECIPE, '--seed-feeds-from', feeds], R19, env)
    now = json.loads((R19 / 'candidate-manifest.json').read_text())
    a, b = prior['package_audit'], now['package_audit']
    assert b['boot_args'].split() == a['boot_args'].split() + TOKENS
    assert {k for k in a if a[k] != b[k]} == {'boot_args', 'payload_content_bytes'}
    before, after = prior['artifacts'], now['artifacts']
    assert before.keys() == after.keys()
    assert {n for n in before if before[n] != after[n]} == {
        'boot.img', 'payload.img', 'self-check/kernel.macho', 'self-check/unixnu.toml'}
    for n, info in after.items():
        assert describe(R19 / artifact_path(n)) == info, n
    extracted = R19 / TRUSTCACHE.parent
    assert describe(extracted / 'kernel.macho') == describe(NEW / 'prelink.macho')
    trustcache = describe(R19 / TRUSTCACHE)
    assert trustcache == describe(R17 / TRUSTCACHE)
    payload = (R19 / 'payload.img').read_bytes()
    with (R19 / 'boot.img').open('rb') as fp:
        header = fp.read(48)
        assert header.startswith(b'ANDROID!')
        ks, _, rs = struct.unpack_from('<III', header, 8)
        pg, = struct.unpack_from('<I', header, 36)
        fp.seek(pg + ((ks + pg - 1) // pg) * pg)
        assert rs == len(payload) and fp.read(rs) == payload
    output = run('root-match', [sys.executable, '-B', DEVICE / 'scripts/check-enuma-root-match.py',
                  '--build-dir', extracted.parent / 'packaging', '--macho', extracted / 'kernel.macho'], R19, env)
    assert output.startswith('OK:'), output
    assert baseline()[4] == frozen
    write_json(R19 / 'delta-vs-r17.json', dict(before=before, after=after, package_before=a,
        package_after=b, trustcache=trustcache, native_before=describe(OLD / 'native.macho'),
        native_after=describe(NEW / 'native.macho'), **delta))


if __name__ == '__main__':
    commands = {'kernel': kernel, 'package': package}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        raise SystemExit(f'usage: {Path(__file__).name} {{kernel|package}}')
    commands[sys.argv[1]]()
