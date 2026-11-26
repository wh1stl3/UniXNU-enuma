#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Build the isolated r4-display/r5-proc two-instance run_state diagnostic."""
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
spec = importlib.util.spec_from_file_location(
    "display", HERE.parent / "bootprogress-display-events-20261126/build.py")
display = importlib.util.module_from_spec(spec)
spec.loader.exec_module(display)
r6, R5, DEVICE, BASE = display.r6, display.R5, display.DEVICE, display.BASE
R4 = DEVICE / "out/bootprogress-display-events-20261126-r4"
PINS = {
    HERE.parent / "bootprogress-display-events-20261126/build.py":
        "ce9894d72402cb6dfdde601d7ceb3ff3498d52c305bfc03e2345ae5fb5c003bb",
    HERE.parent / "bootprogress-20261125/build-full.py":
        "08764ada9547245327949707287fe0550d38805f778513202a49b2971c821c65",
    HERE.parent / "bootprogress-20261125/build-enuma-gop-legacy.py":
        "663764e04cfe1dab127df2b4d320c756d8db562af7e8c0e75ac077c99ea0cf71",
    R5 / "boot.img": "50bb81c21b0b56e08aad6a1f8a99e3f57d04e3eeea40914efc19baf5f5680fa2",
    R5 / "commands.json": "1a1efe9bd6214c1ed719ea2b9af03b17c7ef9b3e80ec48778c983e16d9a18ca6",
    R5 / "kern_exec.c": "b5b1d21c2e997ce4ccf70066f9a10115bf99360a6f207ed01e68edf41d255490",
    R5 / "kern_exit.o": "db64be8feb6c92fd69a5e51d4e6d6a077eedf502ee6626eaf4c2e43213fec0d8",
    R5 / "EnumaProcExecReport.inc": "90a9c68a66ad6e7279ec6614cdddb3e8ec4f074902c91d85b62febf196511907",
    R5 / "EnumaBbScan.inc": "eba03004b07723ee401605b11f42c8aaf635a3a6089290c3fa3e45fa5f41b5d1",
    R5 / "proc-events.h": "f8a21a392c0f481d2964316aae86fb13659b8829a21ce17b7e9baa09964dbf94",
    R5 / "proc-recorder.inc": "51aeadda31b97b355376fae162a3b957db67b4623df9cb9625be28efd69badc3",
    R5 / "stock/EnumaBootProgress2.inc": "2007b6908330b14a6e78d06b668cc9ecf05f79a484f7580c88d87f663cb5fc2d",
    R4 / "boot.img": "5849e9c67ebce4440544cee96d5d54a37b6c0f9c2705a6389a513e0807086183",
    R4 / "boot.json": "be4576022eb44653f78f889834dcd1fcbf0d544994ef598efcc2b5a5e5d86af9",
    R4 / "embedded.toml": "f02c33006a68ed9accc77eaa93a7824902836e8dedda785f7477fd3ba8039578",
    R4 / "commands.json": "fec6716b578208446222152ffa99c6cb5cb97ca5d8080f439c5a6c372cd13af9",
    R4 / "link.filelist": "d42bdf043a6ee8670e4a8849da4892a6b15697c4adf9fe7e0c5d01c32e847287",
    R4 / "payload.img": "fde23fa46d9d820d83fa03403b56a002f93d361521d185ce2d8316db95bbd738",
    R4 / "libEnumaGopLegacy.a": "1bccae1dff30ef5fdd2bc687489b06fe34eadda81d7b8f8022251fbec435bf75",
    R4 / "video_console.o": "39ffb0df0077dda90dae083f5c28b7414fc3937ff8a21073ac1fcbb8827ea728",
    R4 / "video_console.c": "81b4fe597a6ac4b1ace16be18e2e3d8934882bdb8aa6578324d25f747c419dc5",
    R4 / "sample.inc": "f182d0ea52efdb941e96edfae1bc53682d26dcd6afaac1049932ad1a1a91570c",
    R4 / "renderer.inc": "4b688510bb15108460ba5c6d7a1a5bdc1d99537ff75657b40569102538766191",
    R4 / "refresh.inc": "86d9f88022ba30eb3c1fe41ce00577d741ff790bacf55f013f65a350d0bd2479",
    R4 / "page.h": "85f6b04375215a4c9b60c32262f3d2eded7f8e279f49f16b5503ab9da7dea640",
    R4 / "proc-page.inc": "22e937a56a142a12d5abf9e77cf80477420505e5e82f5ac9cb2e0861b512d53f",
    R4 / "display-page.inc": "f3f57d2c4e6d986f01bff2adfa2527e4d699c491de8dda1d58d405be8ceabd71",
    R4 / "final-abi.json": "99650e19e6aacc2d83ef796ff7d7fbcad5666c43dfd32d0336225800cf3ce6e0",
}
OLD_OBJECTS = {"EnumaThreadSnapshot56.o", "EnumaUserStack64.o"}
OLD_SYMBOL = re.compile(r"\b_enuma_(?:th_|stk_)\w+")
need, one = display.need, r6.replace


def generate(out):
    diffs = []

    def emit(name, transform, directory=R5):
        before = (directory / name).read_text()
        after = transform(before)
        (out / name).write_text(after)
        diffs.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                         ("r4/" if directory == R4 else "r5/") + name, "candidate/" + name))

    def exec_source(text):
        anchor = "\t\tobs->proc_identity = (struct enuma_bp_identity){id.p_uniqueid, id.p_pid, id.p_idversion};"
        text = one(text, anchor, anchor + """
		if (obs->proc_slot == ENUMA_BP_BACKBOARDD || obs->proc_slot == ENUMA_BP_SPRINGBOARD)
			obs->initial_tid = thread_tid(imgp->ip_new_thread);""")
        publish = "enuma_bp_record_exec(obs.proc_slot, obs.proc_identity);"
        need(text.count(publish) == 2, "r5 exec publication site drift")
        return text.replace(publish, "enuma_bp_record_exec(obs.proc_slot, obs.proc_identity, obs.initial_tid);")

    def report_source(text):
        return one(one(text, '#include "proc-recorder.inc"',
                       '#include "proc-recorder.inc"\n#include "run-state.inc"'),
                   "\tenum enuma_bp_proc_slot proc_slot;", "\tenum enuma_bp_proc_slot proc_slot;\n\tuint64_t initial_tid;")

    def recorder_source(text):
        text = one(text, "static struct enuma_bp_proc_events enuma_bp_events;", """\
static struct enuma_bp_proc_events enuma_bp_events;
/* Sidecar uses the same lock; the r4 renderer's proc-snapshot ABI is unchanged. */
static uint64_t enuma_bp_initial_tid[ENUMA_BP_PROC_SLOTS];
static bool enuma_bp_matching_exit[ENUMA_BP_PROC_SLOTS];

struct enuma_bp_run_events {
	struct enuma_bp_proc_events events;
	uint64_t tid[ENUMA_BP_PROC_SLOTS];
	bool matching_exit[ENUMA_BP_PROC_SLOTS];
};

static bool
enuma_bp_same_identity(struct enuma_bp_identity a, struct enuma_bp_identity b)
{
	return a.pid == b.pid && a.uniqueid == b.uniqueid && a.idversion == b.idversion;
}

static __attribute__((noinline)) bool
enuma_bp_run_snapshot(struct enuma_bp_run_events *snapshot)
{
	if (!lck_spin_try_lock(&enuma_bp_proc_lock))
		return false;
	snapshot->events = enuma_bp_events;
	memcpy(snapshot->tid, enuma_bp_initial_tid, sizeof(snapshot->tid));
	memcpy(snapshot->matching_exit, enuma_bp_matching_exit, sizeof(snapshot->matching_exit));
	lck_spin_unlock(&enuma_bp_proc_lock);
	return true;
}""")
        text = one(text, "enuma_bp_record_exec(enum enuma_bp_proc_slot slot, struct enuma_bp_identity who)",
                   "enuma_bp_record_exec(enum enuma_bp_proc_slot slot, struct enuma_bp_identity who, uint64_t tid)")
        anchor = "\tenuma_bp_note_event(&enuma_bp_events.slot[slot - 1].exec, who);"
        text = one(text, anchor, """\
	const unsigned i = slot - 1;
	const bool same_exec_id = enuma_bp_events.slot[i].exec.count &&
	    enuma_bp_same_identity(who, enuma_bp_events.slot[i].exec.latest);
	/* An exit can beat exec publication. Do not clear a matching exit by
	 * guessing which re-exec with the same identity it belonged to. */
	enuma_bp_matching_exit[i] = (same_exec_id && enuma_bp_matching_exit[i]) ||
	    (enuma_bp_events.slot[i].exit.count &&
	    enuma_bp_same_identity(who, enuma_bp_events.slot[i].exit.latest));
	enuma_bp_initial_tid[i] = tid;
	enuma_bp_note_event(&enuma_bp_events.slot[i].exec, who);""")
        anchor = "\tenuma_bp_note_event(&enuma_bp_events.slot[slot - 1].exit, who);"
        return one(text, anchor, """\
	const unsigned i = slot - 1;
	if (enuma_bp_events.slot[i].exec.count &&
	    enuma_bp_same_identity(who, enuma_bp_events.slot[i].exec.latest))
		enuma_bp_matching_exit[i] = true;
	enuma_bp_note_event(&enuma_bp_events.slot[i].exit, who);""")

    def legacy_progress(text):
        start = text.index('#include "EnumaThreadSnapshot56Bsd.inc"')
        end = text.index("enum { ENUMA_BP_INTERVAL", start)
        text = text[:start] + '#include "EnumaBootProgress62Cpu.inc"\n' + text[end:]
        text = one(text, "enuma_bp_repeat(thread_call_param_t snapshot_call,",
                   "enuma_bp_repeat(__unused thread_call_param_t unused,")
        start = text.index("\tif (idx == ENUMA_TH_TICK)")
        end = text.index("\tif (idx < ENUMA_BP_REPRINTS)", start)
        text = text[:start] + text[end:]
        text = one(text, "\tthread_call_t snapshot_call = enuma_th_alloc(ENUMA_TH_TICK);\n", "")
        text = one(text, "\t    snapshot_call, THREAD_CALL_PRIORITY_KERNEL, THREAD_CALL_OPTIONS_ONCE);",
                   "\t    NULL, THREAD_CALL_PRIORITY_KERNEL, THREAD_CALL_OPTIONS_ONCE);")
        return one(text, "\t} else if (snapshot_call != NULL) {\n\t\tthread_call_free(snapshot_call);\n", "")

    def report_callback(text):
        anchor = "\tif (++enuma_fb_reports < ENUMA_FB_REPORTS)"
        return one(text, anchor, """\
	/* The ONCE launchd report has one writer; report 4 is the sole dispatch.
	 * The other report (non-null parameter) returned before reaching here. */
	if (++enuma_fb_reports == 4) {
		int mode = 0;
		if (PE_parse_boot_argn("boot-progress", &mode, sizeof(mode)) && mode == 2)
			enuma_bp_run_once();
	}
	if (enuma_fb_reports < ENUMA_FB_REPORTS)""")

    def page_sample(text):
        text = one(text, '#include "display-page.inc"', '#include "display-page.inc"\n#include "run-state-page.inc"')
        anchor = "\tbool proc_available = enuma_bp_proc_snapshot(&proc_events);"
        text = one(text, anchor, anchor + """
	struct enuma_bp_run_report run_report;
	bool run_ready = enuma_bp_run_read(&run_report);""")
        anchor = '\tLINE(12, PANEL_GREY, "PC samples unavailable");'
        return one(text, anchor, anchor + "\n\tpanel_run_state(page, run_ready ? &run_report : NULL);")

    emit("kern_exec.c", exec_source)
    emit("EnumaProcExecReport.inc", report_source)
    emit("EnumaBbScan.inc", report_callback)
    emit("EnumaBootProgress2.inc", legacy_progress, R5 / "stock")
    emit("proc-events.h", lambda text: one(text,
         "void enuma_bp_record_exec(enum enuma_bp_proc_slot, struct enuma_bp_identity);",
         "void enuma_bp_record_exec(enum enuma_bp_proc_slot, struct enuma_bp_identity, uint64_t);"))
    emit("proc-recorder.inc", recorder_source)
    emit("sample.inc", page_sample, R4)
    (out / "source.diff").write_text("".join(diffs))


def verify_run_state(out, call):
    for f in ("link.filelist", "native-link.map", "final-symbols.log"):
        text = (out / f).read_text(encoding="latin-1")
        need(not any(name in text for name in OLD_OBJECTS) and not OLD_SYMBOL.search(text),
             f"old thread/stack diagnostic in {f}")
    image = out / "embedded-kernel.macho"

    def dis(symbol):
        code = call("run-edge" + symbol, ["llvm-objdump", "-d", "--disassemble-symbols=" + symbol, image])
        need(f"<{symbol}>:" in code, f"{symbol}: no body in extracted boot kernel")
        return code

    def calls(symbol):
        return re.findall(r"\s+b(?:l)?\s+[^\n]*?<([^>]+)>", dis(symbol))

    cb = dis("_enuma_fb_dump")
    need(cb.count("<_enuma_bp_run_once>") == 1, "missing or duplicate launchd report-4 dispatch")
    need(re.search(r"\bcmp\s+w\d+, #4\n(?:[^\n]*\n){1,9}[^\n]*<_PE_parse_boot_argn>\n"
                   r"(?:[^\n]*\n){1,5}[^\n]*\bcmp\s+w\d+, #2\n"
                   r"(?:[^\n]*\n){1,3}[^\n]*<_enuma_bp_run_once>", cb),
         "launchd report-4 dispatch/boot-progress gate drift")
    exec_code = dis("_exec_mach_imgact")
    need(len(re.findall(r"\band\s+w\d+, w\d+, #0xfffffffe\n[^\n]*\bcmp\s+w\d+, #2\n"
                        r"[^\n]*\bb\.ne\s+[^\n]+\n[^\n]*\bldr\s+x0, \[x\d+, #696\]\n"
                        r"[^\n]*<_thread_tid>\n[^\n]*\bstr\s+x0,", exec_code)) == 1,
         "pinned initial-thread capture edge drift")
    symbols = (out / "final-symbols.log").read_text()
    collector = "_panel_sample" if re.search(r"\b_panel_sample$", symbols, re.M) else "_enuma_bp_refresh"
    for other in {"_enuma_bp_repeat", "_enuma_bp_refresh", collector}:
        need("_enuma_bp_run_once" not in calls(other), f"unexpected run-state dispatch: {other}")
    collect = dis(collector)
    need(collect.count("<_enuma_bp_run_read>") == 1 and
         collect.index("<_enuma_bp_run_read>") < collect.index("<_ml_set_interrupts_enabled>") and
         not re.search(r"<_(?:thread_info|task_findtid|proc_find_ident)>", collect),
         "page must only acquire-copy the result before the interrupt/lease window")
    reader = dis("_enuma_bp_run_read")
    need(re.search(r"\bldarb?\s", reader) and not re.search(r"\b(?:bl|blr|stlr[b]?)\s", reader),
         "run-state reader is not a leaf acquire-copy")
    worker = dis("_enuma_bp_run_once")
    need(len(re.findall(r"\bstlrb?\s", worker)) == 1,
         "expected a single shared release publication block")
    snap = calls("_enuma_bp_run_once")
    need(snap.count("_enuma_bp_run_snapshot") == 2 and snap.count("_enuma_bp_run_target") == 2,
         "expected pre/post snapshots and bounded target dispatch")
    target = calls("_enuma_bp_run_target")
    for api, count in {"_proc_find_ident": 2, "_task_reference_grp": 1, "_task_findtid": 1,
                       "_thread_info": 1, "_thread_deallocate": 1, "_task_deallocate_grp": 1}.items():
        need(target.count(api) == count, f"run target edge drift: {api}")
    need(target.index("_task_reference_grp") < target.index("_task_findtid") <
         target.index("_thread_info") < target.index("_thread_deallocate") < target.index("_task_deallocate_grp"),
         "run target reference order drift")
    allowed = {
        "_current_thread", "_thread_tid", "_proc_find_ident", "_proc_is_shadow", "_proc_exiting",
        "_proc_in_teardown", "_proc_task", "_task_reference_grp", "_proc_rele", "_task_findtid",
        "_thread_info", "_thread_deallocate", "_task_deallocate_grp", "_enuma_bp_run_snapshot",
        "_enuma_bp_run_target", "_memcpy", "_bzero", "_lck_spin_try_lock",
        "_lck_spin_unlock", "___stack_chk_fail",
    }
    for symbol in set(snap + target + calls("_enuma_bp_run_snapshot")):
        need(symbol in allowed or re.fullmatch(r"_enuma_bp_run_(?:once|target|snapshot)\+0x[\da-f]+", symbol),
             f"unexpected run-state callee {symbol}")


def build(out):
    need(out.parent == DEVICE / "out", "use a fresh directory directly under device out")
    old = json.loads((R5 / "commands.json").read_text())
    r4 = json.loads((R4 / "commands.json").read_text())
    tree = BASE / "out/enuma/ipados-17.7.11-21H461/enuma/tree"
    uefi = DEVICE.parent / "uefi-enuma"
    opts = SimpleNamespace(output=out, tree=tree, uefi=uefi,
        abi_image=tree.parent / "kernel/kernel.macho", abi_plan=tree.parent / "kernel/kernel.json",
        reference_payload=R4 / "payload.img", reference_boot_report=R4 / "boot.json",
        board=DEVICE / "out/ufs-sm8250-fp-20261124-r65/device",
        dtb=Path("/root/enuma-step10/inputs/enuma.dtb"),
        local=DEVICE / "out/ufs-sm8250-launchd-data-20261119-r1/self-check/packaging/local-build.toml",
        fd=uefi / "Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd")
    compile_step = old["compile-kern_exec.o"]
    xnu = next(Path(arg).parent for arg in compile_step["argv"] if arg.endswith("/.cache/xnu-work/bsd"))

    def validate():
        for repo, pin in ((BASE, r6.BASE_PIN), (xnu, r6.SOURCE_PIN)):
            actual = subprocess.check_output(["git", "-C", repo, "rev-parse", "HEAD"], text=True).strip()
            need(actual == pin, f"unexpected HEAD: {repo}: {actual}")
        for path, sha in PINS.items():
            need(r6.digest(path) == sha, f"unexpected input digest: {path}")

    validate()
    out.mkdir()
    (out / "tmp").mkdir()
    commands = {}
    env = {**os.environ, **r6.linux_env(opts), "TMPDIR": str(out / "tmp"), "PYTHONDONTWRITEBYTECODE": "1"}
    env["PATH"] = "/home/wh1stl3/.local/bin:" + env["PATH"]
    host_env = {**os.environ, "TMPDIR": str(out / "tmp")}

    def call(tag, argv, cwd=out, environment=env):
        argv = list(map(str, argv))
        result = subprocess.run(argv, cwd=cwd, env=environment, text=True, capture_output=True)
        log = out / (tag + ".log")
        log.write_text(result.stdout + result.stderr)
        commands[tag] = {"argv": argv, "cwd": str(cwd), "exit": result.returncode}
        (out / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        need(result.returncode == 0, f"{tag} exit {result.returncode}; see {log}")
        return result.stdout

    def replay(tag, step, substitutions, extra=()):
        argv = step["argv"].copy()
        for original, changed in substitutions:
            need(argv.count(str(original)) == 1, f"{tag}: missing/ambiguous argument {original}")
            argv[argv.index(str(original))] = str(changed)
        call(tag, argv + list(extra), step["cwd"] if step["cwd"] not in (str(R4), str(R5)) else out)

    generate(out)
    for name in ("video_console.c", "renderer.inc"):
        shutil.copyfile(R4 / name, out / name)
    call("compile-test-run-state", ["cc", "-std=gnu11", "-Wall", "-Wextra", "-Werror",
         "-Wno-unused-function", "-fsanitize=address,undefined", "-fno-pie", "-no-pie",
         "-I", out, "-I", R4, "-I", HERE.parent / "bootprogress-20261125",
         "-I", DEVICE.parent / "uefi-enuma/Silicon/Silicium/SiliciumPkg/Library/FrameBufferSerialPortLib",
         HERE / "test-run-state.c",
         "-o", out / "test-run-state"], environment=host_env)
    call("test-run-state", [out / "test-run-state"], environment=host_env)
    replay("compile-kern_exec.o", compile_step,
           [(arg, out / Path(arg).name) for arg in compile_step["argv"]
            if Path(arg).name in {"kern_exec.c", "kern_exec.o"}],
           ("-iquote", str(HERE)))
    replay("compile-video_console.o", r4["compile-video_console.o"],
           [(R4 / f, out / f) for f in ("video_console.c", "video_console.o")],
           ("-iquote", str(HERE), "-iquote", str(R4)))
    files = list(map(Path, (R4 / "link.filelist").read_text().splitlines()))
    need([p for p in files if p.name == "kern_exec.o"] == [R5 / "kern_exec.o"], "expected r5 exec object")
    need([p for p in files if p.name == "kern_exit.o"] == [R5 / "kern_exit.o"], "expected r5 exit object")
    need([p for p in files if p.name == "video_console.o"] == [R4 / "video_console.o"], "expected r4 video object")
    need(sorted(p.name for p in files if p.name in OLD_OBJECTS) == sorted(OLD_OBJECTS), "old objects drift")
    rebuilt = {"kern_exec.o", "video_console.o"}
    (out / "link.filelist").write_text("".join(f"{out / p.name if p.name in rebuilt else p}\n"
                                             for p in files if p.name not in OLD_OBJECTS))
    replay("link", r4["link"], [(R4 / f, out / f) for f in ("link.filelist", "native.macho")] +
           [(f"-Wl,-map,{R4}/native-link.map", f"-Wl,-map,{out}/native-link.map")])
    donor = Path(old["prelink"]["argv"][old["prelink"]["argv"].index("--prelinked") + 1])
    need(r6.digest(donor) == json.loads(opts.abi_plan.read_text())["original_sha256"], "prelink donor drift")
    replay("prelink", r4["prelink"], [(R4 / f, out / f) for f in ("native.macho", "prelink.macho")])
    for name in ("native", "prelink"):
        need(not call(name + "-undefined", ["llvm-nm", "-u", out / (name + ".macho")]).strip(),
             f"{name}: unforeseen unresolved symbol")
    replay("inspect-final", r4["inspect-final"],
           [(R4 / f, out / f) for f in ("prelink.macho", "prelink.json", "final-abi.json")])
    prev, new = (json.loads((d / "final-abi.json").read_text()) for d in (R4, out))
    for key in ("checks", "pure", "family_text_sha256", "bindings", "compiled_slots_requalified",
                "field_instructions", "stride_units", "slots", "instance_bytes"):
        need(prev[key] == new[key], f"display ABI drift: {key}")
    r6.pack(opts, out / "prelink.macho", call)
    need((out / "embedded.toml").read_bytes() == (R4 / "embedded.toml").read_bytes(), "r4 boot args changed")
    display.verify_final(out, call)
    verify_run_state(out, call)
    validate()
    (out / "run-state-verified.json").write_text(json.dumps({
        "status": "self-checked", "boot_sha256": r6.digest(out / "boot.img"),
        "bytes": (out / "boot.img").stat().st_size, "hardware_tested": False,
        "pinned_inputs": {str(p): sha for p, sha in PINS.items()},
    }, indent=2) + "\n")


if __name__ == "__main__":
    build(Path(sys.argv[1]).resolve())
