import pathlib, re, sys

root = pathlib.Path("/mnt/d/Code/PortingiOS/enuma/UniXNU-enuma")
tree = root / "out/ownerdata-20261125/source-xnu"
lst  = root / "docs/build-full-pipeline-20261125-hooks-r64.txt"
out  = root / "out/hook-check-20261125.txt"

lines = [l.rstrip("\n") for l in lst.read_text(errors="replace").splitlines() if l.strip()]
hits, miss = 0, []
for l in lines:
    # 期望格式: path:line:marker  或 path:marker
    parts = l.split(":", 2)
    if len(parts) < 3:
        if len(parts) < 2:
            miss.append((l, ""))
            continue
        parts = l.split(":", 1)
    rel, marker = parts[0], parts[-1].strip()
    rel = rel.replace("\\", "/")
    tp = tree / rel
    ok = False
    if tp.is_file():
        txt = tp.read_text(errors="replace")
        ok = marker in txt
    if ok: hits += 1
    else: miss.append((rel, marker))

out.write_text(
    "total=%d hits=%d miss=%d\n" % (len(lines), hits, len(miss)) +
    "\n".join("%s :: %s" % (r, m) for r, m in miss)
)
print("total=%d hits=%d miss=%d" % (len(lines), hits, len(miss)))
for r, m in miss[:20]:
    print("MISS", r, "::", m)
