#!/usr/bin/env python3
"""Repackage r58 with only the r61 dual-core boot argument changes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tomllib

parser = argparse.ArgumentParser()
parser.add_argument("--r61", action="store_true", required=True)
parser.add_argument("--out", type=Path)
opts = parser.parse_args()
sys.dont_write_bytecode = True
device = Path(__file__).resolve().parents[1]
base = device.parents[1] / "UniXNU"
parent = device / "out/ufs-sm8250-rxpid-20261123-r58"
out = (opts.out or device / "out/ufs-sm8250-smp2-20261124-r61").resolve()
assert out.parent == device / "out"
assert not out.exists()
helpers = runpy.run_path(str(device / "scripts/build-enuma-r23-hid-standin.py"))
digest, read_member, fat_tree = (helpers["R"][k] for k in ("digest", "read_member", "fat_tree"))
assert subprocess.check_output(["git", "-C", base, "rev-parse", "HEAD"], text=True).strip() == helpers["BASE_PIN"]
names = ("kernel.macho.adt", "native.macho", "prelink.macho", "payload.img", "boot.img")
prior = json.loads((parent / "candidate-manifest.json").read_text())
before = {n: digest(parent / n) for n in names}
assert before == prior["after"]
assert before["boot.img"] == "e65ad679a1f13adb22012cb825e85deacb741be7cddd8cdc46737e7d838ea285"
old = read_member(parent / "payload.img", "unixnu.toml")
entry = lambda b: next(e["args"] for e in tomllib.loads(b.decode())["entry"] if e["id"] == "xnu")
old_args = entry(old)
assert old_args == prior["args"]
removed = ("enuma-fx-diag=1", "enuma-bp=1", "enuma-fb-fill=1", "enuma-th=1", "enuma-txpeer=1")
added = ("sheng-smp=1", "armcpu-spi-ipi=1", "armcpu-self-ipi=1", "cpus=2", "armcpu-diagnostics=1")
args = old_args
for token in removed:
    assert args.split().count(token) == 1
    args = args.replace(" " + token, "", 1)
assert all(token.split("=")[0] not in [x.split("=")[0] for x in args.split()] for token in added)
args += " " + " ".join(added)
assert old.count(old_args.encode()) == 1
new = old.replace(old_args.encode(), args.encode(), 1)
assert entry(new) == args
out.mkdir()
shutil.copytree(parent / "device", out / "device")
for n in names[:-1]:
    shutil.copyfile(parent / n, out / n)
for n in ("native-link.map", "link.filelist"):
    shutil.copyfile(parent / n, out / n)
config = out / "unixnu.toml"
config.write_bytes(new)
os.utime(config, (946684800, 946684800))
subprocess.run(["env", "MTOOLS_SKIP_CHECK=1", "TZ=UTC", "mcopy", "-o", "-m",
                "-i", str(out / "payload.img"), str(config), "::/EFI/UniXNU/unixnu.toml"], check=True)
tree = fat_tree(parent / "payload.img")
assert fat_tree(out / "payload.img") == tree
members = [p.removeprefix("::/EFI/UniXNU/") for p in tree if not p.endswith("/")]
old_members = {n: hashlib.sha256(read_member(parent / "payload.img", n)).hexdigest() for n in members}
new_members = {n: hashlib.sha256(read_member(out / "payload.img", n)).hexdigest() for n in members}
assert old_members == prior["payload_members_after"]
assert [n for n in members if old_members[n] != new_members[n]] == ["unixnu.toml"]
assert read_member(out / "payload.img", "unixnu.toml") == new
assert read_member(out / "payload.img", "Payloads/kernel.macho.adt") == (parent / "kernel.macho.adt").read_bytes()
for n in ("native.macho", "prelink.macho"):
    p = out / n
    assert not subprocess.check_output(["llvm-nm", "-u", str(p)], text=True).strip()
    blob = p.read_bytes()
    _, syms = helpers["symbols"](blob, helpers["macho"](blob))
    assert not [s for s in syms if not s[1] & 0xe0 and s[1] & 0x0e == 0]
    del blob
sys.path.insert(0, str(base / "scripts"))
from unixnu import bootimg
from unixnu.cli import parser as cli_parser
from unixnu.config import Context
local = device / "out/ufs-sm8250-launchd-keystore-20261122-r21/self-check-package/packaging/local-build.toml"
ctx = Context(cli_parser().parse_args(["bootimg", "-D", str(out / "device"), "--out", str(out / "work"),
    "--config", str(local), "--local-module", "soc:sm8250=" + str(device.parent / "UniXNU-sm8250-common")]))
uefi = device.parent / "uefi-enuma"
fd = uefi / "Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd"
dtb = Path("/root/enuma-step10/inputs/enuma.dtb")
ref = json.loads((parent / "boot.json").read_text())
assert digest(fd) == ref["fd_sha256"] and digest(dtb) == ref["dtb_sha256"]
bootimg.build(ctx, uefi, fd, dtb, out / "payload.img", out / "boot.img")
offset = prior["boot_payload_offset"]
embedded = out / "embedded-payload.img"
with (parent / "boot.img").open("rb") as a, (out / "boot.img").open("rb") as b:
    x, y = a.read(offset), b.read(offset)
    assert x[:576] == y[:576] and x[596:] == y[596:]
    assert hashlib.file_digest(a, "sha256").hexdigest() == before["payload.img"]
    with embedded.open("wb") as target:
        shutil.copyfileobj(b, target)
assert digest(embedded) == digest(out / "payload.img")
assert entry(read_member(embedded, "unixnu.toml")) == args
embedded.unlink()
assert {n: digest(parent / n) for n in names} == before
assert (out / "kernel.macho.adt").read_bytes() == (parent / "kernel.macho.adt").read_bytes()
result = dict(args_before=old_args, args_after=args, removed=removed, added=added, before=before,
              after={n: digest(out / n) for n in names},
              sizes={n: (out / n).stat().st_size for n in names},
              deltas={n: (out / n).stat().st_size - (parent / n).stat().st_size for n in names},
              payload_members_before=old_members, payload_members_after=new_members,
              boot_payload_offset=offset, zero_undefined_including_weak=True)
(out / "candidate-manifest.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
