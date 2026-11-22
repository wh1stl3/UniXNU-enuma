#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Rebuild only the r23 exec/exit probes and replace the packed kernel (WSL)."""

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
H = runpy.run_path(str(Path(__file__).with_name('build-enuma-r23-hid-standin.py')))
R = H['R']
DEVICE, BASE, OUT, INPUT, R19 = (H[k] for k in ('DEVICE', 'BASE', 'OUT', 'INPUT', 'R19'))
OLD = OUT / 'ufs-sm8250-launchd-hid-20261122-r23'
DEFAULT = OUT / 'ufs-sm8250-launchd-census-20261122-r25'
read_json, artifact = H['json_file'], H['artifact']
digest, snapshot, read_member = (R[k] for k in ('digest', 'snapshot', 'read_member'))
FORMATS = ('enuma-census: begin n=%u\n',
           'enuma-census: %s exec=%u exit=%u last_st=%d last_sig=%d\n',
           'enuma-census: end\n', 'enuma-census: table-full\n')
OLD_SOURCES = {
    'exec': '2f1226a204d1870e75bfe0b10f52b85178445a26ead079ba7c0284a5bd1f10ba',
    'exit': '75e86b5cd04141f068b5feb608fcc3558955670b5216a10d71a6ba3ed49bdb22',
}


def check_base():
    assert subprocess.check_output(['git', '-C', BASE, 'rev-parse', 'HEAD'],
                                   text=True).strip() == H['BASE_PIN']


def string_counts(path, expect):
    blob = path.read_bytes()
    assert all(f'enuma-{event}:'.encode() not in blob for event in ('exec', 'exit')), path
    result = {fmt: blob.count(fmt.encode() + b'\0') for fmt in FORMATS}
    assert all(n == expect for n in result.values()), (path, result)
    return result


def check_linked(out, name, call):
    path = out / name
    assert not call('undefined-' + name, ['llvm-nm', '-u', path]).strip()
    blob = path.read_bytes()
    _, syms = H['symbols'](blob, H['macho'](blob))
    assert not [sym for sym in syms if not sym[1] & 0xe0 and sym[1] & 0x0e == 0]
    counts = dict(formats=string_counts(path, 1), undefined_including_weak=0)

    def branches(sym):
        dump = call(f'{name}-{sym}', ['llvm-objdump', '-d', '--disassemble-symbols=' + sym, path])
        assert f'<{sym}>:' in dump, (path, sym)
        return re.findall(r'\b(?:bl|b)\s+\S+\s+<(_\w+)>', dump)

    for event, hook in (('exec', '_exec_mach_imgact'), ('exit', '_proc_prepareexit')):
        helper = f'_enuma_census_record_{event}'
        counts[hook + '_to_' + helper] = branches(hook).count(helper)
        assert counts[hook + '_to_' + helper] == 1, (path, hook)
        assert '_printf' not in branches(helper), (path, helper)
    for helper, targets in (
        ('_enuma_census_record_exec', {'_thread_call_allocate_with_options': 1,
                                      '_thread_call_enter_delayed': 1}),
        ('_enuma_census_dump', {'_thread_call_enter_delayed': 1, '_thread_call_free': 1,
                               '_printf': 4}),
    ):
        actual = branches(helper)
        counts[helper] = {target: actual.count(target) for target in targets}
        assert counts[helper] == targets, (path, helper, actual)
    hid = branches('_load_init_program')
    assert hid.count('_enuma_hid_standin_start') == 1
    assert hid.index('_sheng_boot_watchdog_policy') < hid.index('_enuma_hid_standin_start')
    counts['post_watchdog_hid_calls'] = 1
    return counts


def pack(out, prior, dtb):
    src, payload = OLD / 'payload.img', out / 'payload.img'
    shutil.copytree(OLD / 'device', out / 'device')
    shutil.copyfile(src, payload)
    kernel = out / 'prelink.macho'
    stamp = H['payload_step'].EPOCH
    os.utime(kernel, (stamp, stamp))
    subprocess.run(['mcopy', '-o', '-m', '-i', payload, kernel, '::/EFI/UniXNU/' + R['MEMBERS'][0]],
                   env=dict(os.environ, MTOOLS_SKIP_CHECK='1', TZ='UTC'), check=True)
    assert R['fat_tree'](src) == R['fat_tree'](payload)
    members = {}
    for name in R['MEMBERS']:
        data = read_member(payload, name)
        members[name] = {'bytes': len(data), 'sha256': H['sha'](data)}
        if name != R['MEMBERS'][0]:
            assert data == read_member(src, name)
        if name == R['ADT']:
            adt = R['read_properties'](data)
            assert adt[R['SIZE_KEY']] == struct.pack('<Q', 0xaa000000)
            assert adt[R['SLEEP_KEY']] == struct.pack('<I', 1)
            (out / Path(name).name).write_bytes(data)
        if name == 'unixnu.toml':
            (out / name).write_bytes(data)
    changed = [n for n in members if members[n] != prior['fat_members'][n]]
    assert changed == [R['MEMBERS'][0]] and members[changed[0]] == artifact(kernel)
    config = tomllib.loads((out / 'unixnu.toml').read_text())
    args, = [x['args'] for x in config['entry'] if x['id'] == 'xnu']
    assert args.split() == tomllib.loads((out / 'device/board.toml').read_text())['payload']['kernel_args']
    local = H['R21'] / 'self-check-package/packaging/local-build.toml'
    uefi = DEVICE.parent / 'uefi-enuma'
    fd = uefi / 'Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd'
    ref = read_json(OLD / 'boot.json')
    assert digest(fd) == ref['fd_sha256'] and digest(dtb) == ref['dtb_sha256']
    ctx = H['Context'](H['parser']().parse_args([
        'bootimg', '-D', str(out / 'device'), '--out', str(out / 'work'), '--config', str(local),
        '--local-module', 'soc:sm8250=' + str(DEVICE.parent / 'UniXNU-sm8250-common'),
    ]))
    boot = out / 'boot.img'
    H['bootimg'].build(ctx, uefi, fd, dtb, payload, boot)
    offset = prior['boot_payload_offset']
    with (OLD / 'boot.img').open('rb') as a, boot.open('rb') as b:
        x, y = a.read(offset), b.read(offset)
        assert x[:576] == y[:576] and x[596:] == y[596:] and x[576:596] != y[576:596]
        assert hashlib.file_digest(b, 'sha256').hexdigest() == digest(payload)
    assert all((out / n).stat().st_size == prior['artifacts'][n]['bytes'] for n in ('payload.img', 'boot.img'))
    return dict(fat_members=members, changed_fat_members=changed, args=args,
                adt_memory_size='0xaa000000', adt_sleep_disabled=1,
                boot_payload_offset=offset, boot_prefix_only_id_changed=True)


def build(out, dtb):
    check_base()
    prior = read_json(OLD / 'candidate-manifest.json')
    assert prior['artifacts']['boot.img']['sha256'] == 'f82391886dea2a47915a51c6455b51924285dc3ff8e447adc768ea1775e0da1b'
    assert all(artifact(OLD / n) == v for n, v in prior['artifacts'].items())
    assert all(artifact(OLD / n) == v['new'] for n, v in prior['outputs'].items())
    assert all(artifact(OLD / 'objects' / n) == v for n, v in prior['archive_and_objects'].items())
    assert artifact(OLD / 'objects/kern_exec.o') == prior['kern_exec_new']
    for n in R['MEMBERS']:
        member = read_member(OLD / 'payload.img', n)
        assert {'bytes': len(member), 'sha256': H['sha'](member)} == prior['fat_members'][n]

    r23_paths = [p for p in sorted(OLD.rglob('*')) if p.is_file()]
    old_files = snapshot(r23_paths)
    paths = [Path(line) for line in (OLD / 'link.filelist').read_text().splitlines()]
    watch = R19 / 'objects/libEnumaBootWatchdogPolicy.a'
    hid = OLD / 'objects/libShengHidInputStandin.a'
    steps = {e['tag']: e for e in read_json(INPUT / 'kernel-build-result.json')['r13_delta']['steps']}
    link = steps['link']
    tree = Path(link['cwd']).parents[3]
    pins = {Path(p): h for h, p in
            (line.split('  ', 1) for line in (H['R22'] / 'r21-link-inputs.sha256').read_text().splitlines())}
    direct = [Path(a.rsplit(',', 1)[-1]) for a in link['argv'] if a.endswith(('.o', '.a'))]
    search = [Path(a[2:]) for a in link['argv'] if a.startswith('-L')]
    for a in link['argv']:
        if a.startswith('-l'):
            direct.append(next(d / ('lib' + a[2:] + '.a') for d in search if
                               (d / ('lib' + a[2:] + '.a')).is_file()))
    assert digest(watch) == pins[INPUT / 'objects' / watch.name]
    frozen_inputs = snapshot([*paths, watch, hid, *direct])
    for p in paths:
        if p != OLD / 'objects/kern_exec.o':
            assert frozen_inputs[str(p)] == pins[p], p

    source = out / 'source/bsd/kern'
    for directory in (out / 'logs', out / 'objects', out / 'tmp'):
        directory.mkdir(parents=True)
    source.mkdir(parents=True)
    # Use the same local headers as the r23 build, without copying unrelated TUs.
    old_source = OLD / 'source/bsd/kern'
    for p in old_source.glob('*.h'):
        shutil.copyfile(p, source / p.name)
    for event, pin in OLD_SOURCES.items():
        name = f'kern_{event}.c'
        assert digest(old_source / name) == pin
        shutil.copyfile(old_source / name, source / name)
    for name in ('EnumaProcessCensus.h', 'EnumaProcessCensus.inc'):
        shutil.copyfile(DEVICE / 'package' / name, source / name)
    env = {**os.environ, **H['linux_env'](SimpleNamespace(tree=tree)), 'PYTHONDONTWRITEBYTECODE': '1'}
    env.update(PATH='/home/wh1stl3/.local/bin:' + env['PATH'], TMPDIR=str(out / 'tmp'))

    def call(tag, argv, cwd=out):
        return H['run'](argv, cwd, env, out / 'logs' / (tag + '.log'))

    patch = ['patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i',
             DEVICE / 'patches/xnu/enuma-r25-census.patch']
    for tag, cmd in (('patch-check', patch + ['--dry-run']), ('patch', patch)):
        assert 'offset' not in call(tag, cmd, out / 'source')

    exec_cc = steps['compile-kern_exec.o']
    exit_db = Path(exec_cc['cwd']) / 'kern_exit.o.json'
    exit_cc = json.loads(exit_db.read_text().strip().rstrip(','))
    replacements, units = {}, {}
    for event, argv, cwd in (('exec', exec_cc['argv'], exec_cc['cwd']),
                             ('exit', exit_cc['arguments'], exit_cc['directory'])):
        argv = list(argv)
        name = f'kern_{event}'
        old, = [p for p in paths if p.name == name + '.o']
        obj = out / 'objects' / old.name
        assert argv[1] == '-xc' and Path(argv[2]).name == name + '.c' and argv[3] == '-o'
        argv[2], argv[4] = source / (name + '.c'), obj
        if '-MF' in argv:
            argv[argv.index('-MF') + 1] = obj.with_suffix('.d')
        assert not {'-MJ', '-serialize-diagnostics'} & set(argv)
        call(name, argv, cwd)
        assert digest(obj) != frozen_inputs[str(old)]
        units[old.name] = dict(old=artifact(old), new=artifact(obj),
                               formats=string_counts(obj, int(event == 'exec')))
        replacements[old] = obj
    (out / 'link.filelist').write_text(''.join(f'{replacements.get(p, p)}\n' for p in paths))
    for tag in ('link', 'prelink'):
        step = steps[tag]
        origin = Path(steps['prelink']['cwd'])
        argv = step['argv']
        for n in ('link.filelist', 'native.macho', 'native-link.map', 'prelink.macho'):
            argv = [arg.replace(str(origin / n), str(out / n)) for arg in argv]
        if tag == 'link':
            argv += [f'-Wl,-force_load,{p}' for p in (watch, hid)]
        call(tag, argv, out if tag == 'prelink' else step['cwd'])
    linked = {n: check_linked(out, n, call) for n in ('native.macho', 'prelink.macho')}
    old_plan, new_plan = (read_json(p / 'prelink.json') for p in (OLD, out))
    for key in ('components', 'codeless_components', 'original_executable_sha256'):
        assert new_plan[key] == old_plan[key]
    result = pack(out, prior, dtb)
    assert old_files == snapshot(r23_paths) and frozen_inputs == snapshot(map(Path, frozen_inputs))
    check_base()
    outputs = {}
    for n in ('native.macho', 'prelink.macho', 'payload.img', 'boot.img'):
        before, after = artifact(OLD / n), artifact(out / n)
        outputs[n] = dict(old=before, new=after, delta_bytes=after['bytes'] - before['bytes'])
    H['write_json'](out / 'candidate-manifest.json',
                    dict(status='self-checked; host only', base=H['BASE_PIN'],
                         units=units, linked=linked, outputs=outputs,
                         unchanged_filelist_entries=len(paths) - len(replacements),
                         unchanged_link_inputs=len(frozen_inputs) - len(replacements),
                         r23_files_unchanged={str(Path(p).relative_to(OLD)): h for p, h in old_files.items()},
                         **result))
    print(out / 'candidate-manifest.json')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=DEFAULT)
    parser.add_argument('--dtb', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    assert out.parent == OUT and not out.exists()
    build(out, args.dtb.resolve())
