#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Replay r13 with only the pre-exec cache lookup paths changed (WSL, Python 3.11)."""
import json
import os
import re
import runpy
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True
REPLAY = runpy.run_path(str(Path(__file__).with_name('build-enuma-r13-console-throughput.py')))
BASE, DEVICE, R13, PIN, FORMATS = (REPLAY[k] for k in ('BASE', 'DEVICE', 'R13', 'PIN', 'FORMATS'))
sha, describe, write_json = (REPLAY[k] for k in ('sha', 'describe', 'write_json'))
R14 = R13.with_name(R13.name.removesuffix('13') + '14')
OLD = R13 / 'self-check/build-final'
NEW = R14 / 'self-check/build-final'
VN = b'enuma-vn: %d %s %s\n\0'
PATHS = re.compile(r'^\tENUMAVN(?:_LABEL)?\("([^"]+)"(?:, "([^"]+)")?\);$', re.M)
REMOVED = {
    '/System/Library/dyld',
    '/System/Library/Caches/com.apple.dyld',
    '/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64e',
}
ADDED = {
    '/System/Cryptexes/OS',
    '/System/Cryptexes/OS/System/Library',
    '/System/Cryptexes/OS/System/Library/dyld/dyld_shared_cache_arm64',
    '/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64',
    '/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.symbols',
}


def run(tag, argv, cwd, env):
    argv = list(map(str, argv))
    result = subprocess.run(argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    log = NEW / 'logs' / f'{tag}.log'
    log.write_text(result.stdout)
    if result.returncode:
        first = next((s for s in result.stdout.splitlines() if 'error:' in s.lower()),
                     result.stdout.partition('\n')[0])
        raise SystemExit(f'{tag}: {first} (exit {result.returncode}; {log})')
    print(tag, flush=True)
    return result.stdout


def artifact_path(name):
    # r13's manifest keeps historical self-check/* keys for FAT readbacks.
    return ('self-check-package/extracted/' + name.removeprefix('self-check/')
            if name.startswith('self-check/') else name)


def baseline():
    assert subprocess.check_output(['git', '-C', BASE, 'rev-parse', 'HEAD'],
                                   text=True).strip() == PIN
    data = json.loads((OLD / 'kernel-build-result.json').read_text())
    manifest = json.loads((R13 / 'candidate-manifest.json').read_text())
    assert manifest['artifacts']['boot.img']['sha256'] == \
        '0fc6fd9536be414e420d4dedae48494e6ad10c257b7e824a4b7bcfb0a25e5ae4'
    for name, info in manifest['artifacts'].items():
        assert describe(R13 / artifact_path(name)) == info, name
    assert sha(OLD / 'native.macho') == data['diff_vs_r4']['new_sha256']
    assert sha(OLD / 'prelink.macho') == data['diff_vs_r4']['prelink_sha256']
    names = [*map(artifact_path, manifest['artifacts']), 'candidate-manifest.json', 'run_packaging.py',
             'r7-payload-wrapper.py', 'self-check-package/extracted/kernel.macho.trustcache']
    names += [str(p.relative_to(R13)) for p in (
        OLD / 'native.macho', OLD / 'prelink.macho', OLD / 'link.filelist',
        OLD / 'kernel-build-result.json', OLD / 'source/bsd/kern/kern_exec.c',
        *(OLD / 'objects').iterdir())]
    return data, manifest, {name: sha(R13 / name) for name in names}


def audit(path, count, env):
    blob = path.read_bytes()
    assert blob.count(b'enuma-vn:') == blob.count(VN) == 1, path
    assert blob.count(b'enuma-con:') == len(FORMATS), path
    assert all(blob.count(fmt + b'\0') == 1 for fmt in FORMATS), path
    if path.suffix == '.o':
        return
    tag = f'{path.parent.parent.parent.name}-{path.name}'
    instructions = run(f'load-init-{tag}', ['llvm-objdump', '-d',
                       '--disassemble-symbols=_load_init_program', path], NEW, env)
    callees = re.findall(r'\b(?:b|bl)\s+\S+\s+<(_\w+)>', instructions)
    end = callees.index('_enuma_fs_probe')
    assert callees[:end].count('_printf') == count, path
    # The two earlier non-probe lookups precede the first probe's lookup.
    assert callees[:end].count('_vnode_lookup') == count + 2, path
    assert callees.count('_enuma_fs_probe') == 2 and callees.count('_enuma_console_probe') == 1
    assert not run(f'undefined-{tag}', ['llvm-nm', '-u', path], NEW, env).strip()
    return count


def kernel():
    data, _, frozen = baseline()
    commands = {s['tag']: s for s in data['r13_delta']['steps']}
    prior_hashes = data['r13_delta']['unchanged_explicit_link_inputs']
    assert all(sha(path) == digest for path, digest in prior_hashes.items())
    cc = commands['compile-kern_exec.o']
    old_source, old_object = map(Path, (cc['argv'][2], cc['argv'][4]))
    macro = data['macros']['kern_exec.o']
    assert sha(old_source) == macro['source_sha256'] == \
        'd8551dbd677134fb024f05c42b60b7ca88ab3ac2815a8e7d266e688c0ca228c5'
    assert sha(old_object) == macro['object_sha256']
    old_list = (OLD / 'link.filelist').read_text().splitlines()
    assert old_list.count(str(old_object)) == 1

    (NEW / 'logs').mkdir(parents=True)
    (NEW / 'tmp').mkdir()
    obj = NEW / 'objects'
    obj.mkdir()
    sources = NEW / 'source'
    source = sources / 'bsd/kern/kern_exec.c'
    shutil.copytree(old_source.parent, source.parent, symlinks=True)

    sys.path.insert(0, str(BASE / 'scripts'))
    from unixnu.kernel import linux_env
    env = dict(os.environ)
    env.update(linux_env(SimpleNamespace(tree=Path(commands['link']['cwd']).parents[3])))
    env.update(PATH='/home/wh1stl3/.local/bin:' + env['PATH'],
               TMPDIR=str(NEW / 'tmp'), PYTHONDONTWRITEBYTECODE='1')
    patch = DEVICE / 'patches/xnu/enuma-r14-arm64-cache-probe.patch'
    patch_args = ['patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i', patch]
    for tag, args in (('patch-dry-run', patch_args + ['--dry-run']), ('patch', patch_args)):
        result = run(tag, args, sources, env)
        assert 'offset' not in result and 'fuzz' not in result, result
    old_text, new_text = old_source.read_text(), source.read_text()
    assert [line for line in old_text.splitlines() if not PATHS.fullmatch(line)] == \
        [line for line in new_text.splitlines() if not PATHS.fullmatch(line)]
    old_paths, paths = (PATHS.findall(text) for text in (old_text, new_text))
    assert len(old_paths) == 12 and len(paths) == len(set(paths)) == 14
    old_names, new_names = {p for p, _ in old_paths}, {p for p, _ in paths}
    assert old_names - new_names == REMOVED
    assert new_names - old_names == ADDED
    assert {p for p in old_paths if p[0] in old_names & new_names} == \
        {p for p in paths if p[0] in old_names & new_names}
    assert [p for p in old_paths if 'dyld' not in p[0]] == [p for p in paths if 'dyld' not in p[0]
                                                         and '/Cryptexes/' not in p[0]]
    assert max(len(f'enuma-vn: 999 OTHER {label or path}\n') for path, label in paths) < 80

    def includes(argv, tag):
        reply = run(tag, argv + ['-###'], cc['cwd'], env)
        line, = [s.strip() for s in reply.splitlines() if '"-cc1"' in s]
        args = shlex.split(line)
        return [args[i + 1] for i, arg in enumerate(args[:-1]) if arg == '-I']

    pre = includes(cc['argv'], 'cc1-r13')
    for tag in ('compile-kern_exec.o', 'macros-kern_exec.o'):
        entry = commands[tag]
        argv = list(entry['argv'])
        assert argv[2:4] == [str(old_source), '-o']
        argv[2], argv[4] = str(source), str(obj / Path(argv[4]).name)
        if tag == 'compile-kern_exec.o':
            assert pre == includes(argv, 'cc1-r14')
        run(tag, argv, entry['cwd'], env)
    write_json(NEW / 'cc1-includes.json', dict(r13=pre, r14=pre))
    assert sha(obj / 'kern_exec.o.i') == sha(OLD / 'objects/kern_exec.o.i')
    replacement = obj / 'kern_exec.o'
    assert sha(replacement) != sha(old_object)
    (NEW / 'link.filelist').write_text('\n'.join(
        str(replacement) if p == str(old_object) else p for p in old_list) + '\n')
    for tag in ('link', 'prelink'):
        entry = commands[tag]
        argv = list(entry['argv'])
        for name in ('link.filelist', 'native.macho', 'native-link.map', 'prelink.macho'):
            argv = [a.replace(str(OLD / name), str(NEW / name)) for a in argv]
        run(tag, argv, NEW if tag == 'prelink' else entry['cwd'], env)

    for path in (OLD / 'objects').iterdir():
        if not (obj / path.name).exists():
            shutil.copyfile(path, obj / path.name)
        assert (sha(obj / path.name) == sha(path)) == (path != old_object), path
    assert all(sha(path) == digest for path, digest in prior_hashes.items())
    for folder, count in ((OLD, len(old_paths)), (NEW, len(paths))):
        for path in (folder / 'objects/kern_exec.o', folder / 'native.macho', folder / 'prelink.macho'):
            audit(path, count, env)
    data['diff_vs_r4'].update(new_sha256=sha(NEW / 'native.macho'),
                             prelink_sha256=sha(NEW / 'prelink.macho'),
                             prelink_bytes=(NEW / 'prelink.macho').stat().st_size)
    macro.update(object_sha256=sha(replacement), object_bytes=replacement.stat().st_size,
                 source_sha256=sha(source), macros_dump_sha256=sha(obj / 'kern_exec.o.i'))
    data['r14_delta'] = dict(paths=paths, removed=[p for p in old_paths if p not in paths],
                             printf_sites=dict(r13=len(old_paths), r14=len(paths)),
                             old_object=describe(old_object), new_object=describe(replacement),
                             unchanged_explicit_link_inputs=len(prior_hashes),
                             frozen_r13=frozen)
    write_json(NEW / 'kernel-build-result.json', data)
    shutil.copyfile(OLD / 'seed-inspection.json', NEW / 'seed-inspection.json')


def package():
    _, prior, frozen = baseline()
    data = json.loads((NEW / 'kernel-build-result.json').read_text())
    assert frozen == data['r14_delta']['frozen_r13']
    recipe = R13 / 'run_packaging.py'
    wrapper = R13 / 'r7-payload-wrapper.py'
    assert sha(recipe) == 'c2f37534b4d3695dfd7aa324af83bc09bb9ebaedacf991fd978809edff7b7d39'
    assert sha(wrapper) == '2db5b7f1a215cdabf9394d0d47a2b03a23c6874d9de45bba38d884d36c21867a'
    shutil.copyfile(wrapper, R14 / wrapper.name)
    packaged = R14 / recipe.name
    packaged.write_text(recipe.read_text().replace('r13 pre-exec console throughput probe; not deployed',
                                                     'r14 pre-exec arm64 cache path probe; not deployed'))
    feeds = R13 / 'self-check-package/packaging/out/feeds'
    assert feeds.is_dir()
    env = dict(os.environ)
    run('package', [sys.executable, '-B', packaged, '--seed-feeds-from', feeds], R14, env)
    now = json.loads((R14 / 'candidate-manifest.json').read_text())
    for key in prior['package_audit'].keys() - {'payload_content_bytes'}:
        assert prior['package_audit'][key] == now['package_audit'][key], key
    assert {k for k, v in prior['artifacts'].items() if v != now['artifacts'][k]} == {
        'boot.img', 'payload.img', 'self-check/kernel.macho'}
    for name, info in now['artifacts'].items():
        assert describe(R14 / artifact_path(name)) == info, name
    extracted = R14 / 'self-check-package/extracted'
    trustcache = describe(extracted / 'kernel.macho.trustcache')
    assert trustcache == describe(R13 / 'self-check-package/extracted/kernel.macho.trustcache')
    output = run('root-match', [sys.executable, '-B', DEVICE / 'scripts/check-enuma-root-match.py',
                 '--build-dir', extracted.parent / 'packaging', '--macho', extracted / 'kernel.macho'],
                 R14, env)
    assert output.startswith('OK:'), output
    _, _, after = baseline()
    assert after == frozen
    write_json(R14 / 'delta-vs-r13.json', dict(before=prior['artifacts'], after=now['artifacts'],
               package_before=prior['package_audit'], package_after=now['package_audit'],
               trustcache=trustcache, native_before=describe(OLD / 'native.macho'),
               native_after=describe(NEW / 'native.macho'), **data['r14_delta']))


if __name__ == '__main__':
    commands = {'kernel': kernel, 'package': package}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        raise SystemExit(f'usage: {Path(__file__).name} {{kernel|package}}')
    commands[sys.argv[1]]()
