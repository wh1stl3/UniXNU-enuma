#!/usr/bin/env python3
"""Stage and inspect enuma vendor_boot v3 DTBs from the proven read-only backup.

Ownership: UniXNU-enuma only. The backup root is read-only per
`../../docs/backup-manifest-2026-11-06.md` section E: files are copied one at a
time into `.cache/firmware/` (never whole directories), nothing is written back
to the backup, and every processing step stays inside `.cache/firmware/`.

Reports and provenance are sanitized: serial, MAC, ECID, and kernel bootargs are
never emitted. The raw artifacts stay in the git-ignored `.cache/firmware/` tree.

Commands
--------
stage       Copy one proven backup file into .cache/firmware/ and record its
            sanitized provenance sidecar (`.provenance.json`).
inspect     Parse the staged vendor_boot v3 header, walk the concatenated DTB
            boundaries structurally (advancing by each FDT `totalsize`, not by
            blind magic scan), validate each blob with `dtc`, inventory identity
            (model / compatible / qcom,msm-id / qcom,board-id) and
            memory / reserved-memory / CPU-GPU OPP presence, then compare the
            staged live FDT identity against the candidates.
self-test   Run the synthetic parser boundary tests (no device data).

Exit codes: 0 success, 1 validation/hash/boundary failure, 2 usage error.
"""

import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # UniXNU-enuma
FIRMWARE = ROOT / ".cache" / "firmware"

FDT_MAGIC = 0xD00DFEED
VENDOR_MAGIC = b"VNDRBOOT"
FDT_HEADER = struct.Struct(">10I")                  # 10 big-endian u32

# vendor_boot v3 header (little-endian), offsets from AOSP bootimg.h.
_VB_V3_FIELDS = (
    ("magic", 0, 8),
    ("header_version", 8, 4),
    ("page_size", 12, 4),
    ("kernel_addr", 16, 4),
    ("ramdisk_addr", 20, 4),
    ("vendor_ramdisk_size", 24, 4),
    ("cmdline", 28, 2048),
    ("tags_addr", 2076, 4),
    ("name", 2080, 16),
    ("header_size", 2096, 4),
    ("dtb_size", 2100, 4),
    ("dtb_addr", 2104, 8),
)
_VB_V3_HEADER_SIZE = 2112


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _round_up(value, align):
    return (value + align - 1) // align * align


def _require_within(path, base, what):
    """Processing inputs/outputs must live inside the device cache."""
    p = Path(path).resolve()
    b = Path(base).resolve()
    try:
        p.relative_to(b)
    except ValueError:
        raise SystemExit(f"{what} must be inside {b}: {p}")
    return p


# ----------------------------------------------------------------------------
# vendor_boot v3 header and DTB region
# ----------------------------------------------------------------------------

def parse_vendor_header(data):
    if len(data) < _VB_V3_HEADER_SIZE:
        raise ValueError(f"vendor image too small for v3 header ({len(data)} bytes)")
    magic = data[0:8]
    if magic != VENDOR_MAGIC:
        raise ValueError(f"bad vendor_boot magic {magic!r}")
    out = {}
    for name, off, size in _VB_V3_FIELDS:
        raw = data[off:off + size]
        if size == 4:
            out[name] = struct.unpack("<I", raw)[0]
        elif size == 8:
            out[name] = struct.unpack("<Q", raw)[0]
        else:
            out[name] = raw
    if out["header_version"] != 3:
        raise ValueError(f"expected vendor_boot v3, got header_version {out['header_version']}")
    if out["page_size"] not in (2048, 4096):
        raise ValueError(f"unexpected page_size {out['page_size']}")
    if out["header_size"] != _VB_V3_HEADER_SIZE:
        raise ValueError(f"unexpected header_size {out['header_size']}")
    if out["dtb_size"] == 0:
        raise ValueError("vendor_boot carries no DTB (dtb_size = 0)")
    return out


def dtb_region_offset(header):
    """First DTB byte = page-aligned end of the vendor ramdisk."""
    ramdisk_start = _round_up(header["header_size"], header["page_size"])
    ramdisk_end = ramdisk_start + header["vendor_ramdisk_size"]
    return _round_up(ramdisk_end, header["page_size"])


def parse_fdt_header(data):
    """Return the parsed FDT header dict, or None when `data` is too short."""
    if len(data) < FDT_HEADER.size:
        return None
    (magic, totalsize, off_struct, off_strings, off_rsv, version,
     last_comp, boot_cpuid, size_strings, size_struct) = FDT_HEADER.unpack(data[:FDT_HEADER.size])
    return dict(magic=magic, totalsize=totalsize, off_struct=off_struct,
                off_strings=off_strings, off_rsv=off_rsv, version=version,
                last_comp=last_comp, boot_cpuid=boot_cpuid,
                size_strings=size_strings, size_struct=size_struct)


def parse_dtb_boundaries(region):
    """Walk concatenated DTBs by each FDT `totalsize` (structural, not magic scan).

    Returns a list of dicts ``{offset, totalsize, header}``. Raises ValueError on
    any boundary violation (bad magic, out-of-bounds totalsize, inconsistent
    struct/strings offsets, or trailing bytes).
    """
    blobs = []
    off = 0
    total = len(region)
    while off < total:
        remaining = total - off
        if remaining < FDT_HEADER.size:
            raise ValueError(f"trailing {remaining} bytes after last DTB (expected exact concatenation)")
        hdr = parse_fdt_header(region[off:])
        if hdr["magic"] != FDT_MAGIC:
            raise ValueError(
                f"no valid FDT header at offset {off} (magic=0x{region[off:off + 4].hex()})")
        if hdr["totalsize"] < FDT_HEADER.size:
            raise ValueError(f"blob@{off}: totalsize {hdr['totalsize']} < {FDT_HEADER.size}")
        if off + hdr["totalsize"] > total:
            raise ValueError(
                f"blob@{off}: totalsize {hdr['totalsize']} overruns region (end {off + hdr['totalsize']} > {total})")
        if hdr["off_struct"] < FDT_HEADER.size or hdr["off_struct"] + hdr["size_struct"] > hdr["totalsize"]:
            raise ValueError(f"blob@{off}: struct block out of bounds")
        if hdr["off_strings"] < FDT_HEADER.size or hdr["off_strings"] + hdr["size_strings"] > hdr["totalsize"]:
            raise ValueError(f"blob@{off}: strings block out of bounds")
        blobs.append(dict(offset=off, totalsize=hdr["totalsize"], header=hdr))
        off += hdr["totalsize"]
    return blobs


# ----------------------------------------------------------------------------
# dtc helpers
# ----------------------------------------------------------------------------

def dtc_version():
    try:
        r = subprocess.run(["dtc", "--version"], capture_output=True, text=True, check=True)
        return r.stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"dtc unavailable: {exc}")


def dtc_validate(blob_bytes, label):
    """Run `dtc -I dtb -O dtb` on a blob; return ``(returncode, stderr)``."""
    r = subprocess.run(
        ["dtc", "-I", "dtb", "-O", "dtb", "-q", "-o", "/dev/null", "-"],
        input=blob_bytes, capture_output=True)
    return r.returncode, r.stderr.decode(errors="replace").strip()


def dtc_to_dts(blob_bytes):
    r = subprocess.run(["dtc", "-I", "dtb", "-O", "dts", "-q", "-"],
                       input=blob_bytes, capture_output=True)
    if r.returncode != 0:
        raise ValueError(f"dtc failed: {r.stderr.decode(errors='replace').strip()[:300]}")
    return r.stdout.decode(errors="replace")


_HEX2 = re.compile(r"<\s*0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)\s*>")


def _parse_pair_cells(text):
    m = _HEX2.search(text)
    if not m:
        return None
    return (int(m.group(1), 16), int(m.group(2), 16))


def _top_level_prop(lines, key):
    for ln in lines:
        s = ln.strip()
        if s.startswith(key + " ") or s.startswith(key + "\t"):
            return s[len(key):].strip().lstrip("= ").rstrip(";")
    return None


def _count(lines, needle):
    return sum(1 for ln in lines if needle in ln)


def _parse_compatible(text):
    if text is None:
        return None
    # dtc renders a multi-value compatible with \0 separators inside one string.
    s = text.strip().strip('"')
    return [v for v in s.split("\\0") if v]


def _memory_reg(lines):
    """Extract the `reg` property of the top-level `memory` node (may be empty)."""
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == "memory {":
            start = i
            break
    if start is None:
        return None
    depth = 0
    for ln in lines[start:]:
        depth += ln.count("{") - ln.count("}")
        s = ln.strip()
        if s.startswith("reg ="):
            return s[5:].strip().lstrip("= ").rstrip(";")
        if depth <= 0:
            break
    return None


def inventory_dtb(blob_bytes):
    """Inventory a validated DTB via dtc DTS output (identity + memory + OPP)."""
    txt = dtc_to_dts(blob_bytes)
    lines = txt.splitlines()
    model = _top_level_prop(lines, "model")
    compatible = _parse_compatible(_top_level_prop(lines, "compatible"))
    msm_id = _parse_pair_cells(_top_level_prop(lines, "qcom,msm-id") or "")
    board_id = _parse_pair_cells(_top_level_prop(lines, "qcom,board-id") or "")
    mem_reg = _memory_reg(lines)
    return dict(
        model=model,
        compatible=compatible,
        msm_id=msm_id,
        board_id=board_id,
        memory_reg=mem_reg,
        reserved_memory=("reserved-memory" in txt),
        removed_dma_pools=_count(lines, "removed-dma-pool"),
        shared_dma_pools=_count(lines, "shared-dma-pool"),
        cpu_count=_count(lines, 'device_type = "cpu"'),
        cpu_opp_epss=("qcom,cpufreq-hw-epss" in txt),
        operating_points_v2=_count(lines, "operating-points-v2"),
        gpu_kgsl=("qcom,kgsl-3d0" in txt),
        gpu_pwrlevels=("qcom,gpu-pwrlevels" in txt),
        gpu_pwrlevel_bins=("qcom,gpu-pwrlevel-bins" in txt),
    )


# ----------------------------------------------------------------------------
# stage
# ----------------------------------------------------------------------------

def _extract_provenance(data, command_name):
    commands = data.get("commands")
    if not isinstance(commands, list):
        raise ValueError("provenance JSON has no 'commands' list")
    for cmd in commands:
        if cmd.get("name") == command_name:
            args = cmd.get("arguments_without_serial") or cmd.get("args_without_serial")
            if not args:
                raise ValueError(f"provenance command {command_name!r} has no args record")
            for key in ("exit_code", "stdout_bytes", "stdout_sha256"):
                if key not in cmd:
                    raise ValueError(f"provenance command {command_name!r} missing {key}")
            return dict(
                name=command_name,
                args=args,
                exit_code=cmd["exit_code"],
                bytes=cmd["stdout_bytes"],
                sha256=cmd["stdout_sha256"],
            )
    raise ValueError(f"provenance JSON has no command named {command_name!r}")


def stage(source, name, sha256, size, provenance, provenance_command):
    source = Path(source).resolve()
    if not source.is_file():
        raise SystemExit(f"source is not a regular file: {source}")
    dest = _require_within(FIRMWARE / name, FIRMWARE, "destination")

    if provenance is not None:
        prov_data = json.loads(Path(provenance).read_text())
        rec = _extract_provenance(prov_data, provenance_command)
        if rec["sha256"].lower() != sha256.lower():
            raise SystemExit(
                f"provenance sha256 {rec['sha256']} != expected {sha256}")
        if rec["bytes"] != size:
            raise SystemExit(
                f"provenance bytes {rec['bytes']} != expected {size}")
        if rec["exit_code"] != 0:
            raise SystemExit(f"provenance command exited {rec['exit_code']}")
    else:
        rec = None

    if source.stat().st_size != size:
        raise SystemExit(f"source size {source.stat().st_size} != expected {size}")
    measured = sha256_file(source)
    if measured != sha256.lower():
        raise SystemExit(f"source sha256 {measured} != expected {sha256}")

    FIRMWARE.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".tmp")
    with open(source, "rb") as src, open(tmp, "wb") as out:
        for chunk in iter(lambda: src.read(1 << 20), b""):
            out.write(chunk)
    # Re-verify the staged copy before it becomes authoritative.
    if sha256_file(tmp) != sha256.lower() or tmp.stat().st_size != size:
        tmp.unlink(missing_ok=True)
        raise SystemExit("staged copy changed while writing")
    tmp.replace(dest)

    sidecar = dict(
        name=name,
        sha256=sha256.lower(),
        size=size,
        source=source.name,
        source_path=str(source),
        provenance=rec,
        provenance_file=str(Path(provenance)) if provenance else None,
        sanitized=True,
    )
    (dest.with_name(name + ".provenance.json")).write_text(
        json.dumps(sidecar, indent=2) + "\n")
    return dest, rec


# ----------------------------------------------------------------------------
# inspect
# ----------------------------------------------------------------------------

def inspect(vendor_boot_name, live_fdt_name, report_name, extract):
    vb_path = _require_within(FIRMWARE / vendor_boot_name, FIRMWARE, "vendor_boot input")
    if not vb_path.is_file():
        raise SystemExit(f"vendor_boot input not staged: {vb_path}")

    with open(vb_path, "rb") as f:
        head = f.read(_VB_V3_HEADER_SIZE)
        header = parse_vendor_header(head)
        region_off = dtb_region_offset(header)
        f.seek(region_off)
        region = f.read(header["dtb_size"])

    blobs = parse_dtb_boundaries(region)
    candidates = []
    for i, blob in enumerate(blobs):
        data = region[blob["offset"]:blob["offset"] + blob["totalsize"]]
        rc, err = dtc_validate(data, f"blob{i}")
        inv = inventory_dtb(data) if rc == 0 else None
        candidates.append(dict(
            index=i,
            offset=region_off + blob["offset"],
            size=blob["totalsize"],
            sha256=sha256_bytes(data),
            version=blob["header"]["version"],
            dtc_rc=rc,
            dtc_error=err or None,
            inventory=inv,
        ))

    live = None
    if live_fdt_name:
        live_path = _require_within(FIRMWARE / live_fdt_name, FIRMWARE, "live FDT input")
        if not live_path.is_file():
            raise SystemExit(f"live FDT input not staged: {live_path}")
        live_bytes = live_path.read_bytes()
        rc, err = dtc_validate(live_bytes, "live")
        if rc != 0:
            raise SystemExit(f"live FDT failed dtc validation: {err[:300]}")
        live = dict(
            sha256=sha256_bytes(live_bytes),
            size=len(live_bytes),
            dtc_rc=rc,
            inventory=inventory_dtb(live_bytes),
        )

    comparison = None
    if live is not None:
        li = live["inventory"]
        msm_hits = [c["index"] for c in candidates
                    if c["inventory"] and c["inventory"]["msm_id"] == li["msm_id"]]
        board_hits = [c["index"] for c in candidates
                      if c["inventory"] and c["inventory"]["board_id"] == li["board_id"]]
        comparison = dict(
            live_msm_id=li["msm_id"],
            live_board_id=li["board_id"],
            msm_id_candidates=msm_hits,
            board_id_candidates=board_hits,
        )

    report = dict(
        tool="enuma_firmware_inputs.py",
        vendor_boot=dict(
            name=vendor_boot_name,
            sha256=sha256_file(vb_path),
            header=dict(
                header_version=header["header_version"],
                page_size=header["page_size"],
                vendor_ramdisk_size=header["vendor_ramdisk_size"],
                header_size=header["header_size"],
                dtb_size=header["dtb_size"],
                dtb_addr=header["dtb_addr"],
                dtb_region_offset=region_off,
            ),
        ),
        dtc_version=dtc_version(),
        candidate_count=len(candidates),
        candidates=candidates,
        live_fdt=live,
        comparison=comparison,
    )

    out = _require_within(FIRMWARE / report_name, FIRMWARE, "report output")
    out.write_text(json.dumps(report, indent=2) + "\n")

    if extract:
        outdir = FIRMWARE / "dtbs"
        outdir.mkdir(parents=True, exist_ok=True)
        for c in candidates:
            data = region[c["offset"] - region_off:c["offset"] - region_off + c["size"]]
            (outdir / f"blob{c['index']}.dtb").write_bytes(data)
            (outdir / f"blob{c['index']}.sha256").write_text(c["sha256"] + "\n")
        report["extracted"] = str(outdir)

    return report


def _summarize(report):
    lines = []
    h = report["vendor_boot"]["header"]
    lines.append("vendor_boot v3: page=%d ramdisk=%d dtb_size=%d dtb@%d" % (
        h["page_size"], h["vendor_ramdisk_size"], h["dtb_size"], h["dtb_region_offset"]))
    lines.append("candidate_count=%d" % report["candidate_count"])
    for c in report["candidates"]:
        inv = c["inventory"] or {}
        lines.append("  blob%d @%d size=%d dtc=%d model=%r msm-id=%s board-id=%s compat=%s" % (
            c["index"], c["offset"], c["size"], c["dtc_rc"],
            inv.get("model"), inv.get("msm_id"), inv.get("board_id"),
            inv.get("compatible") and inv["compatible"][0]))
    if report["comparison"]:
        cmp_ = report["comparison"]
        lines.append("live msm-id=%s board-id=%s | msm-id_candidates=%s board-id_candidates=%s" % (
            cmp_["live_msm_id"], cmp_["live_board_id"],
            cmp_["msm_id_candidates"], cmp_["board_id_candidates"]))
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# self-test (synthetic parser boundary tests)
# ----------------------------------------------------------------------------

def _make_fdt(model):
    """Build a minimal, dtc-valid FDT with a single root `model` property."""
    value = model.encode() + b"\x00"
    struct_block = bytearray()
    struct_block += struct.pack(">I", 0x1)             # FDT_BEGIN_NODE
    struct_block += b"\x00"                            # root node name ""
    struct_block += b"\x00" * (-len(struct_block) % 4)
    prop = struct.pack(">III", 0x3, len(value), 0)     # FDT_PROP, nameoff=0
    struct_block += prop + value
    struct_block += b"\x00" * (-len(struct_block) % 4)
    struct_block += struct.pack(">I", 0x2)             # FDT_END_NODE
    struct_block += struct.pack(">I", 0x9)             # FDT_END
    strings = b"model\x00"
    off_rsv = 40
    rsvmap = struct.pack(">QQ", 0, 0)
    off_struct = off_rsv + len(rsvmap)
    off_strings = _round_up(off_struct + len(struct_block), 4)
    totalsize = _round_up(off_strings + len(strings), 8)
    buf = bytearray(totalsize)
    FDT_HEADER.pack_into(buf, 0, FDT_MAGIC, totalsize, off_struct, off_strings,
                         off_rsv, 17, 16, 0, len(strings), len(struct_block))
    buf[off_rsv:off_rsv + len(rsvmap)] = rsvmap
    buf[off_struct:off_struct + len(struct_block)] = struct_block
    buf[off_strings:off_strings + len(strings)] = strings
    return bytes(buf)


def self_test():
    a = _make_fdt("alpha")
    b = _make_fdt("bravo")
    results = []

    def check(name, fn):
        try:
            fn()
            results.append((name, True, None))
        except Exception as exc:  # noqa: BLE001
            results.append((name, False, str(exc)))

    # 1. exact concatenation splits into two blobs at their totalsize boundaries.
    def t_concat():
        blobs = parse_dtb_boundaries(a + b)
        assert [x["offset"] for x in blobs] == [0, len(a)], blobs
        assert [x["totalsize"] for x in blobs] == [len(a), len(b)], blobs

    # 2. a false 0xd00dfeed inside a blob payload does not create a boundary.
    def t_inner_magic():
        tampered = bytearray(a)
        tampered[64:68] = struct.pack(">I", FDT_MAGIC)  # inside blob a's body
        blobs = parse_dtb_boundaries(bytes(tampered) + b)
        assert [x["offset"] for x in blobs] == [0, len(a)], blobs

    # 3. totalsize overrun is rejected.
    def t_overrun():
        truncated = a + b[:len(b) - 4]
        try:
            parse_dtb_boundaries(truncated)
        except ValueError as exc:
            assert "overruns" in str(exc) or "trailing" in str(exc), exc
            return
        raise AssertionError("overrun not rejected")

    # 4. corrupt magic at a boundary is rejected.
    def t_bad_magic():
        bad = bytearray(b)
        bad[0:4] = b"\x00\x00\x00\x00"
        try:
            parse_dtb_boundaries(a + bytes(bad))
        except ValueError as exc:
            assert "no valid FDT header" in str(exc), exc
            return
        raise AssertionError("bad magic not rejected")

    # 5. trailing garbage is rejected.
    def t_trailing():
        try:
            parse_dtb_boundaries(a + b + b"\x00\x00\x00\x00")
        except ValueError as exc:
            assert "trailing" in str(exc), exc
            return
        raise AssertionError("trailing bytes not rejected")

    # 6. synthetic vendor header computes the page-aligned DTB offset.
    def t_header():
        hdr = parse_vendor_header(
            struct.pack("<8sIIII", VENDOR_MAGIC, 3, 4096, 0x8000, 0x1000000)
            + struct.pack("<I", 2230)
            + b"\x00" * 2048 + struct.pack("<I", 0x100) + b"\x00" * 16
            + struct.pack("<IIQ", _VB_V3_HEADER_SIZE, 1613832, 0x1F00000))
        assert dtb_region_offset(hdr) == 8192, dtb_region_offset(hdr)

    for name, fn in (
        ("concat", t_concat),
        ("inner-magic-ignored", t_inner_magic),
        ("totalsize-overrun-rejected", t_overrun),
        ("bad-boundary-magic-rejected", t_bad_magic),
        ("trailing-garbage-rejected", t_trailing),
        ("vendor-header-dtb-offset", t_header),
    ):
        check(name, fn)

    failed = [(n, e) for n, ok, e in results if not ok]
    for n, ok, e in results:
        print(f"  {'PASS' if ok else 'FAIL'} {n}" + (f"  ({e})" if not ok else ""))
    if failed:
        print(f"self-test: {len(failed)} failure(s)")
        return 1
    print(f"self-test: {len(results)} checks passed")
    return 0


# ----------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Stage and inspect enuma vendor_boot v3 DTBs (bounded, reproducible).")
    sub = parser.add_subparsers(dest="command", required=True)

    p_stage = sub.add_parser("stage", help="copy one proven backup file into .cache/firmware")
    p_stage.add_argument("--source", required=True, help="backup source file (read-only)")
    p_stage.add_argument("--name", required=True, help="destination filename in .cache/firmware")
    p_stage.add_argument("--sha256", required=True, help="expected SHA-256 (hex)")
    p_stage.add_argument("--size", required=True, type=int, help="expected byte size")
    p_stage.add_argument("--provenance", help="backup provenance JSON (report.json / capture.json)")
    p_stage.add_argument("--provenance-command", help="command name in provenance JSON bound to this file")

    p_inspect = sub.add_parser("inspect", help="parse staged vendor_boot DTB boundaries and inventory")
    p_inspect.add_argument("--vendor-boot", default="vendor_boot_a.img")
    p_inspect.add_argument("--live-fdt", default="fdt.stdout")
    p_inspect.add_argument("--report", default="dtb-report.json")
    p_inspect.add_argument("--extract", action="store_true", help="write each DTB blob to .cache/firmware/dtbs/")
    p_inspect.add_argument("--summary", action="store_true", help="print a concise text summary to stdout")

    sub.add_parser("self-test", help="run synthetic parser boundary tests")

    args = parser.parse_args(argv)

    if args.command == "self-test":
        return self_test()

    if args.command == "stage":
        dest, rec = stage(args.source, args.name, args.sha256, args.size,
                          args.provenance, args.provenance_command)
        print(f"staged {dest} ({args.size} bytes, sha256 {args.sha256.lower()})")
        if rec:
            print(f"  provenance {rec['name']}: exit={rec['exit_code']} args={rec['args']}")
        return 0

    if args.command == "inspect":
        report = inspect(args.vendor_boot, args.live_fdt, args.report, args.extract)
        if args.summary:
            print(_summarize(report))
        print(f"report {FIRMWARE / args.report}")
        print(f"candidate_count={report['candidate_count']} dtc={report['dtc_version']}")
        return 0

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    sys.exit(main())
