#!/usr/bin/env python3
"""Build r48 by changing only r47's payload entry arguments."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
device = Path(__file__).resolve().parents[1]
base = device.parents[1] / 'UniXNU'
r47 = device / 'out/ufs-sm8250-fxdiag-20261123-r47'
out = device / 'out/ufs-sm8250-fxdiagbp-20261123-r48'
assert not out.exists()
helpers = runpy.run_path(str(device / 'scripts/build-enuma-r23-hid-standin.py'))
digest, read_member, fat_tree = (helpers['R'][k] for k in ('digest', 'read_member', 'fat_tree'))
assert subprocess.check_output(['git', '-C', base, 'rev-parse', 'HEAD'], text=True).strip() == helpers['BASE_PIN']
names = ('kernel.macho.adt', 'native.macho', 'prelink.macho', 'payload.img', 'boot.img')
before = {n: digest(r47 / n) for n in names}
assert before['boot.img'] == 'e1b6a49959aff7d6aa094d3ce47ce061f9621a9f057551ae185b81c4dbfade83'
prior = json.loads((r47 / 'candidate-manifest.json').read_text())
assert all(before[n] == prior[n]['new'] for n in names)
old = read_member(r47 / 'payload.img', 'unixnu.toml')
needle = b'"\n[[entry]]\nid = "reset"'
assert old.count(needle) == 1
new = old.replace(needle, b' enuma-fx-diag=1 enuma-bp=1' + needle)
out.mkdir()
shutil.copytree(r47 / 'device', out / 'device')
for n in names[:-1]:
    shutil.copyfile(r47 / n, out / n)
tmp = out / 'unixnu.toml'
tmp.write_bytes(new)
os.utime(tmp, (946684800, 946684800))
subprocess.run(['env', 'MTOOLS_SKIP_CHECK=1', 'TZ=UTC', 'mcopy', '-o', '-m',
                '-i', str(out / 'payload.img'), str(tmp), '::/EFI/UniXNU/unixnu.toml'], check=True)
tree = fat_tree(r47 / 'payload.img')
assert fat_tree(out / 'payload.img') == tree
members = [p.removeprefix('::/EFI/UniXNU/') for p in tree if not p.endswith('/')]
old_members = {n: hashlib.sha256(read_member(r47 / 'payload.img', n)).hexdigest() for n in members}
new_members = {n: hashlib.sha256(read_member(out / 'payload.img', n)).hexdigest() for n in members}
assert [n for n in members if old_members[n] != new_members[n]] == ['unixnu.toml']
assert read_member(out / 'payload.img', 'unixnu.toml') == new
assert read_member(out / 'payload.img', 'Payloads/kernel.macho.adt') == (r47 / 'kernel.macho.adt').read_bytes()
import tomllib
entry = lambda b: next(e for e in tomllib.loads(b.decode())['entry'] if e['id'] == 'xnu')['args']
old_args, args = entry(old), entry(new)
assert args == old_args + ' enuma-fx-diag=1 enuma-bp=1'
sys.path.insert(0, str(base / 'scripts'))
from unixnu import bootimg
from unixnu.cli import parser
from unixnu.config import Context
local = device / 'out/ufs-sm8250-launchd-keystore-20261122-r21/self-check-package/packaging/local-build.toml'
ctx = Context(parser().parse_args(['bootimg', '-D', str(out / 'device'), '--out', str(out / 'work'),
    '--config', str(local), '--local-module', 'soc:sm8250=' + str(device.parent / 'UniXNU-sm8250-common')]))
uefi = device.parent / 'uefi-enuma'
fd = uefi / 'Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd'
dtb = Path('/root/enuma-step10/inputs/enuma.dtb')
ref = json.loads((r47 / 'boot.json').read_text())
assert digest(fd) == ref['fd_sha256'] and digest(dtb) == ref['dtb_sha256']
bootimg.build(ctx, uefi, fd, dtb, out / 'payload.img', out / 'boot.img')
offset = json.loads((device / 'out/ufs-sm8250-launchd-ipc-20261123-r34/candidate-manifest.json').read_text())['boot_payload_offset']
with (r47 / 'boot.img').open('rb') as a, (out / 'boot.img').open('rb') as b:
    x, y = a.read(offset), b.read(offset)
    assert x[:576] == y[:576] and x[596:] == y[596:]
    assert hashlib.file_digest(a, 'sha256').hexdigest() == before['payload.img']
    assert hashlib.file_digest(b, 'sha256').hexdigest() == digest(out / 'payload.img')
for n in ('native.macho', 'prelink.macho'):
    undefined = subprocess.check_output(['llvm-nm', '-u', str(out / n)], text=True)
    assert not undefined.strip(), (n, undefined)
assert {n: digest(r47 / n) for n in names} == before
result = {'args_before': old_args, 'args_after': args, 'before': before,
          'after': {n: digest(out / n) for n in names},
          'boot_bytes': (out / 'boot.img').stat().st_size,
          'payload_members_before': old_members, 'payload_members_after': new_members,
          'boot_payload_offset': offset, 'zero_undefined_including_weak': True}
(out / 'candidate-manifest.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
