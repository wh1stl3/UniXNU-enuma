#!/usr/bin/env python3
"""Repackage r61 dual-core or build its r62 boot-progress CPU report."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys
import tomllib
from types import SimpleNamespace


def rebuild_r62(device, parent, out, helpers):
    """Replay the pinned r58/r61 link with the original console object."""
    def load(directory, name="candidate-manifest.json"):
        return json.loads((directory / name).read_text())

    base = device.parents[1] / "UniXNU"
    sys.path.insert(0, str(base / "scripts"))
    from unixnu.kernel import linux_env

    r58 = device / "out/ufs-sm8250-rxpid-20261123-r58"
    r57 = device / "out/ufs-sm8250-txpeer-20261123-r57"
    r56 = device / "out/ufs-sm8250-thsnap-20261123-r56"
    r54 = device / "out/ufs-sm8250-fbfill3-20261123-r54"
    digest, snapshot = (helpers["R"][k] for k in ("digest", "snapshot"))
    records = {r: load(r) for r in (r54, r56, r57, r58)}
    recipe = load(r58, "commands.json")
    frozen = (parent / "link.filelist").read_bytes()
    assert frozen == (r58 / "link.filelist").read_bytes()
    prior = load(parent)
    assert all(records[r58]["after"][n] == prior["after"][n]
               for n in ("native.macho", "prelink.macho", "kernel.macho.adt"))
    paths = [Path(x) for x in frozen.decode().splitlines()]
    exe, = (p for p in paths if p.name == "kern_exec.o")
    assert exe == r56 / "objects/kern_exec.o"
    video, = (p for p in paths if p.name == "video_console.o")
    assert video == r54 / "objects/video_console.o"
    link = recipe["link"]
    prelink = recipe["prelink"]
    archives = sorted({Path(a.rsplit(",", 1)[-1]) for a in link["argv"] if a.endswith(".a")})
    armcpu, = (a for a in archives if a.name == "libArmCpu.a")
    donor = Path(prelink["argv"][prelink["argv"].index("--prelinked") + 1])
    inputs = snapshot([*paths, *archives, donor])
    for p in [*paths, *archives, donor]:
        owner = p.parent.parent
        want = (records[owner]["objects"][p.name][1] if owner in records and p.parent.name == "objects"
                else records[r54]["unchanged_inputs"][str(p)])
        assert inputs[str(p)] == want, p

    step = load(r56, "commands.json")["compile-kern_exec.o"]
    src = Path(step["argv"][2]).parent
    assert src == r56 / "source/bsd/kern"
    tree = Path(link["cwd"]).parents[3]
    build_xnu = tree / ".cache/xnu-work"
    build_base = armcpu.parents[9]
    xnu_pin = "d8b80295118ef25ac3a784134bcf95cd8e88109f"
    def check_pins():
        for repo, pin in ((base, helpers["BASE_PIN"]), (build_base, helpers["BASE_PIN"]),
                          (build_xnu, xnu_pin)):
            assert subprocess.check_output(["git", "-C", repo, "rev-parse", "HEAD"],
                                           text=True).strip() == pin, repo
    check_pins()
    commands = {}
    out.mkdir()
    for sub in ("logs", "objects", "tmp"):
        (out / sub).mkdir()
    env = {**os.environ, **linux_env(SimpleNamespace(tree=tree)),
           "PYTHONDONTWRITEBYTECODE": "1", "TMPDIR": str(out / "tmp")}
    env["PATH"] = "/home/wh1stl3/.local/bin:" + env["PATH"]

    def run(tag, argv, cwd=out):
        argv = list(map(str, argv))
        with (out / "logs" / (tag + ".log")).open("w") as log:
            proc = subprocess.run(argv, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT)
        commands[tag] = dict(argv=argv, cwd=str(cwd), exit=proc.returncode)
        (out / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        if proc.returncode:
            raise SystemExit(f'{tag}: exit {proc.returncode}; see {out / "logs" / (tag + ".log")}')
        print(tag, flush=True)
        return (out / "logs" / (tag + ".log")).read_text()

    dest = out / "source/bsd/kern"
    shutil.copytree(src, dest)
    inc = "EnumaBootProgress62Cpu.inc"
    shutil.copyfile(device / "package" / inc, dest / inc)
    bp = dest / "EnumaBootProgress2.inc"
    text = bp.read_text()
    lines = text.splitlines(keepends=True)
    removed_fill = [line for line in lines if "g_enuma_fbfill_" in line]
    assert len(removed_fill) == 4
    text = "".join(line for line in lines if "g_enuma_fbfill_" not in line)
    for anchor, replacement in (
        ('#include "EnumaThreadSnapshot56Bsd.inc"',
         f'#include "EnumaThreadSnapshot56Bsd.inc"\n#include "{inc}"'),
        ("\tenuma_ex_dump();\n}", "\tenuma_ex_dump();\n\tenuma_bp_cpu_report();\n}"),
    ):
        assert text.count(anchor) == 1, anchor
        text = text.replace(anchor, replacement)
    bp.write_text(text)
    old_sources = {p.name: digest(p) for p in src.iterdir()}
    new_sources = {p.name: digest(p) for p in dest.iterdir()}
    assert new_sources.keys() - old_sources.keys() == {inc}
    assert [n for n in old_sources if old_sources[n] != new_sources[n]] == [bp.name]

    obj = out / "objects/kern_exec.o"
    argv = step["argv"].copy()
    assert argv[3:5] == ["-o", str(exe)]
    argv[2], argv[4] = dest / "kern_exec.c", obj
    if "-MF" in argv:
        argv[argv.index("-MF") + 1] = obj.with_suffix(".d")
    run("compile-kern_exec.o", argv, step["cwd"])
    assert inputs[str(exe)] != digest(obj)
    baseline = device / "out/ufs-sm8250-bp2-20261123-r49"
    baseline_paths = [Path(x) for x in (baseline / "link.filelist").read_text().splitlines()]
    video_obj, = (p for p in baseline_paths if p.name == "video_console.o")
    assert inputs[str(video)] != digest(video_obj)
    replacements = {exe: obj, video: video_obj}
    (out / "link.filelist").write_text("".join(f"{replacements.get(p, p)}\n" for p in paths))
    for tag, step in (("link", link), ("prelink", prelink)):
        argv = [a.replace(str(r58), str(out)) for a in step["argv"]]
        run(tag, argv, step["cwd"] if tag == "link" else out)

    formats = (b"enuma-cpu: online=%u seen1=0x%llx step1=%u fail1=%u\n\0",
               b"enuma-cpu: mpidr1=0x%llx\n\0")
    sites = {}
    for name in ("native.macho", "prelink.macho"):
        blob = (out / name).read_bytes()
        assert all(blob.count(fmt) == 1 for fmt in formats), name
        del blob
        calls = {"_enuma_fb_dump": "_enuma_bp_start", "_enuma_bp_start": "_enuma_bp_print",
                 "_enuma_bp_repeat": "_enuma_bp_print", "_enuma_bp_print": "_enuma_bp_cpu_report"}
        sites[name] = {}
        for caller in (*calls, "_enuma_bp_cpu_report"):
            asm = run(f"calls-{name}-{caller}", ["llvm-objdump", "-d",
                      "--disassemble-symbols=" + caller, out / name])
            assert f"<{caller}>:" in asm, (name, caller)
            matches = re.findall(r"^([0-9a-f]+):[^\n]*\bb[l]?\s+[^\n]*<(_\w+)>", asm, re.M)
            target = calls.get(caller, "_printf")
            sites[name][caller] = [addr for addr, callee in matches if callee == target]
            assert len(sites[name][caller]) == (1 if caller in calls else 2), (name, caller, matches)
    assert snapshot([*paths, *archives, donor]) == inputs
    assert (parent / "link.filelist").read_bytes() == frozen
    check_pins()
    changed_sources = {n: [old_sources.get(n), new_sources[n]] for n in (bp.name, inc)}
    return dict(objects={exe.name: [inputs[str(exe)], digest(obj)],
                         video.name: [inputs[str(video)], digest(video_obj)]},
                video_baseline=str(video_obj),
                changed_sources=changed_sources,
                unchanged_filelist_inputs=len(paths) - 2, unchanged_direct_archives=len(archives),
                armcpu_archive_sha256=inputs[str(armcpu)], unique_formats=True, callsites=sites)

parser = argparse.ArgumentParser()
mode = parser.add_mutually_exclusive_group(required=True)
mode.add_argument("--r61", action="store_true")
mode.add_argument("--r62", action="store_true")
parser.add_argument("--out", type=Path)
opts = parser.parse_args()
sys.dont_write_bytecode = True
device = Path(__file__).resolve().parents[1]
base = device.parents[1] / "UniXNU"
r61 = device / "out/ufs-sm8250-smp2-20261124-r61"
parent = r61 if opts.r62 else device / "out/ufs-sm8250-rxpid-20261123-r58"
out = (opts.out or (device / "out/ufs-sm8250-smpobs-20261124-r62" if opts.r62 else r61)).resolve()
assert out.parent == device / "out"
assert not out.exists()
helpers = runpy.run_path(str(device / "scripts/build-enuma-r23-hid-standin.py"))
digest, read_member, fat_tree = (helpers["R"][k] for k in ("digest", "read_member", "fat_tree"))
assert subprocess.check_output(["git", "-C", base, "rev-parse", "HEAD"], text=True).strip() == helpers["BASE_PIN"]
names = ("kernel.macho.adt", "native.macho", "prelink.macho", "payload.img", "boot.img")
prior = json.loads((parent / "candidate-manifest.json").read_text())
before = {n: digest(parent / n) for n in names}
assert before == prior["after"]
assert before["boot.img"] == ("6f13c3b5ca3139309019ff966214a1f13acaa819bb8b928a42998452ffde015b" if opts.r62
                             else "e65ad679a1f13adb22012cb825e85deacb741be7cddd8cdc46737e7d838ea285")
old = read_member(parent / "payload.img", "unixnu.toml")
entry = lambda b: next(e["args"] for e in tomllib.loads(b.decode())["entry"] if e["id"] == "xnu")
old_args = entry(old)
assert old_args == prior["args_after" if opts.r62 else "args"]
disabled = ("enuma-fx-diag", "enuma-fb-fill", "enuma-th", "enuma-txpeer")
removed = ("armcpu-spi-ipi=1", "armcpu-self-ipi=1") if opts.r62 else (
    "enuma-fx-diag=1", "enuma-bp=1", "enuma-fb-fill=1", "enuma-th=1", "enuma-txpeer=1")
added = ("enuma-bp=1",) if opts.r62 else (
    "sheng-smp=1", "armcpu-spi-ipi=1", "armcpu-self-ipi=1", "cpus=2", "armcpu-diagnostics=1")
args = old_args
for token in removed:
    assert args.split().count(token) == 1
    args = args.replace(" " + token, "", 1)
assert all(token.split("=")[0] not in [x.split("=")[0] for x in args.split()] for token in added)
args += " " + " ".join(added)
assert not set(disabled).intersection(t.split("=")[0] for t in args.split())
if opts.r62:
    keys = args.split()
    assert not {"armcpu-spi-ipi", "armcpu-self-ipi"}.intersection(t.split("=")[0] for t in keys)
    assert {"sheng-smp=1", "cpus=2", "armcpu-diagnostics=1"}.issubset(keys)
    parse_adt = runpy.run_path(str(device / "scripts/compare-display-config-20261123.py"))["parse"]
    adt = parse_adt((parent / "kernel.macho.adt").read_bytes())
    irq = sorted(key for key in adt if "interrupt" in key.rsplit(":", 1)[-1])
    assert irq == ["/arm-io/intc:#interrupt-cells", "/arm-io/intc:interrupt-controller"]
    adt_irq = dict(property_records=len(adt), interrupt_properties=irq,
                   cpu1_reg=hex(int.from_bytes(adt["/cpus/cpu1:reg"][0], "little")))
assert old.count(old_args.encode()) == 1
new = old.replace(old_args.encode(), args.encode(), 1)
assert entry(new) == args
if opts.r62:
    mechanical = rebuild_r62(device, parent, out, helpers)
    mechanical["adt_irq_inventory"] = adt_irq
else:
    out.mkdir()
    mechanical = {}
    for n in ("native.macho", "prelink.macho", "native-link.map", "link.filelist"):
        shutil.copyfile(parent / n, out / n)
shutil.copytree(parent / "device", out / "device")
for n in ("kernel.macho.adt", "payload.img"):
    shutil.copyfile(parent / n, out / n)
config = out / "unixnu.toml"
config.write_bytes(new)
replace = [(config, "unixnu.toml")]
if opts.r62:
    replace.insert(0, (out / "prelink.macho", "Payloads/kernel.macho"))
for src, member in replace:
    os.utime(src, (946684800, 946684800))
    subprocess.run(["env", "MTOOLS_SKIP_CHECK=1", "TZ=UTC", "mcopy", "-o", "-m",
                    "-i", str(out / "payload.img"), str(src), "::/EFI/UniXNU/" + member], check=True)
tree = fat_tree(parent / "payload.img")
assert fat_tree(out / "payload.img") == tree
members = [p.removeprefix("::/EFI/UniXNU/") for p in tree if not p.endswith("/")]
old_members = {n: hashlib.sha256(read_member(parent / "payload.img", n)).hexdigest() for n in members}
new_members = {n: hashlib.sha256(read_member(out / "payload.img", n)).hexdigest() for n in members}
assert old_members == prior["payload_members_after"]
changed = sorted(n for n in members if old_members[n] != new_members[n])
assert changed == (["Payloads/kernel.macho", "unixnu.toml"] if opts.r62 else ["unixnu.toml"])
assert new_members["Payloads/kernel.macho"] == digest(out / "prelink.macho")
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
readback = entry(read_member(embedded, "unixnu.toml"))
assert readback == args
if opts.r62:
    assert readback.split() == [t for t in old_args.split() if t not in removed] + list(added)
embedded.unlink()
assert {n: digest(parent / n) for n in names} == before
assert (out / "kernel.macho.adt").read_bytes() == (parent / "kernel.macho.adt").read_bytes()
result = dict(args_before=old_args, args_after=args, removed=removed, added=added, before=before,
              after={n: digest(out / n) for n in names},
              sizes={n: (out / n).stat().st_size for n in names},
              deltas={n: (out / n).stat().st_size - (parent / n).stat().st_size for n in names},
              payload_members_before=old_members, payload_members_after=new_members,
               boot_payload_offset=offset, zero_undefined_including_weak=True,
               changed_payload_members=changed, **mechanical)
(out / "candidate-manifest.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
