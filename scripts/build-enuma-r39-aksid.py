#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Rebuild the r35 keystore callback and repack its unchanged ADT."""
import argparse
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
device = Path(__file__).resolve().parents[1]
base = device.parents[1] / 'UniXNU'
parser_args = argparse.ArgumentParser()
parser_args.add_argument('--out', type=Path, default=device / 'out/ufs-sm8250-launchd-aksid-20261123-r39')
out = parser_args.parse_args().out.resolve()
assert out.parent == (device / 'out').resolve()
r35 = device / 'out/ufs-sm8250-launchd-scale-20261123-r35'
r34 = device / 'out/ufs-sm8250-launchd-ipc-20261123-r34'
r11 = device / 'out/ufs-sm8250-launchd-keystore-20261121-r11/self-check/build-final'
r21 = device / 'out/ufs-sm8250-launchd-keystore-20261122-r21/self-check/build-final'
helpers = runpy.run_path(str(device / 'scripts/build-enuma-r23-hid-standin.py'))
h = helpers['R']
digest, snapshot, read_member, fat_tree = (h[k] for k in ('digest', 'snapshot', 'read_member', 'fat_tree'))
assert not out.exists()
assert subprocess.check_output(['git', '-C', base, 'rev-parse', 'HEAD'], text=True).strip() == helpers['BASE_PIN']
assert digest(r35 / 'kernel.macho.adt') == '1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457'
frozen_files = [r35 / n for n in ('kernel.macho.adt', 'payload.img', 'boot.img')]
frozen_files += [r34 / n for n in ('native.macho', 'prelink.macho', 'link.filelist')]
frozen = snapshot(frozen_files)
paths = [Path(x) for x in (r34 / 'link.filelist').read_text().splitlines()]
inputs = snapshot(paths)
steps = {s['tag']: s for s in json.loads((r21 / 'kernel-build-result.json').read_text())['r13_delta']['steps']}
probe = {s['tag']: s for s in json.loads((r11 / 'kernel-build-result.json').read_text())['r11_delta']['steps']}['compile-probe']
tree = Path(steps['link']['cwd']).parents[3]
sys.path.insert(0, str(base / 'scripts'))
from unixnu.kernel import linux_env
from unixnu import bootimg, payload as payload_step
from unixnu.cli import parser
from unixnu.config import Context

for name in ('objects', 'logs', 'tmp'):
    (out / name).mkdir(parents=True)
env = {**os.environ, **linux_env(SimpleNamespace(tree=tree)), 'PYTHONDONTWRITEBYTECODE': '1',
       'TMPDIR': str(out / 'tmp')}
env['PATH'] = '/home/wh1stl3/.local/bin:' + env['PATH']
def call(tag, argv, cwd=out):
    argv = list(map(str, argv))
    p = subprocess.run(argv, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (out / 'logs' / (tag + '.log')).write_text(p.stdout)
    if p.returncode:
        print(p.stdout, file=sys.stderr)
        raise SystemExit(f'{tag}: exit {p.returncode}')
    print(tag, flush=True)
    return p.stdout

obj = out / 'objects/EnumaKeyStoreProbe.o'
argv = probe['argv'].copy()
argv[2], argv[4] = str(device / 'package/EnumaKeyStoreProbe.cpp'), str(obj)
call('compile-probe', argv, probe['cwd'])
old_obj = r11 / 'objects/EnumaKeyStoreProbe.o'
assert digest(obj) != digest(old_obj)
old_archive = r11 / 'libAppleKeyStoreState.a'
state = r11 / 'objects/NativeKeyStoreEvents.late.o'
archive = out / 'objects/libAppleKeyStoreState.a'
assert call('old-members', ['llvm-ar', 't', old_archive]).splitlines() == [state.name, old_obj.name]
assert subprocess.check_output(['llvm-ar', 'p', old_archive, state.name], env=env).rstrip(b'\n') == state.read_bytes().rstrip(b'\n')
call('archive', ['llvm-ar', 'rcs', archive, state, obj])
(out / 'link.filelist').write_text((r34 / 'link.filelist').read_text())
origin = Path(steps['prelink']['cwd'])
old_display = device / 'out/ufs-sm8250-launchd-display-20261121-r10/self-check/build-final/display/libEnumaGopLegacy.a'
new_display = r34 / 'objects/libEnumaGopLegacy.a'
hid = device / 'out/ufs-sm8250-launchd-hid-20261122-r23/objects/libShengHidInputStandin.a'
watch = helpers['R19'] / 'objects/libEnumaBootWatchdogPolicy.a'
for tag in ('link', 'prelink'):
    step = steps[tag]
    argv = step['argv'].copy()
    for name in ('link.filelist', 'native.macho', 'native-link.map', 'prelink.macho'):
        argv = [a.replace(str(origin / name), str(out / name)) for a in argv]
    if tag == 'link':
        assert sum(str(old_archive) in a for a in argv) == 1
        assert sum(str(old_display) in a for a in argv) == 1
        argv = [a.replace(str(old_archive), str(archive)).replace(str(old_display), str(new_display)) for a in argv]
        argv += [f'-Wl,-force_load,{p}' for p in (watch, hid)]
    call(tag, argv, out if tag == 'prelink' else step['cwd'])
for name in ('native.macho', 'prelink.macho'):
    path = out / name
    assert not call('undefined-' + name, ['llvm-nm', '-u', path]).strip()
    blob = path.read_bytes()
    assert blob.count(b'enuma-aks: aksid %zu %s\n\0') == 1
    dis = call('probe-call-' + name, ['llvm-objdump', '-d', '--disassemble-symbols=_enuma_keystore_probe', path])
    assert '<_native_aks_device_id>' in dis
    _, syms = helpers['symbols'](blob, helpers['macho'](blob))
    assert not [s for s in syms if not s[1] & 0xe0 and s[1] & 0x0e == 0]
shutil.copytree(r35 / 'device', out / 'device')
shutil.copyfile(r35 / 'kernel.macho.adt', out / 'kernel.macho.adt')
shutil.copyfile(r35 / 'payload.img', out / 'payload.img')
os.utime(out / 'prelink.macho', (payload_step.EPOCH, payload_step.EPOCH))
subprocess.run(['mcopy', '-o', '-m', '-i', str(out / 'payload.img'), str(out / 'prelink.macho'),
                '::/EFI/UniXNU/Payloads/kernel.macho'], check=True,
               env={**env, 'MTOOLS_SKIP_CHECK': '1', 'TZ': 'UTC'})
old_tree = fat_tree(r35 / 'payload.img')
assert fat_tree(out / 'payload.img') == old_tree
members = [x.removeprefix('::/EFI/UniXNU/') for x in old_tree if not x.endswith('/')]
changed = [n for n in members if read_member(r35 / 'payload.img', n) != read_member(out / 'payload.img', n)]
assert changed == ['Payloads/kernel.macho'], changed
assert read_member(out / 'payload.img', 'Payloads/kernel.macho.adt') == (r35 / 'kernel.macho.adt').read_bytes()
local = device / 'out/ufs-sm8250-launchd-keystore-20261122-r21/self-check-package/packaging/local-build.toml'
ctx = Context(parser().parse_args(['bootimg', '-D', str(out / 'device'), '--out', str(out / 'work'),
    '--config', str(local), '--local-module', 'soc:sm8250=' + str(device.parent / 'UniXNU-sm8250-common')]))
uefi = device.parent / 'uefi-enuma'
fd = uefi / 'Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd'
dtb = Path('/root/enuma-step10/inputs/enuma.dtb')
reference = json.loads((r35 / 'boot.json').read_text())
assert digest(fd) == reference['fd_sha256'] and digest(dtb) == reference['dtb_sha256']
bootimg.build(ctx, uefi, fd, dtb, out / 'payload.img', out / 'boot.img')
assert snapshot(frozen_files) == frozen and snapshot(paths) == inputs
results = {n: {'old': digest((r35 if (r35 / n).exists() else r34) / n),
               'new': digest(out / n), 'bytes': (out / n).stat().st_size}
           for n in ('kernel.macho.adt', 'native.macho', 'prelink.macho', 'payload.img', 'boot.img')}
results.update(old_object=digest(old_obj), new_object=digest(obj), old_archive=digest(old_archive),
               new_archive=digest(archive), unchanged_link_inputs=len(inputs), changed_payload_members=changed,
               frozen=frozen)
(out / 'candidate-manifest.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results, indent=2))
