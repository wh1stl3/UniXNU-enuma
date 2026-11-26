#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Repack the wrapped r6 page with three isolated process-event objects."""
import difflib
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
R64_SHA = {
    "commands.json": "701376e90e392f149e622d9055649a78bd35c336cfff80353c34e263e5476ac9",
    "objects/kern_exec.o": "18930a3213bffb6ae2bc63e3512a1cf4f90b32183079a1cc0b10dfa9d10710f1",
    "objects/kern_exit.o": "24511f185e69fb0ed92cb4e5a6ee504658f634482f14d63f3cac474b5ccbebc3",
}
R62_SHA = {
    "kern_exec.c": "a0bce9367a028818faf0a2063f09175f9c841fb624e6d1b735f866c7d3e92c34",
    "EnumaBbScan.inc": "eba03004b07723ee401605b11f42c8aaf635a3a6089290c3fa3e45fa5f41b5d1",
    "EnumaBootProgress2.inc": "9fad4669e933b1048817cc58bdc6f635cef5641d0140b9daf2401c439a436d14",
    "EnumaIpc.inc": "df1a0d2bb315fa39fa8d792c389ce46dedb1bf0ca573ec9b4f8a49a1adb68924",
    "EnumaProcExecReport.inc": "12c24d5512d51684946ae1871f91a1a0726d7f4e70d24f1a51a0f5b8455ad36b",
}
R64_BP_SHA = "2007b6908330b14a6e78d06b668cc9ecf05f79a484f7580c88d87f663cb5fc2d"
R64_EXIT_INPUT_SHA = "14b85d7f495a4ec9d2af751a2de424ffae43eabfba5494e9f9e4ec904cc9b23c"
R64_EXIT_CONFIG_SHA = "06bd0c2b7af9fdc2553aba899a5238d0b6e284bd359750f4630fa2d4835f115e"
EXIT_LOG = '\t\tprintf("enuma-exit: pid=%d st=%d sig=%d comm=%s\\n", pid, status, sig, comm);\n'


def restore_r64_sources(r62, exit_input, stock):
    # The original r64 recipe inherited these r62 inputs except for two
    # substitutions below. The remaining r64 stage is not a clean replay.
    # scripts/build-enuma-r64-ustack.py @ a05d60c6908834fae9f7eb8f2c46b6ecd169a0ad.
    stock.mkdir()
    for p in r62.iterdir():
        if p.suffix in (".h", ".inc") or p.name == "kern_exec.c":
            shutil.copyfile(p, stock / p.name)
    exit_anchor = "proc_prepareexit(proc_t p, int rv, boolean_t perf_notify)\n{\n"
    (stock / "kern_exit.c").write_text(r6.replace(exit_input.read_text(), exit_anchor, exit_anchor +
        """\tif (!proc_is_shadow(p)) {
\t\tchar comm[17];
\t\tint pid = proc_getpid(p);
\t\tint status = rv;
\t\tint sig = WIFSIGNALED(status) ? WTERMSIG(status) : 0;
\t\tstrlcpy(comm, p->p_comm, sizeof(comm));
""" + EXIT_LOG + "\t}\n"))
    bp = stock / "EnumaBootProgress2.inc"
    text = r6.replace(bp.read_text(), '#include "EnumaBootProgress62Cpu.inc"\n',
                      '#include "EnumaBootProgress62Cpu.inc"\nextern void enuma_stk_submit(void);\n')
    bp.write_text(r6.replace(text, "\tif (idx == ENUMA_TH_TICK && snapshot_call != NULL) {",
        "\tif (idx == ENUMA_TH_TICK) {\n\t\tenuma_stk_submit();\n\t}\n"
        "\tif (idx == ENUMA_TH_TICK && snapshot_call != NULL) {"))
    if r6.digest(bp) != R64_BP_SHA:
        raise ValueError("restored EnumaBootProgress2.inc differs from r64 manifest")


def generate_proc_sources(source, out):
    def generate(name, edits):
        old = (source / name).read_text()
        new = old
        for before, after in edits:
            new = r6.replace(new, before, after)
        (out / name).write_text(new)
        return "".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                                           f"a/{name}", f"b/{name}"))

    obs = "\tbool reached, failed;\n"
    reached = "\tobs->reached = true;\n"
    local = "\tboolean_t exec_done = FALSE;\n"
    notify = "\t\tproc_knote(p, NOTE_EXEC);\n"
    finish = "\tenuma_ex_finish(&obs);\n"
    gate = """\tif (obs.proc_slot && enuma_bp_exec_observed(obs.reached, obs.failed, error,
\t    exec_done, bp_notified) && {installed} && !proc_is_shadow(p)) {{
\t\tenuma_bp_record_exec(obs.proc_slot, obs.proc_identity);
\t}}
"""
    patch = generate("EnumaProcExecReport.inc", [
        ("#include <kern/locks.h>\n", '#include <kern/locks.h>\n#include "proc-events.h"\n'
         '#include "proc-recorder.inc"\n'),
        (obs, obs + "\tenum enuma_bp_proc_slot proc_slot;\n"
         "\tstruct enuma_bp_identity proc_identity;\n"),
    ])
    # Keep both syscall sites distinct, and keep exit/notification/cleanup ordering.
    patch += generate("kern_exec.c", [
        (reached, reached + """\tobs->proc_slot = enuma_bp_classify(p->p_comm);
\tif (obs->proc_slot) {
\t\tstruct proc_ident id = proc_ident(p);
\t\tobs->proc_identity = (struct enuma_bp_identity){id.p_uniqueid, id.p_pid, id.p_idversion};
\t}
"""),
        (local + "\tos_reason_t exec_failure_reason", local + "\tbool bp_notified = false;\n"
         "\tos_reason_t exec_failure_reason"),
        (local + "\tvoid *inherit", local + "\tbool bp_notified = false;\n\tvoid *inherit"),
        (f"\tif (!error && ((p->p_lflag & P_LTERM_DECRYPTFAIL) == 0)) {{\n{notify}",
         f"\tif (!error && ((p->p_lflag & P_LTERM_DECRYPTFAIL) == 0)) {{\n{notify}"
         "\t\tbp_notified = true;\n"),
        (f"\tif (exec_done && ((p->p_lflag & P_LTERM_DECRYPTFAIL) == 0)) {{\n{notify}",
         f"\tif (exec_done && ((p->p_lflag & P_LTERM_DECRYPTFAIL) == 0)) {{\n{notify}"
         "\t\tbp_notified = true;\n"),
        (finish + "\tif (exec_failure_reason", finish +
         "\t/* A true spawn already owns the child proc from fork1. SETEXEC must\n"
         "\t * have switched out the old task, not just returned a new_proc. */\n" +
         gate.format(installed="(spawn_no_exec || task_did_exec(old_task))") +
         "\tif (exec_failure_reason"),
        (finish + "\n\t/* terminate the new task", finish +
         "\t/* A failed switch can return the shadow proc with error still zero. */\n" +
         gate.format(installed="task_did_exec(old_task)") + "\n\t/* terminate the new task"),
    ])
    patch += generate("kern_exit.c", [
        ("#include <kern/enuma_pid1.h>\n", '#include <kern/enuma_pid1.h>\n#include "proc-events.h"\n'),
        (EXIT_LOG, """\t\tenum enuma_bp_proc_slot slot = enuma_bp_classify(comm);
\t\tif (slot) {
\t\t\tstruct proc_ident id = proc_ident(p);
\t\t\tstruct enuma_bp_identity who = {id.p_uniqueid, id.p_pid, id.p_idversion};
\t\t\tenuma_bp_record_exit(slot, who, rv);
\t\t}
""" + EXIT_LOG),
    ])
    (out / "proc-source.diff").write_text(patch)


def build(out):
    baseline = DEVICE / "out/bootprogress-full-link-20261125-r6"
    r64 = DEVICE / "out/ufs-sm8250-ustack-20261124-r64"
    r64_source = r64 / "source/bsd/kern"
    r62_source = DEVICE / "out/ufs-sm8250-smpobs-20261124-r62/source/bsd/kern"
    r64_commands = json.loads((r64 / "commands.json").read_text())
    replay_tree = Path(r64_commands["link"]["cwd"]).parents[3]
    replay_xnu = replay_tree / ".cache/xnu-work"
    exit_input = replay_xnu / "bsd/kern/kern_exit.c"
    # The recorded ios-obj input was truncated after r64. The preserved
    # sibling reproduces the original kern_exit.o byte-for-byte at its
    # recorded source path. Do not apply this substitution to other TUs.
    exit_config = replay_tree / "build/xnu/obj/san/kasan-blacklist-arm64"
    exit_config_flag = "-fsanitize-ignorelist="
    exit_argv_replay = {
        exit_config_flag + str(replay_tree / "build/xnu/ios-obj/san/kasan-blacklist-arm64"):
        exit_config_flag + str(exit_config),
    }
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
              R6_SRC / "renderer.inc": R6_RENDERER, font: FONT_SHA,
              baseline / "link.filelist": "75bb2afd62a19b5761f613ee6cffc9ac26ac04ad6767150fdcd7df28be9f222b",
              exit_input: R64_EXIT_INPUT_SHA,
              exit_config: R64_EXIT_CONFIG_SHA,
              **{r62_source / n: sha for n, sha in R62_SHA.items()},
              **{r64 / n: sha for n, sha in R64_SHA.items()}}

    def validate_inputs():
        for path, expected in checks.items():
            if r6.digest(path) != expected:
                raise ValueError(f"unexpected input digest: {path}")
        for repo, pin in ((BASE, r6.BASE_PIN), (tree / ".cache/xnu-work", r6.SOURCE_PIN),
                          (replay_xnu, r6.SOURCE_PIN)):
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
    for file in ("page.h", "sample.inc", "refresh.inc", "proc-events.h",
                 "proc-page.inc", "proc-recorder.inc"):
        shutil.copyfile(HERE / file, out / file)
    renderer = (R6_SRC / "renderer.inc").read_text()
    old_start = renderer.index("static void\nenuma_bp_glyph_row(")
    old_end = renderer.index("static void\nenuma_bp_start(", old_start)
    (out / "renderer.inc").write_text(renderer[:old_start] +
        '#include "sample.inc"\n#include "refresh.inc"\n\n' + renderer[old_end:])
    shutil.copyfile(baseline / "video_console.c", out / "video_console.c")
    original = json.loads((baseline / "commands.json").read_text())

    def replay(tag, substitutions, source=None, extra=(), environment=env, steps=original, cwd=None):
        step = steps[source or tag]
        argv = step["argv"].copy()
        for before, after in substitutions.items():
            if argv.count(str(before)) != 1:
                raise ValueError(f"expected one argument in {tag}: {before}")
            argv[argv.index(str(before))] = str(after)
        return call(tag, argv + list(extra), cwd or (step["cwd"] if source is None else out), environment)

    obj = out / "video_console.o"
    replay("compile-video_console.o", {baseline / obj.name: obj,
        baseline / "video_console.c": out / "video_console.c"},
         extra=("-I", ref))
    # Reconstruct pre-edit inputs and verify their original machine code and
    # relocations before compiling the edited source.
    stock_source = out / "stock"
    restore_r64_sources(r62_source, exit_input, stock_source)
    generate_proc_sources(stock_source, out)
    shutil.copyfile(stock_source / "EnumaBbScan.inc", out / "EnumaBbScan.inc")
    objects = {baseline / obj.name: obj}
    for stem in ("kern_exec", "kern_exit"):
        src = stem + ".c"
        stock = r64 / "objects" / (stem + ".o")
        objects[stock] = out / stock.name
        control = stock_source / stock.name
        overrides = exit_argv_replay if stem == "kern_exit" else {}
        replay("control-" + stock.name, {r64_source / src: stock_source / src, stock: control, **overrides},
               source="compile-" + stock.name, steps=r64_commands,
               cwd=r64_commands["compile-" + stock.name]["cwd"],
               extra=(f"-fmacro-prefix-map={stock_source}={r64_source}",))
        for name, flags, trim in (
            ("text", ["--section=__TEXT,__text", "--full-contents"], lambda s: s.split("\n", 1)[1]),
            ("relocs", ["--reloc"], lambda s: s.split("\n", 1)[1].split("\nRelocation information", 1)[0]),
        ):
            old = call(f"control-{stem}-original-{name}", ["llvm-objdump", "--macho", *flags, stock])
            new = call(f"control-{stem}-replay-{name}", ["llvm-objdump", "--macho", *flags, control])
            if not trim(old) or trim(old) != trim(new):
                raise ValueError(f"r64 no-telemetry replay differs in {name}: {stock.name}")
        replay("compile-" + stock.name, {r64_source / src: out / src, stock: objects[stock], **overrides},
               extra=("-iquote", stock_source, f"-fmacro-prefix-map={out}={r64_source}"),
               steps=r64_commands)
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
    call("compile-proc-test", ["cc", "-std=gnu11", "-Wall", "-Wextra", "-Werror",
         "-fsanitize=address,undefined", "-fno-pie", "-no-pie", "-Wno-unused-function",
         "-pthread", "-I", out, "-I", ref, "-I", R6_SRC, HERE / "test-proc.c", "-o", out / "test-proc"],
         environment=host_env)
    call("test-proc", [out / "test-proc"], environment=host_env)

    files = (baseline / "link.filelist").read_text()
    new_files = files
    for before, after in objects.items():
        new_files = r6.replace(new_files, f"{before}\n", f"{after}\n")
    (out / "link.filelist").write_text(new_files)
    native, prelink = out / "native.macho", out / "prelink.macho"
    archive = baseline / "display/libEnumaGopLegacy.a"
    report = baseline / "display/result.json"
    abi = json.loads(opts.abi_plan.read_text())
    donor = Path(original["prelink"]["argv"][original["prelink"]["argv"].index("--prelinked") + 1])
    if r6.digest(donor) != abi["original_sha256"]:
        raise ValueError("r6 prelink donor differs from ABI donor")
    input_digests = {str(p): r6.digest(p) for p in (*checks, *objects, archive, donor,
        *(p for p in r62_source.iterdir() if p.suffix in (".h", ".inc")),
        *(p for p in HERE.iterdir() if p.is_file()),
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
    for caller, target in (("_posix_spawn", "_enuma_bp_record_exec"),
                           ("___mac_execve", "_enuma_bp_record_exec"),
                           ("_proc_prepareexit", "_enuma_bp_record_exit"),
                           ("_panel_sample" if re.search(r" _panel_sample$", table, re.M)
                            else "_enuma_bp_refresh", "_enuma_bp_proc_snapshot")):
        code = call("event-edges" + caller, ["llvm-objdump", "-d",
                    f"--disassemble-symbols={caller}", out / "embedded-kernel.macho"])
        if len(re.findall(r"\bbl\s+[^\n]*<" + target + ">", code)) != 1:
            raise ValueError(f"expected one final edge: {caller} -> {target}")
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
