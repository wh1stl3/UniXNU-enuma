#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Repack r6 with only its video_console.o rebuilt using the upstream page."""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
R6_SRC = HERE.parent / "bootprogress-20261125"
spec = importlib.util.spec_from_file_location("r6", R6_SRC / "build-full.py")
r6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r6)
DEVICE, BASE = r6.DEVICE, r6.BASE
SHENG = "c8f92b208068eeaa4cd2b0f592671f04ee70076e"
R6_SHA = "8e09f44fee2ab2526eec5f0a41bc9d98a04660ab21347bebc780243e223e75a2"
R6_RENDERER = "266388ce5b06a6f412e32c3bbb39111f955b083d74909bf88a1c246c9f12427a"
R6_VC = "81b4fe597a6ac4b1ace16be18e2e3d8934882bdb8aa6578324d25f747c419dc5"
FONT_SHA = "7749b211129f6f669f53fd9ee16b8e8dc9464aad41ba1bb6f7ce9b45c4eb2f1d"


def build(out):
    baseline = DEVICE / "out/bootprogress-full-link-20261125-r6"
    confirmed = DEVICE / "out/ufs-sm8250-fp-20261124-r65"
    tree = BASE / "out/enuma/ipados-17.7.11-21H461/enuma/tree"
    uefi = DEVICE.parent / "uefi-enuma"
    font = uefi / "Silicon/Silicium/SiliciumPkg/Library/FrameBufferSerialPortLib/Font.h"
    opts = SimpleNamespace(output=out, tree=tree, uefi=uefi,
        abi_image=tree.parent / "kernel/kernel.macho",
        abi_plan=tree.parent / "kernel/kernel.json",
        reference_payload=baseline / "payload.img",
        reference_boot_report=baseline / "boot.json",
        board=confirmed / "device", dtb=Path("/root/enuma-step10/inputs/enuma.dtb"),
        local=DEVICE / "out/ufs-sm8250-launchd-data-20261119-r1/self-check/packaging/local-build.toml",
        fd=uefi / "Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd")
    if not out.is_relative_to(DEVICE / "out"):
        raise ValueError("fresh output under device out required")
    checks = {baseline / "boot.img": R6_SHA, baseline / "video_console.c": R6_VC,
              R6_SRC / "renderer.inc": R6_RENDERER, font: FONT_SHA}

    def validate_inputs():
        for path, expected in checks.items():
            if r6.digest(path) != expected:
                raise ValueError(f"unexpected input digest: {path}")
        for repo, pin in ((BASE, r6.BASE_PIN), (tree / ".cache/xnu-work", r6.SOURCE_PIN)):
            if subprocess.check_output(["git", "-C", repo, "rev-parse", "HEAD"], text=True).strip() != pin:
                raise ValueError(f"unexpected source pin: {repo}")

    validate_inputs()
    out.mkdir(parents=True)
    (out / "tmp").mkdir()
    env = {**os.environ, **r6.linux_env(opts), "TMPDIR": str(out / "tmp"),
           "PYTHONDONTWRITEBYTECODE": "1"}
    env["PATH"] = "/home/wh1stl3/.local/bin:" + env["PATH"]
    host_env = {**os.environ, "TMPDIR": str(out / "tmp")}
    commands = {}

    def call(tag, argv, cwd=out, environment=env):
        argv = list(map(str, argv))
        proc = subprocess.run(argv, cwd=cwd, env=environment, text=True, capture_output=True)
        (out / (tag + ".log")).write_text(proc.stdout + proc.stderr)
        commands[tag] = {"argv": argv, "cwd": str(cwd), "exit": proc.returncode}
        (out / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        proc.check_returncode()
        return proc.stdout

    ref = out / "reference"
    ref.mkdir()
    upstream = DEVICE / ".cache/bootprogress-sheng-c8f92b.git"
    for file in ("BootProgress.c", "BootProgressCore.h", "BootProgressDisplay.h"):
        raw = subprocess.check_output(["git", "--git-dir", upstream, "show", f"{SHENG}:package/{file}"])
        (ref / file).write_bytes(raw)
    shutil.copyfile(font, ref / "Font.h")
    for file in ("page.h", "sample.inc", "refresh.inc"):
        shutil.copyfile(HERE / file, out / file)
    renderer = (R6_SRC / "renderer.inc").read_text()
    old_start = renderer.index("static void\nenuma_bp_glyph_row(")
    old_end = renderer.index("static void\nenuma_bp_start(", old_start)
    (out / "renderer.inc").write_text(renderer[:old_start] +
        '#include "sample.inc"\n#include "refresh.inc"\n\n' + renderer[old_end:])
    shutil.copyfile(baseline / "video_console.c", out / "video_console.c")
    original = json.loads((baseline / "commands.json").read_text())

    def replay(tag, substitutions, source=None, extra=(), environment=env):
        step = original[source or tag]
        argv = step["argv"].copy()
        for before, after in substitutions.items():
            if argv.count(str(before)) != 1:
                raise ValueError(f"expected one argument in {tag}: {before}")
            argv[argv.index(str(before))] = str(after)
        return call(tag, argv + list(extra), step["cwd"] if source is None else out, environment)

    obj = out / "video_console.o"
    replay("compile-video_console.o", {baseline / obj.name: obj,
        baseline / "video_console.c": out / "video_console.c"},
        extra=("-I", ref))
    for file in ("screen.inc", "pe.inc", "blit.inc", "bp-init.inc"):
        old = baseline / file
        hashes = json.loads((baseline / "generated-test-inputs.json").read_text())["excerpts"]
        if r6.digest(old) != hashes[file]:
            raise ValueError(f"r6 self-test input drift: {file}")
        shutil.copyfile(old, out / file)
    replay("compile-screen", {baseline: out, baseline / "test-screen": out / "test-screen"},
           source="compile-screen-test", environment=host_env)
    call("test-screen", [out / "test-screen"], environment=host_env)
    replay("compile-host", {baseline / "test-framebuffer": out / "test-framebuffer"}, environment=host_env)
    call("test-host", [out / "test-framebuffer"], environment=host_env)
    call("generate-reference", [sys.executable, HERE / "reference.py", out])
    call("compile-page", ["cc", "-std=gnu11", "-Wall", "-Wextra", "-Werror",
         "-fsanitize=address,undefined", "-fno-pie", "-no-pie", "-Wno-unused-function",
         "-I", out, "-I", ref, "-I", R6_SRC, HERE / "test-page.c",
         HERE / "test-reference.c", "-o", out / "test-page"],
         environment=host_env)
    call("test-page", [out / "test-page"], environment=host_env)

    files = (baseline / "link.filelist").read_text()
    (out / "link.filelist").write_text(r6.replace(files, str(baseline / obj.name) + "\n", str(obj) + "\n"))
    native, prelink = out / "native.macho", out / "prelink.macho"
    archive = baseline / "display/libEnumaGopLegacy.a"
    report = baseline / "display/result.json"
    abi = json.loads(opts.abi_plan.read_text())
    donor = Path(original["prelink"]["argv"][original["prelink"]["argv"].index("--prelinked") + 1])
    if r6.digest(donor) != abi["original_sha256"]:
        raise ValueError("r6 prelink donor differs from ABI donor")
    input_digests = {str(p): r6.digest(p) for p in (*checks, archive, donor,
        baseline / "payload.img", baseline / "link.filelist", baseline / "commands.json",
        *(ref / n for n in ("BootProgress.c", "BootProgressCore.h", "BootProgressDisplay.h")),
        *(Path(p) for p in files.splitlines() if Path(p).parent == baseline))}
    replay("link", {baseline / "link.filelist": out / "link.filelist",
        baseline / "native.macho": native, f"-Wl,-map,{baseline / 'native-link.map'}":
        f"-Wl,-map,{out / 'native-link.map'}"})
    pre_args = original["prelink"]["argv"]
    call("prelink", [str(native) if arg == str(baseline / "native.macho") else
        str(prelink) if arg == str(baseline / "prelink.macho") else arg for arg in pre_args])
    for image in (native, prelink):
        if call(image.stem + "-undefined", ["llvm-nm", "-u", image]).strip():
            raise ValueError(f"undefined symbols: {image}")
    call("inspect-final", [sys.executable, R6_SRC / "build-enuma-gop-legacy.py",
        "--candidate", prelink, "--plan", prelink.with_suffix(".json"),
        "--source", DEVICE / "out/bootprogress-display-source-20261125", "--tree", tree,
        "--inspect", out / "final-abi.json", "--check-vtable", report])
    old_abi = json.loads((baseline / "final-abi.json").read_text())
    final_abi = json.loads((out / "final-abi.json").read_text())
    for key in ("checks", "pure", "family_text_sha256", "bindings", "compiled_slots_requalified"):
        if old_abi[key] != final_abi[key]:
            raise ValueError(f"r6 ABI drift: {key}")
    r6.pack(opts, prelink, call)
    table = (out / "final-symbols.log").read_text()
    if re.search(r" _boot_progress_(?:bind|start|prepare_scanout|pulse_anchor)\b", table):
        raise ValueError("unexpected upstream writer in final kernel")
    edges = (out / "calls_enuma_bp_refresh.log").read_text()
    if re.search(r" _panel_sample$", table, re.M):
        edges += call("calls_panel_sample", ["llvm-objdump", "-d",
            "--disassemble-symbols=_panel_sample", out / "embedded-kernel.macho"])
    for target in ("_bsd_log_lock", "_bsd_log_unlock", "_ml_set_interrupts_enabled"):
        if not re.search(r"\bbl\s+[^\n]*<" + target + ">", edges):
            raise ValueError(f"missing collector/raster edge: {target}")
    if (out / "embedded.toml").read_bytes() != (baseline / "embedded.toml").read_bytes():
        raise ValueError("r6 embedded config changed")
    validate_inputs()
    for path, digest in input_digests.items():
        if r6.digest(Path(path)) != digest:
            raise ValueError(f"input changed during build: {path}")
    (out / "provenance.json").write_text(json.dumps({"sheng": SHENG, "base": r6.BASE_PIN,
        "xnu": r6.SOURCE_PIN, "inputs": input_digests,
        "boot_bytes": (out / "boot.img").stat().st_size}, indent=2) + "\n")


if __name__ == "__main__":
    build(Path(sys.argv[1]).resolve())
