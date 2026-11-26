#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Replay the actual r9 link, changing only the HID publisher and page sampler."""
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
RUN = HERE.parent / "bootprogress-run-state-20261126"
spec = importlib.util.spec_from_file_location("run_state", RUN / "build.py")
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
r6, need, one = run.r6, run.need, run.one
DEVICE, BASE, R4 = run.DEVICE, run.BASE, run.R4
R9 = DEVICE / "out/bootprogress-run-state-20261126-r9"
R64 = DEVICE / "out/ufs-sm8250-ustack-20261124-r64"
HID = DEVICE / "package/EnumaHidStandin.cpp"
ARCHIVE = R64 / "objects/libShengHidInputStandin.a"
PINS = {
    R9 / "boot.img": "0a7df79d01478eb96ccf5932a3e13891deb8ca886e855a000527491bb25994e0",
    R9 / "boot.json": "dd5bc9c7e1086e9c83dcea2b35824d17547430ebcc16ac7e43d8c0afa90a40e5",
    R9 / "commands.json": "2c8d118ba511b629b3f76f32b6bb785ac12eacd0f0868e3d526447b53988054c",
    R9 / "link.filelist": "65433691a5ee7889d4cc6692a35d7956c6b69172e9d11bce9b11242c413376e9",
    R9 / "video_console.c": "81b4fe597a6ac4b1ace16be18e2e3d8934882bdb8aa6578324d25f747c419dc5",
    R9 / "renderer.inc": "4b688510bb15108460ba5c6d7a1a5bdc1d99537ff75657b40569102538766191",
    R9 / "sample.inc": "13241ad977cda704dc2bf730e7df4a4ac70d93d9bbdf235b0aeb1c9d4bd3c550",
    R9 / "embedded-kernel.macho": "d360e0fbcc40190434b311e2b9f6fb71998582372d123d82117a1d67c699bea5",
    R9 / "kern_exec.o": "8cc32c7fcee1aa55b9c141892ad2e59ecf7ec9332ec0de77d00cb4172790a597",
    R9 / "payload.img": "53c819b89785e04b3cf6223eb356678de9357887c346abfd08d685f22d6bfe25",
    R64 / "commands.json": "701376e90e392f149e622d9055649a78bd35c336cfff80353c34e263e5476ac9",
    ARCHIVE: "71bf25bc334a931097003b2236af215de11d11f2417931ded1fd0a42742fa1ec",
}
ROW = '"TOUCH HID reports=%u | digitizer properties: %s"'
TEXT = '"observed" : "not observed"'


def generate(out):
    before = (R9 / "sample.inc").read_text()
    after = one(before, "extern volatile uint32_t native_touch_hid_reports;",
                "extern volatile uint32_t native_touch_hid_reports;\n"
                "extern unsigned enuma_hid_digitizer_sample(void);")
    start = "panel_sample(struct panel_page *page)\n{"
    after = one(after, start, start + "\n\tconst unsigned digitizer_seen = enuma_hid_digitizer_sample();")
    after = one(after, '"TOUCH HID reports=%u | pad and controller trace unavailable", '
                'PANEL_LOAD(native_touch_hid_reports));',
                f'{ROW}, PANEL_LOAD(native_touch_hid_reports),\n\t    digitizer_seen ? {TEXT});')
    (out / "sample.inc").write_text(after)
    (out / "source.diff").write_text("".join(difflib.unified_diff(
        before.splitlines(True), after.splitlines(True), "r9/sample.inc", "candidate/sample.inc")))
    for f in ("video_console.c", "renderer.inc"):
        shutil.copyfile(R9 / f, out / f)
    source = HID.read_text()
    atomic = source[source.index("static unsigned enuma_hid_digitizer_seen;"):
                    source.index("static IORegistryEntry *findEventDriver")]
    checkpoint = source[source.index("static bool publishDigitizerProperties"):
                        source.index("static void startStandin")]
    (out / "checkpoint.inc").write_text(atomic + checkpoint)
    cols = re.search(r"\bPANEL_COLS = (\d+)", (R4 / "page.h").read_text())[1]
    (out / "hid-format.inc").write_text(
        f"    const int n = snprintf(text, sizeof(text), {ROW}, 0xffffffffu,\n"
        f"        enuma_hid_digitizer_sample() ? {TEXT});\n")
    return cols


def verify_hid(out, call):
    image = out / "embedded-kernel.macho"

    def dis(prefix, file, name):
        text = call(prefix + name, ["llvm-objdump", "-d", "--disassemble-symbols=" + name, file])
        need(f"<{name}>:" in text, f"{name}: missing body")
        return text

    reader = dis("hid-edge", image, "_enuma_hid_digitizer_sample")
    need(re.search(r"\bldr\s+w0,", reader) and
         not re.search(r"\b(?:bl|blr|str|stlr)\s", reader), "reader is not a leaf relaxed load")
    name = "_native_hid_live_checkpoint"
    writer = dis("hid-edge", image, name)
    old = dis("r9-hid-edge", R9 / "embedded-kernel.macho", name)
    branch = r"\bbl\s+[^\n]*?<([^>]+)>"
    need(re.findall(branch, writer) == re.findall(branch, old),
         "checkpoint changed direct call sequence")
    timer = dis("hid-edge", image, "__ZN14NativeHidInput4tickEP8OSObjectP18IOTimerEventSource")
    need(timer.count(f"<{name}>") == 1, "missing checkpoint timer edge")
    symbols = (out / "final-symbols.log").read_text()
    collector = "_panel_sample" if re.search(r"\b_panel_sample$", symbols, re.M) else "_enuma_bp_refresh"
    sample = dis("hid-edge", image, collector)
    edge = "<_enuma_hid_digitizer_sample>"
    need(sample.count(edge) == 1 and sample.index(edge) < sample.index("<_ml_set_interrupts_enabled>"),
         "HID read is not before the interrupt/lease window")
    need(b"TOUCH HID reports=%u | digitizer properties: %s\0" in image.read_bytes(),
         "HID line format missing in extracted boot kernel")


def build(out):
    need(out.parent == DEVICE / "out", "use a fresh directory directly under device out")
    old = json.loads((R9 / "commands.json").read_text())
    hid = json.loads((R64 / "commands.json").read_text())
    tree = BASE / "out/enuma/ipados-17.7.11-21H461/enuma/tree"
    uefi = DEVICE.parent / "uefi-enuma"
    opts = SimpleNamespace(output=out, tree=tree, uefi=uefi,
        abi_image=tree.parent / "kernel/kernel.macho", abi_plan=tree.parent / "kernel/kernel.json",
        reference_payload=R9 / "payload.img", reference_boot_report=R9 / "boot.json",
        board=DEVICE / "out/ufs-sm8250-fp-20261124-r65/device",
        dtb=Path("/root/enuma-step10/inputs/enuma.dtb"),
        local=DEVICE / "out/ufs-sm8250-launchd-data-20261119-r1/self-check/packaging/local-build.toml",
        fd=uefi / "Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd")
    xnu = next(Path(arg).parent for arg in old["compile-kern_exec.o"]["argv"]
               if arg.endswith("/.cache/xnu-work/bsd"))

    def validate():
        for repo, pin in ((BASE, r6.BASE_PIN), (xnu, r6.SOURCE_PIN)):
            actual = subprocess.check_output(["git", "-C", repo, "rev-parse", "HEAD"], text=True).strip()
            need(actual == pin, f"unexpected HEAD: {repo}: {actual}")
        for path, sha in {**run.PINS, **PINS}.items():
            need(r6.digest(path) == sha, f"unexpected input digest: {path}")

    validate()
    out.mkdir()
    (out / "tmp").mkdir()
    commands = {}
    env = {**os.environ, **r6.linux_env(opts), "TMPDIR": str(out / "tmp"), "PYTHONDONTWRITEBYTECODE": "1"}
    env["PATH"] = "/home/wh1stl3/.local/bin:" + env["PATH"]

    def call(tag, argv, cwd=out, binary=False, host=False):
        argv = list(map(str, argv))
        environment = {**os.environ, "TMPDIR": str(out / "tmp")} if host else env
        result = subprocess.run(argv, cwd=cwd, env=environment, capture_output=True)
        log = out / (tag + ".log")
        log.write_bytes((b"" if binary else result.stdout) + result.stderr)
        commands[tag] = {"argv": argv, "cwd": str(cwd), "exit": result.returncode}
        (out / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        need(result.returncode == 0, f"{tag} exit {result.returncode}; see {log}")
        return result.stdout if binary else result.stdout.decode(errors="replace")

    def replay(tag, step, substitutions, extra=()):
        argv = step["argv"].copy()
        for before, after in substitutions:
            need(argv.count(str(before)) == 1, f"{tag}: missing/ambiguous argument {before}")
            argv[argv.index(str(before))] = str(after)
        call(tag, argv + list(extra), out if step["cwd"] == str(R9) else step["cwd"])

    cols = generate(out)
    call("compile-test-hid", ["/usr/bin/c++", "-std=c++17", "-Wall", "-Wextra", "-Werror",
        "-fsanitize=address,undefined", "-fno-pie", "-no-pie", f"-DHID_ROW_COLS={cols}",
        "-I", out, HERE / "test-hid.cpp", "-o", out / "test-hid"], host=True)
    for i in range(10):
        call(f"test-hid-{i}", [out / "test-hid", i], host=True)

    replay("compile-video_console.o", old["compile-video_console.o"],
           [(R9 / f, out / f) for f in ("video_console.c", "video_console.o")], ("-H",))
    includes = (out / "compile-video_console.o.log").read_text()
    for path in [out / f for f in ("renderer.inc", "sample.inc")] + [
            R4 / f for f in ("page.h", "refresh.inc", "display-page.inc", "proc-page.inc")] + [
            RUN / "run-state-page.inc"]:
        need(re.search(rf"^\.+ {re.escape(str(path))}$", includes, re.M),
             f"wrong include resolution: {path}")
    obj = "EnumaHidStandin.o"
    replay("compile-" + obj, hid["EnumaHidStandin"], [(ARCHIVE.parent / obj, out / obj)])
    new_archive = out / ARCHIVE.name
    shutil.copyfile(ARCHIVE, new_archive)
    call("replace-hid-member", ["llvm-ar", "rD", new_archive, out / obj])
    members = call("old-hid-members", ["llvm-ar", "t", ARCHIVE]).splitlines()
    need(members == ["NativeHidInput.late.o", "hid-original-bindings.o", obj] and
         members == call("new-hid-members", ["llvm-ar", "t", new_archive]).splitlines(),
         "HID archive order changed")
    for member in members:
        new = call("new-member-" + member, ["llvm-ar", "p", new_archive, member], binary=True)
        prev = call("old-member-" + member, ["llvm-ar", "p", ARCHIVE, member], binary=True)
        need(new == ((out / obj).read_bytes() if member == obj else prev),
             f"unexpected archive bytes: {member}")
    files = (R9 / "link.filelist").read_text()
    need(str(R9 / "kern_exec.o") in files, "r9 exec object lost")
    (out / "link.filelist").write_text(one(files, str(R9 / "video_console.o"), str(out / "video_console.o")))
    replay("link", old["link"], [(R9 / f, out / f) for f in ("link.filelist", "native.macho")] +
           [(f"-Wl,-map,{R9}/native-link.map", f"-Wl,-map,{out}/native-link.map"),
            (f"-Wl,-force_load,{ARCHIVE}", f"-Wl,-force_load,{new_archive}")])
    donor = Path(old["prelink"]["argv"][old["prelink"]["argv"].index("--prelinked") + 1])
    need(r6.digest(donor) == json.loads(opts.abi_plan.read_text())["original_sha256"], "prelink donor drift")
    replay("prelink", old["prelink"], [(R9 / f, out / f) for f in ("native.macho", "prelink.macho")])
    for name in ("native", "prelink"):
        need(not call(name + "-undefined", ["llvm-nm", "-u", out / (name + ".macho")]).strip(),
             f"{name}: unforeseen unresolved symbol")
    replay("inspect-final", old["inspect-final"],
           [(R9 / f, out / f) for f in ("prelink.macho", "prelink.json", "final-abi.json")])
    prev, new = (json.loads((d / "final-abi.json").read_text()) for d in (R9, out))
    for key in ("checks", "pure", "family_text_sha256", "bindings", "compiled_slots_requalified",
                "field_instructions", "stride_units", "slots", "instance_bytes"):
        need(prev[key] == new[key], f"display ABI drift: {key}")
    r6.pack(opts, out / "prelink.macho", call)
    need((out / "embedded.toml").read_bytes() == (R9 / "embedded.toml").read_bytes(), "r9 boot args changed")
    run.display.verify_final(out, call)
    run.verify_run_state(out, call)
    verify_hid(out, call)
    validate()
    (out / "hid-event-verified.json").write_text(json.dumps({
        "status": "self-checked", "boot_sha256": r6.digest(out / "boot.img"),
        "bytes": (out / "boot.img").stat().st_size, "hardware_tested": False,
    }, indent=2) + "\n")


if __name__ == "__main__":
    build(Path(sys.argv[1]).resolve())
