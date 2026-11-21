#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Replay r16 without CPU calibration and with a BSD exit probe (WSL root)."""
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True
R = runpy.run_path(str(Path(__file__).with_name('build-enuma-r16-cpu-calibration.py')))
BASE, DEVICE, R13, R15, R16, PIN, RESULT = (R[k] for k in
    ('BASE', 'DEVICE', 'R13', 'R15', 'R16', 'PIN', 'RESULT'))
sha, describe, write_json, artifact_path, layout = (R[k] for k in
    ('sha', 'describe', 'write_json', 'artifact_path', 'layout'))
R17 = R16.with_name(R16.name.removesuffix('16') + '17')
OLD, NEW = (root / 'self-check/build-final' for root in (R16, R17))
RECIPE, WRAPPER, TRUSTCACHE = (R[k] for k in ('RECIPE', 'WRAPPER', 'TRUSTCACHE'))
FORMAT = b'enuma-exit: pid=%d st=%d sig=%d\n\0'
CPU_SYMBOLS = {'_enuma_cpu_probe', '_enuma_cpu_src', '_enuma_cpu_dst'}


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
    r15_data, _, r15_frozen = R['baseline']()
    _, r15_inputs, restored = R['link_inputs'](r15_data)
    data = json.loads((OLD / RESULT).read_text())
    delta = data['r16_delta']
    assert delta['frozen_r15'] == r15_frozen
    prior = json.loads((R16 / 'candidate-manifest.json').read_text())
    assert prior['artifacts']['boot.img']['sha256'] == \
        '9e94a06c41e4d1556a2d0c569bfca983e5d3bba0515ee311f37e0800637796a9'
    assert sha(R16 / RECIPE) == '3c076bb02db2c0041077103a91de18c01380bae4e3bf4b14f4bf25c6ac6c23c9'
    assert sha(R16 / WRAPPER) == sha(R15 / WRAPPER)
    names = [R16 / artifact_path(name) for name in prior['artifacts']]
    for name, info in prior['artifacts'].items():
        assert describe(R16 / artifact_path(name)) == info, name
    assert describe(OLD / 'prelink.macho') == prior['artifacts']['self-check/kernel.macho']
    assert sha(OLD / 'native.macho') == data['diff_vs_r4']['new_sha256']
    names += [R16 / n for n in ('candidate-manifest.json', 'delta-vs-r15.json', RECIPE, WRAPPER, TRUSTCACHE)]
    names += [OLD / n for n in ('native.macho', 'prelink.macho', 'link.filelist', RESULT, 'seed-inspection.json')]
    names += sorted((OLD / 'objects').iterdir())
    names += [OLD / R['SOURCE']]
    inputs = {Path(p): h for p, h in delta['unchanged_explicit_link_inputs'].items()}
    assert r15_inputs == {**inputs, restored: delta['old_object']['sha256']}
    old_exec = OLD / R['OBJECT']
    assert describe(old_exec) == delta['new_object']
    inputs[old_exec] = delta['new_object']['sha256']
    filelist = list(map(Path, (OLD / 'link.filelist').read_text().splitlines()))
    old_exit, = [p for p in filelist if p.name == 'kern_exit.o']
    assert filelist.count(old_exec) == 1 and all(p in inputs for p in filelist)
    assert all(sha(p) == h for p, h in inputs.items())
    assert all(sha(OLD / 'objects' / n) == h for n, h in delta['unchanged_saved_objects'].items())
    frozen = {str(p.relative_to(R16)): sha(p) for p in names}
    return data, prior, frozen, filelist, inputs, restored, old_exec, old_exit


def symbols(path, env, tag):
    text = run(tag, ['llvm-nm', path], NEW, env)
    return set(re.findall(r'^\S+ \w (_\w+)$', text, re.M))


def audit(restored, new_exit, env):
    counts = {}
    for tag, path, n in [('kern_exec.o', restored, 0), ('kern_exit.o', new_exit, 1),
                         ('native', NEW / 'native.macho', 1), ('prelink', NEW / 'prelink.macho', 1)]:
        blob = path.read_bytes()
        assert blob.count(FORMAT) == blob.count(b'enuma-exit:') == n, path
        assert b'enuma-cpu:' not in blob, path
        assert not CPU_SYMBOLS & symbols(path, env, f'symbols-{tag}'), path
        counts[tag] = dict(exit_format=n, cpu_formats=0, cpu_symbols=0)
        if tag in ('native', 'prelink'):
            assert not run(f'undefined-{tag}', ['llvm-nm', '-u', path], NEW, env).strip()
            for fmt in R['R']['FORMATS']:
                assert blob.count(fmt) == 1, path
    for folder, expected in ((OLD, 0), (NEW, 1)):
        for kind in ('native', 'prelink'):
            path = folder / f'{kind}.macho'
            tag = f'{folder.parents[1].name[-3:]}-{kind}'
            blob = path.read_bytes()
            assert blob.count(FORMAT) == expected
            assert [blob.count(fmt) for fmt in R['FORMATS']] == [1 - expected] * 2
            body = run(f'disasm-{tag}-proc_exit',
                       ['llvm-objdump', '-d', '--disassemble-symbols=_proc_exit', path], NEW, env)
            targets = re.findall(r'\b(?:bl|b)\s+\S+\s+<(_\w+)>', body)
            printf_sites = targets.count('_printf')
            counts[tag] = dict(proc_exit_printf=printf_sites)
            if not expected:
                counts[tag]['exit_format'] = 0
            else:
                before = counts[f'r16-{kind}']['proc_exit_printf']
                assert printf_sites == before + 1, (tag, targets)
                assert before == 0, (tag, targets)
                assert targets.index('_proc_rele') < targets.index('_printf'), (tag, targets)
    return counts


def kernel():
    assert len(f'enuma-exit: pid={-2**31} st={-2**31} sig={-2**31}\n') < 80
    data, _, frozen, filelist, inputs, restored, old_exec, old_exit = baseline()
    commands = {s['tag']: s for s in data['r13_delta']['steps']}
    tree = Path(commands['link']['cwd']).parents[3]
    old_source = tree / '.cache/xnu-work/bsd/kern/kern_exit.c'
    db = old_exit.with_suffix('.o.json')
    assert sha(old_source) == '14b85d7f495a4ec9d2af751a2de424ffae43eabfba5494e9f9e4ec904cc9b23c'
    assert sha(db) == 'b8ce8a2521e36ab7a249e8d512799cfd13c27f073b19ae9fb1057dc6a8a3ac16'
    cc = json.loads(db.read_text().rstrip().removesuffix(','))
    assert Path(cc['directory']) / cc['output'] == old_exit
    argv = cc['arguments']
    assert argv[1:5] == ['-xc', cc['file'], '-o', cc['output']]

    (NEW / 'logs').mkdir(parents=True)
    (NEW / 'tmp').mkdir()
    (NEW / 'objects').mkdir()
    source = NEW / 'source/bsd/kern/kern_exit.c'
    source.parent.mkdir(parents=True)
    shutil.copyfile(old_source, source)
    new_exit = NEW / 'objects/kern_exit.o'
    new_exec = NEW / R['OBJECT']
    shutil.copyfile(restored, new_exec)
    assert sha(new_exec) == data['r16_delta']['old_object']['sha256'] != sha(old_exec)

    sys.path.insert(0, str(BASE / 'scripts'))
    from unixnu.kernel import linux_env
    env = dict(os.environ)
    env.update(linux_env(SimpleNamespace(tree=tree)))
    env.update(PATH='/home/wh1stl3/.local/bin:' + env['PATH'],
               TMPDIR=str(NEW / 'tmp'), PYTHONDONTWRITEBYTECODE='1')
    patch = DEVICE / 'patches/xnu/enuma-r17-exit-probe.patch'
    patch_args = ['patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i', patch]
    for tag, args in (('patch-dry-run', patch_args + ['--dry-run']), ('patch', patch_args)):
        output = run(tag, args, NEW / 'source', env)
        assert 'offset' not in output and 'fuzz' not in output, output

    # Keep the recorded include flags and put any outputs in the new tree.
    argv[2], argv[4] = str(source), str(new_exit)
    if '-MF' in argv:
        i = argv.index('-MF') + 1
        assert Path(argv[i]).name == 'kern_exit.d', argv[i]
        argv[i] = str(new_exit.with_suffix('.d'))
    for flag in ('-MJ', '-serialize-diagnostics'):
        assert flag not in argv, flag
    run('compile-kern_exit.o', argv, cc['directory'], env)
    assert sha(new_exit) != inputs[old_exit]
    replacements = {old_exec: new_exec, old_exit: new_exit}
    (NEW / 'link.filelist').write_text('\n'.join(str(replacements.get(p, p)) for p in filelist) + '\n')
    for tag in ('link', 'prelink'):
        entry = commands[tag]
        args = list(entry['argv'])
        for name in ('link.filelist', 'native.macho', 'native-link.map', 'prelink.macho'):
            original = R13 / 'self-check/build-final' / name
            args = [a.replace(str(original), str(NEW / name)) for a in args]
        run(tag, args, NEW if tag == 'prelink' else entry['cwd'], env)
    for path in sorted((OLD / 'objects').iterdir()):
        name = path.name
        if name == old_exec.name:
            continue
        expected = frozen[str(path.relative_to(R16))]
        shutil.copyfile(OLD / 'objects' / name, NEW / 'objects' / name)
        assert sha(NEW / 'objects' / name) == expected, name
    assert baseline()[2] == frozen
    counts = audit(restored, new_exit, env)
    segments = {f'{root.name[-3:]}/{name}': layout(folder / name)
                for root, folder in ((R15, R15 / 'self-check/build-final'), (R16, OLD), (R17, NEW))
                for name in ('native.macho', 'prelink.macho')}
    for name in ('native.macho', 'prelink.macho'):
        sizes = [segments[f'r{r}/{name}']['__DATA']['vm_bytes'] for r in (15, 16, 17)]
        assert sizes == [1310720, 18087936, 1310720], (name, sizes)

    data['diff_vs_r4'].update(new_sha256=sha(NEW / 'native.macho'),
                              prelink_sha256=sha(NEW / 'prelink.macho'),
                              prelink_bytes=(NEW / 'prelink.macho').stat().st_size)
    data['diff_vs_r5']['native_bytes_delta'] += (
        (NEW / 'native.macho').stat().st_size - (OLD / 'native.macho').stat().st_size)
    data['r17_delta'] = dict(objects={old.name: dict(before=describe(old), after=describe(new))
                                      for old, new in replacements.items()},
        compile_argv=argv, compile_cwd=cc['directory'], compile_db=describe(db),
        source_before=describe(old_source), source_after=describe(source),
        unchanged_filelist_entries=len(filelist) - len(replacements),
        unchanged_explicit_link_inputs={str(p): h for p, h in inputs.items() if p not in replacements},
        unchanged_saved_objects=data['r16_delta']['unchanged_saved_objects'],
        counts=counts, frozen_r16=frozen, segments=segments)
    write_json(NEW / RESULT, data)
    shutil.copyfile(OLD / 'seed-inspection.json', NEW / 'seed-inspection.json')


def package():
    _, prior, frozen, *_ = baseline()
    data = json.loads((NEW / RESULT).read_text())
    assert data['r17_delta']['frozen_r16'] == frozen
    shutil.copyfile(R16 / WRAPPER, R17 / WRAPPER)
    text = (R16 / RECIPE).read_text()
    label = 'r16 CPU calibration; not deployed'
    assert text.count(label) == 1
    (R17 / RECIPE).write_text(text.replace(label, 'r17 BSD exit probe; not deployed'))
    feeds = R16 / 'self-check-package/packaging/out/feeds'
    assert feeds.is_dir()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    run('package', [sys.executable, '-B', R17 / RECIPE, '--seed-feeds-from', feeds], R17, env)
    now = json.loads((R17 / 'candidate-manifest.json').read_text())
    for key in prior['package_audit'].keys() - {'payload_content_bytes'}:
        assert prior['package_audit'][key] == now['package_audit'][key], key
    assert prior['artifacts'].keys() == now['artifacts'].keys()
    assert {k for k, v in prior['artifacts'].items() if v != now['artifacts'][k]} == {
        'boot.img', 'payload.img', 'self-check/kernel.macho'}
    for name, info in now['artifacts'].items():
        assert describe(R17 / artifact_path(name)) == info, name
    extracted = R17 / TRUSTCACHE.parent
    assert describe(extracted / 'kernel.macho') == describe(NEW / 'prelink.macho')
    trustcache = describe(R17 / TRUSTCACHE)
    assert trustcache == describe(R16 / TRUSTCACHE)
    output = run('root-match', [sys.executable, '-B', DEVICE / 'scripts/check-enuma-root-match.py',
                  '--build-dir', extracted.parent / 'packaging', '--macho', extracted / 'kernel.macho'], R17, env)
    assert output.startswith('OK:'), output
    assert baseline()[2] == frozen
    write_json(R17 / 'delta-vs-r16.json', dict(before=prior['artifacts'], after=now['artifacts'],
               package_before=prior['package_audit'], package_after=now['package_audit'],
               trustcache=trustcache, native_before=describe(OLD / 'native.macho'),
               native_after=describe(NEW / 'native.macho'), **data['r17_delta']))


if __name__ == '__main__':
    commands = {'kernel': kernel, 'package': package}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        raise SystemExit(f'usage: {Path(__file__).name} {{kernel|package}}')
    commands[sys.argv[1]]()
