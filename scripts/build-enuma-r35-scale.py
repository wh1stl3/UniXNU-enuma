#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Repackage r34 with one experimental chosen property; do not compile XNU."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tomllib
from unittest.mock import patch

DEVICE = Path(__file__).resolve().parents[1]
BASE = DEVICE.parents[1] / 'UniXNU'
R34 = DEVICE / 'out/ufs-sm8250-launchd-ipc-20261123-r34'
OUT = DEVICE / 'out/ufs-sm8250-launchd-scale-20261123-r35'
PKG = DEVICE / 'out/ufs-sm8250-launchd-keystore-20261122-r21/self-check-package/packaging'
ADT = 'Payloads/kernel.macho.adt'
KEY = ('device-tree', 'chosen', 'display-scale')
SEED = ('device-tree', 'chosen', 'random-seed')

spec = importlib.util.spec_from_file_location('r22', DEVICE / 'scripts/build-enuma-r22-memory-window.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
digest, read_member, read_properties, fat_tree, snapshot = (helper.digest, helper.read_member,
    helper.read_properties, helper.fat_tree, helper.snapshot)
sys.path.insert(0, str(BASE / 'scripts'))
from unixnu import bootimg, devicetree, payload as payload_step
from unixnu.cli import parser
from unixnu.config import Context

assert not OUT.exists()
assert subprocess.check_output(['git', '-C', BASE, 'rev-parse', 'HEAD'], text=True).strip() == helper.BASE_PIN
assert digest(R34 / 'kernel.macho.adt') == '5f3ebeb6b29a9e47c7c314443dc3564db07caf830de5054e9bec0e5773f521d5'
assert digest(R34 / 'payload.img') == '69feca6c43aea783a0adb4b0959c23168fbb78fbfaba1f01389e1df8889b0343'
assert digest(R34 / 'boot.img') == '345741e4b48153ca2635905c7b9da47d376b62fd3b23784ac7fd0bac5e9a0e80'
filelist = R34 / 'link.filelist'
objects = snapshot([Path(line) for line in filelist.read_text().splitlines()] +
                   [p for p in (R34 / 'objects').iterdir() if p.is_file()])
frozen = snapshot([R34 / name for name in ('kernel.macho.adt', 'payload.img', 'boot.img',
                   'native.macho', 'prelink.macho', 'candidate-manifest.json', 'link.filelist')])
old_tree = fat_tree(R34 / 'payload.img')
members = sorted(x.removeprefix('::/EFI/UniXNU/') for x in old_tree if not x.endswith('/'))
assert all('::/EFI/UniXNU/' + x in old_tree for x in members)
old = {n: read_member(R34 / 'payload.img', n) for n in members}
assert old[ADT] == (R34 / 'kernel.macho.adt').read_bytes()
before = read_properties(old[ADT])
assert KEY not in before
OUT.mkdir()
(OUT / 'device').mkdir()
board = (R34 / 'device/board.toml').read_text(encoding='utf-8')
assert '[adt.chosen.u32]' not in board
(OUT / 'device/board.toml').write_text(board + '\n[adt.chosen.u32]\ndisplay-scale = 2\n', encoding='utf-8')
local = PKG / 'local-build.toml'
ctx = Context(parser().parse_args(['bootimg', '-D', str(OUT / 'device'), '--out', str(OUT / 'work'),
    '--config', str(local), '--local-module', 'soc:sm8250=' + str(DEVICE.parent / 'UniXNU-sm8250-common')]))
hardware = PKG / 'out/enuma/ipados-17.7.11-21H461/enuma/device-tree/hardware.dtb'
chip = tomllib.loads(local.read_text())['build']['unique_chip_id']
with patch.object(devicetree.os, 'urandom', side_effect=lambda n: before[SEED] if n == 256 else (_ for _ in ()).throw(ValueError(n))):
    adt = devicetree.generate(hardware, ctx.board, unique_chip_id=chip, data=True, trust=True)
after = read_properties(adt)
assert after == (before | {KEY: struct.pack('<I', 2)}), 'unexpected ADT delta'
(OUT / 'kernel.macho.adt').write_bytes(adt)
os.utime(OUT / 'kernel.macho.adt', (payload_step.EPOCH, payload_step.EPOCH))
shutil.copyfile(R34 / 'payload.img', OUT / 'payload.img')
subprocess.run(['mcopy', '-o', '-m', '-i', OUT / 'payload.img', OUT / 'kernel.macho.adt',
                '::/EFI/UniXNU/' + ADT], check=True, env=dict(os.environ, MTOOLS_SKIP_CHECK='1', TZ='UTC'))
assert fat_tree(OUT / 'payload.img') == old_tree
final = {n: read_member(OUT / 'payload.img', n) for n in members}
assert final == (old | {ADT: adt})
assert read_properties(final[ADT])[KEY] == struct.pack('<I', 2)
print('/chosen/display-scale =', struct.unpack('<I', read_properties(final[ADT])[KEY])[0], flush=True)
uefi = DEVICE.parent / 'uefi-enuma'
fd = uefi / 'Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd'
dtb = Path('/root/enuma-step10/inputs/enuma.dtb')
reference = json.loads((R34 / 'boot.json').read_text())
assert digest(fd) == reference['fd_sha256'] and digest(dtb) == reference['dtb_sha256']
bootimg.build(ctx, uefi, fd, dtb, OUT / 'payload.img', OUT / 'boot.img')
a, b = (R34 / 'boot.img').read_bytes(), (OUT / 'boot.img').read_bytes()
kernel_size = struct.unpack_from('<I', a, 8)[0]
page, version = struct.unpack_from('<II', a, 36)
assert (page, version) == (4096, 1)
offset = page * (1 + (kernel_size + page - 1) // page)
assert a[offset:] == (R34 / 'payload.img').read_bytes() and b[offset:] == (OUT / 'payload.img').read_bytes()
assert a[:576] == b[:576] and a[596:offset] == b[596:offset]
limit = tomllib.loads((DEVICE / 'board.toml').read_text(encoding='utf-8'))['package']['boot_partition_bytes']
assert len(a) == len(b) and len(b) <= int(limit)
assert frozen == snapshot(map(Path, frozen))
assert objects == snapshot(map(Path, objects))
(OUT / 'r34-link-inputs.sha256').write_text(''.join(f'{sha}  {path}\n' for path, sha in objects.items()))
for name in ('kernel.macho.adt', 'native.macho', 'prelink.macho', 'payload.img', 'boot.img'):
    p = OUT / name if (OUT / name).exists() else R34 / name
    print(name, p.stat().st_size, digest(p))
print('r34 frozen artifacts unchanged; link inputs unchanged:', len(objects))
