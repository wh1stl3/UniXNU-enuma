#!/usr/bin/env python3
"""Build isolated stage recorder and recompile its two candidate callers."""
import hashlib
import json
import subprocess
from pathlib import Path

DEVICE = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TREE = Path("/mnt/d/Code/PortingiOS/UniXNU/out/enuma/ipados-17.7.11-21H461/enuma/tree")
XNU = TREE / ".cache/xnu-work"
OUT = DEVICE / "out/bootprogress-stage-only-20261125"
OBJDIR = TREE / "build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837"
assert subprocess.check_output(["git", "-C", str(XNU), "rev-parse", "HEAD"]).strip() == b"d8b80295118ef25ac3a784134bcf95cd8e88109f"
OUT.mkdir(parents=True, exist_ok=True)

def replace_once(text, before, after):
    if text.count(before) != 1:
        raise RuntimeError("source anchor is not unique: " + before[:80])
    return text.replace(before, after, 1)

def guarded(body):
    return "#if defined(XNU_BOOT_PROGRESS) && XNU_BOOT_PROGRESS\n" + body + "\n#endif\n"

decl = guarded("extern void enuma_bp_init(void);\nextern void enuma_bp_stage(const char *);")
startup = (XNU / "osfmk/kern/startup.c").read_text()
for func in ("kernel_bootstrap_log", "kernel_bootstrap_thread_log"):
    anchor = func + "(const char *message)\n{\n"
    startup = replace_once(startup, anchor, anchor + guarded(
        '\tif (startup_phase >= STARTUP_SUB_KPRINTF) enuma_bp_stage(message);'))
arm = (XNU / "osfmk/arm/arm_init.c").read_text()
anchor = "\tPE_init_platform(FALSE, args); /* Get platform expert set up */\n"
arm = replace_once(arm, anchor, anchor + guarded("\tenuma_bp_init();"))

def compile_one(record, source, output):
    rec = json.loads(record.read_text().strip().rstrip(","))
    args = rec["arguments"]
    cmd = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == rec["file"]:
            cmd.append(str(source))
        elif arg in ("-o", "-MF", "-MT", "-MJ"):
            if arg == "-o":
                cmd += ["-o", str(output)]
            i += 1
        elif arg == "-D" and args[i + 1].startswith("XNU_BOOT_PROGRESS="):
            i += 1
        elif not arg.startswith("-DXNU_BOOT_PROGRESS="):
            cmd.append(arg)
        i += 1
    cmd += ["-DXNU_BOOT_PROGRESS=1"]
    (OUT / (output.name + ".command.json")).write_text(json.dumps(cmd, indent=2) + "\n")
    subprocess.run(cmd, cwd=rec["directory"], check=True)

sources = [("arm_init", arm, "osfmk"), ("startup", startup, "osfmk")]
manifest = {}
for name, content, component in sources:
    source = OUT / (name + ".c")
    source.write_text(decl + content)
    manifest[name] = hashlib.sha256(content.encode()).hexdigest()
    rec = OBJDIR / component / "DEVELOPMENT" / (name + ".o.json")
    compile_one(rec, source, OUT / (name + ".o"))
rec = OBJDIR / "osfmk/DEVELOPMENT/startup.o.json"
compile_one(rec, HERE / "recorder.c", OUT / "recorder.o")
subprocess.run(["llvm-ar", "rcs", str(OUT / "libEnumaBootRecorder.a"),
                str(OUT / "recorder.o")], check=True)
(OUT / "source-hashes.json").write_text(json.dumps(manifest, indent=2) + "\n")
print("candidate callers and recorder archive built; no final link")
