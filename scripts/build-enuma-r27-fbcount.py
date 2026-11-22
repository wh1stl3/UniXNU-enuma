#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Replay r23 with two replacement objects and the original display archive (WSL)."""

import argparse
import os
from pathlib import Path
import re
import runpy
import shutil
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
C = runpy.run_path(str(Path(__file__).with_name('build-enuma-r25-census.py')))
H = C['H']
DEVICE, OLD, OUT, INPUT, R19 = (C[k] for k in ('DEVICE', 'OLD', 'OUT', 'INPUT', 'R19'))
digest, artifact, snapshot, read_json = (C[k] for k in ('digest', 'artifact', 'snapshot', 'read_json'))
DEFAULT = OUT / 'ufs-sm8250-launchd-fbcount-20261123-r27'
R10 = OUT / 'ufs-sm8250-launchd-display-20261121-r10/self-check/build-final'
DISPLAY = 'libEnumaGopLegacy.a'
DISPLAY_INIT = '__GLOBAL__sub_I_NativeLegacyDisplay.cpp'
DISPLAY_PIN = 'c88510ae599cd678d2b0f83a98034d61a5e5e167e05295cb9c58085672cbb1b5'
FORMATS = ('enuma-fb: begin\n', 'enuma-fb: fb_client=%llu last_comm=%s\n', 'enuma-fb: end\n')


def check_linked(path, call):
    blob = path.read_bytes()
    formats = {fmt: blob.count(fmt.encode() + b'\0') for fmt in FORMATS}
    assert set(formats.values()) == {1} and blob.count(b'enuma-fb: ') == 3
    assert not call('undefined-' + path.name, ['llvm-nm', '-u', path]).strip()
    _, syms = H['symbols'](blob, H['macho'](blob))
    assert not [sym for sym in syms if not sym[1] & 0xe0 and sym[1] & 0x0e == 0]
    definition, = [sym for sym in syms if sym[0] == DISPLAY_INIT and not sym[1] & 0xe0]
    assert definition[1] & 0x0f == 0x0f

    def branches(sym):
        text = call(f'{path.name}-{sym}', ['llvm-objdump', '-d', '--disassemble-symbols=' + sym, path])
        assert f'<{sym}>:' in text, (path, sym)
        return re.findall(r'\b(?:bl|b)\s+\S+\s+<(_\w+)>', text)

    calls = {}
    for caller, targets in (
        ('_is_io_service_open_extended', {'_enuma_fb_record_open': 1}),
        ('_exec_mach_imgact', {'_enuma_fb_arm': 1}),
        ('_enuma_fb_arm', {'_thread_call_allocate_with_options': 1, '_thread_call_enter_delayed': 1}),
        ('_enuma_fb_dump', {'_printf': 3, '_thread_call_enter_delayed': 1, '_thread_call_free': 1}),
    ):
        actual = branches(caller)
        calls[caller] = {target: actual.count(target) for target in targets}
        assert calls[caller] == targets, (path, caller, calls[caller])
    hid = branches('_load_init_program')
    assert hid.count('_enuma_hid_standin_start') == 1
    assert hid.index('_sheng_boot_watchdog_policy') < hid.index('_enuma_hid_standin_start')
    return dict(formats=formats, calls=calls, undefined_including_weak=0, post_watchdog_hid_calls=1,
                display_init=dict(symbol=DISPLAY_INIT, address=hex(definition[3])))


def build(out, dtb):
    C['check_base']()
    prior = read_json(OLD / 'candidate-manifest.json')
    assert prior['artifacts']['boot.img']['sha256'] == 'f82391886dea2a47915a51c6455b51924285dc3ff8e447adc768ea1775e0da1b'
    assert all(artifact(OLD / n) == v for n, v in prior['artifacts'].items())
    assert all(artifact(OLD / n) == v['new'] for n, v in prior['outputs'].items())
    assert all(artifact(OLD / 'objects' / n) == v for n, v in prior['archive_and_objects'].items())
    old_files = snapshot(p for p in sorted(OLD.rglob('*')) if p.is_file())
    paths = [Path(line) for line in (OLD / 'link.filelist').read_text().splitlines()]
    old_exec, = [p for p in paths if p.name == 'kern_exec.o']
    old_uc, = [p for p in paths if p.name == 'IOUserClient.cpo']
    assert old_exec == OLD / 'objects/kern_exec.o' and artifact(old_exec) == prior['kern_exec_new']
    assert old_uc == R10 / 'objects/IOUserClient.cpo'

    steps = {e['tag']: e for e in read_json(INPUT / 'kernel-build-result.json')['r13_delta']['steps']}
    link = steps['link']
    watch, hid = R19 / 'objects/libEnumaBootWatchdogPolicy.a', OLD / 'objects/libShengHidInputStandin.a'
    direct = [Path(a.rsplit(',', 1)[-1]) for a in link['argv'] if a.endswith(('.o', '.a'))]
    search = [Path(a[2:]) for a in link['argv'] if a.startswith('-L')]
    for a in link['argv']:
        if a.startswith('-l'):
            direct.append(next(d / ('lib' + a[2:] + '.a') for d in search
                               if (d / ('lib' + a[2:] + '.a')).is_file()))
    archive, = [p for p in direct if p.name == DISPLAY]
    assert link['argv'].count(f'-Wl,-force_load,{archive}') == 1
    assert digest(archive) == DISPLAY_PIN
    frozen_inputs = snapshot([*paths, watch, hid, *direct])
    pins = {Path(p): h for h, p in
            (line.split('  ', 1) for line in (H['R22'] / 'r21-link-inputs.sha256').read_text().splitlines())}
    assert frozen_inputs[str(watch)] == pins[INPUT / 'objects' / watch.name]
    for p in paths:
        if p != old_exec:
            assert frozen_inputs[str(p)] == pins[p], p

    src, objects = out / 'source', out / 'objects'
    bsd, iokit = src / 'bsd/kern', src / 'iokit/Kernel'
    for directory in (bsd, iokit, objects, out / 'logs', out / 'tmp'):
        directory.mkdir(parents=True)
    env = {**os.environ, **H['linux_env'](SimpleNamespace(tree=Path(link['cwd']).parents[3])),
           'PYTHONDONTWRITEBYTECODE': '1'}
    env.update(PATH='/home/wh1stl3/.local/bin:' + env['PATH'], TMPDIR=str(out / 'tmp'))

    def call(tag, argv, cwd=out):
        return H['run'](argv, cwd, env, out / 'logs' / (tag + '.log'))

    old_bsd = OLD / 'source/bsd/kern'
    for p in old_bsd.glob('*.h'):
        shutil.copyfile(p, bsd / p.name)
    assert digest(old_bsd / 'kern_exec.c') == C['OLD_SOURCES']['exec']
    shutil.copyfile(old_bsd / 'kern_exec.c', bsd / 'kern_exec.c')
    shutil.copyfile(DEVICE / 'package/EnumaFbOpenCount.inc', bsd / 'EnumaFbOpenCount.inc')
    r10 = read_json(R10 / 'kernel-build-result.json')
    uc_cc, = [e for e in r10['commands'] if e['tag'] == 'compile-IOUserClient.cpo']
    uc_source = Path(uc_cc['argv'][2])
    assert artifact(uc_source) == r10['inputs'][str(uc_source)]
    assert Path(uc_cc['argv'][4]) == old_uc
    shutil.copyfile(uc_source, iokit / uc_source.name)
    patch = ['patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i',
             DEVICE / 'patches/xnu/enuma-r27-fbcount.patch']
    for tag, argv in (('patch-check', patch + ['--dry-run']), ('patch', patch)):
        assert 'offset' not in call(tag, argv, src)

    replacements, units = {}, {}
    for cc, old, new_src in ((steps['compile-kern_exec.o'], old_exec, bsd / 'kern_exec.c'),
                             (uc_cc, old_uc, iokit / uc_source.name)):
        argv = cc['argv'].copy()
        assert argv[1] in ('-xc', '-xc++') and Path(argv[2]).name == new_src.name and argv[3] == '-o'
        obj = objects / old.name
        argv[2], argv[4] = new_src, obj
        if '-MF' in argv:
            argv[argv.index('-MF') + 1] = obj.with_suffix('.d')
        assert not {'-MJ', '-serialize-diagnostics'} & set(argv)
        if old == old_uc:
            argv += ['-iquote', uc_source.parent]
        call('compile-' + old.name, argv, cc['cwd'])
        assert digest(obj) != frozen_inputs[str(old)]
        units[old.name] = dict(old=artifact(old), new=artifact(obj))
        replacements[old] = obj

    (out / 'link.filelist').write_text(''.join(f'{replacements.get(p, p)}\n' for p in paths))
    origin = Path(steps['prelink']['cwd'])
    for tag in ('link', 'prelink'):
        step = steps[tag]
        argv = step['argv']
        for name in ('link.filelist', 'native.macho', 'native-link.map', 'prelink.macho'):
            argv = [arg.replace(str(origin / name), str(out / name)) for arg in argv]
        if tag == 'link':
            argv += [f'-Wl,-force_load,{p}' for p in (watch, hid)]
        call(tag, argv, out if tag == 'prelink' else step['cwd'])
    linked = {n: check_linked(out / n, call) for n in ('native.macho', 'prelink.macho')}
    link_map = (out / 'native-link.map').read_text(encoding='utf-8', errors='surrogateescape')
    owner, = re.findall(r'^\[(\d+)\] ' + re.escape(f'{archive}(NativeLegacyDisplay.late.o)') + '$',
                        link_map, re.M)
    assert re.search(r'\[' + owner + r'\]\s+' + re.escape(DISPLAY_INIT) + '$', link_map, re.M)
    old_plan, new_plan = (read_json(p / 'prelink.json') for p in (OLD, out))
    for key in ('components', 'codeless_components', 'original_executable_sha256'):
        assert new_plan[key] == old_plan[key]
    result = C['pack'](out, prior, dtb)
    assert old_files == snapshot(p for p in sorted(OLD.rglob('*')) if p.is_file())
    assert frozen_inputs == snapshot(map(Path, frozen_inputs))
    C['check_base']()
    outputs = {}
    for n in ('native.macho', 'prelink.macho', 'payload.img', 'boot.img'):
        before, after = artifact(OLD / n), artifact(out / n)
        outputs[n] = dict(old=before, new=after, delta_bytes=after['bytes'] - before['bytes'])
    H['write_json'](out / 'candidate-manifest.json', dict(
        status='self-checked; host only', base=H['BASE_PIN'], units=units, linked=linked, outputs=outputs,
        display_archive=dict(path=str(archive), native_init_owner=f'[{owner}] NativeLegacyDisplay.late.o',
                             **artifact(archive)),
        unchanged_filelist_entries=len(paths) - len(replacements),
        reused_link_inputs={p: h for p, h in frozen_inputs.items() if Path(p) not in replacements},
        r23_files_unchanged={str(Path(p).relative_to(OLD)): h for p, h in old_files.items()}, **result))
    print(out / 'candidate-manifest.json')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=DEFAULT)
    parser.add_argument('--dtb', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    assert out.parent == OUT and not out.exists()
    build(out, args.dtb.resolve())
