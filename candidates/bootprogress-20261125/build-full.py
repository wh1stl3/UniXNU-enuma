#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Prepare a separate enuma full-screen candidate using explicit local inputs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tomllib
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
DEVICE = HERE.parents[1]
BASE = DEVICE.parents[1] / "UniXNU"
BASE_PIN = "693f5d9cae8a408dd18b39f3f9fdc4228c934241"
SOURCE_PIN = "d8b80295118ef25ac3a784134bcf95cd8e88109f"
sys.path.insert(0, str(BASE / "scripts"))
sys.dont_write_bytecode = True
from unixnu.kernel import linux_env


def replace(text, old, new):
    if text.count(old) != 1:
        raise ValueError("expected one source site: " + old)
    return text.replace(old, new)


def blit_source(text):
    start = text.index("static void\nvc_blit_rect(")
    end = text.index("\nstatic void\nvc_blit_rect_8(", start)
    original = text[start:end]
    signature = original[:original.index("\n{")]
    leased = signature.replace("static void\nvc_blit_rect(", "static __attribute__((noinline)) bool\nvc_blit_rect_leased(")
    leased = replace(leased, "unsigned int flags)", "unsigned int flags, const struct enuma_bp_vc_lease *lease)")
    dispatch = original[original.index("\tswitch (vinfo.v_depth)"):]
    dispatch = replace(dispatch, "(unsigned char *) backBuffer, flags );\n\t\t}\n\t\tbreak;",
                       "(unsigned char *) backBuffer, flags );\n\t\t\treturn true;\n\t\t}\n\t\treturn false;")
    if dispatch.count("\t\tbreak;") != 3:
        raise ValueError("blit dispatch changed")
    dispatch = dispatch.replace("\t\tbreak;", "\t\treturn true;")
    dispatch = replace(dispatch, "\n\t}\n}", "\n\t}\n\treturn false;\n}")
    guards = """
{
	if (!lease->counted || x < 0 || y < 0 || width <= 0 || height <= 0 ||
	    (unsigned)x > vinfo.v_width || (unsigned)width > vinfo.v_width - (unsigned)x ||
	    (unsigned)y > vinfo.v_height || (unsigned)height > vinfo.v_height - (unsigned)y)
		return false;
"""
    wrapper = signature + """
{
	ENUMA_BP_VC_OR_RETURN();
	(void)vc_blit_rect_leased(x, y, bx, width, height, sourceWidth, sourceHeight,
	    sourceRow, backRow, dataPtr, backBuffer, flags, &bp_lease);
}
"""
    text = text[:start] + leased + guards + dispatch + "\n" + wrapper + text[end:]
    # These store-only leaves are private to the dispatcher. A caller which
    # already owns a lease may finish while a transition is draining it.
    for depth in (8, 16, 30, 32):
        if len(re.findall(rf"\bvc_blit_rect_{depth}\b", text)) != 3:
            raise ValueError(f"unexpected blit writer caller: {depth}")
    return text


def vc_source(text):
    text = replace(text, '#include "iso_font.c"', '#include "iso_font.c"\n#include "renderer.inc"')
    # Actual pixel-writing leaves, including the LZSS no-root icon which
    # writes independently of vcputc and the ordinary blit dispatcher.
    leaves = ("vc_clear_screen", "vc_paint_char_8", "vc_paint_char_16",
              "vc_paint_char_32", "vc_reverse_cursor", "vc_scroll_down",
              "vc_scroll_up", "vc_display_icon", "vc_display_lzss_icon")
    for leaf in leaves:
        start = text.index("\n" + leaf + "(")
        body = text.index("\n{", start)
        if text.index(")", start) > body:
            raise ValueError(leaf)
        result = "-1" if leaf == "vc_display_lzss_icon" else ""
        text = text[:body + 2] + f"\n\tENUMA_BP_VC_OR_RETURN({result});" + text[body + 2:]
    text = blit_source(text)
    text = replace(text, "\t\tif (gc_enabled) {\n\t\t\tgc_hide_cursor(gc_x, gc_y);",
                   """		struct enuma_bp_vc_lease lease __attribute__((cleanup(enuma_bp_vc_end))) = {0};
		if (gc_enabled && (lease.counted = enuma_bp_vc_enter())) {
			gc_hide_cursor(gc_x, gc_y);""")
    text = replace(text, "\t\tif (!ep_console_can_write(&enuma_pid1_console, gc_enabled) ||",
                   """		struct enuma_bp_vc_lease lease __attribute__((cleanup(enuma_bp_vc_end))) = {enuma_bp_vc_enter()};
		if (!lease.counted || !ep_console_can_write(&enuma_pid1_console, gc_enabled) ||""")
    text = replace(text, "\tif (vc_progress_enable) {\n\t\tdo {\n\t\t\tvc_progress_count++;",
                   """	if (vc_progress_enable) {
		do {
			struct enuma_bp_vc_lease lease __attribute__((cleanup(enuma_bp_vc_end))) = {enuma_bp_vc_enter()};
			if (!lease.counted) {
				clock_deadline_for_periodic_event(vc_progress_interval, mach_absolute_time(), &vc_progress_deadline);
				thread_call_enter_delayed(&vc_progress_call, vc_progress_deadline);
				break;
			}
			vc_progress_count++;""")
    text = replace(text, "\t\t\tvc_blit_rect( x, y, 0,\n\t\t\t    width,", "\t\t\tif (vc_blit_rect_leased(x, y, 0,\n\t\t\t    width,")
    anchor = "\t\t\t    | (vc_needsave ? kSave : 0));\n\t\t\tvc_needsave = FALSE;"
    text = replace(text, anchor, """			    | (vc_needsave ? kSave : 0), &lease))
				vc_needsave = FALSE;
			enuma_bp_vc_end(&lease);
			lease.counted = 0;""")
    anchor = "void\ninitialize_screen(PE_Video * boot_vinfo, unsigned int op)\n{"
    text = replace(text, anchor, """static int
enuma_bp_screen_begin(bool attach_bootstrap)
{
	/* No VCPUTC/progress lock held here. Runtime IRQ or preemption-disabled
	 * callers refuse before ep notifications, mapping edits, or any wait. */
	bool waitable = vm_initialized && enuma_bp_waitable();
	if ((vm_initialized && !waitable && !attach_bootstrap) ||
	    !bp_transition_begin(&enuma_bp_gate, waitable))
		return EBUSY;
	bp_transition_drain(&enuma_bp_gate, enuma_bp_wait, NULL);
	return 0;
}

static int
enuma_bp_screen_apply(PE_Video *boot_vinfo, unsigned int op, bool stop, bool gui)
{
""")
    anchor = "\t\t/* Update the vinfo structure atomically"
    text = replace(text, anchor, """		if (ep_first_mapping && ep_boot_owned && boot_vinfo->v_offset < newMapSize) {
			const struct bp_framebuffer fb = {
				(volatile unsigned char *)new_vinfo.v_baseaddr,
				newMapSize - boot_vinfo->v_offset, new_vinfo.v_width,
				new_vinfo.v_height, new_vinfo.v_rowbytes
			};
			/* DarwinBootVideoFromGop rejects every other GOP pixel format.
			 * Only the initial boot_args Video populated by that path binds. */
			const boot_args *args = (const boot_args *)PE_state.bootArgs;
			enuma_bp_initial_mapping(&fb, args && args->Video.v_display == 1 &&
			    args->Video.v_depth == 32 &&
			    strcmp(boot_vinfo->v_pixelFormat, "BBBBBBBBGGGGGGGGRRRRRRRR") == 0 &&
			    args->Video.v_baseAddr == new_vinfo.v_physaddr);
		}
""" + anchor)
    anchor = "\tgraphics_now = gc_graphics_boot && !gc_desire_text;"
    text = replace(text, anchor, """	/* Old mapping is retired. Only the transition's own synchronous stock
	 * clear/cursor calls can use the new VC mapping before publication. */
	if (vm_initialized && !gui && op != kPEReleaseScreen && op != kPEDisableScreen &&
	    (stop || !(__atomic_load_n(&enuma_bp_gate.state, __ATOMIC_ACQUIRE) & BP_ACTIVE)))
		__atomic_store_n(&enuma_bp_vc_owner, current_thread(), __ATOMIC_RELEASE);
""" + anchor)
    tail = "\n}\n\nvoid vcattach(void);"
    text = replace(text, tail, """
	__atomic_store_n(&enuma_bp_vc_owner, THREAD_NULL, __ATOMIC_RELEASE);
	return op == kPEReleaseScreen || op == kPEDisableScreen ? stop || gui :
	    op == kPEAcquireScreen || op == kPEEnableScreen || op == kPETextScreen ? 0 : -1;
}

typedef void (*enuma_screen_hook)(PE_Video *, unsigned int);
static void
enuma_bp_screen_reserved(PE_Video *info, unsigned int op, bool attach_bootstrap, bool gui,
    enuma_screen_hook before, enuma_screen_hook after)
{
	if (before)
		before(info, op);
	bool stop = (info || (op == kPEReleaseScreen && !attach_bootstrap) ||
	    op == kPEDisableScreen) &&
	    __atomic_load_n(&enuma_bp_mode, __ATOMIC_ACQUIRE) == 2;
	int paused = enuma_bp_screen_apply(info, op, stop, gui);
	if (after)
		after(info, op);
	bp_transition_finish(&enuma_bp_gate, stop, gui, paused);
}

static __attribute__((noinline)) int
enuma_bp_screen(PE_Video *info, unsigned int op, bool attach_bootstrap, bool gui)
{
	if (!gui) {
		int error = enuma_bp_screen_begin(attach_bootstrap);
		if (error)
			return error;
	}
	enuma_bp_screen_reserved(info, op, attach_bootstrap, gui, NULL, NULL);
	return 0;
}

extern int enuma_bp_pe_screen(PE_Video *, unsigned int, enuma_screen_hook, enuma_screen_hook);
int
enuma_bp_pe_screen(PE_Video *info, unsigned int op,
    enuma_screen_hook before, enuma_screen_hook after)
{
	int error = enuma_bp_screen_begin(false);
	if (error)
		return error;
	enuma_bp_screen_reserved(info, op, false, false, before, after);
	return 0;
}

void
initialize_screen(PE_Video *info, unsigned int op)
{
	/* Startup's void text/acquire requests are best-effort; no replay or BP
	 * start follows here. PE uses its status-returning transaction above. */
	(void)enuma_bp_screen(info, op, false, false);
}

extern bool enuma_bp_gui_take(const PE_Video *);
bool
enuma_bp_gui_take(const PE_Video *video)
{
	int reservation = bp_gui_begin(&enuma_bp_gate, vm_initialized && enuma_bp_waitable());
	if (reservation != BP_GUI_PENDING)
		return reservation == BP_GUI_OWNED;
	bp_transition_drain(&enuma_bp_gate, enuma_bp_wait, NULL);
	uint32_t state = __atomic_load_n(&enuma_bp_gate.state, __ATOMIC_ACQUIRE);
	if ((state & BP_PANIC) || vinfo.v_physaddr != video->v_baseAddr ||
	    vinfo.v_width != video->v_width || vinfo.v_height != video->v_height ||
	    vinfo.v_rowbytes != video->v_rowBytes || vinfo.v_depth != 32 || vinfo.v_rotate) {
		bp_transition_finish(&enuma_bp_gate, false, false, -1);
		return false;
	}
	/* The stock kPEReleaseScreen switch and ep leave run before ownership
	 * publication; serial-routing policy is not a pixel release signal. */
	return enuma_bp_screen(NULL, kPEReleaseScreen, false, true) == 0 &&
	    !(__atomic_load_n(&enuma_bp_gate.state, __ATOMIC_ACQUIRE) & BP_PANIC);
}

void vcattach(void);""")
    text = replace(text, "\t\tif (gc_acquired) {\n\t\t\tinitialize_screen(NULL, kPEReleaseScreen);\n\t\t}",
                   """		if (gc_acquired && enuma_bp_screen(NULL, kPEReleaseScreen, true, false))
			return;""")
    text = replace(text, "\t\tinitialize_screen(NULL, kPEAcquireScreen);",
                   """		if (enuma_bp_screen(NULL, kPEAcquireScreen, true, false))
			return;""")
    tail = "\n}\n\n#if defined(XNU_TARGET_OS_OSX)\n\n// redraw progress meter"
    return replace(text, tail, "\n\tenuma_bp_start();" + tail)


def pe_source(text):
    start = text.index("int\nPE_initialize_console(PE_Video * info, int op)\n{")
    end = text.index("\nvoid\nPE_init_iokit(void)", start)
    original = text[start:end]
    scale = original[original.index("\tif (info &&"):original.index("\n\tswitch (op)")]
    release = original[original.index("\tcase kPEReleaseScreen:"):original.index("\n\tdefault:")]
    release = replace(release, "\tcase kPEReleaseScreen:", "\tif (op == kPEReleaseScreen) {")
    release = replace(release, "\t\tinitialize_screen(info, op);\n\t\tbreak;", "\t}")
    routing = original[original.index("\tswitch (op)"):original.index("\tcase kPEReleaseScreen:")]
    if routing.count("\t\tinitialize_screen(info, op);\n") != 2:
        raise ValueError("PE routing dispatch changed")
    routing = routing.replace("\t\tinitialize_screen(info, op);\n", "")
    return text[:start] + """typedef void (*enuma_screen_hook)(PE_Video *, unsigned int);
extern int enuma_bp_pe_screen(PE_Video *, unsigned int, enuma_screen_hook, enuma_screen_hook);

static void
enuma_pe_before(PE_Video *info, unsigned int op)
{
""" + scale + "\n" + release + """}

static void
enuma_pe_after(PE_Video *info, unsigned int op)
{
	static int last_console = -1;

""" + routing + """	default:
		break;
	}
}

int
PE_initialize_console(PE_Video *info, int op)
{
	return enuma_bp_pe_screen(info, op, enuma_pe_before, enuma_pe_after);
}
""" + text[end:]


def digest(path):
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ("tree", "abi-image", "abi-plan", "display-source", "link-record",
                 "kernel-source", "output"):
        cli.add_argument("--" + name, required=True, type=Path)
    cli.add_argument("--compile-only", action="store_true")
    for name in ("reference-payload", "reference-boot-report", "board", "local",
                 "uefi", "fd", "dtb"):
        cli.add_argument("--" + name, type=Path)
    opts = cli.parse_args()
    for key, value in vars(opts).items():
        if isinstance(value, Path):
            setattr(opts, key, value.resolve())
    out = opts.output
    if not out.is_relative_to(DEVICE / "out") or out.exists():
        raise ValueError("fresh output under ignored device out required")
    for repo, pin in ((BASE, BASE_PIN), (opts.tree / ".cache/xnu-work", SOURCE_PIN)):
        actual = subprocess.check_output(["git", "-C", repo, "rev-parse", "HEAD"], text=True).strip()
        if actual != pin:
            raise ValueError(f"{repo}: {actual} != {pin}")
    out.mkdir(parents=True)
    (out / "tmp").mkdir()
    env = {**os.environ, **linux_env(SimpleNamespace(tree=opts.tree)), "TMPDIR": str(out / "tmp"),
           "PYTHONDONTWRITEBYTECODE": "1"}
    env["PATH"] = "/home/wh1stl3/.local/bin:" + env["PATH"]
    commands = {}

    def call(tag, command, cwd=out, environment=env):
        argv = list(map(str, command))
        proc = subprocess.run(argv, cwd=cwd, env=environment, capture_output=True, text=True)
        (out / (tag + ".log")).write_text(proc.stdout + proc.stderr)
        commands[tag] = {"argv": argv, "cwd": str(cwd), "exit": proc.returncode}
        (out / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        proc.check_returncode()
        return proc.stdout

    obj = opts.tree / "build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837"
    xnu = opts.tree / ".cache/xnu-work"
    locations = {
        "video_console.o": ("osfmk", "osfmk/console/video_console.c"),
        "debug.o": ("osfmk", "osfmk/kern/debug.c"),
        "pe_init.o": ("pexpert", "pexpert/arm/pe_init.c"),
        "bsd_init.o": ("bsd", "bsd/kern/bsd_init.c"),
        "IOUserClient.cpo": ("iokit", "iokit/Kernel/IOUserClient.cpp"),
    }
    for name, (area, relative) in locations.items():
        record = json.loads((obj / area / "DEVELOPMENT" / (name + ".json"))
                            .read_text().strip().rstrip(","))
        src = xnu / relative
        alternate = opts.kernel_source / relative
        if name in ("bsd_init.o", "IOUserClient.cpo") and alternate.is_file():
            src = alternate
        text = src.read_text()
        if name == "video_console.o":
            text = vc_source(text)
        elif name == "debug.o":
            before = "\t/* call machine-layer panic handler */"
            text = replace(text, before, "\textern void enuma_bp_panic(void);\n\tenuma_bp_panic();\n\n" + before)
        elif name == "pe_init.o":
            text = pe_source(text)
        elif name == "bsd_init.o":
            before = "bsd_init(void)\n{"
            text = replace(text, before, before + "\n\textern void enuma_bp_checkpoint(unsigned);\n"
                           "\tenuma_bp_checkpoint(1);")
            before = "\tload_init_program(p);"
            text = replace(text, before, "\textern void enuma_bp_checkpoint(unsigned);\n"
                           "\tenuma_bp_checkpoint(2);\n" + before)
        new = out / src.name
        new.write_text(text)
        args = record["arguments"].copy()
        args[args.index(record["file"])] = str(new)
        args[args.index("-o") + 1] = str(out / name)
        for flag in ("-MF", "-MT", "-MJ"):
            if flag in args:
                at = args.index(flag)
                del args[at:at + 2]
        for i in range(len(args) - 1, 0, -1):
            if args[i].startswith(("-DXNU_NATIVE_LEGACY_DISPLAY=", "XNU_NATIVE_LEGACY_DISPLAY=")):
                del args[i - (args[i - 1] == "-D"):i + 1]
        args += ["-DXNU_NATIVE_LEGACY_DISPLAY=1", "-I", str(HERE), "-iquote", str(src.parent)]
        call("compile-" + name, args, record["directory"])
    call("build-display", [sys.executable, HERE / "build-enuma-gop-legacy.py", "--handoff",
                           "--candidate", opts.abi_image, "--plan", opts.abi_plan,
                           "--source", opts.display_source, "--tree", opts.tree,
                           "--output", out / "display"])
    host_test = out / "test-framebuffer"
    host_cc = shutil.which("cc", path=os.environ["PATH"])
    if host_cc is None:
        raise ValueError("host cc is required for framebuffer tests")
    host_env = {**os.environ, "TMPDIR": str(out / "tmp")}
    call("compile-host", [host_cc, "-std=c11", "-Wall", "-Wextra", "-Werror", "-pthread",
                           "-fsanitize=address,undefined", "-fno-pie", "-no-pie",
                           "-DENUMA_BP_LEGACY_LAYOUT", "-I", out / "display/source",
                           HERE / "test-framebuffer.c", "-o", host_test], environment=host_env)
    call("test-host", [host_test], environment=host_env)
    call("extract-screen-test", [sys.executable, HERE / "test-generated.py", out])
    screen_test = out / "test-screen"
    call("compile-screen-test", [host_cc, "-std=gnu11", "-Wall", "-Wextra", "-Werror",
                                  "-fsanitize=address,undefined", "-fno-pie", "-no-pie",
                                  "-I", out, HERE / "test-screen.c", "-o", screen_test],
         environment=host_env)
    call("test-screen", [screen_test], environment=host_env)
    if opts.compile_only:
        return
    recipe = json.loads(opts.link_record.read_text())
    step = recipe["link"]
    args = step["argv"].copy()
    files = Path(args[args.index("-filelist") + 1]).read_text().splitlines()
    for name in locations:
        if sum(Path(p).name == name for p in files) != 1:
            raise ValueError(f"wrong number of callers in link filelist: {name}")
    filelist = out / "link.filelist"
    filelist.write_text("".join(str(out / Path(p).name if Path(p).name in locations else p) + "\n"
                               for p in files))
    args[args.index("-filelist") + 1] = str(filelist)
    native = out / "native.macho"
    args[args.index("-o") + 1] = str(native)
    archive = [i for i, arg in enumerate(args) if arg.endswith("/libEnumaGopLegacy.a")]
    if len(archive) != 1:
        raise ValueError("expected one baseline legacy display archive")
    args[archive[0]] = "-Wl,-force_load," + str(out / "display/libEnumaGopLegacy.a")
    args = [f"-Wl,-map,{out / 'native-link.map'}" if a.startswith("-Wl,-map,") else a for a in args]
    call("link", args, step["cwd"])
    if call("native-undefined", ["llvm-nm", "-u", native]).strip():
        raise ValueError("undefined symbols in native")
    prelink = out / "prelink.macho"
    args = recipe["prelink"]["argv"].copy()
    original = Path(args[args.index("--prelinked") + 1])
    plan = json.loads(opts.abi_plan.read_text())
    if digest(original) != plan["original_sha256"]:
        raise ValueError("prelink donor differs from ABI donor")
    args[:2] = [sys.executable, str(BASE / "kits/XnuPrelink/emit_prelink.py")]
    args[args.index("--kernel") + 1] = str(native)
    args[args.index("--output") + 1] = str(prelink)
    call("prelink", args)
    if call("prelink-undefined", ["llvm-nm", "-u", prelink]).strip():
        raise ValueError("undefined symbols in final prelink")
    call("inspect-final", [sys.executable, HERE / "build-enuma-gop-legacy.py",
                           "--candidate", prelink, "--plan", prelink.with_suffix(".json"),
                           "--source", opts.display_source, "--tree", opts.tree,
                           "--inspect", out / "final-abi.json",
                           "--check-vtable", out / "display/result.json"])
    qualified = json.loads((out / "display/result.json").read_text())["abi"]
    final = json.loads((out / "final-abi.json").read_text())
    for key in ("checks", "pure", "family_text_sha256"):
        if qualified[key] != final[key]:
            raise ValueError(f"linked ABI drift: {key}")
    if any(qualified["bindings"][key] != va for key, va in final["bindings"].items()):
        raise ValueError("linked absolute binding drift")
    if opts.reference_payload is not None:
        pack(opts, prelink, call)
    else:
        verify_edges(prelink, call)


def verify_edges(kernel, call):
    table = call("final-symbols", ["llvm-nm", kernel])
    names = [line.split()[-1] for line in table.splitlines() if line.strip()]
    kick, = [name for name in names if "NativeLegacyDisplay8kickOnceEv" in name
             and name.startswith("__ZN")]
    half, = [name for name in names if name.startswith("__ZL15convertHalfRows")]
    row, = [name for name in names if name.startswith("_enuma_bp_refresh") and "." not in name]
    for caller, targets in (
        ("_native_legacy_prepare_scanout", ("_enuma_bp_gui_take",)),
        ("_panic_trap_to_debugger", ("_enuma_bp_panic",)),
        ("_bsd_init", ("_enuma_bp_checkpoint",)),
        ("_bsdinit_task", ("_enuma_bp_checkpoint", "_load_init_program")),
        ("_PE_initialize_console", ("_enuma_bp_pe_screen",)),
        ("_PE_init_printf", ("_vcattach",)),
        ("_kernel_bootstrap_thread", ("_PE_init_iokit", "_initialize_screen", "_vm_commpage_init")),
        ("_initialize_screen", ("_enuma_bp_screen",)),
        ("_vcattach", ("_enuma_bp_screen", "_thread_call_setup_with_options", "_thread_call_enter")),
        ("_vc_progress_task", ("_vc_blit_rect_leased",)),
        (row, ("_thread_call_enter_delayed",)),
        (kick, ("_enuma_bp_scanout_context", "_native_legacy_prepare_scanout", half,
                "native_legacy_fill_pixels", "native_legacy_copy_pixels", "native_legacy_copy_diff")),
    ):
        dis = call("calls" + caller, ["llvm-objdump", "-d", "--disassemble-symbols=" + caller, kernel])
        for target in targets:
            pattern = r"\bb(?:l)?\s+[^\n]*<[^>]*" + re.escape(target) + r"[^>]*>"
            if not re.search(pattern, dis):
                raise ValueError(f"missing final edge {caller} -> {target}")
        if caller == kick and len(re.findall(r"\bbl\s+[^\n]*<_native_legacy_prepare_scanout>", dis)) < 3:
            raise ValueError("blank, half and BGRA paths must each call pixel release")


def pack(opts, prelink, call):
    from unixnu import bootimg, payload as payload_step
    from unixnu.cli import parser
    from unixnu.config import Context

    out = opts.output
    image = out / "payload.img"
    shutil.copyfile(opts.reference_payload, image)
    path = "::/EFI/UniXNU/"
    original = opts.reference_payload

    def extract(source, member, dst):
        call("read-" + dst.name, ["mcopy", "-i", source, path + member, dst])
        return dst

    members_before = call("members-before", ["mdir", "-b", "-s", "-i", original, path])
    old = extract(original, "unixnu.toml", out / "reference.toml").read_text()
    parsed = tomllib.loads(old)
    entry, = [e for e in parsed["entry"] if e["type"] == "xnu"]
    kargs = [arg for arg in entry["args"].split() if not arg.startswith(("enuma-bp=", "boot-progress="))]
    kargs.append("boot-progress=2")
    # Keep all unrelated payload entries and fields byte-for-byte unchanged.
    config = replace(old, 'args = "' + entry["args"] + '"', 'args = "' + " ".join(kargs) + '"')
    config_path = out / "unixnu.toml"
    config_path.write_text(config)
    os.utime(prelink, (payload_step.EPOCH, payload_step.EPOCH))
    os.utime(config_path, (payload_step.EPOCH, payload_step.EPOCH))
    for member, src in ((entry["path"], prelink), ("unixnu.toml", config_path)):
        call("write-" + src.name, ["env", "MTOOLS_SKIP_CHECK=1", "TZ=UTC", "mcopy",
                                    "-o", "-m", "-i", image, src, path + member])
    members_after = call("members-after", ["mdir", "-b", "-s", "-i", image, path])
    if sorted(members_before.splitlines()) != sorted(members_after.splitlines()):
        raise ValueError("payload member list changed")
    if extract(image, "unixnu.toml", out / "payload.toml").read_text() != config:
        raise ValueError("payload args differ")
    if digest(extract(image, entry["path"], out / "payload-kernel.macho")) != digest(prelink):
        raise ValueError("payload kernel differs")
    for i, line in enumerate(members_before.splitlines()):
        if not line.lower().startswith(path.lower()) or line.endswith("/"):
            continue
        member = line[len(path):]
        if member in ("unixnu.toml", entry["path"]):
            continue
        a = extract(original, member, out / "tmp" / f"before-{i}")
        b = extract(image, member, out / "tmp" / f"after-{i}")
        if digest(a) != digest(b):
            raise ValueError(f"unrelated payload member changed: {member}")
    ref = json.loads(opts.reference_boot_report.read_text())
    for name, p in (("fd", opts.fd), ("dtb", opts.dtb)):
        if digest(p) != ref[name + "_sha256"]:
            raise ValueError("reference " + name + " differs")
    ctx = Context(parser().parse_args(["bootimg", "-D", str(opts.board), "--out", str(out / "work"),
        "--config", str(opts.local), "--local-module", "soc:sm8250=" + str(DEVICE.parent / "UniXNU-sm8250-common")]))
    boot = out / "boot.img"
    bootimg.build(ctx, opts.uefi, opts.fd, opts.dtb, image, boot)
    report = json.loads((out / "boot.json").read_text())
    if report["kernel_sha256"] != ref["kernel_sha256"]:
        raise ValueError("boot firmware/DTB bytes drift")
    embedded = out / "embedded-payload.img"
    with boot.open("rb") as source, embedded.open("xb") as target:
        head = source.read(2048)
        if head[:8] != b"ANDROID!" or struct.unpack_from("<I", head, 40)[0] != 1:
            raise ValueError("expected Android v1 header")
        kernel_size, ramdisk_size, page = (struct.unpack_from("<I", head, i)[0] for i in (8, 16, 36))
        if not page or ramdisk_size != image.stat().st_size:
            raise ValueError("embedded payload extent mismatch")
        source.seek(page * (1 + (kernel_size + page - 1) // page))
        left = ramdisk_size
        while left:
            chunk = source.read(min(left, 1024 * 1024))
            if not chunk:
                raise ValueError("short embedded payload")
            target.write(chunk)
            left -= len(chunk)
    if digest(embedded) != digest(image):
        raise ValueError("embedded payload bytes differ")
    if extract(embedded, "unixnu.toml", out / "embedded.toml").read_text() != config:
        raise ValueError("embedded boot arguments differ")
    extracted = extract(embedded, entry["path"], out / "embedded-kernel.macho")
    if digest(extracted) != digest(prelink):
        raise ValueError("embedded kernel bytes differ")
    verify_edges(extracted, call)
    (out / "bootprogress-manifest.json").write_text(json.dumps({
        "boot_args": kargs, "abi_image": digest(opts.abi_image), "abi_plan": digest(opts.abi_plan),
        "prelink_sha256": digest(prelink), "payload_sha256": digest(image),
        "boot_sha256": digest(boot), "hardware_tested": False,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
