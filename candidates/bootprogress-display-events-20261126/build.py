#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Replay the pinned r5 link/package with display-only observation."""
import difflib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
R6_SRC = HERE.parent / "bootprogress-20261125"
WRAP = HERE.parent / "bootprogress-wrap-20261126"
spec = importlib.util.spec_from_file_location("r6", R6_SRC / "build-full.py")
r6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r6)
DEVICE, BASE = r6.DEVICE, r6.BASE
R5 = DEVICE / "out/bootprogress-proc-events-20261126-r5"
DISPLAY = DEVICE / "out/bootprogress-full-link-20261125-r6/display"
ABI_SOURCE = DEVICE / "out/bootprogress-display-source-20261125"
PINS = {
    R5 / "boot.img": "50bb81c21b0b56e08aad6a1f8a99e3f57d04e3eeea40914efc19baf5f5680fa2",
    R5 / "payload.img": "b09e2b572ec7ef64a65313a4bd82694b1396f5bdeb33e8781a6fd04802521384",
    R5 / "commands.json": "1a1efe9bd6214c1ed719ea2b9af03b17c7ef9b3e80ec48778c983e16d9a18ca6",
    R5 / "link.filelist": "3b1b568033e07e5b8f935a88479a5c10afde376d217bcd67bbd308b31aaff6bf",
    R5 / "kern_exec.o": "c21e9f6fbc561f8e1bbe9282f4a2daa502afd65d943b44818404313f499ef6cd",
    R5 / "kern_exit.o": "db64be8feb6c92fd69a5e51d4e6d6a077eedf502ee6626eaf4c2e43213fec0d8",
    R5 / "sample.inc": "8dcc8b8b134d1315efe0dc5b5697d75d0b22659ec39efd8cae568d78b35d8491",
    DISPLAY / "source/NativeLegacyDisplay.cpp": "478a48846b25ad35b8e39af449f1cab8447a3d40cf556e551dc8754d5e0c0584",
    DISPLAY / "EnumaLegacyDisplay.cpp": "7dcc3cdfb41041351a08a8689904d10e64e78a9f166a403fca84f9757831694f",
    DISPLAY / "libEnumaGopLegacy.a": "a60ce83ac4b4a7a760e03ea8b66a6e519ac2178439a75735914f7b943c6a0069",
    DISPLAY / "original-bindings.o": "3650732909f83fc31951f9dfea24eae435e89004d7a5c391ee2888f11fad5773",
    DISPLAY / "result.json": "209aad5bf8c7320605d247b59d02188add43baef5ed30e5d9f055877056be684",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def excerpt(text, begin, end):
    at = text.index(begin)
    return text[at:text.index(end, at)]


def generate(out):
    one = r6.replace
    native_name = "NativeLegacyDisplay.cpp"
    backend_name = "EnumaLegacyDisplay.cpp"
    native = (DISPLAY / "source" / native_name).read_text()
    backend = (DISPLAY / backend_name).read_text()
    sample = (R5 / "sample.inc").read_text()
    vstart = "    bool validateSwap(const OriginalLegacySwapRequest *request) override {\n"
    vend = "    // The original slot-188"
    cstart = "    IOReturn newUserClient(task_t task,void *security,UInt32 type,IOUserClient **client) override {\n"
    cend = "    bool startHardware()"
    native_new = one(native, '#include "NativeLegacyRequest.h"\n',
                     '#include "NativeLegacyRequest.h"\n#include "display-events.h"\n')
    native_new = one(native_new, vstart, vstart +
                     "        enuma_bp_display_mark(ENUMA_DISPLAY_VALIDATE_ENTER);\n")
    line = "        native_legacy_swap_validation_observed(accepted,reason,request,surface);return accepted;\n"
    native_new = one(native_new, line,
                     "        enuma_bp_display_mark(accepted ? ENUMA_DISPLAY_VALIDATE_ACCEPT : ENUMA_DISPLAY_VALIDATE_REJECT);\n" + line)
    native_new = one(native_new, cstart, cstart +
                     "        enuma_bp_display_mark(ENUMA_DISPLAY_LEGACY4_ENTER);\n")
    line = "        IOReturn status=IOMobileFramebufferLegacy::newUserClient(task,security,type,client);\n"
    native_new = one(native_new, line, line +
                     "        enuma_bp_display_mark(status == kIOReturnSuccess ? ENUMA_DISPLAY_PARENT_OK : ENUMA_DISPLAY_PARENT_ERR);\n")
    line = "    displayObject->registerService();\n"
    backend_new = one(backend, line, line + "    enuma_bp_display_mark(ENUMA_DISPLAY_REGISTERED);\n")
    include = "#include <machine/machine_routines.h>\n"
    backend_new = one(backend_new, include, include + '#include "display-events.inc"\n')
    pstart = "bool native_legacy_prepare_scanout(const PE_Video *v) {\n"
    before = pstart + "    return displayObject && enuma_bp_gui_take(v);\n}\n"
    after = pstart + """    enuma_bp_display_mark(ENUMA_DISPLAY_PREPARE_ENTER);
    const bool prepared = displayObject && enuma_bp_gui_take(v);
    if (!prepared) enuma_bp_display_mark(ENUMA_DISPLAY_PREPARE_FALSE);
    return prepared;
}
"""
    backend_new = one(backend_new, before, after)
    sample_new = one(sample, '#include "proc-page.inc"\n',
                     '#include "proc-page.inc"\n#include "display-page.inc"\n')
    line = "\tstruct enuma_bp_proc_events proc_events;\n"
    sample_new = one(sample_new, line, """\tstruct enuma_bp_display_sample display_events;
\tenuma_bp_display_sample(&display_events);
""" + line)
    rows = excerpt(sample_new, "\tLINE(31,", "\tLINE(35,")
    sample_new = one(sample_new, rows, "\tpanel_display_events(page, &display_events);\n")
    patch = ""
    for name, old, new in ((native_name, native, native_new), (backend_name, backend, backend_new),
                           ("sample.inc", sample, sample_new)):
        (out / name).write_text(new)
        patch += "".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                                             fromfile="old/" + name, tofile="new/" + name))
    (out / "display-source.diff").write_text(patch)
    (out / "test-callbacks.inc").write_text(excerpt(native_new, vstart, vend) +
                                            excerpt(native_new, cstart, cend))
    (out / "test-prepare.inc").write_text(after)
    refresh = (out / "refresh.inc").read_text()
    (out / "test-refresh.inc").write_text(one(refresh, '__asm__ volatile("dsb st" ::: "memory");',
                                             "host_dsb();"))


def verify_object(out, abi, call):
    sys.path.insert(0, str(BASE / "kits/XnuPrelink"))
    from native_prelink import macho

    def symtab(raw):
        at = next(at for cmd, at, _ in macho(raw)["commands"] if cmd == 2)
        so, count, strings, _ = struct.unpack_from("<4I", raw, at + 8)
        entries = []
        for i in range(count):
            pos = so + i * 16
            idx, kind, _, _, value = struct.unpack_from("<IBBHQ", raw, pos)
            entries.append((raw[strings + idx:raw.index(b"\0", strings + idx)].decode(),
                            kind, value, pos))
        return entries

    def section(raw, name):
        return next(s for g in macho(raw)["segments"] for s in g["sections"] if s["name"] == name)

    raw = (out / "NativeLegacyDisplay.o").read_bytes()
    sym = symtab(raw)
    table, = (value for name, _, value, _ in sym if name == "__ZTV19NativeLegacyDisplay")
    sec = next(s for g in macho(raw)["segments"] for s in g["sections"]
               if s["va"] <= table < s["va"] + s["size"])
    at, count = struct.unpack_from("<II", raw, sec["command_offset"] + 56)
    relocs = {}
    for i in range(count):
        offset, bits = struct.unpack_from("<II", raw, at + i * 8)
        if bits >> 27 & 1 and not (bits >> 28) and bits >> 25 & 3 == 3:
            relocs[sec["va"] + offset] = sym[bits & 0xffffff][0]
    slots = [relocs.get(table + 16 + 8 * i) for i in range(358)]
    need(slots == abi["compiled_vtable_symbols"] and table + 16 + 358 * 8 not in relocs,
         "compiled subclass 358-slot layout drift")
    late_path = out / "NativeLegacyDisplay.late.o"
    late = bytearray(late_path.read_bytes())
    _, kind, _, pos = next(e for e in symtab(late) if e[0] == "__GLOBAL__sub_I_NativeLegacyDisplay.cpp")
    need(kind & 0x0f == 0x0e, "initializer object type changed")
    late[pos + 4] |= 1
    need(not any(s["name"] == "__mod_init_func" for g in macho(late)["segments"] for s in g["sections"]),
         "unexpected eager initializer")
    for old, new in ((raw, late),):
        a, b = section(old, "__text"), section(new, "__text")
        need(old[a["fileoff"]:a["fileoff"] + a["size"]] ==
             new[b["fileoff"]:b["fileoff"] + b["size"]], "late conversion altered text")
    late_path.write_bytes(late)
    for name, allowed in (("NativeLegacyDisplay.o", {"_enuma_bp_display_mark"}),
                          ("EnumaLegacyDisplay.o", set()), ("video_console.o", {"_enuma_bp_display_sample"})):
        def imports(path, tag):
            return {line.split()[-1] for line in call(tag, ["llvm-nm", "-u", path]).splitlines() if line.strip()}
        old = imports((R5 if name == "video_console.o" else DISPLAY) / name, "imports-old-" + name)
        new = imports(out / name, "imports-new-" + name)
        need(new - old == allowed, f"unexpected imports in {name}: {new - old}")
    (out / "compiled-slots.json").write_text(json.dumps(slots, indent=2) + "\n")


def verify_final(out, call):
    image = out / "embedded-kernel.macho"
    table = (out / "final-symbols.log").read_text()
    symbols = {line.split()[-1] for line in table.splitlines() if line.strip()}
    need(not re.search(r" _boot_progress_(?:bind|start|prepare_scanout|pulse_anchor)\b", table),
         "unexpected upstream framebuffer writer")
    collector = "_panel_sample" if "_panel_sample" in symbols else "_enuma_bp_refresh"
    client = "__ZN19NativeLegacyDisplay13newUserClientEP4taskPvjPP12IOUserClient"
    validate = "__ZN19NativeLegacyDisplay12validateSwapEPK25OriginalLegacySwapRequest"
    kick = "__ZN19NativeLegacyDisplay8kickOnceEv"
    register = "_native_legacy_display_late_probe"
    mark = "_enuma_bp_display_mark"
    sample = "_enuma_bp_display_sample"

    def dis(symbol):
        code = call("events" + symbol, ["llvm-objdump", "-d", "--disassemble-symbols=" + symbol, image])
        need(f"<{symbol}>:" in code, f"missing final body: {symbol}")
        return code

    def edges(code, target, count=1):
        found = list(re.finditer(r"\bb(?:l)?\s+[^\n]*<" + re.escape(target) + ">", code))
        need(len(found) == count, f"expected {count} final edges to {target}; got {len(found)}")
        return found

    for caller, target in (("_posix_spawn", "_enuma_bp_record_exec"),
                           ("___mac_execve", "_enuma_bp_record_exec"),
                           ("_proc_prepareexit", "_enuma_bp_record_exit"),
                           (collector, "_enuma_bp_proc_snapshot")):
        edges(dis(caller), target)
    code = dis(collector)
    read, = edges(code, sample)
    need(read.start() < code.index("<_ml_set_interrupts_enabled>") and
         "<_bsd_log_lock>" in code and "<_bsd_log_unlock>" in code,
         "display sample no longer before the interrupt window")
    if collector != "_enuma_bp_refresh":
        code = dis("_enuma_bp_refresh")
        collect, = edges(code, collector)
        need(collect.start() < code.index("<_ml_set_interrupts_enabled>"), "collector inside raster window")
    code = dis(kick)
    edges(code, "_native_legacy_prepare_scanout", 3)
    code = dis("_native_legacy_prepare_scanout")
    entry, failure = edges(code, mark, 2)
    take, = edges(code, "_enuma_bp_gui_take")
    need(entry.start() < take.start() < failure.start() and re.search(r"\bcbz\s", code),
         "prepare short circuit / false edge drift")
    code = dis(client)
    first, second = edges(code, mark, 2)
    parent = list(re.finditer(r"\bblr\s+x\d+", code))
    need(len(parent) == 1 and first.start() < parent[0].start() < second.start() and
         re.search(r"\bldr\s+x\d+, \[x\d+, #1144\]", code[:parent[0].start()]),
         "legacy4 parent slot 143 call/order drift")
    edges(code, "_native_legacy_client_enter")
    edges(code, "_native_legacy_client_observed")
    edges(dis(validate), mark, 2)
    code = dis(register)
    registered, = edges(code, mark)
    need(re.search(r"\bldr\s+x\d+, \[x\d+, #672\][^\n]*\n(?:[^\n]*\n){0,2}"
                   r"[^\n]*\bblr\s+x\d+", code[:registered.start()]),
         "registration observation not after original registerService slot 84")
    for function in (mark, sample):
        code = dis(function)
        need(not re.search(r"\b(?:bl|blr|ldaxr|stlxr|ldxr|stxr)\s", code), f"non-leaf atomic code: {function}")


def build(out):
    need(out.is_relative_to(DEVICE / "out") and out.parent == DEVICE / "out",
         "use a fresh directory directly under device out")
    originals = json.loads((R5 / "commands.json").read_text())
    archive_report = json.loads((DISPLAY / "result.json").read_text())
    files = (R5 / "link.filelist").read_text()
    tree = BASE / "out/enuma/ipados-17.7.11-21H461/enuma/tree"
    uefi = DEVICE.parent / "uefi-enuma"
    opts = SimpleNamespace(output=out, tree=tree, uefi=uefi,
        abi_image=tree.parent / "kernel/kernel.macho", abi_plan=tree.parent / "kernel/kernel.json",
        reference_payload=R5 / "payload.img", reference_boot_report=R5 / "boot.json",
        board=DEVICE / "out/ufs-sm8250-fp-20261124-r65/device",
        dtb=Path("/root/enuma-step10/inputs/enuma.dtb"),
        local=DEVICE / "out/ufs-sm8250-launchd-data-20261119-r1/self-check/packaging/local-build.toml",
        fd=uefi / "Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd")
    donor = Path(originals["prelink"]["argv"][originals["prelink"]["argv"].index("--prelinked") + 1])
    pins = {**{p: r6.digest(p) for p in map(Path, files.splitlines())}, **PINS}
    need(r6.digest(donor) == json.loads(opts.abi_plan.read_text())["original_sha256"], "prelink donor drift")

    def validate():
        for repo, pin in ((BASE, r6.BASE_PIN), (tree / ".cache/xnu-work", r6.SOURCE_PIN)):
            need(subprocess.check_output(["git", "-C", repo, "rev-parse", "HEAD"], text=True).strip() == pin,
                 f"unexpected HEAD: {repo}")
        for path, sha in pins.items():
            need(r6.digest(path) == sha, f"unexpected input digest: {path}")

    validate()
    out.mkdir()
    (out / "tmp").mkdir()
    commands = {}
    env = {**os.environ, **r6.linux_env(opts), "TMPDIR": str(out / "tmp"),
           "PYTHONDONTWRITEBYTECODE": "1"}
    env["PATH"] = "/home/wh1stl3/.local/bin:" + env["PATH"]
    host_env = {**os.environ, "TMPDIR": str(out / "tmp"), "PYTHONDONTWRITEBYTECODE": "1"}

    def call(tag, argv, cwd=out, environment=env):
        argv = list(map(str, argv))
        result = subprocess.run(argv, cwd=cwd, env=environment, text=True, capture_output=True)
        log = out / (tag + ".log")
        log.write_text(result.stdout + result.stderr)
        commands[tag] = {"argv": argv, "cwd": str(cwd), "exit": result.returncode}
        (out / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        need(result.returncode == 0, f"{tag} exit {result.returncode}; see {log}")
        return result.stdout

    def replay(tag, step, substitutions=(), extra=(), cwd=None):
        argv = step["argv"].copy()
        for old, new in substitutions:
            need(argv.count(str(old)) == 1, f"{tag}: missing or ambiguous argument {old}")
            argv[argv.index(str(old))] = str(new)
        call(tag, argv + list(extra), cwd or step["cwd"])

    for file in ("video_console.c", "page.h", "renderer.inc", "refresh.inc", "proc-events.h",
                 "proc-page.inc", "blit.inc", "bp-init.inc", "screen.inc", "pe.inc"):
        shutil.copyfile(R5 / file, out / file)
    for file in ("display-events.h", "display-events.inc", "display-page.inc"):
        shutil.copyfile(HERE / file, out / file)
    shutil.copytree(R5 / "reference", out / "reference")
    generate(out)
    replay("compile-video_console.o", originals["compile-video_console.o"],
           [(R5 / f, out / f) for f in ("video_console.c", "video_console.o")] +
           [(R5 / "reference", out / "reference")])
    for i, src, obj in ((2, "source/NativeLegacyDisplay.cpp", "NativeLegacyDisplay.o"),
                        (5, "EnumaLegacyDisplay.cpp", "EnumaLegacyDisplay.o")):
        replay("compile-" + obj, archive_report["commands"][i],
               [(DISPLAY / src, out / Path(src).name), (DISPLAY / obj, out / obj)],
               extra=("-iquote", DISPLAY / "source"))
    replay("late", archive_report["commands"][4],
           [(DISPLAY / f, out / f) for f in ("NativeLegacyDisplay.o", "NativeLegacyDisplay.late.o")], cwd=out)
    verify_object(out, archive_report["abi"], call)
    archive = "libEnumaGopLegacy.a"
    replay("archive", archive_report["commands"][6],
           [(DISPLAY / f, out / f) for f in (archive, "NativeLegacyDisplay.late.o", "EnumaLegacyDisplay.o")],
           cwd=out)
    need(call("archive-members", ["llvm-ar", "t", out / archive]) ==
         call("archive-members-r6", ["llvm-ar", "t", DISPLAY / archive]), "archive members drift")

    sanitizer = ["-Wall", "-Wextra", "-Werror", "-Wno-unused-function",
                 "-fsanitize=address,undefined", "-fno-pie", "-no-pie", "-pthread"]
    call("compile-display-test", ["c++", "-std=gnu++17", *sanitizer,
         "-I", out, "-I", out / "reference", "-I", R6_SRC, "-I", DISPLAY / "source",
         HERE / "test-display.cpp", "-o", out / "test-display"], environment=host_env)
    call("test-display", [out / "test-display"], environment=host_env)
    call("generate-reference", [sys.executable, WRAP / "reference.py", out])
    (out / "test-page-events.cpp").write_text('#include "display-events.inc"\n')
    call("compile-page-events", ["c++", "-std=gnu++17", "-fsanitize=address,undefined",
         "-fno-pie", "-c", out / "test-page-events.cpp", "-o", out / "test-page-events.o"], environment=host_env)
    (out / "test-page.c").write_text(r6.replace((WRAP / "test-page.c").read_text(),
        'assert(strstr(page.main[31].text, "unavailable"));',
        '''assert(strstr(page.main[31].text, "registered=0"));
	assert(strstr(page.main[34].text, "caller/BB unknown"));'''))
    call("compile-page", ["cc", "-std=gnu11", *sanitizer, "-I", out, "-I", out / "reference",
         "-I", R6_SRC, out / "test-page.c", WRAP / "test-reference.c", out / "test-page-events.o",
         "-o", out / "test-page"], environment=host_env)
    call("test-page", [out / "test-page"], environment=host_env)

    # Only this filelist member changes. The original proc objects are linked in place.
    (out / "link.filelist").write_text(r6.replace(files, f"{R5}/video_console.o\n", f"{out}/video_console.o\n"))
    replay("link", originals["link"], [(R5 / f, out / f) for f in ("link.filelist", "native.macho")] +
           [(f"-Wl,-map,{R5}/native-link.map", f"-Wl,-map,{out}/native-link.map"),
            (f"-Wl,-force_load,{DISPLAY}/{archive}", f"-Wl,-force_load,{out}/{archive}")])
    replay("prelink", originals["prelink"], [(R5 / f, out / f) for f in ("native.macho", "prelink.macho")])
    for name in ("native", "prelink"):
        need(not call(name + "-undefined", ["llvm-nm", "-u", out / (name + ".macho")]).strip(),
             f"{name}: unforeseen unresolved symbol")
    call("inspect-final", [sys.executable, R6_SRC / "build-enuma-gop-legacy.py",
         "--candidate", out / "prelink.macho", "--plan", out / "prelink.json", "--source", ABI_SOURCE,
         "--tree", tree, "--inspect", out / "final-abi.json", "--check-vtable", DISPLAY / "result.json"])
    abi = json.loads((out / "final-abi.json").read_text())
    old = json.loads((R5 / "final-abi.json").read_text())
    for key in ("checks", "pure", "family_text_sha256", "bindings", "compiled_slots_requalified",
                "field_instructions", "stride_units", "slots", "instance_bytes"):
        need(abi[key] == old[key], f"final ABI drift: {key}")
    need(len(abi["checks"]) == 31 and abi["compiled_slots_requalified"] == 358, "unexpected ABI gate size")
    r6.pack(opts, out / "prelink.macho", call)
    need((out / "embedded.toml").read_bytes() == (R5 / "embedded.toml").read_bytes(), "r5 config changed")
    verify_final(out, call)
    validate()
    (out / "display-events-verified.json").write_text(json.dumps(
        {"status": "self-checked", "boot_sha256": r6.digest(out / "boot.img"),
         "bytes": (out / "boot.img").stat().st_size, "hardware_tested": False,
         "pinned_inputs": {str(p): sha for p, sha in PINS.items()}}, indent=2) + "\n")


if __name__ == "__main__":
    build(Path(sys.argv[1]).resolve())
