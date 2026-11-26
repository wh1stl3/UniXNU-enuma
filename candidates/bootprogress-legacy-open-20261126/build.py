#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Extend the pinned enuma Legacy open r4 observation in an isolated host build."""
import argparse
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
SEED = "cf29ecd04e9d05cb894a3d4903ec6fc7908e5112"
METHODS = (
    ("is_io_connect_method_var_output", "VAR", "(selector, &args)"),
    ("is_io_connect_method", "SYNC", "( selector, &args )"),
    ("is_io_connect_async_method", "ASYNC", "( selector, &args )"),
)


def load(file, name):
    spec = importlib.util.spec_from_file_location(name, file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def one(text, old, new):
    need(text.count(old) == 1, f"non-unique source or argv anchor: {old!r}")
    return text.replace(old, new) if isinstance(text, str) else [
        new if token == old else token for token in text]


def iokit(text):
    start = "kern_return_t\nis_io_service_open_extended("
    text = one(text, start, '#include "iokit.inc"\n\n' + start)
    pos = text.index(start)
    end = text.index("/* Routine io_service_close */", pos)
    old = text[pos:end]
    part = one(old, "\tbool           disallowAccess = false;",
               "\tbool           disallowAccess = false;\n\tbool observedOpen = false;")
    call = "\t\tres = service->newUserClient( owningTask, (void *) owningTask,\n" \
           "\t\t    connect_type, propertiesDict, &client );"
    part = one(part, call, """\
		observedOpen = owningTask == current_task() &&
		    strcmp(service->getMetaClass()->getClassName(), "NativeLegacyDisplay") == 0 &&
		    enuma_legacy_open_claim(connect_type);
""" + call + "\n\t\tconst IOReturn originalOpenResult = res;")
    part = one(part, "\t\tif (res == kIOReturnSuccess) {\n\t\t\tif (!client->reserved)", """\
		if (observedOpen) {
			enuma_legacy_open_raw(originalOpenResult, res == kIOReturnSuccess ?
			    client->getMetaClass()->getClassName() : nullptr);
		}
		if (res == kIOReturnSuccess) {
			if (!client->reserved)""")
    part = one(part, "\t*result = res;\n\n\treturn err;", """\
	*result = res;

	if (observedOpen) {
		const uint64_t registry = err == KERN_SUCCESS && res == kIOReturnSuccess && client ?
		    client->getRegistryEntryID() : 0;
		enuma_legacy_open_final(err, res, client != nullptr, registry);
	}
	return err;""")
    text = text[:pos] + part + text[end:]
    for name, kind, args in METHODS:
        pos = text.index("\n" + name + "\n")
        end = text.index("\n}\n", pos)
        part = text[pos:end]
        anchor = "\tif (kIOReturnSuccess == ret) {\n\t\tret = client->callExternalMethod" + args + ";"
        need(part.index("->io_filter_applier(client,") < part.index(anchor), name)
        part = one(part, anchor, anchor.replace("\t\tret", f"\t\tenuma_legacy_method(client, selector, ENUMA_METHOD_{kind});\n\t\tret"))
        text = text[:pos] + part + text[end:]
    return text


def chain_iokit(text):
    text = one(text, '#include "iokit.inc"\n\n', '')
    text = one(text, "kern_return_t\nis_io_iterator_next(",
               '#include "iokit.inc"\n\nkern_return_t\nis_io_iterator_next(')

    def routine(start, end, old, new):
        nonlocal text
        a = text.index(start)
        b = text.index(end, a)
        text = text[:a] + one(text[a:b], old, new) + text[b:]

    routine("is_io_iterator_next(", "/* Routine io_iterator_reset */",
            "\t\t*object = obj;\n\t\tret = kIOReturnSuccess;",
            """\
		*object = obj;
		ret = kIOReturnSuccess;
		IOService *returned = OSDynamicCast(IOService, obj);
		if (enuma_chain_service(returned))
			enuma_chain_note(ENUMA_ITER_SERVICE, 0, true,
			    returned->getRegistryEntryID());""")
    routine("internal_io_service_add_notification(", "/* Routine io_service_add_notification */",
            "\t} while (false);", "\t\tenuma_chain_first_match(sym, dict, err);\n\t} while (false);")
    routine("is_io_registry_entry_from_path(", "is_io_registry_entry_from_path_ool(",
            "\t*registry_entry = entry;",
            "\t*registry_entry = entry;\n\tenuma_chain_dt(path, entry);")
    routine("is_io_registry_entry_from_path_ool(", "/* Routine io_registry_entry_in_plane */",
            "\t*result = res;", "\t*result = res;\n\tif (path[0])\n\t\tenuma_chain_dt(path, entry);")
    routine("is_io_service_open_extended(", "/* Routine io_service_close */",
            "\t\treturn kIOReturnNotPermitted;", """\
		if (enuma_chain_service(service))
			enuma_chain_note(ENUMA_OPEN_REJECT, ENUMA_REJECT_MAC, false,
			    service->getRegistryEntryID());
		return kIOReturnNotPermitted;""")
    routine("is_io_service_open_extended(", "/* Routine io_service_close */",
            "\t\t\treturn kIOReturnUnsupported;", """\
			if (enuma_chain_service(service))
				enuma_chain_note(ENUMA_OPEN_REJECT, ENUMA_REJECT_PROPERTIES, false,
				    service->getRegistryEntryID());
			return kIOReturnUnsupported;""")
    return one(text,
               'strcmp(service->getMetaClass()->getClassName(), "NativeLegacyDisplay") == 0 &&\n'
               '\t\t    enuma_legacy_open_claim(connect_type);',
               'enuma_chain_service(service) &&\n'
               '\t\t    enuma_legacy_open_claim(connect_type, service->getRegistryEntryID());')


def sample(text):
    text = one(text, '#include "run-state-page.inc"', '#include "run-state-page.inc"\n#include "page.inc"')
    text = one(text, "\tconst unsigned digitizer_seen", """\
	struct enuma_open_snapshot legacy = {0};
	enuma_legacy_open_read(&legacy);
	const unsigned digitizer_seen""")
    text = one(text, "uint64_t ticks, freq, tcr, ttbr0, ttbr1, sctlr, vct, cval, ctl, sampled_daif;",
               "uint64_t ticks, freq;")
    def cut(before, after, replacement=""):
        nonlocal text
        a = text.index(before)
        b = text.index(after, a + len(before))
        text = text[:a] + replacement + text[b:]
    cut("\tPANEL_MRS(tcr,", "\tLINE(5,")
    text = one(text, '\tLINE(12, PANEL_GREY, "PC samples unavailable");',
               "\tpanel_legacy_open(page, &legacy, proc_available ?\n"
               "\t    &proc_events.slot[ENUMA_BP_BACKBOARDD - 1].exec : NULL);")
    cut("\tpanel_proc_events(", "\tpanel_display_events(")
    text = one(text, '#include "proc-page.inc"\n', "")
    cut("\tLINE(35,", "\tLINE(41,")
    cut("\tPANEL_MRS(vct,", "#undef LINE",
        '\tLINE(43, PANEL_GREY, "XNU msgbuf dropped chars=%u", PANEL_LOAD(oslog_msgbuf_dropped_charcount));\n')
    text = one(text, "time=%us idle=%us IRQ=n/a monitor=%u lost=n/a root=%d procs=n/a free=%u",
               "time=%us idle=%us refresh=%u root=%d free=%u")
    return one(text, "time/idle unavailable IRQ=n/a monitor=%u root=%d procs=n/a free=%u",
               "time/idle unavailable refresh=%u root=%d free=%u")


def display_page(text):
    at = text.index('\tsnprintf(text, sizeof(text), "CLIENT caller/BB unknown')
    text = text[:at] + "}\n"
    for before, after in ((31, 9), (32, 10), (33, 15)):
        text = one(text, f"page->main[{before}]", f"page->main[{after}]")
    return text


def page_layout(text):
    text = one(text, "unsigned r = 24;", "enum { recent_rows = 8 };\n\tunsigned r = recent_rows;")
    text = one(text, "rows > r && r != 24", "rows > r && r != recent_rows")
    return one(text, "r < LOG_EXTRA ? &page->extra[r] : &page->main[17 + r - LOG_EXTRA]", "&page->extra[r]")


def verify(out, call):
    image = out / "embedded-kernel.macho"

    def dis(name, file=image, prefix="legacy"):
        result = call(prefix + "-" + name, ["llvm-objdump", "-d", "--disassemble-symbols=" + name, file])
        need(f"<{name}>:" in result, f"missing linked body: {name}")
        return result

    names = (out / "final-symbols.log").read_text()
    open_code = dis("_is_io_service_open_extended")
    for edge in ("claim", "raw", "final"):
        need(open_code.count(f"<_enuma_legacy_open_{edge}>") == 1, "open edge count: " + edge)
    # Actual XNU service vtable entry; distinct from the Legacy parent's
    # four-argument slot at 1144 that the inherited display gate checks.
    def slot_calls(code):
        return list(re.finditer(r"ldr\s+(x\d+), \[x\d+, #1120\]\n(?:[^\n]*\n){0,12}?[^\n]*\bblr\s+\1\b", code))
    orig = os.fspath(out.parent / "bootprogress-hid-event-20261126-r2/embedded-kernel.macho")
    before = dis("_is_io_service_open_extended", orig, "baseline")
    calls = slot_calls(open_code)
    need(len(slot_calls(before)) == len(calls) == 1, "five-argument slot #1120 call count drift")
    need(open_code.index("<_enuma_legacy_open_claim>") < calls[0].start() < calls[0].end() <
         open_code.index("<_enuma_legacy_open_raw>") < open_code.index("<_enuma_legacy_open_final>"),
         "open attempt/raw/final call order drift")
    for name, _, _ in METHODS:
        code = dis("_" + name)
        target = re.findall(r"<([^>]*enuma_legacy_method[^>]*)>", code)
        need(len(target) == 1 and code.count("callExternalMethod") == 1 and
             code.index(f"<{target[0]}>") < code.index("callExternalMethod"),
             f"{name}: dispatch observation is not unique/before external dispatch")
        # The original indirect applier returns its result in w0. Reject jumps
        # past BOTH calls; the zero result back-branches into the unlocked
        # common dispatch block.
        matches = re.findall(r"\bblr\s+x\d+\n(?:[^\n]*\bmov\s+x\d+, x0\n)?"
                             r"[^\n]*\bcbnz\s+w0, 0x([a-f0-9]+)[^\n]*\n"
                             r"[^\n]*\bb\s+0x([a-f0-9]+)", code)
        def address(fragment):
            return int(next(line.split(":")[0] for line in code.splitlines() if fragment in line), 16)
        hook = address(f"<{target[0]}>")
        dispatch = address("callExternalMethod")
        need(sum(hook - 20 <= int(ok, 16) < hook < dispatch < int(reject, 16)
                 for reject, ok in matches) == 1, f"{name}: missing filter success guard")
    helper = dis(target[0])
    need("getRegistryEntryID" in helper and "<_enuma_legacy_method_key>" in helper and
         "<_enuma_legacy_method_note>" in helper, "method key/getter edges missing")
    getter = dis("__ZN15IORegistryEntry18getRegistryEntryIDEv")
    need(not re.search(r"\bbl(?:r)?\s", getter) and re.search(r"\bldr\s+x", getter),
         "registry ID getter is not a load-only leaf")
    collector = "_panel_sample" if re.search(r"\b_panel_sample$", names, re.M) else "_enuma_bp_refresh"
    code = dis(collector)
    need(code.count("<_enuma_legacy_open_read>") == 1 and
         code.index("<_enuma_legacy_open_read>") < code.index("<_ml_set_interrupts_enabled>"),
         "reader does not run before interrupt/lease window")
    for name in ("claim", "method"):
        symbol = "_enuma_legacy_open_claim" if name == "claim" else "_enuma_legacy_method_note"
        code = dis(symbol)
        need("<_lck_spin_try_lock>" in code and "<_lck_spin_lock>" not in code and
             re.search(r"\b(?:cas|ldxr)\w*\s", code), f"{name}: trylock/CAS drift")
    need(1 <= open_code.count("<_enuma_chain_note>") <= 2, "missing original open-rejection observations")
    iterator = dis("_is_io_iterator_next")
    need(iterator.count("<_enuma_chain_note>") == 1 and "getRegistryEntryID" in iterator,
         "iterator returned-object edge missing")

    def helper(fragment):
        matches = [line.split()[-1] for line in names.splitlines()
                   if line.split() and fragment in line.split()[-1]]
        need(len(matches) == 1, f"expected one linked helper: {fragment}")
        return matches[0]

    dt = helper("enuma_chain_dt")
    for suffix in ("", "_ool"):
        code = dis("_is_io_registry_entry_from_path" + suffix)
        need(code.count(f"<{dt}>") == 1 and "fromPath" in code, f"DT inline edge {suffix}")
    need(1 <= dis(dt).count("<_enuma_chain_note>") <= 2, "DT parent/child outcome edges missing")
    first_match = helper("enuma_chain_first_match")
    notify = dis(helper("internal_io_service_add_notificationP"))
    # Clang duplicates the observer at the two original result blocks.
    branch = re.search(r"<[^>]*addMatchingNotification[^>]*>\n[^\n]*\bcbz\s+x0, 0x([a-f0-9]+)", notify)
    need(branch is not None and notify.count(f"<{first_match}>") == 2,
         "notification registration result split missing")
    fail_at = notify.index("\n" + branch[1] + ":")
    success, fail = notify[branch.end():fail_at], notify[fail_at:]
    need(re.search(r"\bmov\s+w2, #0\n[^\n]*<" + re.escape(first_match) + r">", success) and
         re.search(r"\bmov\s+w2, #711\n[^\n]*\bmovk\s+w2, #57344, lsl #16\n[^\n]*<" +
                   re.escape(first_match) + r">", fail),
         "notification success/unsupported result edges missing")
    need("<_enuma_chain_note>" in dis(first_match), "notification recorder edge missing")
    note = dis("_enuma_chain_note")
    need("<_lck_spin_try_lock>" in note and "<_lck_spin_lock>" not in note, "chain recorder blocks")


def build(device, out):
    need(out.parent == device / "out" and not out.exists(), "fresh direct device out required")
    r2 = device / "out/bootprogress-hid-event-20261126-r2"
    legacy = device / "out/bootprogress-legacy-open-20261126-r4"
    r6out = device / "out/bootprogress-full-link-20261125-r6"
    r9 = device / "out/bootprogress-run-state-20261126-r9"
    r4 = device / "out/bootprogress-display-events-20261126-r4"
    recipe = device / "candidates"
    run = load(recipe / "bootprogress-run-state-20261126/build.py", "run")
    r6 = run.r6
    hid_path = recipe / "bootprogress-hid-event-20261126/build.py"
    # The active worktree need not contain the prior local candidate branch.
    hid = SimpleNamespace(__file__=str(hid_path), __name__="hid")
    blob = subprocess.check_output(["git", "-C", device, "show", f"{SEED}:{hid_path.relative_to(device)}"])
    exec(compile(blob, str(hid_path), "exec"), vars(hid))
    tree = run.BASE / "out/enuma/ipados-17.7.11-21H461/enuma/tree"
    uefi = device.parent / "uefi-enuma"
    opts = SimpleNamespace(output=out, tree=tree, uefi=uefi,
        abi_image=tree.parent / "kernel/kernel.macho", abi_plan=tree.parent / "kernel/kernel.json",
        reference_payload=r2 / "payload.img", reference_boot_report=r2 / "boot.json",
        board=device / "out/ufs-sm8250-fp-20261124-r65/device",
        dtb=Path("/root/enuma-step10/inputs/enuma.dtb"),
        local=device / "out/ufs-sm8250-launchd-data-20261119-r1/self-check/packaging/local-build.toml",
        fd=uefi / "Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd")
    pins = {
        **run.PINS, **hid.PINS,
        legacy / "boot.img":"cd76efaa275bd07f834938d79d833e1d3d8e74eb84eaae1361134c6267a3dbf5",
        legacy / "IOUserClient.cpp":"3fe13a24f8fcf8decb5015148fa111bb718d8ede5f0c21f5bec5e4d03a799c05",
        legacy / "sample.inc":"55e04af45abc385bbfa4e6f65eb43a607a79e2923795e65b895a89d80cefb340",
        legacy / "embedded-kernel.macho":"1a24a9da79e4936ceb9ee0c5db03fb0867e22aabc15394223598012581c3179f",
        legacy / "payload.img":"bac5342b0bfe84d407b1758bf3383d133c82e19bbb2d66a0aa70ce258fa1e8b0",
        **{r2 / f: h for f,h in {
            "boot.img":"e278d568b7c59fb9dafffbfe3617159d6f062421ebbad5e4447703c9732f13eb",
            "commands.json":"3de369068d91287d49610a89c668d07fbd1f6e40fc4d77b3b32dba4c294a8b0c",
            "link.filelist":"5bc4f1c914d35cd3c2562279ab0c10a9bf1700c2735bf223767916802b86f683",
            "video_console.c":"81b4fe597a6ac4b1ace16be18e2e3d8934882bdb8aa6578324d25f747c419dc5",
            "renderer.inc":"4b688510bb15108460ba5c6d7a1a5bdc1d99537ff75657b40569102538766191",
            "sample.inc":"ebcb8bdb538c60dc80295962cf9106cc50c6a1af9e59ceeaaef99561e5c32ca7",
            "boot.json":"ff113c72c8643ab38eb7ab952a0e138445939960c7b7fcb2025113566c33e0d3",
            "payload.img":"94e49c67cff940c28822fb7a03b43fcc091c572dcb3f82fce1b3a3da30b377d1",
            "libShengHidInputStandin.a":"8861e7dc3cb8ca54fb80859bc71c32b00204402ba14b4f3805f2404ed58cee30",
            "final-abi.json":"a580dcea6a1cced775feaa4ef49e63ea1b9a9a8cb95df90e31e48253d7436f41",
            "embedded-kernel.macho":"4e8ed4eb2be36ed976c28f2960b350cf47dcb62c107b5211c68b85a4bae575c8",
        }.items()},
        r6out / "commands.json":"3db8dc9b874db9ca19a5559cd8db65d8305cd5b9128926b44324cb151af5dc24",
        r6out / "IOUserClient.cpp":"58e6266180a5443af42e10e85f7554a9b28728332c20ec4713eea2cf721c277b",
        r6out / "IOUserClient.cpo":"27a8ebd5c1ae6fa793d3e7d586666d9553f3145e2a58ff78750d57fa8e5252db",
        r9 / "kern_exec.c":"44fee9088e60d6f9224930e0f65641b860380f58017d4bc7c1bc5f5f5358954c",
        r9 / "EnumaBbScan.inc":"6b16c62594ead0290dd1819ac7f7780a4dbc2bfcd80108ddfc0556e198093ebe",
        r9 / "EnumaProcExecReport.inc":"8fed3318777527bedc9a6cb52e308d0ac6cdc2e45645ca55845184168046be72",
        r9 / "EnumaBootProgress2.inc":"665f4e9b910a4fc2ac2324a9460ad59008fa3a78feb57e5d6faa81ae3148d2d2",
        r9 / "proc-recorder.inc":"36cc18ac2e4e03c95eb132448121b30ae646273db909184b454ebb07e4e3a7ff",
        r9 / "proc-events.h":"2b702d29193af2eee09cfc27602db04f5bf321e2603e901fc7f7aa3c6b4217a6",
    }
    def git(repo, *args):
        return subprocess.check_output(["git", "-C", repo, *args], text=True).strip()
    def validate():
        for repo, pin in ((run.BASE, r6.BASE_PIN), (tree / ".cache/xnu-work", r6.SOURCE_PIN)):
            need(git(repo, "rev-parse", "HEAD") == pin, f"HEAD drift: {repo}")
        for path, expected in pins.items():
            need(r6.digest(path) == expected, f"input drift: {path}")
    def protected():
        names = git(device, "ls-files", "--others", "--exclude-standard", "-z").split("\0")
        return {p: r6.digest(device / p) for p in names if p}
    validate()
    before = protected()
    old = json.loads((r2 / "commands.json").read_text())
    out.mkdir()
    (out / "tmp").mkdir()
    env = {**os.environ, **r6.linux_env(opts), "TMPDIR": str(out / "tmp"), "PYTHONDONTWRITEBYTECODE":"1"}
    env["PATH"] = "/home/wh1stl3/.local/bin:" + env["PATH"]
    records = {}

    def call(tag, argv, cwd=out, host=False):
        argv = list(map(str, argv))
        proc = subprocess.run(argv, cwd=cwd, env=({**os.environ, "TMPDIR": env["TMPDIR"]} if host else env),
                              capture_output=True)
        log = out / (tag + ".log")
        log.write_bytes(proc.stdout + proc.stderr)
        records[tag] = dict(argv=argv, cwd=str(cwd), exit=proc.returncode)
        (out / "commands.json").write_text(json.dumps(records, indent=2) + "\n")
        need(proc.returncode == 0, f"{tag}: exit {proc.returncode}; see {log}")
        return proc.stdout.decode(errors="replace")

    def replay(tag, step, replacements, extra=()):
        argv = step["argv"]
        for a, b in replacements:
            argv = one(argv, str(a), str(b))
        call(tag, [*argv, *extra], out if step["cwd"] == str(r2) else step["cwd"])

    diffs = []
    def generate(original, transform):
        text = original.read_text()
        after = transform(text)
        diffs.extend(difflib.unified_diff(text.splitlines(True), after.splitlines(True),
                                          str(original), original.name))
        (out / original.name).write_text(after)

    for origin in (r9 / "kern_exec.c", r9 / "EnumaBbScan.inc", r9 / "EnumaBootProgress2.inc",
                   r2 / "video_console.c", r2 / "renderer.inc"):
        shutil.copyfile(origin, out / origin.name)
    need(iokit((r6out / "IOUserClient.cpp").read_text()) == (legacy / "IOUserClient.cpp").read_text(),
         "r4 IOKit generated source is not reproduced")
    generate(legacy / "IOUserClient.cpp", chain_iokit)
    generate(r9 / "EnumaProcExecReport.inc",
             lambda s: one(s, '#include "proc-recorder.inc"', '#include "proc-recorder.inc"\n#include "record.inc"'))
    need(sample((r2 / "sample.inc").read_text()) == (legacy / "sample.inc").read_text(),
         "r4 sample generated source is not reproduced")
    generate(legacy / "sample.inc", lambda s: one(s, "i = 0, r = 6", "i = 0, r = 18"))
    generate(r4 / "display-page.inc", display_page)
    generate(r4 / "page.h", page_layout)
    (out / "source.diff").write_text("".join(diffs))

    call("compile-host", ["/usr/bin/cc", "-std=gnu11", "-Wall", "-Wextra", "-Werror", "-pthread",
         "-fsanitize=address,undefined", "-fno-pie", "-no-pie", "-I", out, "-I", r9, "-I", r4,
         "-I", r4 / "reference", "-I", recipe / "bootprogress-20261125", HERE / "test.c", "-o", out / "test"], host=True)
    call("test-host", [out / "test"], host=True)

    files = (r2 / "link.filelist").read_text().splitlines()
    positions = ((238, r2, "video_console.c", "video_console.o", old, ()),
                 (585, r9, "kern_exec.c", "kern_exec.o", json.loads((r9 / "commands.json").read_text()),
                  ("-iquote", str(r9), "-H")),
                 (935, r6out, "IOUserClient.cpp", "IOUserClient.cpo",
                  json.loads((r6out / "commands.json").read_text()), ("-H",)))
    for line, base, source, obj, steps, extra in positions:
        need(files[line - 1] == str(base / obj) and files.count(str(base / obj)) == 1, "r2 filelist drift")
        name = "compile-" + obj
        replay(name, steps[name], [(base / n, out / n) for n in (source, obj)],
               extra + ("-iquote", str(HERE), f"-fmacro-prefix-map={out}={base}"))
        files[line - 1] = str(out / obj)
    for obj, includes in (("kern_exec.o", (out / "EnumaProcExecReport.inc", out / "EnumaBootProgress2.inc",
                                           r9 / "proc-recorder.inc", HERE / "record.inc")),
                          ("video_console.o", (out / "sample.inc", out / "display-page.inc", HERE / "page.inc",
                                               r4 / "refresh.inc", out / "page.h")),
                          ("IOUserClient.cpo", (HERE / "iokit.inc",))):
        log = (out / f"compile-{obj}.log").read_text()
        for path in includes:
            need(re.search(rf"^\.+ {re.escape(str(path))}$", log, re.M), f"wrong include: {path}")
    (out / "link.filelist").write_text("\n".join(files) + "\n")
    replay("link", old["link"], [(r2 / p, out / p) for p in ("link.filelist", "native.macho")] +
           [(f"-Wl,-map,{r2}/native-link.map", f"-Wl,-map,{out}/native-link.map")])
    link_map = (out / "native-link.map").read_bytes().splitlines()
    for _, base, _, obj, _, _ in positions:
        need(sum(line.endswith(("] " + str(out / obj)).encode()) for line in link_map) == 1 and
             not any(line.endswith(("] " + str(base / obj)).encode()) for line in link_map), f"link map: {obj}")
    argv = old["prelink"]["argv"]
    donor = Path(argv[argv.index("--prelinked") + 1])
    need(r6.digest(donor) == json.loads(opts.abi_plan.read_text())["original_sha256"], "donor drift")
    replay("prelink", old["prelink"], [(r2 / p, out / p) for p in ("native.macho", "prelink.macho")])
    for name in ("native", "prelink"):
        need(not call(name + "-undefined", ["llvm-nm", "-u", out / (name + ".macho")]).strip(),
             f"unexpected unresolved symbol: {name}")
    replay("inspect-final", old["inspect-final"],
           [(r2 / p, out / p) for p in ("prelink.macho", "prelink.json", "final-abi.json")])
    a, b = (json.loads((p / "final-abi.json").read_text()) for p in (r2, out))
    for k in ("checks", "pure", "family_text_sha256", "bindings", "compiled_slots_requalified",
              "field_instructions", "stride_units", "slots", "instance_bytes"):
        need(a[k] == b[k], f"display ABI drift: {k}")
    r6.pack(opts, out / "prelink.macho", call)
    need((out / "embedded.toml").read_bytes() == (r2 / "embedded.toml").read_bytes(), "r2 boot config drift")
    need((out / "embedded.toml").read_bytes() == (legacy / "embedded.toml").read_bytes(),
         "r4 boot config drift")
    run.display.verify_final(out, call)
    run.verify_run_state(out, call)
    hid.verify_hid(out, call)
    verify(out, call)
    validate()
    need(before == protected(), "active untracked inputs changed")
    size = (out / "boot.img").stat().st_size
    need(size == (legacy / "boot.img").stat().st_size and size < 201326592, "boot_b budget drift")
    (out / "display-chain-verified.json").write_text(json.dumps({
        "status": "self-checked", "sha256": r6.digest(out / "boot.img"), "device_tested": False,
        "untracked_before_after": before, "bytes": size,
        "boot_b_budget": 201326592, "boot_b_remaining": 201326592 - size,
        "embedded_kernel_sha256": r6.digest(out / "embedded-kernel.macho"),
    }, indent=2) + "\n")


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("output", type=Path)
    cli.add_argument("--device", type=Path, default=HERE.parents[1])
    ns = cli.parse_args()
    build(ns.device.resolve(), ns.output.resolve())
