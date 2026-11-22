#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Build the isolated r26 framebuffer-count candidate on WSL."""

import argparse
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
C = runpy.run_path(str(Path(__file__).with_name('build-enuma-r25-census.py')))
H = C['H']
DEVICE, OLD, OUT, INPUT = (C[k] for k in ('DEVICE', 'OLD', 'OUT', 'INPUT'))
digest, artifact, snapshot, read_json = (C[k] for k in ('digest', 'artifact', 'snapshot', 'read_json'))
DEFAULT = OUT / 'ufs-sm8250-launchd-fbcount-20261122-r26'
DISPLAY = OUT / 'enuma-gop-production-20261114-r5/display'
ARCHIVE = 'libEnumaGopLegacy.a'
MEMBERS = ('NativeLegacyDisplay.late.o', 'EnumaLegacyDisplay.o', 'original-bindings.o')
FORMATS = ('enuma-fb: begin\n', 'enuma-fb: start=%llu userclient=%llu swap=%llu last_comm=%s\n',
           'enuma-fb: end\n')


def check_linked(path, call):
    blob = path.read_bytes()
    formats = {fmt: blob.count(fmt.encode() + b'\0') for fmt in FORMATS}
    assert set(formats.values()) == {1} and blob.count(b'enuma-fb: ') == 3
    assert not call('undefined-' + path.name, ['llvm-nm', '-u', path]).strip()
    _, syms = H['symbols'](blob, H['macho'](blob))
    assert not [sym for sym in syms if not sym[1] & 0xe0 and sym[1] & 0x0e == 0]

    def branches(sym):
        text = call(f'{path.name}-{sym}', ['llvm-objdump', '-d', '--disassemble-symbols=' + sym, path])
        assert f'<{sym}>:' in text, (path, sym)
        return re.findall(r'\b(?:bl|b)\s+\S+\s+<(_\w+)>', text)

    calls = {}
    for caller, targets in (
        ('__ZN19NativeLegacyDisplay5startEP9IOService', {'_enuma_fb_record_start': 1}),
        ('__ZN19NativeLegacyDisplay13newUserClientEP4taskPvjPP12IOUserClient', {'_enuma_fb_record_client': 1}),
        ('__ZN19NativeLegacyDisplay12validateSwapEPK25OriginalLegacySwapRequest', {'_enuma_fb_record_swap': 1}),
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
    return dict(formats=formats, calls=calls, undefined_including_weak=0, post_watchdog_hid_calls=1)


def build(out, dtb):
    C['check_base']()
    prior = read_json(OLD / 'candidate-manifest.json')
    assert prior['artifacts']['boot.img']['sha256'] == 'f82391886dea2a47915a51c6455b51924285dc3ff8e447adc768ea1775e0da1b'
    assert all(artifact(OLD / n) == v for n, v in prior['artifacts'].items())
    assert all(artifact(OLD / n) == v['new'] for n, v in prior['outputs'].items())
    assert all(artifact(OLD / 'objects' / n) == v for n, v in prior['archive_and_objects'].items())
    r23_files = snapshot(p for p in sorted(OLD.rglob('*')) if p.is_file())

    steps = {e['tag']: e for e in read_json(INPUT / 'kernel-build-result.json')['r13_delta']['steps']}
    link = steps['link']
    tree = Path(link['cwd']).parents[3]
    paths = [Path(line) for line in (OLD / 'link.filelist').read_text().splitlines()]
    old_exec, = [p for p in paths if p.name == 'kern_exec.o']
    assert old_exec == OLD / 'objects/kern_exec.o' and artifact(old_exec) == prior['kern_exec_new']
    watch = C['R19'] / 'objects/libEnumaBootWatchdogPolicy.a'
    hid = OLD / 'objects/libShengHidInputStandin.a'
    direct = [Path(a.rsplit(',', 1)[-1]) for a in link['argv'] if a.endswith(('.o', '.a'))]
    search = [Path(a[2:]) for a in link['argv'] if a.startswith('-L')]
    for a in link['argv']:
        if a.startswith('-l'):
            direct.append(next(d / ('lib' + a[2:] + '.a') for d in search if
                               (d / ('lib' + a[2:] + '.a')).is_file()))
    old_archive, = [p for p in direct if p.name == ARCHIVE]
    assert digest(old_archive) == digest(DISPLAY / ARCHIVE) == 'c88510ae599cd678d2b0f83a98034d61a5e5e167e05295cb9c58085672cbb1b5'
    inputs = snapshot([*paths, watch, hid, *direct])
    pins = {Path(p): h for h, p in
            (line.split('  ', 1) for line in (H['R22'] / 'r21-link-inputs.sha256').read_text().splitlines())}
    assert inputs[str(watch)] == pins[INPUT / 'objects' / watch.name]
    for p in paths:
        if p != old_exec:
            assert inputs[str(p)] == pins[p], p

    src, objects = out / 'source', out / 'objects'
    bsd, display = src / 'bsd/kern', src / 'display'
    for p in (bsd, display, objects, out / 'logs', out / 'tmp'):
        p.mkdir(parents=True)
    env = {**os.environ, **H['linux_env'](SimpleNamespace(tree=tree)), 'PYTHONDONTWRITEBYTECODE': '1'}
    env.update(PATH='/home/wh1stl3/.local/bin:' + env['PATH'], TMPDIR=str(out / 'tmp'))

    def call(tag, argv, cwd=out):
        return H['run'](argv, cwd, env, out / 'logs' / (tag + '.log'))

    old_bsd = OLD / 'source/bsd/kern'
    for p in old_bsd.glob('*.h'):
        shutil.copyfile(p, bsd / p.name)
    assert digest(old_bsd / 'kern_exec.c') == C['OLD_SOURCES']['exec']
    shutil.copyfile(old_bsd / 'kern_exec.c', bsd / 'kern_exec.c')
    shutil.copyfile(DEVICE / 'package/EnumaFbCount.inc', bsd / 'EnumaFbCount.inc')
    saved = DISPLAY / 'source/NativeLegacyDisplay.cpp'
    assert digest(saved) == 'a49d4bfa879aeff270c24b204f64d513dfc132ad09e52ac7483adb7d5df468f8'
    for p in saved.parent.glob('*.h'):
        shutil.copyfile(p, display / p.name)
    shutil.copyfile(saved, display / saved.name)
    patch = ['patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i',
             DEVICE / 'patches/xnu/enuma-r26-fbcount.patch']
    for tag, argv in (('patch-check', patch + ['--dry-run']), ('patch', patch)):
        assert 'offset' not in call(tag, argv, src)

    cc = steps['compile-kern_exec.o']
    argv = cc['argv'].copy()
    assert argv[1] == '-xc' and Path(argv[2]).name == 'kern_exec.c' and argv[3] == '-o'
    new_exec = objects / old_exec.name
    argv[2], argv[4] = bsd / 'kern_exec.c', new_exec
    if '-MF' in argv:
        argv[argv.index('-MF') + 1] = new_exec.with_suffix('.d')
    assert not {'-MJ', '-serialize-diagnostics'} & set(argv)
    call('compile-exec', argv, cc['cwd'])

    recipes = read_json(DISPLAY / 'result.json')['commands']
    cc, objcopy = recipes[2], recipes[4]
    argv = cc['argv'].copy()
    assert argv[1:4] == ['-xc++', str(saved), '-o']
    intermediate = objects / 'NativeLegacyDisplay.o'
    argv[2], argv[4] = display / saved.name, intermediate
    call('compile-display', argv, cc['cwd'])
    late = objects / MEMBERS[0]
    assert objcopy['argv'][1] == '--remove-section=__DATA,__mod_init_func'
    call('strip-display-init', [*objcopy['argv'][:2], intermediate, late])
    # Replay the frozen r5 late-init conversion after its recorded objcopy:
    # Linux objcopy cannot globalize a Mach-O symbol; set only its N_EXT bit.
    blob = bytearray(late.read_bytes())
    table, symbols = H['symbols'](blob, H['macho'](blob))
    index, = [i for i, (name, _, _, _) in enumerate(symbols)
              if name == '__GLOBAL__sub_I_NativeLegacyDisplay.cpp']
    kind_offset = table + 16 * index + 4
    assert blob[kind_offset] & 0x0f == 0x0e
    blob[kind_offset] |= 1
    late.write_bytes(blob)

    units = {old_exec.name: dict(old=artifact(old_exec), new=artifact(new_exec))}
    old_members = {}
    for n in MEMBERS:
        data = subprocess.check_output(['llvm-ar', 'p', old_archive, n], cwd=out, env=env)
        old_member = DISPLAY / n
        raw = old_member.read_bytes()
        # Darwin ar may include trailing newline alignment in the member size.
        assert data in (raw, raw + b'\n' * (-len(raw) % 8)), n
        old_members[n] = data
        if n != late.name:
            (objects / n).write_bytes(raw)
        units[n] = dict(old=artifact(old_member), new=artifact(objects / n))
    assert {n for n, v in units.items() if v['old'] != v['new']} == {old_exec.name, late.name}
    new_archive = objects / ARCHIVE
    call('archive', ['llvm-ar', 'rcs', new_archive, *[objects / n for n in MEMBERS]])
    assert call('archive-members', ['llvm-ar', 't', new_archive]).splitlines() == list(MEMBERS)
    for n in MEMBERS:
        data = subprocess.check_output(['llvm-ar', 'p', new_archive, n], cwd=out, env=env)
        assert (data != old_members[n]) == (n == late.name), n
    (out / 'link.filelist').write_text(''.join(f'{new_exec if p == old_exec else p}\n' for p in paths))
    origin = Path(steps['prelink']['cwd'])
    for tag in ('link', 'prelink'):
        step = steps[tag]
        argv = step['argv']
        for n in ('link.filelist', 'native.macho', 'native-link.map', 'prelink.macho'):
            argv = [arg.replace(str(origin / n), str(out / n)) for arg in argv]
        if tag == 'link':
            assert argv.count(f'-Wl,-force_load,{old_archive}') == 1
            argv = [a.replace(str(old_archive), str(new_archive)) for a in argv]
            argv += [f'-Wl,-force_load,{p}' for p in (watch, hid)]
        call(tag, argv, out if tag == 'prelink' else step['cwd'])
    linked = {n: check_linked(out / n, call) for n in ('native.macho', 'prelink.macho')}
    old_plan, new_plan = (read_json(p / 'prelink.json') for p in (OLD, out))
    for key in ('components', 'codeless_components', 'original_executable_sha256'):
        assert new_plan[key] == old_plan[key]
    result = C['pack'](out, prior, dtb)
    assert r23_files == snapshot(p for p in sorted(OLD.rglob('*')) if p.is_file())
    assert inputs == snapshot(map(Path, inputs))
    C['check_base']()
    outputs = {}
    for n in ('native.macho', 'prelink.macho', 'payload.img', 'boot.img'):
        before, after = artifact(OLD / n), artifact(out / n)
        outputs[n] = dict(old=before, new=after, delta_bytes=after['bytes'] - before['bytes'])
    H['write_json'](out / 'candidate-manifest.json', dict(
        status='self-checked; host only', base=H['BASE_PIN'], units=units, linked=linked, outputs=outputs,
        archive=dict(old=artifact(old_archive), new=artifact(new_archive)),
        unchanged_filelist_entries=len(paths) - 1, reused_link_inputs={
            p: h for p, h in inputs.items() if p not in {str(old_exec), str(old_archive)}},
        r23_files_unchanged={str(Path(p).relative_to(OLD)): h for p, h in r23_files.items()}, **result))
    print(out / 'candidate-manifest.json')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=DEFAULT)
    parser.add_argument('--dtb', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    assert out.parent == OUT and not out.exists()
    build(out, args.dtb.resolve())
