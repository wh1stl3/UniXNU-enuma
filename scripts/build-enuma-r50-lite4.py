#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Derive r50 from the recorded r49 link and payload."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
p = argparse.ArgumentParser()
p.add_argument('--r50', action='store_true', required=True)
p.add_argument('--out', type=Path)
opts = p.parse_args()
device = Path(__file__).resolve().parents[1]
base = device.parents[1] / 'UniXNU'
old = device / 'out/ufs-sm8250-bp2-20261123-r49'
out = (opts.out or device / 'out/ufs-sm8250-lite4-20261123-r50').resolve()
assert out.parent == device / 'out' and not out.exists()
helpers = runpy.run_path(str(device / 'scripts/build-enuma-r23-hid-standin.py'))
digest, snapshot, read_member, fat_tree = (helpers['R'][k] for k in
                                           ('digest', 'snapshot', 'read_member', 'fat_tree'))
assert subprocess.check_output(['git', '-C', base, 'rev-parse', 'HEAD'], text=True).strip() == helpers['BASE_PIN']
names = ('kernel.macho.adt', 'native.macho', 'prelink.macho', 'payload.img', 'boot.img')
before = {n: digest(old / n) for n in names}
prior = json.loads((old / 'candidate-manifest.json').read_text())
assert before == prior['after']
assert before['boot.img'] == '1180a2c7b2c7f903cf412791a704a3051dbf6335f696f0183896a4c3b1f9d3f5'
recipe = json.loads((old / 'commands.json').read_text())
paths = [Path(x) for x in (old / 'link.filelist').read_text().splitlines()]
archives = sorted({Path(a.rsplit(',', 1)[-1]) for a in recipe['link']['argv'] if a.endswith('.a')})
watch, = (x for x in archives if x.name == 'libEnumaBootWatchdogPolicy.a')
donor = Path(recipe['prelink']['argv'][recipe['prelink']['argv'].index('--prelinked') + 1])
inputs = snapshot([*paths, *archives, donor])
frozen = snapshot([old / n for n in names])
tree = Path(recipe['link']['cwd']).parents[3]
sys.path.insert(0, str(base / 'scripts'))
from unixnu import bootimg, payload as payload_step
from unixnu.cli import parser
from unixnu.config import Context
from unixnu.kernel import linux_env

out.mkdir()
for d in ('objects', 'logs', 'tmp'):
    (out / d).mkdir()
env = {**os.environ, **linux_env(SimpleNamespace(tree=tree)), 'PYTHONDONTWRITEBYTECODE': '1',
       'TMPDIR': str(out / 'tmp')}
env['PATH'] = '/home/wh1stl3/.local/bin:' + env['PATH']
commands = {}
def call(tag, argv, cwd=out):
    argv = list(map(str, argv))
    result = subprocess.run(argv, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    commands[tag] = dict(argv=argv, cwd=str(cwd), exit=result.returncode)
    (out / 'logs' / (tag + '.log')).write_text(result.stdout)
    (out / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    if result.returncode:
        print(result.stdout, file=sys.stderr)
        raise SystemExit(f'{tag}: exit {result.returncode}')
    print(tag, flush=True)
    return result.stdout

obj = out / 'objects/BootWatchdogPolicy.o'
archive = out / 'objects/libEnumaBootWatchdogPolicy.a'
argv = recipe['compile-kern_exec.o']['argv'].copy()
argv[2], argv[4] = str(device / 'package/BootWatchdogPolicy.c'), str(obj)
if '-MF' in argv:
    argv[argv.index('-MF') + 1] = str(obj.with_suffix('.d'))
call('compile-policy', argv + ['-mgeneral-regs-only'], recipe['compile-kern_exec.o']['cwd'])
call('archive', ['llvm-ar', 'rcsD', archive, obj])
assert call('archive-members', ['llvm-ar', 't', archive]).splitlines() == [obj.name]
assert digest(watch) != digest(archive)
shutil.copyfile(old / 'link.filelist', out / 'link.filelist')
for tag in ('link', 'prelink'):
    step = recipe[tag]
    args = step['argv'].copy()
    for name in ('link.filelist', 'native.macho', 'native-link.map', 'prelink.macho'):
        args = [a.replace(str(old / name), str(out / name)) for a in args]
    if tag == 'link':
        args = [a.replace(str(watch), str(archive)) for a in args]
    call(tag, args, out if tag == 'prelink' else step['cwd'])

labels = b'com.apple.identityservicesd,com.apple.locationd,com.apple.CommCenter,com.apple.bluetoothd'
for name in ('native.macho', 'prelink.macho'):
    path = out / name
    assert not call('undefined-' + name, ['llvm-nm', '-u', path]).strip()
    blob = path.read_bytes()
    _, syms = helpers['symbols'](blob, helpers['macho'](blob))
    assert not [s for s in syms if not s[1] & 0xe0 and s[1] & 0x0e == 0]
    assert blob.count(labels + b'\0') == 1
    assert blob.count(b'enuma launch policy: watchdogd=%d lite=%d errno=%d\n\0') == 1
    assert blob.count(b'enuma bp r49 i=%u t=%lu\n\0') == 1
    assert b'com.apple.photoanalysisd,com.apple.mediaanalysisd' not in blob
    del blob
    asm = call('calls-' + name, ['llvm-objdump', '-d',
        '--disassemble-symbols=_load_init_program,_sheng_boot_watchdog_policy', path])
    assert '<_sheng_boot_watchdog_policy>' in asm

shutil.copytree(old / 'device', out / 'device')
shutil.copyfile(old / 'kernel.macho.adt', out / 'kernel.macho.adt')
shutil.copyfile(old / 'payload.img', out / 'payload.img')
os.utime(out / 'prelink.macho', (payload_step.EPOCH, payload_step.EPOCH))
call('replace-kernel', ['env', 'MTOOLS_SKIP_CHECK=1', 'TZ=UTC', 'mcopy', '-o', '-m',
     '-i', out / 'payload.img', out / 'prelink.macho', '::/EFI/UniXNU/Payloads/kernel.macho'])
old_tree = fat_tree(old / 'payload.img')
assert fat_tree(out / 'payload.img') == old_tree
members = [x.removeprefix('::/EFI/UniXNU/') for x in old_tree if not x.endswith('/')]
changed = [n for n in members if read_member(old / 'payload.img', n) != read_member(out / 'payload.img', n)]
assert changed == ['Payloads/kernel.macho']
assert read_member(out / 'payload.img', changed[0]) == (out / 'prelink.macho').read_bytes()
assert (out / 'kernel.macho.adt').read_bytes() == (old / 'kernel.macho.adt').read_bytes()
local = device / 'out/ufs-sm8250-launchd-keystore-20261122-r21/self-check-package/packaging/local-build.toml'
ctx = Context(parser().parse_args(['bootimg', '-D', str(out / 'device'), '--out', str(out / 'work'),
    '--config', str(local), '--local-module', 'soc:sm8250=' + str(device.parent / 'UniXNU-sm8250-common')]))
uefi = device.parent / 'uefi-enuma'
fd = uefi / 'Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd'
dtb = Path('/root/enuma-step10/inputs/enuma.dtb')
ref = json.loads((device / 'out/ufs-sm8250-fxdiag-20261123-r47/boot.json').read_text())
assert digest(fd) == ref['fd_sha256'] and digest(dtb) == ref['dtb_sha256']
bootimg.build(ctx, uefi, fd, dtb, out / 'payload.img', out / 'boot.img')
offset = prior['boot_payload_offset']
with (old / 'boot.img').open('rb') as a, (out / 'boot.img').open('rb') as b:
    x, y = a.read(offset), b.read(offset)
    assert x[:576] == y[:576] and x[596:] == y[596:]
    assert hashlib.file_digest(a, 'sha256').hexdigest() == before['payload.img']
    assert hashlib.file_digest(b, 'sha256').hexdigest() == digest(out / 'payload.img')
assert snapshot([old / n for n in names]) == frozen
assert snapshot([*paths, *archives, donor]) == inputs
assert subprocess.check_output(['git', '-C', base, 'rev-parse', 'HEAD'], text=True).strip() == helpers['BASE_PIN']
result = {'baseline': before, 'after': {n: digest(out / n) for n in names},
          'sizes': {n: (out / n).stat().st_size for n in names},
          'deltas': {n: (out / n).stat().st_size - (old / n).stat().st_size for n in names},
          'archive': {'before': digest(watch), 'after': digest(archive)},
          'inputs': inputs, 'r49_frozen': frozen, 'changed_payload_members': changed,
          'args': prior['args'], 'zero_undefined_including_weak': True,
          'boot_payload_offset': offset, 'labels': labels.decode()}
(out / 'candidate-manifest.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
