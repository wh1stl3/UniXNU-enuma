#!/usr/bin/env python3
"""Import the extracted enuma vendor tree into the uefi-enuma firmware repo.

Read-only with respect to the device: no adb, no device access. Only copies the
already-extracted files from the git-ignored scratch dir into the firmware repo
(Binaries/enuma and enumaPkg/EnumaInputs), gated on provenance hashes and on git
ignore/track state. Idempotent; refuses to overwrite a differing file unless
--force. stdlib only, Python 3.10-compatible.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

EXPECTED_XBL_SHA256 = "7ac67cbf4c7870a972cb4ffd9cc09d5db1c96b7f4a5abc7a80c0da9cabc65057"

REPORT_REL = ".cache/extract-root/reports/enuma-oem-modules.json"
VENDOR_ROOT_REL = ".cache/extract-root/out/firmware-vendor"
LIVE_CAPTURE_REL = ".cache/live-capture"

VENDOR_INC_NAMES = ("Vendor.apriori.inc", "Vendor.dsc.inc", "Vendor.fdf.inc", "Vendor.raw.fdf.inc")
RAW_INC_REL = "Platforms/Xiaomi/enumaPkg/Include/RAW.inc"
ENUMA_INPUTS_REL = "Platforms/Xiaomi/enumaPkg/EnumaInputs"
BINARIES_ENUMA_REL = "Binaries/enuma"

# Nine non-panel raw inputs extracted separately (FFS GUID verified equal to the
# RAW.inc entry; each is the exact RAW section payload). These are the RAW.inc
# entries NOT gated behind !if $(USE_CUSTOM_DISPLAY_DRIVER). sha256 recorded by
# the extracting worker; a mismatch or empty file -> refuse.
RAW_EXTRA_SHA256 = {
    "SecParti.cfg": "32e1f996b0e2bfb592d30a6d07b927377ddc0dad31a5e639117bc042b6018b2a",
    "uefipil.cfg": "2a4bef8bece3dc6cc6b0cadd462f709b07baa547571e3da4a5230c6fc202fe93",
    "QcomChargerCfg.cfg": "52eea886c6359e2477aea4b8bd02dceae02a0da52ffeed280e68216536a3b341",
    "BATTERY.PROVISION": "41e8b47cee9ff5d5c5a892f7bb225c2b16296bc511462f1dd06abfa833dc5080",
    "GY.BATTERY.PROVISION": "731aabbf0701edb494a2c947554d1d99e5d446bd353656875d0d5ef93f3b6f7e",
    "NVT.BATTERY.PROVISION": "181100111e8ff0d577443cccf0117c30a79ffed6a6c0fdc63e3a60f5ab1ce8fd",
    "BATTERY.PROVISION1": "138ee2871c4d2dadb0f06ff41547a4521e9fd496a0abf4c64bcbab355de80d2e",
    "BATTERY.PROVISION2": "5f05cd9a6d16d22b7de5171955fec3304ddc57ae56b4dd7b58532c9ad8830cbb",
    "SUNWODA.M82.BATTERY.PROVISION": "83a288a1d55559dd5705f1bcd59ae09fae029cbf57bd262feae55914b94d5ba7",
}


class ImportAbort(Exception):
    """A provenance or git-safety gate failed; nothing was written."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(uefi: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(uefi), *args],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def git_tracked(uefi: Path, rel: str) -> list[str]:
    proc = _git(uefi, "ls-files", "--", rel)
    if proc.returncode != 0:
        raise ImportAbort(
            f"git ls-files {rel!r} failed (exit {proc.returncode}): "
            f"{proc.stderr.decode('utf-8', 'replace').strip()}")
    return [line for line in proc.stdout.decode("utf-8", "replace").splitlines() if line.strip()]


def git_ignored(uefi: Path, rel: str) -> bool:
    return _git(uefi, "check-ignore", "--no-index", "-q", "--", rel).returncode == 0


def load_report(device_root: Path, expected_xbl: str) -> dict:
    report = device_root / REPORT_REL
    if not report.is_file():
        raise ImportAbort(f"provenance report missing: {report}")
    data = json.loads(report.read_text(encoding="utf-8"))
    if data.get("xbl_sha256") != expected_xbl:
        raise ImportAbort(
            f"recorded xbl_sha256 {data.get('xbl_sha256')!r} != expected {expected_xbl}")
    return data


def xbl_source_matches(device_root: Path, expected: str) -> tuple[list[Path], list[Path]]:
    """Return (matching, ignored) capture paths; require at least one match."""
    copies = sorted((device_root / LIVE_CAPTURE_REL).glob("*/partition_xbl_a.bin"))
    if not copies:
        raise ImportAbort("no source xbl copy found under .cache/live-capture/*/partition_xbl_a.bin")
    matched = [p for p in copies if sha256_file(p) == expected]
    ignored = [p for p in copies if p not in matched]
    if not matched:
        raise ImportAbort("no source xbl copy matches the recorded xbl_sha256")
    return matched, ignored


def _plan_item(src: Path, dest: Path, rel: str, category: str, src_sha: str, force: bool) -> dict:
    dest_sha = sha256_file(dest) if dest.is_file() else None
    if dest_sha is None:
        action = "write"
    elif dest_sha == src_sha:
        action = "unchanged"
    elif force:
        action = "overwrite"
    else:
        action = "refused"
    return {"src": src, "dest": dest, "rel": rel, "category": category,
            "src_sha": src_sha, "dest_sha": dest_sha, "action": action}


def build_plan(vendor_root: Path, uefi: Path, report: dict, force: bool,
               extra_raw_sha256: dict) -> dict:
    modules = report.get("selected_modules") or []
    items = []
    module_files = {"efi": 0, "inf": 0, "depex": 0}
    efi_checked = 0
    for mod in modules:
        name = mod["name"]
        src_dir = vendor_root / "Binaries" / "enuma" / name
        for ext in (".efi", ".inf", ".depex"):
            src = src_dir / (name + ext)
            if not src.is_file():
                if ext == ".depex":
                    continue  # a few modules carry no depex section
                raise ImportAbort(f"missing module file: {src}")
            src_sha = sha256_file(src)
            if ext == ".efi":
                efi_checked += 1
                if src_sha != mod.get("pe_sha256"):
                    raise ImportAbort(
                        f"pe_sha256 mismatch for {name}: efi {src_sha} != recorded {mod.get('pe_sha256')}")
            rel = f"{BINARIES_ENUMA_REL}/{name}/{name}{ext}"
            items.append(_plan_item(src, uefi / rel, rel, "module", src_sha, force))
            module_files[ext.lstrip(".")] += 1

    raw_names = set()
    # Report-recorded raw inputs: the two panel XMLs + uefiplat.cfg.
    for raw_name in sorted(report.get("raw_inputs") or {}):
        src = vendor_root / "raw" / raw_name
        if not src.is_file():
            raise ImportAbort(f"missing raw file: {src}")
        src_sha = sha256_file(src)
        expected = report["raw_inputs"][raw_name]
        if src_sha != expected:
            raise ImportAbort(f"raw sha256 mismatch for {raw_name}: {src_sha} != recorded {expected}")
        raw_names.add(raw_name)
        rel = f"{BINARIES_ENUMA_REL}/RawFiles/{raw_name}"
        items.append(_plan_item(src, uefi / rel, rel, "raw", src_sha, force))
    # Nine config/provision inputs with a hardcoded provenance table.
    for raw_name, expected in sorted(extra_raw_sha256.items()):
        src = vendor_root / "raw" / raw_name
        if not src.is_file():
            raise ImportAbort(f"missing raw file: {raw_name}")
        if src.stat().st_size == 0:
            raise ImportAbort(f"raw file is empty: {raw_name}")
        src_sha = sha256_file(src)
        if src_sha != expected:
            raise ImportAbort(f"raw sha256 mismatch for {raw_name}: {src_sha} != expected {expected}")
        raw_names.add(raw_name)
        rel = f"{BINARIES_ENUMA_REL}/RawFiles/{raw_name}"
        items.append(_plan_item(src, uefi / rel, rel, "raw", src_sha, force))

    for inc_name in VENDOR_INC_NAMES:
        src = vendor_root / inc_name
        if not src.is_file():
            raise ImportAbort(f"missing vendor inc file: {src}")
        rel = f"{ENUMA_INPUTS_REL}/{inc_name}"
        items.append(_plan_item(src, uefi / rel, rel, "inc", sha256_file(src), force))
    return {"items": items, "module_files": module_files,
            "efi_checked": efi_checked, "raw_names": raw_names,
            "modules": len(modules)}


def verify_git_safety(uefi: Path) -> None:
    # Binaries is an uninitialised gitlink; anything under Binaries/enuma/ must
    # stay untracked and git-ignored.
    tracked = git_tracked(uefi, BINARIES_ENUMA_REL)
    if tracked:
        raise ImportAbort(f"{BINARIES_ENUMA_REL}/ contains tracked files; refusing ({len(tracked)})")
    if not git_ignored(uefi, BINARIES_ENUMA_REL + "/"):
        raise ImportAbort(f"{BINARIES_ENUMA_REL}/ is not git-ignored; refusing to write untracked vendor binaries")
    # EnumaInputs holds generated text that will be committed, but must not
    # already be tracked at import time.
    tracked_inc = git_tracked(uefi, ENUMA_INPUTS_REL)
    if tracked_inc:
        raise ImportAbort(f"{ENUMA_INPUTS_REL} contains tracked files; refusing ({len(tracked_inc)})")


def raw_inc_references(uefi: Path) -> list[tuple[str, bool]]:
    """Return (name, gated) pairs from RAW.inc, tracking !if/!endif nesting."""
    raw_inc = uefi / RAW_INC_REL
    if not raw_inc.is_file():
        return []
    refs = []
    depth = 0
    for raw_line in raw_inc.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if line.startswith("!if "):
            depth += 1
            continue
        if line == "!endif":
            depth = max(0, depth - 1)
            continue
        m = re.search(r"SECTION\s+RAW\s*=\s*Binaries/enuma/RawFiles/(\S+)", raw_line)
        if m:
            refs.append((m.group(1), depth > 0))
    return refs


def raw_inc_gaps(uefi: Path, raw_names: set) -> tuple[list[str], int, list[str], list[str]]:
    """Return (needed_now_gaps, gated_count, gated_missing, imported_unreferenced)."""
    refs = raw_inc_references(uefi)
    needed = [n for n, g in refs if not g]
    gated = [n for n, g in refs if g]
    needed_gaps = [n for n in needed if n not in raw_names]
    gated_missing = [n for n in gated if n not in raw_names]
    unreferenced = [n for n in sorted(raw_names) if n not in {r[0] for r in refs}]
    return needed_gaps, len(gated), gated_missing, unreferenced


def execute_plan(plan: dict) -> None:
    for item in plan["items"]:
        if item["action"] in ("write", "overwrite"):
            item["dest"].parent.mkdir(parents=True, exist_ok=True)
            item["dest"].write_bytes(item["src"].read_bytes())


def run_import(device_root: Path, uefi: Path, *, dry_run: bool, force: bool,
               expected_xbl: str = EXPECTED_XBL_SHA256,
               extra_raw_sha256: dict | None = None) -> dict:
    if extra_raw_sha256 is None:
        extra_raw_sha256 = RAW_EXTRA_SHA256
    report = load_report(device_root, expected_xbl)
    xbl_sha = report["xbl_sha256"]
    matched, ignored = xbl_source_matches(device_root, xbl_sha)

    vendor_root = device_root / VENDOR_ROOT_REL
    if not vendor_root.is_dir():
        raise ImportAbort(f"vendor tree missing: {vendor_root}")

    verify_git_safety(uefi)
    plan = build_plan(vendor_root, uefi, report, force, extra_raw_sha256)

    refused = [it for it in plan["items"] if it["action"] == "refused"]
    if refused:
        joined = ", ".join(f"{it['rel']} (dest {it['dest_sha']})" for it in refused)
        raise ImportAbort(f"refusing to overwrite {len(refused)} differing file(s); use --force: {joined}")

    needed_gaps, gated_count, gated_missing, unreferenced = raw_inc_gaps(uefi, plan["raw_names"])

    if not dry_run:
        execute_plan(plan)

    actions = {"write": 0, "unchanged": 0, "overwrite": 0, "refused": 0}
    raw_files = 0
    inc_files = 0
    for it in plan["items"]:
        actions[it["action"]] += 1
        if it["category"] == "raw":
            raw_files += 1
        elif it["category"] == "inc":
            inc_files += 1

    needed_count = len([n for n, g in raw_inc_references(uefi) if not g])
    return {
        "dry_run": dry_run,
        "force": force,
        "xbl_sha256": xbl_sha,
        "xbl_copies": len(matched) + len(ignored),
        "xbl_matched": [p.parent.name for p in matched],
        "xbl_ignored": [p.parent.name for p in ignored],
        "efi_checked": plan["efi_checked"],
        "modules": plan["modules"],
        "module_files": plan["module_files"],
        "raw_files": raw_files,
        "inc_files": inc_files,
        "total_files": len(plan["items"]),
        "write": actions["write"],
        "unchanged": actions["unchanged"],
        "overwrite": actions["overwrite"],
        "refused": actions["refused"],
        "needed_now_count": needed_count,
        "needed_now_gaps": needed_gaps,
        "gated_count": gated_count,
        "gated_missing": gated_missing,
        "imported_unreferenced_raw": unreferenced,
    }


def format_summary(s: dict) -> str:
    mode = "dry-run (nothing written)" if s["dry_run"] else "live"
    lines = [
        f"enuma vendor import - {mode}, force={s['force']}",
        f"  provenance: report=present, xbl_sha256={s['xbl_sha256']}",
        f"              xbl_copies={s['xbl_copies']} matched={s['xbl_matched']} "
        f"ignored_mismatch={s['xbl_ignored']}",
        f"              efi_pe256_verified={s['efi_checked']}",
        f"  files: modules={s['modules']} (efi={s['module_files']['efi']} "
        f"inf={s['module_files']['inf']} depex={s['module_files']['depex']}) "
        f"raw={s['raw_files']} inc={s['inc_files']} total={s['total_files']}",
        f"  actions: write={s['write']} unchanged={s['unchanged']} "
        f"overwrite={s['overwrite']} refused={s['refused']}",
        f"  RAW.inc split: needed-now (not gated)={s['needed_now_count']} entries, "
        f"missing={len(s['needed_now_gaps'])}",
    ]
    for name in s["needed_now_gaps"]:
        lines.append(f"      MISSING (needed now): {name}")
    lines.append(f"  RAW.inc gated by USE_CUSTOM_DISPLAY_DRIVER (not required, flag=0): "
                 f"{s['gated_count']} entries ({len(s['gated_missing'])} without source file)")
    if s["imported_unreferenced_raw"]:
        lines.append("  imported raw not referenced by RAW.inc: "
                     + ", ".join(s["imported_unreferenced_raw"]))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uefi", default=None,
                        help="firmware repo path (default: ../uefi-enuma relative to device repo root)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return 0 if run_tests() else 1

    device_root = Path(__file__).resolve().parent.parent
    if args.uefi:
        uefi = Path(args.uefi).expanduser().resolve()
    else:
        uefi = (device_root / ".." / "uefi-enuma").resolve()

    try:
        summary = run_import(device_root, uefi, dry_run=args.dry_run, force=args.force)
    except ImportAbort as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 2
    print(format_summary(summary))
    return 0


# --- self-test ---------------------------------------------------------------

def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _make_fake_tree(tmp: Path, *, ignore_binaries: bool = True, efi_mismatch: bool = False) -> tuple[Path, Path, dict]:
    device = tmp / "device"
    vendor = device / ".cache" / "extract-root" / "out" / "firmware-vendor"
    module_dir = vendor / "Binaries" / "enuma" / "CPRDxe"
    module_dir.mkdir(parents=True)
    (vendor / "raw").mkdir(parents=True)
    report_dir = device / ".cache" / "extract-root" / "reports"
    report_dir.mkdir(parents=True)
    live = device / ".cache" / "live-capture" / "20260101T000000Z"
    live.mkdir(parents=True)

    efi = b"MZ fake EFI payload"
    inf = b"[Defines]\n  BASE_NAME = CPRDxe\n"
    depex = b"\x02\x06"
    panel = b"<panel/>"
    xbl = b"FAKE XBL"
    (module_dir / "CPRDxe.efi").write_bytes(efi)
    (module_dir / "CPRDxe.inf").write_bytes(inf)
    (module_dir / "CPRDxe.depex").write_bytes(depex)
    (vendor / "raw" / "Panel_test.xml").write_bytes(panel)
    extra_raw = {}
    for name in sorted(RAW_EXTRA_SHA256):
        content = (f"fake:{name}").encode()
        (vendor / "raw" / name).write_bytes(content)
        extra_raw[name] = _sha(content)
    for inc_name in VENDOR_INC_NAMES:
        (vendor / inc_name).write_text("  INF Binaries/enuma/CPRDxe/CPRDxe.inf\n")
    (live / "partition_xbl_a.bin").write_bytes(xbl)

    report = {
        "xbl_sha256": _sha(xbl),
        "selected_modules": [
            {"name": "CPRDxe", "inf": "Binaries/enuma/CPRDxe/CPRDxe.inf",
             "pe_sha256": "0" * 64 if efi_mismatch else _sha(efi),
             "depex_sha256": _sha(depex)},
        ],
        "raw_inputs": {"Panel_test.xml": _sha(panel)},
    }
    (report_dir / "enuma-oem-modules.json").write_text(json.dumps(report))

    uefi = tmp / "uefi"
    inc_dir = uefi / "Platforms" / "Xiaomi" / "enumaPkg" / "Include"
    inc_dir.mkdir(parents=True)
    (inc_dir / "RAW.inc").write_text(
        "  FILE FREEFORM = 00000000-0000-0000-0000-000000000000 {\n"
        "    SECTION RAW = Binaries/enuma/RawFiles/Panel_test.xml\n"
        "    SECTION RAW = Binaries/enuma/RawFiles/SecParti.cfg\n"
        "  }\n")
    (uefi / ".gitignore").write_text("/Binaries/enuma/\n" if ignore_binaries else "# nothing ignored\n")
    subprocess.run(["git", "init", "-q", str(uefi)], check=True)
    return device, uefi, {"xbl_sha256": report["xbl_sha256"], "efi": efi, "extra_raw": extra_raw}


def run_tests() -> bool:
    class Tests(unittest.TestCase):
        def _run(self, device, uefi, meta, **kw):
            kw.setdefault("expected_xbl", meta["xbl_sha256"])
            kw.setdefault("extra_raw_sha256", meta["extra_raw"])
            return run_import(device, uefi, dry_run=kw.pop("dry_run", False),
                              force=kw.pop("force", False), **kw)

        def test_live_import_writes_and_is_idempotent(self):
            with tempfile.TemporaryDirectory() as tmp:
                device, uefi, meta = _make_fake_tree(Path(tmp))
                first = self._run(device, uefi, meta, dry_run=False)
                # efi+inf+depex + 1 report raw + 9 extra raw + 4 inc
                self.assertEqual(first["write"], 17)
                self.assertEqual(first["unchanged"], 0)
                self.assertEqual(first["refused"], 0)
                self.assertEqual(first["raw_files"], 10)
                self.assertEqual(first["needed_now_gaps"], [])
                self.assertEqual(first["gated_count"], 0)
                self.assertEqual((uefi / "Binaries/enuma/CPRDxe/CPRDxe.efi").read_bytes(), meta["efi"])
                second = self._run(device, uefi, meta, dry_run=False)
                self.assertEqual(second["write"], 0)
                self.assertEqual(second["unchanged"], 17)

        def test_dry_run_writes_nothing(self):
            with tempfile.TemporaryDirectory() as tmp:
                device, uefi, meta = _make_fake_tree(Path(tmp))
                result = self._run(device, uefi, meta, dry_run=True)
                self.assertTrue(result["dry_run"])
                self.assertEqual(result["write"], 17)
                self.assertFalse((uefi / "Binaries").exists())
                self.assertFalse((uefi / "Platforms" / "Xiaomi" / "enumaPkg" / "EnumaInputs").exists())

        def test_efi_hash_mismatch_rejected(self):
            with tempfile.TemporaryDirectory() as tmp:
                device, uefi, meta = _make_fake_tree(Path(tmp), efi_mismatch=True)
                with self.assertRaises(ImportAbort):
                    self._run(device, uefi, meta, dry_run=False)
                self.assertFalse((uefi / "Binaries").exists())

        def test_non_ignored_destination_rejected(self):
            with tempfile.TemporaryDirectory() as tmp:
                device, uefi, meta = _make_fake_tree(Path(tmp), ignore_binaries=False)
                with self.assertRaises(ImportAbort):
                    self._run(device, uefi, meta, dry_run=False)
                self.assertFalse((uefi / "Binaries").exists())

        def test_refuse_overwrite_differing_file_unless_force(self):
            with tempfile.TemporaryDirectory() as tmp:
                device, uefi, meta = _make_fake_tree(Path(tmp))
                self._run(device, uefi, meta, dry_run=False)
                target = uefi / "Binaries" / "enuma" / "CPRDxe" / "CPRDxe.efi"
                target.write_bytes(b"different content")
                with self.assertRaises(ImportAbort):
                    self._run(device, uefi, meta, dry_run=False)
                self.assertEqual(target.read_bytes(), b"different content")
                forced = self._run(device, uefi, meta, dry_run=False, force=True)
                self.assertEqual(forced["overwrite"], 1)
                self.assertEqual(target.read_bytes(), meta["efi"])

        def test_wrong_extra_raw_hash_rejected(self):
            with tempfile.TemporaryDirectory() as tmp:
                device, uefi, meta = _make_fake_tree(Path(tmp))
                bad = dict(meta["extra_raw"])
                bad["SecParti.cfg"] = "0" * 64
                with self.assertRaises(ImportAbort):
                    self._run(device, uefi, meta, dry_run=False, extra_raw_sha256=bad)
                self.assertFalse((uefi / "Binaries").exists())

        def test_raw_inc_gate_split(self):
            with tempfile.TemporaryDirectory() as tmp:
                uefi = Path(tmp) / "uefi"
                inc_dir = uefi / "Platforms" / "Xiaomi" / "enumaPkg" / "Include"
                inc_dir.mkdir(parents=True)
                (inc_dir / "RAW.inc").write_text(
                    "!if $(USE_CUSTOM_DISPLAY_DRIVER) == 1\n"
                    "  FILE FREEFORM = a {\n"
                    "    SECTION RAW = Binaries/enuma/RawFiles/Panel_gated.xml\n"
                    "  }\n"
                    "!endif\n"
                    "  FILE FREEFORM = b {\n"
                    "    SECTION RAW = Binaries/enuma/RawFiles/SecParti.cfg\n"
                    "  }\n"
                    "  FILE FREEFORM = c {\n"
                    "    SECTION RAW = Binaries/enuma/RawFiles/needed_missing.cfg\n"
                    "  }\n")
                refs = raw_inc_references(uefi)
                self.assertEqual(refs, [("Panel_gated.xml", True),
                                        ("SecParti.cfg", False),
                                        ("needed_missing.cfg", False)])
                gaps, gated_count, gated_missing, unreferenced = raw_inc_gaps(uefi, {"SecParti.cfg"})
                self.assertEqual(gaps, ["needed_missing.cfg"])
                self.assertEqual(gated_count, 1)
                self.assertEqual(gated_missing, ["Panel_gated.xml"])
                self.assertEqual(unreferenced, [])

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()


if __name__ == "__main__":
    sys.exit(main())
