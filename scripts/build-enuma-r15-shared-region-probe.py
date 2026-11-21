#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Rebuild only vm_unix.o and replay the pinned r14 packaging (WSL root, Python 3.11)."""
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
R = runpy.run_path(str(Path(__file__).with_name('build-enuma-r14-arm64-cache-probe.py')))
BASE, DEVICE, R13, R14, PIN = (R[k] for k in ('BASE', 'DEVICE', 'R13', 'R14', 'PIN'))
sha, describe, write_json, artifact_path = (R[k] for k in ('sha', 'describe', 'write_json', 'artifact_path'))
R15 = R14.with_name(R14.name.removesuffix('14') + '15')
OLD, NEW = (x / 'self-check/build-final' for x in (R14, R15))
RESULT = 'kernel-build-result.json'
FORMATS = (b'enuma-sr: call=%u size=0x%llx slide=%u kr=%d\n\0',
           b'enuma-sr: check ret=%d first=%u\n\0')
PROBES = {'_shared_region_map_and_slide_2_np': '_enuma_sr_call',
          '_shared_region_check_np': '_enuma_sr_check'}


def run(tag, argv, cwd, env):
    result = subprocess.run(list(map(str, argv)), cwd=cwd, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log = NEW / 'logs' / f'{tag}.log'
    log.write_text(result.stdout)
    if result.returncode:
        first = next((s for s in result.stdout.splitlines() if 'error:' in s.lower()),
                     result.stdout.partition('\n')[0])
        raise SystemExit(f'{tag}: {first} (exit {result.returncode}; {log})')
    print(tag, flush=True)
    return result.stdout


def baseline():
    assert subprocess.check_output(['git', '-C', BASE, 'rev-parse', 'HEAD'], text=True).strip() == PIN
    data = json.loads((OLD / RESULT).read_text())
    manifest = json.loads((R14 / 'candidate-manifest.json').read_text())
    assert manifest['artifacts']['boot.img']['sha256'] == \
        '6022cca4d56b988132a6c96222a7b8537d9d9639359eca0d2b733881c9f2fa4a'
    for name, info in manifest['artifacts'].items():
        assert describe(R14 / artifact_path(name)) == info, name
    assert sha(OLD / 'native.macho') == data['diff_vs_r4']['new_sha256']
    assert sha(OLD / 'prelink.macho') == data['diff_vs_r4']['prelink_sha256']
    names = [*map(artifact_path, manifest['artifacts']), 'candidate-manifest.json', 'run_packaging.py',
             'r7-payload-wrapper.py', 'self-check-package/extracted/kernel.macho.trustcache']
    names += [str(p.relative_to(R14)) for p in (
        OLD / 'native.macho', OLD / 'prelink.macho', OLD / 'link.filelist',
        OLD / RESULT, OLD / 'seed-inspection.json', *(OLD / 'objects').iterdir())]
    return data, manifest, {name: sha(R14 / name) for name in names}


def audit(old_obj, new_obj, env):
    counts = {}
    for path, expected in ((old_obj, 0), (new_obj, 1),
                           (OLD / 'native.macho', 0), (NEW / 'native.macho', 1),
                           (OLD / 'prelink.macho', 0), (NEW / 'prelink.macho', 1)):
        blob = path.read_bytes()
        formats = [blob.count(fmt) for fmt in FORMATS]
        assert formats == [expected, expected] and blob.count(b'enuma-sr:') == 2 * expected, path
        if path.suffix == '.o':
            counts[f'r{14 + expected}/{path.name}'] = {'format_strings': formats}
            continue
        label = f'r{14 + expected}-{path.name}'
        assert not run(f'undefined-{label}', ['llvm-nm', '-u', path], NEW, env).strip()
        sites = {}
        for caller, callee in PROBES.items():
            for symbol, target, count in [(caller, callee, expected)] + (
                    [(callee, '_printf', 1)] if expected else []):
                asm = run(f'disasm-{label}-{symbol}', ['llvm-objdump', '-d',
                          f'--disassemble-symbols={symbol}', path], NEW, env)
                branches = re.findall(r'\b(?:b|bl)\s+\S+\s+<(_\w+)>', asm)
                assert f'<{symbol}>:' in asm and branches.count(target) == count, (path, symbol, target)
                sites[f'{symbol}->{target}'] = count
        counts[f'r{14 + expected}/{path.name}'] = {'format_strings': formats, 'call_sites': sites}
    return counts


def kernel():
    assert len(f'enuma-sr: call={2**32-1} size=0x{2**64-1:x} slide=1 kr={-2**31}\n') < 80
    data, _, frozen = baseline()
    commands = {s['tag']: s for s in data['r13_delta']['steps']}
    prior = {Path(k): v for k, v in data['r13_delta']['unchanged_explicit_link_inputs'].items()}
    old_list = list(map(Path, (OLD / 'link.filelist').read_text().splitlines()))
    old_obj, = [p for p in old_list if p.name == 'vm_unix.o']
    assert prior[old_obj] == 'bc72d157493aebed0f5422109c6b5bce104327a7050da4bd10837238e94e2417'
    for path in set(old_list) - prior.keys():
        assert path == OLD / 'objects/kern_exec.o'
        prior[path] = data['macros']['kern_exec.o']['object_sha256']
    assert all(sha(path) == digest for path, digest in prior.items())
    records = [json.loads(line.rstrip().rstrip(','))
               for line in old_obj.with_suffix('.o.json').read_text().splitlines() if line.strip()]
    assert all(entry['arguments'] == records[0]['arguments'] for entry in records)
    cc = records[0]
    argv = list(cc['arguments'])
    assert argv[1:5] == ['-xc', cc['file'], '-o', old_obj.name]
    assert '-c' in argv and not any(a.startswith(('-M', '-save-temps')) for a in argv)
    # Locate the versioned tree from the actual object; the compile DB may retain an older source pathname.
    tree, = [p for p in old_obj.parents if p.name == 'tree']
    old_source = tree / '.cache/xnu-work/bsd/vm/vm_unix.c'
    assert sha(old_source) == sha(cc['file']) == '81cdb09c3f45b429f14dd93b4e624c4f7ff65b2dbfcd15cf7ead8b1d0a10e482'

    (NEW / 'logs').mkdir(parents=True)
    (NEW / 'tmp').mkdir()
    objects = NEW / 'objects'
    objects.mkdir()
    source = NEW / 'source/bsd/vm/vm_unix.c'
    source.parent.mkdir(parents=True)
    shutil.copyfile(old_source, source)
    sys.path.insert(0, str(BASE / 'scripts'))
    from unixnu.kernel import linux_env
    env = dict(os.environ)
    env.update(linux_env(SimpleNamespace(tree=tree)))
    env.update(PATH='/home/wh1stl3/.local/bin:' + env['PATH'],
               TMPDIR=str(NEW / 'tmp'), PYTHONDONTWRITEBYTECODE='1')

    patch = DEVICE / 'patches/xnu/enuma-r15-shared-region-probe.patch'
    patch_args = ['patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i', patch]
    for tag, args in (('patch-dry-run', patch_args + ['--dry-run']), ('patch', patch_args)):
        output = run(tag, args, NEW / 'source', env)
        assert 'offset' not in output and 'fuzz' not in output, output
    new_obj = objects / old_obj.name
    argv[2], argv[4] = str(source), str(new_obj)
    run('compile-vm_unix.o', argv, old_obj.parent, env)
    assert sha(new_obj) != prior[old_obj]
    for path in (OLD / 'objects').iterdir():
        shutil.copyfile(path, objects / path.name)
        assert sha(objects / path.name) == sha(path), path
    new_list = [new_obj if p == old_obj else p for p in old_list]
    (NEW / 'link.filelist').write_text('\n'.join(map(str, new_list)) + '\n')
    for tag in ('link', 'prelink'):
        entry = commands[tag]
        paths = ['link.filelist', 'native.macho', 'native-link.map', 'prelink.macho']
        original = R13 / 'self-check/build-final'
        args = list(entry['argv'])
        for name in paths:
            args = [a.replace(str(original / name), str(NEW / name)) for a in args]
        run(tag, args, NEW if tag == 'prelink' else entry['cwd'], env)
    assert all(sha(path) == digest for path, digest in prior.items())
    counts = audit(old_obj, new_obj, env)
    data['diff_vs_r4'].update(new_sha256=sha(NEW / 'native.macho'),
                             prelink_sha256=sha(NEW / 'prelink.macho'),
                             prelink_bytes=(NEW / 'prelink.macho').stat().st_size)
    data['diff_vs_r5']['native_bytes_delta'] += (
        (NEW / 'native.macho').stat().st_size - (OLD / 'native.macho').stat().st_size)
    data['r15_delta'] = dict(
        old_object=describe(old_obj), new_object=describe(new_obj), compile_argv=argv,
        compile_cwd=str(old_obj.parent), source_before=describe(old_source), source_after=describe(source),
        unchanged_filelist_entries=len(old_list)-1, unchanged_explicit_link_inputs=len(prior)-1,
        unchanged_saved_objects=len(list((OLD / 'objects').glob('*.o'))) +
        len(list((OLD / 'objects').glob('*.cpo'))),
        counts=counts, frozen_r14=frozen)
    write_json(NEW / RESULT, data)
    shutil.copyfile(OLD / 'seed-inspection.json', NEW / 'seed-inspection.json')


def package():
    _, prior, frozen = baseline()
    data = json.loads((NEW / RESULT).read_text())
    assert data['r15_delta']['frozen_r14'] == frozen
    recipe, wrapper = R14 / 'run_packaging.py', R14 / 'r7-payload-wrapper.py'
    assert sha(recipe) == '59cdfe99e3d100577f2b73b0e223a01a070f1ab1dc659de06c98ec42b8ddd494'
    assert sha(wrapper) == '2db5b7f1a215cdabf9394d0d47a2b03a23c6874d9de45bba38d884d36c21867a'
    shutil.copyfile(wrapper, R15 / wrapper.name)
    label = 'r14 pre-exec arm64 cache path probe; not deployed'
    text = recipe.read_text()
    assert text.count(label) == 1
    packaged = R15 / recipe.name
    packaged.write_text(text.replace(label, 'r15 shared-region syscall probe; not deployed'))
    feeds = R14 / 'self-check-package/packaging/out/feeds'
    assert feeds.is_dir()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    run('package', [sys.executable, '-B', packaged, '--seed-feeds-from', feeds], R15, env)
    now = json.loads((R15 / 'candidate-manifest.json').read_text())
    for key in prior['package_audit'].keys() - {'payload_content_bytes'}:
        assert prior['package_audit'][key] == now['package_audit'][key], key
    assert prior['artifacts'].keys() == now['artifacts'].keys()
    assert {k for k, v in prior['artifacts'].items() if v != now['artifacts'][k]} == {
        'boot.img', 'payload.img', 'self-check/kernel.macho'}
    for name, info in now['artifacts'].items():
        assert describe(R15 / artifact_path(name)) == info, name
    extracted = R15 / 'self-check-package/extracted'
    assert sha(extracted / 'kernel.macho') == sha(NEW / 'prelink.macho')
    trustcache = describe(extracted / 'kernel.macho.trustcache')
    assert trustcache == describe(R14 / 'self-check-package/extracted/kernel.macho.trustcache')
    output = run('root-match', [sys.executable, '-B', DEVICE / 'scripts/check-enuma-root-match.py',
                 '--build-dir', extracted.parent / 'packaging', '--macho', extracted / 'kernel.macho'],
                 R15, env)
    assert output.startswith('OK:'), output
    assert baseline()[2] == frozen
    write_json(R15 / 'delta-vs-r14.json', dict(before=prior['artifacts'], after=now['artifacts'],
               package_before=prior['package_audit'], package_after=now['package_audit'],
               trustcache=trustcache, native_before=describe(OLD / 'native.macho'),
               native_after=describe(NEW / 'native.macho'), **data['r15_delta']))


if __name__ == '__main__':
    commands = {'kernel': kernel, 'package': package}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        raise SystemExit(f'usage: {Path(__file__).name} {{kernel|package}}')
    commands[sys.argv[1]]()
