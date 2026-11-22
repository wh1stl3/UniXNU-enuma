#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Build r49 from r48's payload and r47's recorded native link inputs."""
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
parser_args = argparse.ArgumentParser()
parser_args.add_argument('--r49', action='store_true', required=True)
parser_args.add_argument('--out', type=Path)
opts = parser_args.parse_args()
device = Path(__file__).resolve().parents[1]
base = device.parents[1] / 'UniXNU'
r46 = device / 'out/ufs-sm8250-bp-20261123-r46'
r47 = device / 'out/ufs-sm8250-fxdiag-20261123-r47'
r48 = device / 'out/ufs-sm8250-fxdiagbp-20261123-r48'
out = (opts.out or device / 'out/ufs-sm8250-bp2-20261123-r49').resolve()
assert out.parent == device / 'out' and not out.exists(), out
helpers = runpy.run_path(str(device / 'scripts/build-enuma-r23-hid-standin.py'))
digest, snapshot, read_member, fat_tree = (helpers['R'][k] for k in
                                           ('digest', 'snapshot', 'read_member', 'fat_tree'))
pin = helpers['BASE_PIN']
assert subprocess.check_output(['git', '-C', base, 'rev-parse', 'HEAD'], text=True).strip() == pin
names = ('kernel.macho.adt', 'native.macho', 'prelink.macho', 'payload.img', 'boot.img')
before = {n: digest(r48 / n) for n in names}
prior = json.loads((r48 / 'candidate-manifest.json').read_text())
assert before == prior['after']
assert before['boot.img'] == 'f0fa42d6330625919bb76827b9fcb2df62cefedfe8c3a84c3d5d098cb39adb2b'
frozen_paths = [r48 / n for n in names]
frozen = snapshot(frozen_paths)
recipe = json.loads((r47 / 'commands.json').read_text())
compile_recipe = json.loads((r46 / 'commands.json').read_text())['compile-kern_exec.o']
paths = [Path(x) for x in (r47 / 'link.filelist').read_text().splitlines()]
old_exec, = (p for p in paths if p.name == 'kern_exec.o')
assert old_exec == r46 / 'objects/kern_exec.o'
archives = sorted({Path(a.rsplit(',', 1)[-1]) for a in recipe['link']['argv'] if a.endswith('.a')})
preargs = recipe['prelink']['argv']
donor = Path(preargs[preargs.index('--prelinked') + 1])
inputs = snapshot([*paths, *archives, donor])
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
    p = subprocess.run(argv, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
    commands[tag] = dict(argv=argv, cwd=str(cwd), exit=p.returncode)
    (out / 'logs' / (tag + '.log')).write_text(p.stdout)
    (out / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    if p.returncode:
        print(p.stdout, file=sys.stderr)
        raise SystemExit(f'{tag}: exit {p.returncode}')
    print(tag, flush=True)
    return p.stdout


source = out / 'source/bsd/kern'
shutil.copytree(r47 / 'source/bsd/kern', source)
fb = source / 'EnumaBbScan.inc'
text = fb.read_text()
assert text.count('#include "EnumaBootProgress.inc"') == 1
assert text.count('enuma_bp_print();') == 1
text = text.replace('#include "EnumaBootProgress.inc"', '#include "EnumaBootProgress2.inc"')
text = text.replace('enuma_bp_print();', 'enuma_bp_start();')
fb.write_text(text)
shutil.copyfile(device / 'package/EnumaBootProgress2.inc', source / 'EnumaBootProgress2.inc')
obj = out / 'objects/kern_exec.o'
argv = compile_recipe['argv'].copy()
assert Path(argv[2]).name == 'kern_exec.c' and argv[3] == '-o'
argv[2], argv[4] = source / 'kern_exec.c', obj
if '-MF' in argv:
    argv[argv.index('-MF') + 1] = obj.with_suffix('.d')
call('compile-kern_exec.o', argv, compile_recipe['cwd'])
assert digest(old_exec) != digest(obj)
(out / 'link.filelist').write_text(''.join(f'{obj if p == old_exec else p}\n' for p in paths))
for tag in ('link', 'prelink'):
    step = recipe[tag]
    argv = step['argv'].copy()
    for name in ('link.filelist', 'native.macho', 'native-link.map', 'prelink.macho'):
        argv = [a.replace(str(r47 / name), str(out / name)) for a in argv]
    call(tag, argv, out if tag == 'prelink' else step['cwd'])

for name in ('native.macho', 'prelink.macho'):
    p = out / name
    assert not call('undefined-' + name, ['llvm-nm', '-u', p]).strip()
    blob = p.read_bytes()
    _, syms = helpers['symbols'](blob, helpers['macho'](blob))
    assert not [s for s in syms if not s[1] & 0xe0 and s[1] & 0x0e == 0]
    for s in (b'enuma bp r49 i=%u t=%lu\n\0', b'enuma-bp\0'):
        assert blob.count(s) == 1, (name, s, blob.count(s))
    del blob
    report = call('calls-' + name, ['llvm-objdump', '-d',
        '--disassemble-symbols=_enuma_fb_dump,_enuma_bp_start,_enuma_bp_print,_enuma_bp_repeat', p])
    for symbol in ('_enuma_fb_dump', '_enuma_bp_start', '_enuma_bp_print', '_enuma_bp_repeat',
                   '_PE_parse_boot_argn', '_thread_call_enter1_delayed'):
        assert '<' + symbol + '>' in report, (name, symbol)

shutil.copytree(r48 / 'device', out / 'device')
shutil.copyfile(r48 / 'kernel.macho.adt', out / 'kernel.macho.adt')
shutil.copyfile(r48 / 'payload.img', out / 'payload.img')
os.utime(out / 'prelink.macho', (payload_step.EPOCH, payload_step.EPOCH))
call('replace-kernel', ['env', 'MTOOLS_SKIP_CHECK=1', 'TZ=UTC', 'mcopy', '-o', '-m',
    '-i', out / 'payload.img', out / 'prelink.macho', '::/EFI/UniXNU/Payloads/kernel.macho'])
old_tree = fat_tree(r48 / 'payload.img')
assert fat_tree(out / 'payload.img') == old_tree
members = [x.removeprefix('::/EFI/UniXNU/') for x in old_tree if not x.endswith('/')]
changed = [n for n in members if read_member(r48 / 'payload.img', n) !=
           read_member(out / 'payload.img', n)]
assert changed == ['Payloads/kernel.macho'], changed
assert read_member(out / 'payload.img', changed[0]) == (out / 'prelink.macho').read_bytes()
assert read_member(out / 'payload.img', 'unixnu.toml') == read_member(r48 / 'payload.img', 'unixnu.toml')
assert (out / 'kernel.macho.adt').read_bytes() == (r48 / 'kernel.macho.adt').read_bytes()
local = device / 'out/ufs-sm8250-launchd-keystore-20261122-r21/self-check-package/packaging/local-build.toml'
ctx = Context(parser().parse_args(['bootimg', '-D', str(out / 'device'), '--out', str(out / 'work'),
    '--config', str(local), '--local-module', 'soc:sm8250=' + str(device.parent / 'UniXNU-sm8250-common')]))
uefi = device.parent / 'uefi-enuma'
fd = uefi / 'Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd'
dtb = Path('/root/enuma-step10/inputs/enuma.dtb')
ref = json.loads((r47 / 'boot.json').read_text())
assert digest(fd) == ref['fd_sha256'] and digest(dtb) == ref['dtb_sha256']
bootimg.build(ctx, uefi, fd, dtb, out / 'payload.img', out / 'boot.img')
offset = prior['boot_payload_offset']
with (r48 / 'boot.img').open('rb') as a, (out / 'boot.img').open('rb') as b:
    x, y = a.read(offset), b.read(offset)
    assert x[:576] == y[:576] and x[596:] == y[596:]
    assert hashlib.file_digest(a, 'sha256').hexdigest() == before['payload.img']
    assert hashlib.file_digest(b, 'sha256').hexdigest() == digest(out / 'payload.img')
assert snapshot(frozen_paths) == frozen and snapshot([*paths, *archives, donor]) == inputs
assert subprocess.check_output(['git', '-C', base, 'rev-parse', 'HEAD'], text=True).strip() == pin
result = {'baseline': before, 'after': {n: digest(out / n) for n in names},
          'sizes': {n: (out / n).stat().st_size for n in names},
          'deltas': {n: (out / n).stat().st_size - (r48 / n).stat().st_size for n in names},
          'object': {'name': 'kern_exec.o', 'before': digest(old_exec), 'after': digest(obj)},
          'unchanged_filelist_inputs': len(paths) - 1, 'unchanged_direct_archives': len(archives),
          'unchanged_inputs': inputs, 'changed_payload_members': changed,
          'args': prior['args_after'], 'zero_undefined_including_weak': True,
          'r48_frozen': frozen, 'boot_payload_offset': offset,
          'report_site_line': text[:text.index('enuma_bp_start();')].count('\n') + 1}
(out / 'candidate-manifest.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
