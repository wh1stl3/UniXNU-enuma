# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Incremental r65 implementation for build-enuma-r64-ustack.py --r65."""
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


def build(device, output):
    base = device.parents[1] / "UniXNU"
    r64 = device / "out/ufs-sm8250-ustack-20261124-r64"
    out = (output or device / "out/ufs-sm8250-fp-20261124-r65").resolve()
    assert out.parent == device / "out" and not out.exists(), out
    helpers = runpy.run_path(str(device / "scripts/build-enuma-r23-hid-standin.py"))
    digest, snapshot, read_member, fat_tree = (
        helpers["R"][k] for k in ("digest", "snapshot", "read_member", "fat_tree")
    )
    prior = json.loads((r64 / "candidate-manifest.json").read_text())
    recipe = json.loads((r64 / "commands.json").read_text())
    names = ("kernel.macho.adt", "native.macho", "prelink.macho", "payload.img", "boot.img")
    before = {n: digest(r64 / n) for n in names}
    assert before == prior["after"]
    assert before["boot.img"] == "8a80bfde1891495102bee30326de230735ad1499c6cd1130dd641031ec29b446"

    def head(repo):
        return subprocess.check_output(["git", "-C", repo, "rev-parse", "HEAD"], text=True).strip()

    link = recipe["link"]
    tree = Path(link["cwd"]).parents[3]
    xnu = tree / ".cache/xnu-work"
    assert head(base) == helpers["BASE_PIN"]
    assert head(xnu) == prior["source_pin"] == "d8b80295118ef25ac3a784134bcf95cd8e88109f"
    filelist = r64 / "link.filelist"
    paths = [Path(p) for p in filelist.read_text().splitlines()]
    assert len(paths) == len(set(paths))
    src = device / "package/EnumaUserStack64.c"
    old_obj, = (p for p in paths if p.name == "EnumaUserStack64.o")
    assert old_obj.parent == r64 / "objects"
    direct = {Path(a.rsplit(",", 1)[-1]) for a in link["argv"]
              if a.endswith((".a", ".o", ".exp", ".plist"))}
    assert old_obj not in direct
    firehose = {Path(a[2:]) / "libfirehose_kernel.a" for a in link["argv"]
                if a.startswith("-L") and (Path(a[2:]) / "libfirehose_kernel.a").is_file()}
    assert "-lfirehose_kernel" in link["argv"] and len(firehose) == 1
    pre = recipe["prelink"]["argv"]
    donor = Path(pre[pre.index("--prelinked") + 1])
    inputs = snapshot(set(paths) | direct | firehose | {filelist, donor})
    assert inputs[str(old_obj)] == prior["objects"][old_obj.name][1]
    checked = {p.name for p in {*paths, *direct} if p.name in prior["rebuilt"]}
    for p in {*paths, *direct}:
        if p.name in checked:
            assert inputs[str(p)] == prior["rebuilt"][p.name], p
    source_hash = digest(src)

    sys.path.insert(0, str(base / "scripts"))
    from unixnu import bootimg, payload as payload_step
    from unixnu.cli import parser as cli_parser
    from unixnu.config import Context
    from unixnu.kernel import linux_env

    out.mkdir()
    for subdir in ("objects", "logs", "tmp"):
        (out / subdir).mkdir()
    env = {**os.environ, **linux_env(SimpleNamespace(tree=tree)), "TMPDIR": str(out / "tmp")}
    env["PATH"] = "/home/wh1stl3/.local/bin:" + env["PATH"]
    commands = {}

    def call(tag, argv, cwd=out):
        argv = list(map(str, argv))
        proc = subprocess.run(argv, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
        commands[tag] = dict(argv=argv, cwd=str(cwd), exit=proc.returncode)
        (out / "logs" / (tag + ".log")).write_text(proc.stdout)
        (out / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        if proc.returncode:
            print(proc.stdout, file=sys.stderr)
            raise SystemExit(f"{tag}: exit {proc.returncode}")
        print(tag, flush=True)
        return proc.stdout

    new_obj = out / "objects" / old_obj.name
    compile_step = recipe["compile-" + old_obj.name]
    cc = compile_step["argv"].copy()
    assert cc[2] == str(src) and cc[3:5] == ["-o", str(old_obj)]
    cc[4] = new_obj
    call("compile-" + old_obj.name, cc, compile_step["cwd"])
    assert digest(new_obj) != inputs[str(old_obj)]
    new_list = out / filelist.name
    new_list.write_text("".join(f"{new_obj if p == old_obj else p}\n" for p in paths))

    def replay(tag, replacements, cwd):
        step = recipe[tag]
        argv = step["argv"].copy()
        for old, new in replacements.items():
            assert argv.count(old) == 1, (tag, old)
            argv[argv.index(old)] = new
        call(tag, argv, cwd)

    replay("link", {str(filelist): new_list, str(r64 / "native.macho"): out / "native.macho",
                    f"-Wl,-map,{r64 / 'native-link.map'}": f"-Wl,-map,{out / 'native-link.map'}"},
           link["cwd"])
    replay("prelink", {str(r64 / n): out / n for n in ("native.macho", "prelink.macho")}, out)

    formats = (
        b"enuma-fp: p=%d n=%u\n", b"enuma-fp: p=%d why=%s\n",
        *(b"enuma-fp: %d" + k * b" 0x%llx" + b"\n" for k in range(1, 5)),
    )
    edges = {"_enuma_bp_repeat": "_enuma_stk_submit", "_enuma_stk_capture": "_enuma_fp_walk",
             "_enuma_fp_walk": "_vm_map_read_user"}
    callsites = {}
    for n in ("native.macho", "prelink.macho"):
        p = out / n
        assert not call("undefined-" + n, ["llvm-nm", "-u", p]).strip()
        blob = p.read_bytes()
        _, syms = helpers["symbols"](blob, helpers["macho"](blob))
        assert not [s for s in syms if not s[1] & 0xe0 and s[1] & 0x0e == 0], n
        assert all(blob.count(s + b"\0") == 1 for s in formats), n
        del blob
        report = call("calls-" + n, ["llvm-objdump", "-d", "--disassemble-symbols=" +
                                     ",".join(edges), p])
        labeled = re.split(r"(?m)^[0-9a-f]+ <([^>]+)>:\n", report)
        bodies = dict(zip(labeled[1::2], labeled[2::2], strict=True))
        callsites[n] = {}
        for caller, callee in edges.items():
            site, = re.findall(r"(?m)^\s*([0-9a-f]+):.*\b(?:b|bl)\b.*<" + callee + ">",
                               bodies[caller])
            callsites[n][f"{caller}->{callee}"] = site

    shutil.copytree(r64 / "device", out / "device")
    for n in ("kernel.macho.adt", "payload.img"):
        shutil.copyfile(r64 / n, out / n)
    kernel = "Payloads/kernel.macho"
    os.utime(out / "prelink.macho", (payload_step.EPOCH, payload_step.EPOCH))
    call("replace-kernel", ["env", "MTOOLS_SKIP_CHECK=1", "TZ=UTC", "mcopy", "-o", "-m",
         "-i", out / "payload.img", out / "prelink.macho", "::/EFI/UniXNU/" + kernel])

    local = device / "out/ufs-sm8250-launchd-data-20261119-r1/self-check/packaging/local-build.toml"
    ctx = Context(cli_parser().parse_args(["bootimg", "-D", str(out / "device"), "--out", str(out / "work"),
        "--config", str(local), "--local-module", "soc:sm8250=" + str(device.parent / "UniXNU-sm8250-common")]))
    uefi = device.parent / "uefi-enuma"
    fd = uefi / "Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd"
    dtb = Path("/root/enuma-step10/inputs/enuma.dtb")
    ref = json.loads((r64 / "boot.json").read_text())
    assert digest(fd) == ref["fd_sha256"] and digest(dtb) == ref["dtb_sha256"]
    bootimg.build(ctx, uefi, fd, dtb, out / "payload.img", out / "boot.img")

    offset = prior["boot_payload_offset"]
    embedded = out / "tmp/embedded-payload.img"
    with (r64 / "boot.img").open("rb") as old, (out / "boot.img").open("rb") as new:
        x, y = old.read(offset), new.read(offset)
        assert x[:576] == y[:576] and x[596:] == y[596:]
        assert hashlib.file_digest(old, "sha256").hexdigest() == before["payload.img"]
        with embedded.open("wb") as dst:
            shutil.copyfileobj(new, dst)
    assert digest(embedded) == digest(out / "payload.img")
    members = fat_tree(embedded)
    assert members == fat_tree(r64 / "payload.img")
    member_hashes = {n: hashlib.sha256(read_member(embedded, n)).hexdigest()
                     for p in sorted(members) if not p.endswith("/")
                     for n in [p.removeprefix("::/EFI/UniXNU/")]}
    assert [n for n in member_hashes if member_hashes[n] != prior["payload_members_after"][n]] == [kernel]
    assert member_hashes[kernel] == digest(out / "prelink.macho")
    readback = read_member(embedded, "unixnu.toml")
    assert readback == read_member(r64 / "payload.img", "unixnu.toml")
    args = next(e["args"] for e in tomllib.loads(readback.decode())["entry"] if e["id"] == "xnu")
    assert args == prior["args"]
    assert read_member(embedded, "Payloads/kernel.macho.adt") == (
        out / "kernel.macho.adt").read_bytes() == (r64 / "kernel.macho.adt").read_bytes()
    assert {n: digest(r64 / n) for n in names} == before
    assert snapshot(map(Path, inputs)) == inputs and digest(src) == source_hash
    assert head(base) == helpers["BASE_PIN"] and head(xnu) == prior["source_pin"]

    (out / "link-input-sha256.json").write_text(json.dumps(inputs, indent=2) + "\n")
    result = dict(args=args, before=before, after={n: digest(out / n) for n in names},
        sizes={n: (out / n).stat().st_size for n in names},
        deltas={n: (out / n).stat().st_size - prior["sizes"][n] for n in names},
        objects={old_obj.name: [inputs[str(old_obj)], digest(new_obj)]},
        changed_sources={src.name: [prior["changed_sources"][src.name][1], source_hash]},
        unchanged_r64_link_inputs=len(inputs) - 2, r64_rebuilt_link_inputs_pinned=sorted(checked),
        r64_input_snapshot="link-input-sha256.json", r64_artifacts_unchanged=True,
        changed_payload_members=[kernel], payload_members_after=member_hashes,
        boot_payload_offset=offset, zero_undefined_including_weak=True, adt_byte_identical=True,
        callsites=callsites)
    (out / "candidate-manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
