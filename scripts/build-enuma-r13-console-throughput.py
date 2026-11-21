#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Recompile one XNU object, then replay the r11 link, prelink and packaging."""
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True
DEVICE = Path(__file__).resolve().parents[1]
BASE = DEVICE.parents[1] / 'UniXNU'
R11 = DEVICE / 'out/ufs-sm8250-launchd-keystore-20261121-r11'
R13 = DEVICE / 'out/ufs-sm8250-launchd-keystore-20261122-r13'
OLD = R11 / 'self-check/build-final'
NEW = R13 / 'self-check/build-final'
PIN = '693f5d9cae8a408dd18b39f3f9fdc4228c934241'

FORMATS = (
    b'enuma-con: %04u ' + b'A' * 61 + b'\n',
    b'enuma-con: lines=20 chars=1560 ns=%llu ns_per_line=%llu ns_per_char=%llu\n',
    b'enuma-con: %04u B\n',
    b'enuma-con: lines=5 chars=90 ns=%llu\n',
)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def describe(path):
    return dict(bytes=path.stat().st_size, sha256=sha(path))


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def build_kernel():
    data = json.loads((OLD / 'kernel-build-result.json').read_text())
    commands = {entry['tag']: entry for entry in data['commands'] + data['r11_delta']['steps']}
    link = commands['link']
    objroot = Path(link['cwd'])
    tree = objroot.parents[3]
    assert subprocess.check_output(['git', '-C', BASE, 'rev-parse', 'HEAD'],
                                   text=True).strip() == PIN
    assert sha(OLD / 'native.macho') == data['diff_vs_r4']['new_sha256']
    assert sha(OLD / 'prelink.macho') == data['diff_vs_r4']['prelink_sha256']
    old_list = (OLD / 'link.filelist').read_text().splitlines()
    cc = commands['compile-kern_exec.o']['argv']
    old_object = cc[4]
    assert old_list.count(old_object) == 1
    local_old = OLD / 'objects/kern_exec.o'
    assert sha(old_object) == sha(local_old) == data['macros']['kern_exec.o']['object_sha256']
    assert sha(cc[2]) == '4c4d4d2d9a88ce47bb55d805541189b8075948ed54e561925cd02d9e415b925c'
    # The filelist plus explicit .a/.o inputs (including the r11 AKS archive).
    explicit = [arg.split(',')[-1] for arg in link['argv']
                if arg.endswith(('.o', '.a'))]
    others = sorted((set(old_list) | set(explicit)) - {old_object})
    before = {path: sha(path) for path in others}
    obj = NEW / 'objects'
    obj.mkdir(parents=True)
    (NEW / 'logs').mkdir()
    (NEW / 'tmp').mkdir()
    sources = NEW / 'source'
    source = sources / 'bsd/kern/kern_exec.c'
    source.parent.parent.mkdir(parents=True)
    shutil.copytree(Path(cc[2]).parent, source.parent, symlinks=True)
    assert sha(source) == sha(cc[2])

    sys.path.insert(0, str(BASE / 'scripts'))
    from unixnu.kernel import linux_env
    env = dict(os.environ)
    env.update(linux_env(SimpleNamespace(tree=tree)))
    env['PATH'] = '/home/wh1stl3/.local/bin:' + env['PATH']
    env.update(TMPDIR=str(NEW / 'tmp'), PYTHONDONTWRITEBYTECODE='1')
    steps = []

    def run(tag, argv, cwd=NEW):
        argv = list(map(str, argv))
        reply = subprocess.run(argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True)
        log = NEW / 'logs' / f'{tag}.log'
        log.write_text(reply.stdout)
        steps.append(dict(tag=tag, argv=argv, cwd=str(cwd), exit=reply.returncode))
        if reply.returncode:
            first = next((line for line in reply.stdout.splitlines() if 'error:' in line),
                         reply.stdout.split('\n')[0])
            raise SystemExit(f'{tag}: {first} (exit {reply.returncode}; {log})')
        print(tag, flush=True)
        return reply.stdout

    patch = DEVICE / 'patches/xnu/enuma-r13-console-throughput.patch'
    output = run('apply-console-probe', ['patch', '--batch', '--forward', '--fuzz=0',
                                         '-p1', '-i', patch], sources)
    assert 'offset' not in output and 'fuzz' not in output, output
    def includes(argv, tag):
        output = run(tag, list(argv) + ['-###'], commands['compile-kern_exec.o']['cwd'])
        line, = [line.strip() for line in output.splitlines() if '"-cc1"' in line]
        args = shlex.split(line)
        return [args[i + 1] for i, arg in enumerate(args[:-1]) if arg == '-I']

    old_includes = includes(cc, 'cc1-includes-r11')
    new_cc = list(cc)
    new_cc[2], new_cc[4] = str(source), str(obj / 'kern_exec.o')
    new_includes = includes(new_cc, 'cc1-includes-r13')
    assert old_includes == new_includes
    print('cc1 -I r11 vs r13 (identical):', flush=True)
    for index, path in enumerate(old_includes):
        print(f'{index:02d}: {path} == {new_includes[index]}', flush=True)
    write_json(NEW / 'cc1-includes.json', dict(r11=old_includes, r13=new_includes,
                                                identical=True))
    for tag, name in (('compile-kern_exec.o', 'kern_exec.o'),
                      ('macros-kern_exec.o', 'kern_exec.o.i')):
        entry = commands[tag]
        argv = list(entry['argv'])
        assert argv[2] == cc[2] and argv[3] == '-o', argv[:5]
        argv[2], argv[4] = str(source), str(obj / name)
        run(tag, argv, entry['cwd'])
    # Source-path __FILE__ macros can differ; all selected r11 feature defines must not.
    macro = data['macros']['kern_exec.o']
    defines = (obj / 'kern_exec.o.i').read_text().splitlines()
    assert all('#define ' + definition in defines
               for definition in macro['required_defines'] + ['XNU_ENUMA_PATH_PROBE 1'])
    replacement = obj / 'kern_exec.o'
    assert sha(replacement) != sha(local_old)
    filelist = NEW / 'link.filelist'
    filelist.write_text('\n'.join(str(replacement) if p == old_object else p
                                 for p in old_list) + '\n')
    outputs = ('link.filelist', 'native.macho', 'native-link.map', 'prelink.macho')
    for tag in ('link', 'prelink'):
        entry = commands[tag]
        argv = list(entry['argv'])
        for name in outputs:
            argv = [a.replace(str(OLD / name), str(NEW / name)) for a in argv]
        run(tag, argv, NEW if tag == 'prelink' else entry['cwd'])
    assert before == {path: sha(path) for path in others}

    # The r11 object had no console formats; count NUL-terminated formats
    # separately from machine-code call sites in the two linked kernels.
    assert b'enuma-con:' not in local_old.read_bytes()
    calls = {}
    for path in (replacement, NEW / 'native.macho', NEW / 'prelink.macho'):
        blob = path.read_bytes()
        assert blob.count(b'enuma-con:') == len(FORMATS), path
        assert all(blob.count(fmt + b'\0') == 1 for fmt in FORMATS), path
        if path == replacement:
            continue
        assert not run('undefined-' + path.name, ['llvm-nm', '-u', path]).strip()
        symbols = run('symbols-' + path.name, ['llvm-nm', '-m', path])
        assert '(undefined)' not in symbols
        assert sum(line.endswith(' _enuma_console_probe') for line in symbols.splitlines()) == 1
        assert all(sum(line.endswith(' ' + symbol) for line in symbols.splitlines()) == 1
                   for symbol in data['r11_delta']['owners'])
        disasm = run('console-' + path.name, ['llvm-objdump', '-d',
                     '--disassemble-symbols=_enuma_console_probe', path])
        calls[path.name] = {callee: len(re.findall(r'\bbl\s+\S+\s+<_' + callee + r'>', disasm))
                            for callee in ('printf', 'mach_absolute_time', 'absolutetime_to_nanoseconds')}
        assert calls[path.name] == dict(printf=27, mach_absolute_time=4,
                                       absolutetime_to_nanoseconds=2), calls[path.name]
        init = run('load-init-' + path.name, ['llvm-objdump', '-d',
                   '--disassemble-symbols=_load_init_program', path])
        assert len(re.findall(r'\b(?:b|bl)\s+\S+\s+<_enuma_console_probe>', init)) == 1, path

    data['diff_vs_r4'].update(new_sha256=sha(NEW / 'native.macho'),
                             prelink_sha256=sha(NEW / 'prelink.macho'),
                             prelink_bytes=(NEW / 'prelink.macho').stat().st_size)
    macro.update(object_sha256=sha(replacement), object_bytes=replacement.stat().st_size,
                 source_sha256=sha(source), macros_dump_sha256=sha(obj / 'kern_exec.o.i'))
    data['r13_delta'] = dict(old_object=describe(local_old), new_object=describe(replacement),
                             unchanged_explicit_link_inputs=before, formats=[f.decode() for f in FORMATS],
                             probe_calls=calls, steps=steps)
    write_json(NEW / 'kernel-build-result.json', data)
    for path in (OLD / 'objects').iterdir():
        if not (obj / path.name).exists():
            shutil.copyfile(path, obj / path.name)
            assert sha(path) == sha(obj / path.name), path
    shutil.copyfile(OLD / 'seed-inspection.json', NEW / 'seed-inspection.json')


def package():
    recipe = R11 / 'run_packaging.py'
    wrapper = R11 / 'r7-payload-wrapper.py'
    assert sha(recipe) == '94222d17e627a2a5b790a3fab99f943c5428836ae6ce98eb8c73e614242b283e'
    assert sha(wrapper) == '2db5b7f1a215cdabf9394d0d47a2b03a23c6874d9de45bba38d884d36c21867a'
    text = recipe.read_text()
    start = text.index('    r10objects = ')
    end = text.index("    kernel_build['macros']['kern_exec.o']['object_equals_r4']", start)
    text = text[:start] + f"""    r11objects = Path({str(OLD / 'objects')!r})
    for unit in sorted(p.name for p in r11objects.iterdir()):
        same = sha256_file(original / 'objects' / unit) == sha256_file(r11objects / unit)
        if unit != 'kern_exec.o.i':
            assert same == (unit != 'kern_exec.o'), unit
""" + text[end:]
    text = text.replace('r11 scratch AppleKeyStore state probe; not deployed',
                        'r13 pre-exec console throughput probe; not deployed')
    text = text.replace("'r11_delta': kernel_build['r11_delta'],",
                        "'r13_delta': kernel_build['r13_delta'],")
    shutil.copyfile(wrapper, R13 / wrapper.name)
    packaged = R13 / recipe.name
    packaged.write_text(text)
    feeds = R11 / 'self-check-package/packaging/out/feeds'
    assert feeds.is_dir()
    subprocess.run([sys.executable, '-B', packaged, '--seed-feeds-from', feeds],
                   cwd=R13, check=True)

    prior, now = (json.loads((r / 'candidate-manifest.json').read_text()) for r in (R11, R13))
    for key in prior['package_audit'].keys() - {'payload_content_bytes'}:
        assert prior['package_audit'][key] == now['package_audit'][key], key
    changed = {'boot.img', 'payload.img', 'self-check/kernel.macho'}
    assert {k for k, v in prior['artifacts'].items() if v != now['artifacts'][k]} == changed
    for name in ('boot.img', 'payload.img'):
        assert sha(R11 / name) == prior['artifacts'][name]['sha256']
        assert sha(R13 / name) == now['artifacts'][name]['sha256']
    before = R11 / 'self-check-package/extracted/kernel.macho.trustcache'
    after = R13 / 'self-check-package/extracted/kernel.macho.trustcache'
    assert sha(before) == sha(after)
    write_json(R13 / 'delta-vs-r11.json', dict(before=prior['artifacts'], after=now['artifacts'],
               package_before=prior['package_audit'], package_after=now['package_audit'],
               trustcache=describe(after), native_before=describe(OLD / 'native.macho'),
               native_after=describe(NEW / 'native.macho')))


if __name__ == '__main__':
    commands = {'kernel': build_kernel, 'package': package}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        raise SystemExit('usage: build-enuma-r13-console-throughput.py {kernel|package}')
    commands[sys.argv[1]]()
