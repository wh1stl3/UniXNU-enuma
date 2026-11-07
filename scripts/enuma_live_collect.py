#!/usr/bin/env python3
"""Read-only enuma evidence collection; Python 3.11 stdlib, WSL 3.10-compatible."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shlex
import struct
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

EARLIER_FDT_SHA256 = "45a04e08f47245ca5ec4145faf35346e36c014e8425b7cad470a299a98f12472"
DEFAULT_ADB = r"D:\Code\PortingiOS\enuma\UniXNU-enuma\.cache\tools\platform-tools\adb.exe"
PROPS = (
    "ro.product.device", "ro.product.model", "ro.build.fingerprint",
    "ro.build.version.incremental", "ro.bootloader", "ro.boot.slot_suffix",
    "ro.boot.hardware", "ro.boot.hardware.platform", "ro.boot.flash.locked",
    "ro.boot.verifiedbootstate", "ro.boot.hwversion", "ro.boot.hwc",
    "ro.boot.hwlevel", "ro.product.name",
)
PARTITIONS = ("xbl_a", "xbl_config_a", "abl_a", "dtbo_a", "imagefv_a")
LUNS = tuple(f"sd{x}" for x in "abcdef")
CPUS = tuple(f"cpu{i}" for i in range(8))
REJECT = (" of=", ">", "tee", "mount", "umount", "reboot", "setprop",
          "settings", "rm ", "mv ", "cp ", "chmod", "chown", "echo ",
          "start", "stop", "svc", "fastboot", "flash", "write")

# Read-only collector commands that legitimately contain a forbidden substring
# (e.g. "flash" inside the property name). Permitted only by full-string
# equality against this set -- never by prefix/regex/contains -- so any other
# spelling (extra arguments, shell metacharacters, quote-spliced fragments,
# case changes) falls through to the forbidden-substring scan and is rejected.
FORBIDDEN_EXACT_ALLOW = frozenset({
    "getprop ro.boot.flash.locked",
})


class CollectionError(Exception):
    pass


def reject_unsafe(command: str) -> None:
    # Exact-match allowlist is consulted BEFORE the substring scan and only ever
    # compares the full command string for equality.
    if command in FORBIDDEN_EXACT_ALLOW:
        return
    low = command.lower()
    for token in REJECT:
        if token in low:
            raise ValueError(f"unsafe command rejected ({token!r})")


def select_enuma_device(devices_output: str) -> str:
    matches = []
    for line in devices_output.splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[1] == "device" and "device:enuma" in fields[2:]:
            matches.append(fields[0])
    if len(matches) != 1:
        raise CollectionError(f"expected exactly one online enuma; found {len(matches)}")
    return matches[0]


def redact_text(text: str, serial: str = "", mask_long_hex: bool = False) -> str:
    if serial:
        text = text.replace(serial, "<REDACTED>")
    text = re.sub(r"(?i)(androidboot\.serialno=)[^\s]+", r"\1<REDACTED>", text)
    text = re.sub(r"(?i)(androidboot\.[^=\s]*sn[^=\s]*=)[^\s]+", r"\1<REDACTED>", text)
    text = re.sub(r"(?i)\b(?:serial(?:\s*number)?\s*[:=]\s*)[^\s,;]+", "Serial: <REDACTED>", text)
    text = re.sub(r"(?i)\b(?:imei|meid)\s*[:=]?\s*[0-9]{10,20}\b", "<REDACTED>", text)
    text = re.sub(r"(?i)\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b", "<REDACTED>", text)
    if mask_long_hex:
        text = re.sub(r"\b[0-9a-fA-F]{16,}\b", "<REDACTED>", text)
    return text


def strip_cpu_serial(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not re.match(r"^\s*Serial\s*:", line)) + "\n"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strip_dd_status(data: bytes) -> bytes:
    """Remove toybox dd's trailing transfer report from exec-out stdout."""
    pattern = re.compile(
        rb"[0-9]+\+[0-9]+ records in\n[0-9]+\+[0-9]+ records out\n"
        rb"[0-9]+ bytes \([^\r\n)]*\) copied, [^\r\n]*\r?\n$"
    )
    match = pattern.search(data)
    return data[:match.start()] if match else data


def base_commands() -> list[tuple[str, str, str, int]]:
    """Fixed approved command tuples: (artifact, command, transport, timeout)."""
    out = []
    for prop in PROPS:
        out.append((f"getprop_{prop.replace('.', '_')}.txt", f"getprop {prop}", "shell", 60))
    for name in ("iomem", "cpuinfo", "meminfo", "version", "partitions", "cmdline"):
        out.append((f"proc_{name}.txt", f"cat /proc/{name}", "shell", 60))
    out += [
        ("live_fdt.bin", "cat /sys/firmware/fdt", "exec-out", 60),
        ("by_name_links.txt", "ls -l /dev/block/by-name", "shell", 60),
        ("sys_block_names.txt", "ls -1 /sys/block", "shell", 60),
        ("thermal_zone_names.txt", "ls -d /sys/class/thermal/thermal_zone*", "shell", 60),
        ("thermal_zone_types.txt", "cat /sys/class/thermal/thermal_zone*/type", "shell", 60),
        ("cooling_device_types.txt", "cat /sys/class/thermal/cooling_device*/type", "shell", 60),
        ("power_supply_names.txt", "ls -1 /sys/class/power_supply", "shell", 60),
        ("power_supply_type.txt", "cat /sys/class/power_supply/*/type", "shell", 60),
        ("power_supply_status.txt", "cat /sys/class/power_supply/*/status", "shell", 60),
        ("power_supply_capacity.txt", "cat /sys/class/power_supply/*/capacity", "shell", 60),
        ("power_supply_technology.txt", "cat /sys/class/power_supply/*/technology", "shell", 60),
        ("dmesg_first_400.txt", "dmesg | head -n 400", "shell", 60),
        ("dmesg_last_400.txt", "dmesg | tail -n 400", "shell", 60),
        ("backlight_names.txt", "ls -1 /sys/class/backlight", "shell", 60),
        ("input_names.txt", "ls -1 /sys/class/input", "shell", 60),
        ("input_device_names.txt", "cat /sys/class/input/input*/name", "shell", 60),
        ("spi_device_names.txt", "ls -1 /sys/bus/spi/devices", "shell", 60),
        ("i2c_device_names.txt", "ls -1 /sys/bus/i2c/devices", "shell", 60),
    ]
    for cpu in CPUS:
        for key in ("scaling_available_frequencies", "cpuinfo_max_freq", "cpuinfo_min_freq", "related_cpus"):
            out.append((f"{cpu}_{key}.txt", f"cat /sys/devices/system/cpu/{cpu}/cpufreq/{key}", "shell", 60))
    for key in ("gpu_model", "gpu_available_frequencies", "max_gpuclk", "min_clock_mhz", "max_clock_mhz"):
        out.append((f"gpu_{key}.txt", f"cat /sys/class/kgsl/kgsl-3d0/{key}", "shell", 60))
    return out


def dynamic_commands(luns: list[str], partition_names: list[str]) -> list[tuple[str, str, str, int]]:
    out = []
    for lun in luns:
        out += [
            (f"{lun}_logical_block_size.txt", f"cat /sys/block/{lun}/queue/logical_block_size", "shell", 60),
            (f"{lun}_sectors.txt", f"cat /sys/block/{lun}/size", "shell", 60),
            (f"{lun}_first_32768.bin", f"dd if=/dev/block/{lun} bs=4096 count=8", "exec-out", 60),
        ]
    for part in PARTITIONS:
        if part in partition_names:
            out += [
                (f"partition_{part}.bin", f"dd if=/dev/block/by-name/{part} bs=1048576", "exec-out", 300),
                (f"partition_{part}_device_sha256.txt", f"sha256sum /dev/block/by-name/{part}", "shell", 60),
            ]
    return out


def check_command_list(commands: list[tuple[str, str, str, int]]) -> None:
    allowed = {cmd for _, cmd, _, _ in base_commands()}
    allowed.update(cmd for _, cmd, _, _ in dynamic_commands(list(LUNS), list(PARTITIONS)))
    for _, command, transport, timeout in commands:
        reject_unsafe(command)
        if command not in allowed or transport not in ("shell", "exec-out") or timeout not in (60, 300):
            raise ValueError("command tuple is not in the fixed read-only whitelist")


def adb_run(adb: str, serial: str, command: str | None, transport: str | None,
            timeout: int) -> subprocess.CompletedProcess[bytes]:
    argv = [adb, "-s", serial]
    if transport == "shell":
        argv += ["shell", "su", "-c", command or ""]
    elif transport == "exec-out":
        argv += ["exec-out", "su", "-c", command or ""]
    else:
        argv += [command or ""]
    return subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=timeout, check=False)


def write_artifact(root: Path, name: str, data: bytes, serial: str) -> tuple[int, str] | None:
    # Never persist the transport serial, including as a binary substring.
    if serial and (serial.encode("utf-8", "ignore") in data or serial.encode("utf-16le", "ignore") in data):
        return None
    path = root / name
    path.write_bytes(data)
    return len(data), sha256(data)


def parse_links(text: str) -> dict[str, str]:
    links = {}
    for line in text.splitlines():
        m = re.search(r"\s([^\s]+)\s+->\s+(.+)$", line)
        if m:
            links[Path(m.group(1)).name] = m.group(2).strip()
    return links


def parse_gpt(data: bytes, sector_size: int) -> list[tuple[str, int, int]]:
    if sector_size < 512 or len(data) < sector_size + 92 or data[sector_size:sector_size + 8] != b"EFI PART":
        return []
    header = data[sector_size:sector_size + 92]
    entry_lba = struct.unpack_from("<Q", header, 72)[0]
    count, entry_size = struct.unpack_from("<II", header, 80)
    base = entry_lba * sector_size
    result = []
    for index in range(min(count, 256)):
        pos = base + index * entry_size
        if entry_size < 128 or pos + entry_size > len(data):
            break
        entry = data[pos:pos + entry_size]
        if entry[:16] == b"\0" * 16:
            continue
        first, last = struct.unpack_from("<QQ", entry, 32)
        name = entry[56: min(128, entry_size)].decode("utf-16le", "ignore").split("\0", 1)[0]
        result.append((name, first, last))
    return result


def run_tests() -> bool:
    class Tests(unittest.TestCase):
        def test_rejection_list(self):
            for token in REJECT:
                with self.subTest(token=token), self.assertRaises(ValueError):
                    reject_unsafe("cat /proc/x" + token + "x")
            reject_unsafe("cat /proc/iomem")

        def test_exact_allowlist_passes_forbidden_substring(self):
            # The one read-only property that legitimately contains "flash" is
            # permitted by exact full-string equality and also sits in the fixed
            # read-only whitelist.
            reject_unsafe("getprop ro.boot.flash.locked")
            check_command_list([("getprop_ro_boot_flash_locked.txt",
                                 "getprop ro.boot.flash.locked", "shell", 60)])

        def test_allowlist_variants_rejected(self):
            # Extra arguments / shell metacharacters / case changes are not the
            # exact allowlisted string, so they fall through to the substring
            # scan (never matched by prefix/contains) and are rejected.
            for variant in ("getprop ro.boot.flash.locked; reboot",
                            "getprop ro.boot.flash.locked >x",
                            "getprop ro.boot.flash.locked;",
                            "getprop ro.boot.flash.locked extra",
                            "getprop ro.boot.FLASH.locked"):
                with self.subTest(variant=variant), self.assertRaises(ValueError):
                    reject_unsafe(variant)

        def test_quote_spliced_forms_rejected(self):
            # The old shell quote-splice bypass hides "flash" from the substring
            # scan, so it survives reject_unsafe alone; it is rejected because it
            # is no longer one of the fixed read-only command strings.
            for variant in ("getprop ro.boot.fla''sh.locked",
                            "getprop ro.boot.fl''ash.locked",
                            "getprop ro.boot.flash.locke'd"):
                with self.subTest(variant=variant), self.assertRaises(ValueError):
                    check_command_list([("getprop_ro_boot_flash_locked.txt", variant, "shell", 60)])

        def test_redaction(self):
            s = "FAKE_SERIAL_123"
            text = "androidboot.serialno=" + s + " androidboot.hw_sn=aa 0123456789abcdef 00:11:22:33:44:55 Serial: test"
            redacted = redact_text(text, s, mask_long_hex=True)
            for marker in (s, "0123456789abcdef", "00:11:22:33:44:55", "test"):
                self.assertNotIn(marker, redacted)
            self.assertEqual(strip_cpu_serial("Processor: x\nSerial : secret\n"), "Processor: x\n")

        def test_dd_status_is_not_part_of_binary(self):
            raw = b"\x00\x01\x02" + b"8+0 records in\n8+0 records out\n32768 bytes (32 K) copied, 0.01 s, 3 M/s\n"
            self.assertEqual(strip_dd_status(raw), b"\x00\x01\x02")

        def test_device_selection_nuwa_recovery(self):
            listing = ("List of devices attached\nNUWA_FAKE recovery product:nuwa model:X\n"
                       "ENUMA_FAKE device product:enuma model:X device:enuma\n")
            self.assertEqual(select_enuma_device(listing), "ENUMA_FAKE")

        def test_device_selection_requires_exactly_one(self):
            with self.assertRaises(CollectionError):
                select_enuma_device("N recovery product:nuwa device:nuwa\n")
            with self.assertRaises(CollectionError):
                select_enuma_device("A device product:enuma device:enuma\nB device product:enuma device:enuma\n")

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adb", default=DEFAULT_ADB, help="adb executable path")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return 0 if run_tests() else 1
    if args.dry_run:
        # Read-only discovery makes the dry-run list exact for currently present
        # LUNs and requested by-name partitions; it does not create capture files.
        listing = subprocess.run([args.adb, "devices", "-l"], stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, timeout=60, check=False)
        if listing.returncode != 0:
            print(f"STOP: adb devices -l failed (exit {listing.returncode})")
            return 2
        try:
            serial = select_enuma_device(listing.stdout.decode("utf-8", "replace"))
        except CollectionError as exc:
            print(f"STOP: {exc}")
            return 2
        identity = adb_run(args.adb, serial, "getprop ro.product.device", "shell", 60)
        if identity.returncode != 0 or identity.stdout.decode("utf-8", "replace").strip() != "enuma":
            print("STOP: selected device identity/root-shell check failed; no collection attempted")
            return 2
        discovery = {}
        for artifact, command in (("sys_block_names.txt", "ls -1 /sys/block"),
                                  ("by_name_links.txt", "ls -l /dev/block/by-name")):
            proc = adb_run(args.adb, serial, command, "shell", 60)
            if proc.returncode != 0:
                print(f"STOP: dry-run discovery {artifact} failed (exit {proc.returncode})")
                return 2
            discovery[artifact] = proc.stdout
        luns = [lun for lun in LUNS if lun in discovery["sys_block_names.txt"].decode("utf-8", "replace").split()]
        parts = [part for part in PARTITIONS if part in parse_links(discovery["by_name_links.txt"].decode("utf-8", "replace"))]
        commands = base_commands() + dynamic_commands(luns, parts)
        check_command_list(commands)
        print("DRY RUN (exact approved collection list for current enuma LUNs/partitions):")
        for name, command, transport, timeout in commands:
            print(f"{name}: adb -s <REDACTED> {transport} su -c {shlex.quote(command)} [timeout={timeout}s]")
        return 0

    adb = args.adb
    # The only unscoped adb invocation is the required enumeration; no device is addressed.
    listing = subprocess.run([adb, "devices", "-l"], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, timeout=60, check=False)
    if listing.returncode != 0:
        print(f"STOP: adb devices -l failed (exit {listing.returncode})")
        return 2
    try:
        serial = select_enuma_device(listing.stdout.decode("utf-8", "replace"))
    except CollectionError as exc:
        print(f"STOP: {exc}")
        return 2

    # Verify root-shell command path and device identity before creating output.
    identity = adb_run(adb, serial, "getprop ro.product.device", "shell", 60)
    if identity.returncode != 0:
        print(f"STOP: enuma identity/root-shell check failed (exit {identity.returncode}); no collection attempted")
        return 2
    if identity.stdout.decode("utf-8", "replace").strip() != "enuma":
        print("STOP: selected device did not report ro.product.device=enuma; no collection attempted")
        return 2

    now = datetime.now(timezone.utc)
    capture = Path(__file__).resolve().parent.parent / ".cache" / "live-capture" / now.strftime("%Y%m%dT%H%M%S%fZ")
    capture.mkdir(parents=True, exist_ok=False)
    summary: list[str] = ["Device observation: read-only collection; no writes issued.", f"Capture: {capture.name}"]
    artifacts: dict[str, tuple[int, str]] = {}
    withheld_artifacts: dict[str, tuple[int, str, str]] = {}
    failures: list[str] = []
    versions = subprocess.run([adb, "-s", serial, "version"], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=60, check=False)
    summary.append(f"adb version command exit={versions.returncode}; {redact_text(versions.stdout.decode('utf-8','replace').strip(), serial)}")

    # Initial fixed commands needed to discover which optional LUN/partitions exist.
    initial = base_commands()
    check_command_list(initial)
    results: dict[str, bytes] = {}
    for name, command, transport, timeout in initial:
        try:
            proc = adb_run(adb, serial, command, transport, timeout)
        except subprocess.TimeoutExpired:
            failures.append(f"{name}: timeout after {timeout}s")
            continue
        if proc.returncode:
            failures.append(f"{name}: exit {proc.returncode}")
            continue
        data = proc.stdout
        if name == "proc_cpuinfo.txt":
            data = strip_cpu_serial(data.decode("utf-8", "replace")).encode()
        if name in ("proc_cmdline.txt", "dmesg_first_400.txt", "dmesg_last_400.txt"):
            data = redact_text(data.decode("utf-8", "replace"), serial, mask_long_hex=(name == "proc_cmdline.txt")).encode()
        if name.endswith(".bin"):
            written = write_artifact(capture, name, data, serial)
            if written is None:
                withheld_artifacts[name] = (len(data), sha256(data), "contains device serial; bytes not persisted")
                failures.append(f"{name}: withheld because it contained the device serial")
                continue
            artifacts[name] = written
        else:
            safe = redact_text(data.decode("utf-8", "replace"), serial).encode()
            written = write_artifact(capture, name, safe, serial)
            if written is None:
                failures.append(f"{name}: withheld because it contained the device serial")
                continue
            artifacts[name] = written
            data = safe
        results[name] = data

    # A denied/failed initial su call is an unexpected condition: stop, retaining prior evidence.
    if not any(name in artifacts for name in ("proc_iomem.txt", "by_name_links.txt")):
        (capture / "collection_summary.txt").write_text("STOP: initial su collection failed; no bypass attempted.\n", encoding="utf-8")
        print(f"STOP: initial root-shell collection failed. Capture directory: {capture.name}")
        return 3

    links = parse_links(results.get("by_name_links.txt", b"").decode("utf-8", "replace"))
    lun_listing = results.get("sys_block_names.txt", b"").decode("utf-8", "replace").split()
    present_luns = [lun for lun in LUNS if lun in lun_listing]
    partition_names = [part for part in PARTITIONS if part in links]
    dynamic = dynamic_commands(present_luns, partition_names)
    check_command_list(dynamic)
    for name, command, transport, timeout in dynamic:
        try:
            proc = adb_run(adb, serial, command, transport, timeout)
        except subprocess.TimeoutExpired:
            failures.append(f"{name}: timeout after {timeout}s")
            continue
        if proc.returncode:
            failures.append(f"{name}: exit {proc.returncode}")
            continue
        data = proc.stdout
        if command.startswith("dd "):
            data = strip_dd_status(data)
        written = write_artifact(capture, name, data, serial)
        if written is None:
            failures.append(f"{name}: withheld because it contained the device serial")
            continue
        artifacts[name] = written
        results[name] = data

    # Parse GPTs and device/host partition hash comparisons, preserving no identifiers.
    gpt_facts = []
    for lun in present_luns:
        sec_raw = results.get(f"{lun}_logical_block_size.txt", b"").strip()
        try:
            sector = int(sec_raw)
        except ValueError:
            continue
        gpt = parse_gpt(results.get(f"{lun}_first_32768.bin", b""), sector)
        if gpt:
            userdata = next((p for p in gpt if p[0].lower() == "userdata"), None)
            user_link = links.get("userdata", "")
            link_lun_match = re.search(r"\b(sd[a-f])\d+\b", user_link)
            user_lun = link_lun_match.group(1) if link_lun_match else "unknown"
            fact = f"GPT {lun}: logical block size={sector}; userdata link LUN={user_lun}"
            if userdata:
                fact += f"; userdata first LBA={userdata[1]}; last LBA={userdata[2]}"
            else:
                fact += "; userdata GPT entry not present in captured first 32768 bytes"
            gpt_facts.append(fact)

    xchecks = []
    for part in PARTITIONS:
        local_name = f"partition_{part}.bin"
        device_name = f"partition_{part}_device_sha256.txt"
        if local_name in artifacts and device_name in results:
            host_hash = artifacts[local_name][1]
            m = re.search(rb"\b([0-9a-fA-F]{64})\b", results[device_name])
            device_hash = m.group(1).decode().lower() if m else "unparsed"
            xchecks.append(f"{part}: {'MATCH' if host_hash == device_hash else 'MISMATCH'} host={host_hash} device={device_hash}")

    fdt_hash = artifacts.get("live_fdt.bin", (0, "missing"))[1]
    if "live_fdt.bin" in withheld_artifacts:
        fdt_hash = withheld_artifacts["live_fdt.bin"][1]
    summary += [f"Fresh FDT sha256={fdt_hash}; earlier capture={'EQUAL' if fdt_hash == EARLIER_FDT_SHA256 else 'DIFFERENT' if fdt_hash != 'missing' else 'NOT CAPTURED'} ({EARLIER_FDT_SHA256})"]
    if "live_fdt.bin" in withheld_artifacts:
        size, digest, reason = withheld_artifacts["live_fdt.bin"]
        summary.append(f"FDT artifact not persisted ({reason}); in-memory size={size}, sha256={digest}.")
    summary.extend(gpt_facts or ["GPT: no complete GPT header parsed from the collected LUN prefixes."])
    summary.extend(f"Partition hash cross-check: {line}" for line in xchecks)
    if not xchecks:
        summary.append("Partition hash cross-check: none available (partitions absent or read failed).")
    iomem = results.get("proc_iomem.txt", b"").decode("utf-8", "replace")
    reserved = [line.strip() for line in iomem.splitlines() if re.search(r"reserved|secure|splash|ramoops", line, re.I)]
    summary.append("/proc/iomem reserved-like regions: " + (" | ".join(reserved) if reserved else "none matched"))
    zones = results.get("thermal_zone_names.txt", b"").decode("utf-8", "replace").splitlines()
    summary.append(f"Thermal zone count: {sum(1 for x in zones if 'thermal_zone' in x)}")
    for cpu in CPUS:
        freq = results.get(f"{cpu}_scaling_available_frequencies.txt", b"").decode("utf-8", "replace").strip()
        if freq:
            summary.append(f"{cpu} scaling_available_frequencies: {freq}")
    gpu = results.get("gpu_gpu_available_frequencies.txt", b"").decode("utf-8", "replace").strip()
    summary.append(f"GPU available frequencies: {gpu or 'unavailable'}")
    summary.append("Skipped/missing or failed commands: " + ("; ".join(failures) if failures else "none"))
    summary.append("Artifacts (name, bytes, sha256):")
    summary.extend(f"  {name}: {size}, {digest}" for name, (size, digest) in sorted(artifacts.items()))
    summary.extend(f"  {name}: WITHHELD, {size}, {digest} ({reason})" for name, (size, digest, reason) in sorted(withheld_artifacts.items()))
    (capture / "collection_summary.txt").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
