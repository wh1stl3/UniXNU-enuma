#!/usr/bin/env python3
"""Copy and verify the specified historical out evidence; never delete."""
import hashlib
import os
from pathlib import Path
import re
import shutil

OUT = Path("out")
LIST = Path("/mnt/c/Users/Administrator/AppData/Local/Temp/opencode/disk-cleanup-final-list.md")
PREFIX = r"D:\Code\PortingiOS\enuma\UniXNU-enuma\out" + "\\"
C = ("production-20261114-r5", "preseal", "userdata-clean-20261112", "userdata-prepare-20261112-b")
EXT = (".trustcache", ".module", ".key", ".pem", ".p12", ".pfx", ".cer", ".crt", ".der")
DOC_FILTER = re.compile(r"OUTPUT-REVIEW|DELIVERY|CHECKPOINT|AUTHORIZATION|MAPPING-EXCEPTION|ISSUER-LIFECYCLE|HANDOFF|RATIONALE|README", re.I)
ROUND = re.compile(r"-r5[3-7](?!\d)")


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def retain(src, dest):
    before = digest(src)
    dest.parent.mkdir(parents=True, exist_ok=True)
    target = dest
    n = 0
    while target.exists() or target.is_symlink():
        if target.is_file() and not target.is_symlink() and digest(target) == before:
            if digest(src) != before:
                raise ValueError("source changed")
            return target, before, n
        n += 1
        target = dest.with_name(dest.name + ".dup" + str(n))
    with src.open("rb") as inp, target.open("xb") as out:
        shutil.copyfileobj(inp, out, 1024 * 1024)
    if digest(target) != before or digest(src) != before:
        raise ValueError("SHA-256 mismatch or source changed")
    return target, before, n


def main():
    lines = LIST.read_text(encoding="utf-8-sig").splitlines()
    names = [s[len(PREFIX):] for s in lines if s.startswith(PREFIX) and "\\" not in s[len(PREFIX):]]
    if len(names) != 257 or len(set(names)) != 257:
        raise ValueError(f"expected 257 unique directory paths, got {len(names)}")
    rows, details = [], []
    totals = {"0A": 0, "0B": 0, "boot": 0, "failed": 0}
    for name in names:
        root = OUT / name
        counts = {"0A": 0, "0B": 0, "boot": 0}
        problems = []
        if any(c in name for c in C):
            rows.append((name, 0, 0, "否", "不删(C 类)"))
            continue
        if not root.is_dir() or root.is_symlink():
            rows.append((name, 0, 0, "否", "仍不能删(缺目录或目录为链接)"))
            continue

        def copy(src, dst, category):
            try:
                target, sha, dup = retain(src, dst)
                counts[category] += 1
                totals[category] += 1
                details.append(f"- {category} `{src}` → `{target}` SHA-256 `{sha}`" + ("（同名不同哈希）" if dup else ""))
            except (OSError, ValueError) as exc:
                totals["failed"] += 1
                problems.append(f"{category}: {src}: {exc}")

        def walk_error(exc):
            problems.append(f"扫描: {exc}")

        for base, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
            base = Path(base)
            for d in list(dirs):
                p = base / d
                if p.is_symlink():
                    dirs.remove(d)
                    problems.append(f"未扫描目录链接: {p}")
            for file in files:
                p = base / file
                if "libspdm/unit_test/sample_key/" in p.as_posix():
                    continue
                try:
                    if p.is_symlink():
                        problems.append(f"未扫描文件链接: {p}")
                        continue
                    stat = p.stat()
                    match = file.lower().endswith(EXT)
                    if not match and stat.st_size <= 1024 * 1024:
                        with p.open("rb") as f:
                            match = f.read(10) == b"-----BEGIN"
                    if match:
                        copy(p, OUT / "_retained-signing" / p.relative_to(OUT), "0A")
                except OSError as exc:
                    problems.append(f"扫描: {p}: {exc}")
        try:
            docs = sorted(p for p in root.iterdir() if p.name.lower().endswith(".md") and p.is_file() and not p.is_symlink())
            filtered = sum(p.stat().st_size for p in docs) > 200 * 1000 * 1000
            if filtered:
                details.append(f"- `{name}`：顶层文档超过 200 MB，按指定名称筛选。")
                docs = [p for p in docs if DOC_FILTER.search(p.name)]
            for p in docs:
                copy(p, OUT / "_retained-audit-docs" / name / p.name, "0B")
            boot = root / "boot.img"
            if ROUND.search(name) and boot.is_file() and not boot.is_symlink():
                copy(boot, OUT / "_retained-images" / name / "boot.img", "boot")
        except OSError as exc:
            problems.append(f"扫描顶层: {exc}")
        if problems:
            details.extend(f"- `{name}`：{p}" for p in problems)
        conclusion = "仍不能删(缺完整扫描或核验)" if problems else "可整目录删"
        rows.append((name, counts["0A"], counts["0B"], "是" if counts["boot"] else "否", conclusion))
        print(name, conclusion, flush=True)
    manifest = ["# 最小保全清单（self-checked）", "", "不含密钥内容；源/目标 SHA-256 逐项核验。未对目录链接跟随，发现链接的目录保持不可删。", "", "| 目录名 | 0A 文件数 | 0B 文档数 | boot.img | 结论 |", "|---|---:|---:|---|---|"]
    manifest += [f"| {name} | {a} | {b} | {boot} | {result} |" for name, a, b, boot, result in rows]
    manifest += ["", "## 核验明细与扫描限制", ""] + details
    (OUT / "_retained-manifest-20261124.md").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    print("TOTALS", totals, "ROWS", len(rows), "C", sum(x[4] == "不删(C 类)" for x in rows), "BLOCKED", sum(x[4].startswith("仍不能删") for x in rows), flush=True)


if __name__ == "__main__":
    main()
