#!/usr/bin/env python3
"""Compile the pinned upstream renderer in an isolated directory, not a boot image."""
import hashlib
import json
import subprocess
from pathlib import Path

DEVICE = Path(__file__).resolve().parents[2]
BASE = Path("/mnt/d/Code/PortingiOS/UniXNU")
TREE = BASE / "out/enuma/ipados-17.7.11-21H461/enuma/tree"
OUT = DEVICE / "out/bootprogress-20261125"
REPO = DEVICE / ".cache/bootprogress-sheng-c8f92b.git"
REV = "c8f92b208068eeaa4cd2b0f592671f04ee70076e"
BASE_REV = "693f5d9cae8a408dd18b39f3f9fdc4228c934241"
XNU_REV = "d8b80295118ef25ac3a784134bcf95cd8e88109f"
FONT = DEVICE.parent / "uefi-enuma/Silicon/Silicium/SiliciumPkg/Library/FrameBufferSerialPortLib/Font.h"
FONT_SHA = "7749b211129f6f669f53fd9ee16b8e8dc9464aad41ba1bb6f7ce9b45c4eb2f1d"


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


if git(TREE / ".cache/xnu-work", "rev-parse", "HEAD").decode().strip() != XNU_REV:
    raise SystemExit("XNU source revision mismatch")
font = FONT.read_bytes()
if hashlib.sha256(font).hexdigest() != FONT_SHA:
    raise SystemExit("font differs from reviewed enuma input")
OUT.mkdir(parents=True, exist_ok=True)
src = OUT / "source"
headers = OUT / "include/kern"
src.mkdir(exist_ok=True)
headers.mkdir(parents=True, exist_ok=True)
for name in ("BootProgress.c", "BootProgressCore.h", "BootProgressDisplay.h",
             "BootProgressLifecycle.h", "BootProgressPulse.h", "BootTime.h"):
    (src / name).write_bytes(git(REPO, "show", f"{REV}:package/{name}"))
(src / "Font.h").write_bytes(font)
patch = git(BASE, "show", f"{BASE_REV}:patches/xnu/zzz-boot-progress.patch").decode()
part = patch.split("+++ b/osfmk/kern/boot_progress.h\n", 1)[1]
lines = part.split("\n")
header = []
for line in lines[1:]:
    if line.startswith("--- "):
        break
    if line.startswith("+"):
        header.append(line[1:])
(headers / "boot_progress.h").write_text("\n".join(header) + "\n")

record_path = TREE / "build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/osfmk/DEVELOPMENT/startup.o.json"
record = json.loads(record_path.read_text().strip().rstrip(","))
args = record["arguments"]
cmd = []
i = 0
obj = OUT / "BootProgress.o"
while i < len(args):
    arg = args[i]
    if arg == record["file"]:
        cmd.append(str(src / "BootProgress.c"))
    elif arg in ("-o", "-MF", "-MT", "-MJ"):
        if arg == "-o":
            cmd += ["-o", str(obj)]
        i += 1
    elif arg == "-Xclang" and args[i + 1].startswith("-W"):
        i += 1
    elif arg == "-D" and args[i + 1].startswith("XNU_BOOT_PROGRESS="):
        i += 1
    elif not arg.startswith(("-W", "-DXNU_BOOT_PROGRESS=")):
        cmd.append(arg)
    i += 1
cmd += ["-DXNU_BOOT_PROGRESS=1", "-mgeneral-regs-only", "-Wall", "-Wextra",
        "-Werror", "-I", str(OUT / "include"), "-I", str(TREE / ".cache/xnu-work/osfmk")]
(OUT / "compile-command.json").write_text(json.dumps(cmd, indent=2) + "\n")
subprocess.run(cmd, cwd=record["directory"], check=True)
subprocess.run(["llvm-ar", "rcs", str(OUT / "libBootProgress.a"), str(obj)], check=True)
print("Renderer-only archive built; full link and runtime contracts not established.")
