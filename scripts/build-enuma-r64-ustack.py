#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Build the isolated user-stack diagnostic on the frozen r63 candidate."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys
import textwrap
import tomllib
from types import SimpleNamespace

sys.dont_write_bytecode = True
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--r64", action="store_true", required=True)
parser.add_argument("--out", type=Path, help="fresh path under out/ for independent replay")
opts = parser.parse_args()
device = Path(__file__).resolve().parents[1]
base = device.parents[1] / "UniXNU"
r57 = device / "out/ufs-sm8250-txpeer-20261123-r57"
r62 = device / "out/ufs-sm8250-smpobs-20261124-r62"
r63 = device / "out/ufs-sm8250-smp3-20261124-r63"
out = (opts.out or device / "out/ufs-sm8250-ustack-20261124-r64").resolve()
assert out.parent == device / "out" and not out.exists(), out
helpers = runpy.run_path(str(device / "scripts/build-enuma-r23-hid-standin.py"))
digest, snapshot, read_member, fat_tree = (
    helpers["R"][k] for k in ("digest", "snapshot", "read_member", "fat_tree")
)


def head(repo):
    return subprocess.check_output(["git", "-C", repo, "rev-parse", "HEAD"], text=True).strip()


names = ("kernel.macho.adt", "native.macho", "prelink.macho", "payload.img", "boot.img")
prior = json.loads((r63 / "candidate-manifest.json").read_text())
before = {n: digest(r63 / n) for n in names}
assert before == prior["after"]
assert before["boot.img"] == "f94c738c9b04b8edaec46775c00bd99d239b4a72a1f2fcf2c46a709b096eaa64"
assert (r63 / "link.filelist").read_bytes() == (r62 / "link.filelist").read_bytes()
recipe = json.loads((r62 / "commands.json").read_text())
paths = [Path(p) for p in (r63 / "link.filelist").read_text().splitlines()]
old_obj, = (p for p in paths if p.name == "kern_exec.o")
video, = (p for p in paths if p.name == "video_console.o")
assert len(paths) == len(set(paths))
link_step = recipe["link"]
tree = Path(link_step["cwd"]).parents[3]
xnu = tree / ".cache/xnu-work"
xnu_pin = "d8b80295118ef25ac3a784134bcf95cd8e88109f"
assert head(base) == helpers["BASE_PIN"] and head(xnu) == xnu_pin

# Snapshot the filelist, all direct linker inputs and the donor before compiling.
link_argv = link_step["argv"]
direct = {Path(a.rsplit(",", 1)[-1]) for a in link_argv
          if a.endswith((".a", ".o", ".exp", ".plist"))}
firehose = [Path(a[2:]) / "libfirehose_kernel.a" for a in dict.fromkeys(link_argv)
            if a.startswith("-L") and (Path(a[2:]) / "libfirehose_kernel.a").exists()]
assert "-lfirehose_kernel" in link_argv and len(firehose) == 1
pre = recipe["prelink"]["argv"]
donor = Path(pre[pre.index("--prelinked") + 1])
original_missing = sorted(str(p) for p in set(paths) | direct if not p.is_file())
inputs = snapshot(sorted({p for p in set(paths) | direct if p.is_file()} |
                         set(firehose) | {donor, r63 / "link.filelist"}))
assert inputs[str(old_obj)] == prior["objects"]["kern_exec.o"][1]
assert inputs[str(video)] == prior["video_sha256"]

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
    p = subprocess.run(argv, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
    commands[tag] = dict(argv=argv, cwd=str(cwd), exit=p.returncode)
    (out / "logs" / (tag + ".log")).write_text(p.stdout)
    (out / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
    if p.returncode:
        print(p.stdout, file=sys.stderr)
        raise SystemExit(f"{tag}: exit {p.returncode}")
    print(tag, flush=True)
    return p.stdout


source = out / "source/bsd/kern"
shutil.copytree(r62 / "source/bsd/kern", source)
bp = source / "EnumaBootProgress2.inc"
before_source = {p.name: digest(p) for p in source.iterdir() if p.is_file()}
r62_record = json.loads((r62 / "candidate-manifest.json").read_text())
assert before_source[bp.name] == r62_record["changed_sources"][bp.name][1]
text = bp.read_text()
for old, new in (
    ('#include "EnumaBootProgress62Cpu.inc"\n',
     '#include "EnumaBootProgress62Cpu.inc"\nextern void enuma_stk_submit(void);\n'),
    ("\tif (idx == ENUMA_TH_TICK && snapshot_call != NULL) {",
     "\tif (idx == ENUMA_TH_TICK) {\n\t\tenuma_stk_submit();\n\t}\n"
     "\tif (idx == ENUMA_TH_TICK && snapshot_call != NULL) {"),
):
    assert text.count(old) == 1, old
    text = text.replace(old, new)
bp.write_text(text)
assert {p.name: digest(p) for p in source.iterdir() if p.is_file() and p != bp} == {
    n: h for n, h in before_source.items() if n != bp.name
}


def compile_unit(step, src, obj, *extra):
    argv = iter(step["argv"])
    cmd = []
    for arg in argv:
        if arg in ("-MF", "-MT", "-MQ", "-MJ", "-serialize-diagnostics"):
            next(argv)
        elif arg not in ("-MD", "-MMD", "-MP"):
            cmd.append(arg)
    assert cmd[3] == "-o" and src.is_file(), (src, cmd[:5])
    cmd[2], cmd[4] = src, obj
    argv = [str(owner_header) if a == old_owner_header else a for a in cmd] + list(extra)
    call("compile-" + obj.name, argv, step["cwd"])
    rebuilt[obj.name] = digest(obj)
    return obj


def old_round(n):
    path, = (device / "out").glob(f"ufs-sm8250-*-r{n}")
    return path


def recorded(directory, tag):
    return json.loads((directory / "commands.json").read_text())[tag]


def cc_source(name):
    p, = Path(link_step["cwd"]).glob("*/DEVELOPMENT/" + name + ".json")
    cc = json.loads(p.read_text().strip().removesuffix(","))
    return dict(argv=cc["arguments"], cwd=cc["directory"])


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def stage(rel, text):
    path = out / "source" / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def source_steps(script, start, end, scope):
    # Reuse only the existing source transformation, not the old build.
    text = (device / "scripts" / script).read_text()
    exec(textwrap.dedent(text[text.index(start):text.index(end)]),
         {"replace_once": replace_once}, scope)
    return scope


def patch_source(text, name, file):
    lines = (device / "patches/xnu" / name).read_text().splitlines(keepends=True)
    a = lines.index(f"+++ b/{file}\n")
    b = next((i for i in range(a + 1, len(lines)) if lines[i].startswith("diff --git ")), len(lines))
    for hunk in re.split(r"(?m)^@@ .*?\n", "".join(lines[a + 1:b]))[1:]:
        rows = hunk.splitlines(keepends=True)
        old = "".join(l[1:] for l in rows if l.startswith((" ", "-")))
        new = "".join(l[1:] for l in rows if l.startswith((" ", "+")))
        text = replace_once(text, old, new)
    return text


rebuilt = {}
objects = out / "objects"
pkg = device / "package"
historical_data = device / "out/ufs-sm8250-launchd-data-20261119-r1/self-check"
old_owner_header, = (a for a in recipe["compile-kern_exec.o"]["argv"]
                     if a.endswith("/owner-data-volume.h"))
owner_header = historical_data / "owner-data-volume.h"
assert digest(owner_header) == "eb84a4f930f092498af381f6d0ee79781a85c27a802f656c2135808914a48f13"
r63_native = (r63 / "native.macho").read_bytes()
assert all(r63_native.count(v + b"\0") == 1 for v in
           re.findall(rb'"([0-9A-F-]+)"', owner_header.read_bytes()))
del r63_native
data_cc = {s["tag"]: s for s in json.loads(
    (historical_data / "kernel-build-result.json").read_text())["commands"]}
r40 = old_round(40)
for n, src, step in (
    ("mach_msg.o", old_round(34) / "source/osfmk/ipc/mach_msg.c", cc_source("mach_msg.o")),
    ("vm_fault.o", stage("osfmk/vm/vm_fault.c", source_steps(
        "build-enuma-r42-matchcnt.py", "    v = vm_src.read_text()", "    vm.write_text(v)",
        {"vm_src": xnu / "osfmk/vm/vm_fault.c"})["v"]), recorded(old_round(47), "compile-vm_fault.o")),
):
    compile_unit(step, src, objects / n)

bsd_rel = "bsd/kern/bsd_init.c"
bsd_text = (device / "out/ufs-sm8250-launchd-keystore-20261122-r13-audit-first"
            / "self-check/build-final/source" / bsd_rel).read_text()
for patch in ("enuma-timebase-probe.patch", "enuma-r11-keystore-probe.patch"):
    bsd_text = patch_source(bsd_text, patch, bsd_rel)
assert hashlib.sha256(bsd_text.encode()).hexdigest() == "24a21ca6875a56f4e9292221b9e3ab624a7cb49d15ca0ecca0ba8932f8459fbe"
store = "build-enuma-r40-storegeom.py"
bsd_text = source_steps(store, "seq_anchor =", "bsd_source.write_text(bsd_text)",
                        {"bsd_text": bsd_text})["bsd_text"]
compile_unit(recorded(r40, "compile-bsd"), stage(bsd_rel, bsd_text), objects / "bsd_init.o")

exit_rel = "bsd/kern/kern_exit.c"
old_exit = "proc_prepareexit(proc_t p, int rv, boolean_t perf_notify)\n{\n"
exit_text = replace_once((xnu / exit_rel).read_text(), old_exit, old_exit + """	if (!proc_is_shadow(p)) {
		char comm[17];
		int pid = proc_getpid(p);
		int status = rv;
		int sig = WIFSIGNALED(status) ? WTERMSIG(status) : 0;
		strlcpy(comm, p->p_comm, sizeof(comm));
		printf("enuma-exit: pid=%d st=%d sig=%d comm=%s\\n", pid, status, sig, comm);
	}
""")
compile_unit(cc_source("kern_exit.o"), stage(exit_rel, exit_text), objects / "kern_exit.o")
for n, rel, patch in (
    ("vm_unix.o", "bsd/vm/vm_unix.c", "enuma-r15-shared-region-probe.patch"),
    ("OSKext.cpo", "libkern/c++/OSKext.cpp", "enuma-r11-board-classes.patch"),
):
    compile_unit(cc_source(n), stage(rel, patch_source((xnu / rel).read_text(), patch, rel)),
                 objects / n, "-iquote", (xnu / rel).parent)
uc_src = device / "out/ufs-sm8250-bp-20261123-r46-initial/source/iokit/Kernel/IOUserClient.cpp"
assert uc_src.read_text().count("enuma_matchcnt_record(") == 7
compile_unit(recorded(old_round(43), "compile-IOUserClient.cpo"), uc_src,
             objects / "IOUserClient.cpo", "-iquote", xnu / "iokit/Kernel")
io_step = data_cc["compile-IOKitBSDInit.cpo"]
compile_unit(io_step, Path(io_step["argv"][2]), objects / "IOKitBSDInit.cpo")

orig_native = (device / "out/ufs-sm8250-startroot-wip-20261118/self-check"
               / "resume-20261118-r11/merged-source/NativeUfs.cpp")
assert digest(orig_native) == "6ee5fb866c9bcdc5b1c50268ede8dc86f3eef1526c3784b3e8f0664da27ccb69"
native_text = source_steps(store, "native_text = old_native.read_text()", "native_source.write_text(native_text)",
                           {"old_native": orig_native})["native_text"]
compile_unit(recorded(r40, "compile-ufs"), stage("NativeUfs.cpp", native_text),
             objects / "NativeUfs.o", "-iquote", orig_native.parent)


def archive(name, *members):
    call("archive-" + name, ["llvm-ar", "rcsD", objects / name, *members])
    rebuilt[name] = digest(objects / name)


archive("libShengUfs.a", objects / "NativeUfs.o")
owner_cc = data_cc["compile-EnumaUfsOwnerQuery"]
compile_unit(owner_cc, pkg / "EnumaUfsOwnerQuery.cpp", objects / "EnumaUfsOwnerQuery.o")
watch = compile_unit(recipe["compile-kern_exec.o"], pkg / "BootWatchdogPolicy.c",
                     objects / "BootWatchdogPolicy.o", "-mgeneral-regs-only")
archive("libEnumaBootWatchdogPolicy.a", watch)
aks_source = subprocess.check_output(["git", "-C", base / "drivers/AppleKeyStoreState", "show",
    "8c70daf814aafdf4a3d35e40dde0322655fd0a83:NativeKeyStoreEvents.cpp"], text=True)
state = compile_unit(owner_cc, stage("NativeKeyStoreEvents.cpp", aks_source), objects / "NativeKeyStoreEvents.o")
probe = compile_unit(owner_cc, pkg / "EnumaKeyStoreProbe.cpp", objects / "EnumaKeyStoreProbe.o")
late = objects / "NativeKeyStoreEvents.late.o"
call("strip-keystore-init", ["llvm-objcopy", "--remove-section=__DATA,__mod_init_func", state, late])
ks = runpy.run_path(str(device / "scripts/build-enuma-r11-keystore.py"))
assert ks["init_sections"](state) == {"__DATA": 8} and not ks["init_sections"](late)
ks["export_initializer"](late)
rebuilt[late.name] = digest(late)
archive("libAppleKeyStoreState.a", late, probe)

display = device / "out/enuma-gop-production-20261114-r5/display"
dr = json.loads((display / "result.json").read_text())["commands"]
display_src = display / "source/NativeLegacyDisplay.cpp"
display_text = patch_source(display_src.read_text(), "enuma-r26-fbcount.patch",
                            "display/NativeLegacyDisplay.cpp")
rule = (device / "scripts/build-enuma-r29-bbscan.py").read_text()
edits = ast.literal_eval(rule[rule.index("    replacements = [") + len("    replacements = "):
                              rule.index("    for old, new, expected")])
for old, new, count in edits:
    old, new = old.replace("\\n", "\n"), new.replace("\\n", "\n")
    assert display_text.count(old) == count, old
    display_text = display_text.replace(old, new)
disp = compile_unit(dr[2], stage("display/NativeLegacyDisplay.cpp", display_text),
                    objects / "NativeLegacyDisplay.o", "-iquote", display_src.parent)
late = objects / "NativeLegacyDisplay.late.o"
call("strip-display-init", [*dr[4]["argv"][:2], disp, late])
blob = bytearray(late.read_bytes())
table, symbols = helpers["symbols"](blob, helpers["macho"](blob))
i, = (i for i, (n, *_) in enumerate(symbols) if n == "__GLOBAL__sub_I_NativeLegacyDisplay.cpp")
kind = table + 16 * i + 4
assert blob[kind] & 0xf == 0xe
blob[kind] |= 1
late.write_bytes(blob)
rebuilt[late.name] = digest(late)
archive("libEnumaGopLegacy.a", late, display / "EnumaLegacyDisplay.o", display / "original-bindings.o")

hid_repo = device / "out/r23-upstream/ShengHidInput"
hid_text = subprocess.check_output(["git", "-C", hid_repo, "show",
    helpers["HID_PIN"] + ":NativeHidInput.cpp"], text=True)
hid_src = stage("NativeHidInput.cpp", hid_text)
(objects / "OriginalHidDeviceABI.h").write_text(helpers["abi_header"]())
hid_cc = json.loads((Path(link_step["cwd"]) /
    "iokit/DEVELOPMENT/IOPlatformExpert.cpo.json").read_text().strip().removesuffix(","))
hid_obj, hid_pub, hid_bind, hid_late = (
    objects / f for f in ("NativeHidInput.o", "EnumaHidStandin.o",
                          "hid-original-bindings.o", "NativeHidInput.late.o"))
for src, target in ((hid_src, hid_obj), (pkg / "EnumaHidStandin.cpp", hid_pub)):
    helpers["compile_cxx"](hid_cc, src, target, objects, call)
    rebuilt[target.name] = digest(target)
abi_base = old_round(58)
hid_donor = helpers["check_donor"](abi_base / "prelink.macho",
                                    json.loads((abi_base / "prelink.json").read_text()))
hid_raw = hid_obj.read_bytes()
bindings, vtable, owned = helpers["check_object"](hid_raw, hid_donor)
asm = stage("hid-original-bindings.S", "".join(
    f".globl {n}\n.set {n}, {v:#x}\n" for n, v in sorted(bindings.items())))
call("compile-hid-bindings", [hid_cc["arguments"][0], "--target=arm64-apple-ios17.0",
                             "-c", asm, "-o", hid_bind])
call("strip-hid-init", ["llvm-objcopy", "--remove-section=__DATA,__mod_init_func", hid_obj, hid_late])
helpers["late_init"](hid_late)
assert helpers["check_object"](hid_late.read_bytes(), hid_donor) == (bindings, vtable, owned)
rebuilt.update({p.name: digest(p) for p in (hid_bind, hid_late)})
archive("libShengHidInputStandin.a", hid_late, hid_bind, hid_pub)


obj = out / "objects/kern_exec.o"
compile_unit(recipe["compile-kern_exec.o"], source / "kern_exec.c", obj)
assert digest(obj) != inputs[str(old_obj)]
stk_src = device / "package/EnumaUserStack64.c"
stk_obj = out / "objects/EnumaUserStack64.o"
private_recipe = json.loads((r57 / "commands.json").read_text())["compile-EnumaThreadSnapshot56.o"]
compile_unit(private_recipe, stk_src, stk_obj)
new_paths = [objects / p.name if p.name in rebuilt else p for p in paths] + [stk_obj]
(out / "link.filelist").write_text("".join(f"{p}\n" for p in new_paths))
direct_map = {p: objects / p.name for p in direct if p.name in rebuilt}
for n, h in (
    ("libRamBlock.a", "6f4fda373f69e8b2ba557bbc5a1381784da149e3d4646ac82a6938d2be507395"),
    ("libVerifiedRootDependencies.a", "53e72ccd2a296e97f8fdd10b74c515695a8379c1da8833cba64a3d751eb604c6"),
):
    orig, = (p for p in direct if p.name == n)
    alt = historical_data / n
    assert digest(alt) == h, alt
    direct_map[orig] = alt
missing = [p for p in (*new_paths, *(direct_map.get(p, p) for p in direct), *firehose, donor)
           if not p.is_file()]
assert not missing, missing
for tag in ("link", "prelink"):
    step = recipe[tag]
    argv = [a.replace(str(r62), str(out)) for a in step["argv"]]
    if tag == "link":
        argv = [a.removesuffix(p) + str(direct_map[Path(p)])
                if Path(p := a.rsplit(",", 1)[-1]) in direct_map else a for a in argv]
    call(tag, argv, out if tag == "prelink" else step["cwd"])

formats = (
    b"enuma-stk: p=%d why=vm_map_read_user kr=%d n=0\n\0",
    b"enuma-stk: p=%d why=%s\n\0",
    b"enuma-stk: p=%d slide=0x%x sp=0x%llx n=%u\n\0",
    b"enuma-stk: %d 0x%llx 0x%llx 0x%llx 0x%llx\n\0",
    b"enuma-stk: p=%d why=callout-allocation\n\0",
)
edges = {
    "_enuma_bp_repeat": {"_enuma_stk_submit": 1},
    "_enuma_stk_submit": {"_thread_call_allocate_with_options": 1, "_thread_call_enter1": 1},
    "_enuma_stk_worker": {"_enuma_stk_capture": 2, "_thread_call_free": 1},
    "_enuma_stk_capture": {"_vm_map_read_user": 1, "_enuma_th_task_ref": 1,
                           "_get_task_map_reference": 1, "_vm_map_deallocate": 1},
}
callsites = {}
for n in ("native.macho", "prelink.macho"):
    p = out / n
    assert not call("undefined-" + n, ["llvm-nm", "-u", p]).strip()
    blob = p.read_bytes()
    _, syms = helpers["symbols"](blob, helpers["macho"](blob))
    assert not [s for s in syms if not s[1] & 0xe0 and s[1] & 0x0e == 0]
    assert all(blob.count(s) == 1 for s in formats), n
    del blob
    report = call("calls-" + n, ["llvm-objdump", "-d", "--disassemble-symbols=" +
                                 ",".join(edges), p])
    labeled = re.split(r"(?m)^[0-9a-f]+ <([^>]+)>:\n", report)
    bodies = dict(zip(labeled[1::2], labeled[2::2], strict=True))
    callsites[n] = {}
    for caller, targets in edges.items():
        for callee, count in targets.items():
            sites = re.findall(r"(?m)^\s*([0-9a-f]+):.*\b(?:b|bl)\b.*<" + callee + ">",
                               bodies[caller])
            assert len(sites) == count, (n, caller, callee, sites)
            callsites[n][f"{caller}->{callee}"] = sites

shutil.copytree(r63 / "device", out / "device")
for n in ("kernel.macho.adt", "payload.img"):
    shutil.copyfile(r63 / n, out / n)
kernel_member = "Payloads/kernel.macho"
os.utime(out / "prelink.macho", (payload_step.EPOCH, payload_step.EPOCH))
call("replace-kernel", ["env", "MTOOLS_SKIP_CHECK=1", "TZ=UTC", "mcopy", "-o", "-m",
     "-i", out / "payload.img", out / "prelink.macho", "::/EFI/UniXNU/" + kernel_member])
tree_members = fat_tree(r63 / "payload.img")
assert fat_tree(out / "payload.img") == tree_members
members = [p.removeprefix("::/EFI/UniXNU/") for p in tree_members if not p.endswith("/")]
old_members, new_members = (
    {n: hashlib.sha256(read_member(d / "payload.img", n)).hexdigest() for n in members}
    for d in (r63, out)
)
assert old_members == prior["payload_members_after"]
assert [n for n in members if old_members[n] != new_members[n]] == [kernel_member]
assert new_members[kernel_member] == digest(out / "prelink.macho")

local = historical_data / "packaging/local-build.toml"
ctx = Context(cli_parser().parse_args(["bootimg", "-D", str(out / "device"), "--out", str(out / "work"),
    "--config", str(local), "--local-module", "soc:sm8250=" + str(device.parent / "UniXNU-sm8250-common")]))
uefi = device.parent / "uefi-enuma"
fd = uefi / "Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd"
dtb = Path("/root/enuma-step10/inputs/enuma.dtb")
ref = json.loads((r63 / "boot.json").read_text())
assert digest(fd) == ref["fd_sha256"] and digest(dtb) == ref["dtb_sha256"]
bootimg.build(ctx, uefi, fd, dtb, out / "payload.img", out / "boot.img")
offset = prior["boot_payload_offset"]
embedded = out / "tmp/embedded-payload.img"
with (r63 / "boot.img").open("rb") as a, (out / "boot.img").open("rb") as b:
    x, y = a.read(offset), b.read(offset)
    assert x[:576] == y[:576] and x[596:] == y[596:]
    assert hashlib.file_digest(a, "sha256").hexdigest() == before["payload.img"]
    with embedded.open("wb") as target:
        shutil.copyfileobj(b, target)
assert digest(embedded) == digest(out / "payload.img")
readback = read_member(embedded, "unixnu.toml")
assert readback == read_member(r63 / "payload.img", "unixnu.toml")
args = next(e["args"] for e in tomllib.loads(readback.decode())["entry"] if e["id"] == "xnu")
assert args == prior["args_after"]
assert read_member(embedded, "Payloads/kernel.macho.adt") == (
    out / "kernel.macho.adt").read_bytes() == (r63 / "kernel.macho.adt").read_bytes()
assert {n: digest(r63 / n) for n in names} == before
assert snapshot([Path(p) for p in inputs]) == inputs
assert head(base) == helpers["BASE_PIN"] and head(xnu) == xnu_pin

result = dict(
    args=args, before=before, after={n: digest(out / n) for n in names},
    sizes={n: (out / n).stat().st_size for n in names},
    deltas={n: (out / n).stat().st_size - (r63 / n).stat().st_size for n in names},
    objects={obj.name: [inputs[str(old_obj)], digest(obj)], stk_obj.name: [None, digest(stk_obj)]},
    changed_sources={bp.name: [before_source[bp.name], digest(bp)], stk_src.name: [None, digest(stk_src)]},
    source_pin=xnu_pin, original_missing=original_missing, link_input_missing=0, rebuilt=rebuilt,
    changed_payload_members=[kernel_member], payload_members_after=new_members,
    boot_payload_offset=offset, zero_undefined_including_weak=True, adt_byte_identical=True,
    unique_formats=True, callsites=callsites,
)
(out / "candidate-manifest.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
