#!/usr/bin/env python3
"""Repackage the pinned clean r62, changing only its boot arguments."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tomllib

device = Path(__file__).resolve().parents[1]
base = device.parents[1] / "UniXNU"
parent = device / "out/ufs-sm8250-smpobs-20261124-r62"
out = device / "out/ufs-sm8250-smp3-20261124-r63"
assert not out.exists()
helpers = runpy.run_path(str(device / "scripts/build-enuma-r23-hid-standin.py"))
digest, read_member, fat_tree = (helpers["R"][k] for k in ("digest", "read_member", "fat_tree"))
assert subprocess.check_output(["git", "-C", base, "rev-parse", "HEAD"], text=True).strip() == helpers["BASE_PIN"]
prior = json.loads((parent / "candidate-manifest.json").read_text())
names = ("kernel.macho.adt", "native.macho", "prelink.macho", "payload.img", "boot.img")
before = {n: digest(parent / n) for n in names}
assert before == prior["after"]
assert before["boot.img"] == "e378b1055e26b7d9b743f1ea7f30d8d26bd3a89e48de54ee23428ae0f9c3d894"
video, = (Path(p) for p in (parent / "link.filelist").read_text().splitlines()
          if Path(p).name == "video_console.o")
assert digest(video) == "9394e2950c80eca52f359b41a8b6276e82caf3afbd604aff75e1abd241b6cf02"
old = read_member(parent / "payload.img", "unixnu.toml")
entry = lambda b: next(e["args"] for e in tomllib.loads(b.decode())["entry"] if e["id"] == "xnu")
old_args = entry(old)
assert old_args == prior["args_after"]
assert not any(t.startswith(("armcpu-spi-ipi=", "armcpu-self-ipi=")) for t in old_args.split())
args = old_args + " armcpu-self-ipi=1"
assert old.count(old_args.encode()) == 1
new = old.replace(old_args.encode(), args.encode(), 1)
out.mkdir()
shutil.copytree(parent / "device", out / "device")
for n in (*names[:-1], "native-link.map", "link.filelist"):
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
assert read_member(embedded, "Payloads/kernel.macho.adt") == (parent / "kernel.macho.adt").read_bytes()
embedded.unlink()
assert {n: digest(parent / n) for n in names} == before
assert (out / "kernel.macho.adt").read_bytes() == (parent / "kernel.macho.adt").read_bytes()
assert digest(video) == "9394e2950c80eca52f359b41a8b6276e82caf3afbd604aff75e1abd241b6cf02"
result = dict(args_before=old_args, args_after=args, before=before,
              after={n: digest(out / n) for n in names},
              sizes={n: (out / n).stat().st_size for n in names},
              payload_members_before=old_members, payload_members_after=new_members,
              boot_payload_offset=offset, zero_undefined_including_weak=True,
              changed_payload_members=["unixnu.toml"], video_baseline=str(video),
              video_sha256=digest(video), objects=prior["objects"])
(out / "candidate-manifest.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
