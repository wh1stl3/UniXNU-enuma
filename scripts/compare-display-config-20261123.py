#!/usr/bin/env python3
"""Compare two packaged ADTs without publishing identity or random-seed values."""
import hashlib
import re
import struct
import subprocess
import sys
import tomllib
from pathlib import Path

ENUMA = Path("out/ufs-sm8250-launchd-ipc-20261123-r34/payload.img")
NUWA = Path("../..") / "nuwa/worktree-display-dsp/out/nuwa-resume-display-scale-audit-20261122/actual-vendor-ramdisk.img"
PREFIX = "::/EFI/UniXNU/"
FAMILIES = re.compile(r"(?:display|panel|screen|refresh|vsync|scale|rotation|colou?r|gamma|backlight|brightness|frame[-_]?buffer|backboard|(?:^|[-_])iop|gpu|(?:^|[-_])dp(?:$|[-_0-9])|dsi|dpu)", re.I)
ARGS = re.compile(r"(?:offline-legacy-|offline-mobile-graphics-|boot-progress|vsync|scale|(?:^|-)fb-|gpu|display|panel|screen|refresh|rotation|colou?r|gamma|backlight|brightness|frame[-_]?buffer|backboard|(?:^|-)dp(?:$|-)|dsi|dpu)", re.I)


def member(image, name):
    return subprocess.check_output(["mtype", "-i", str(image), PREFIX + name])


def parse(raw):
    result = {}
    def node(pos, parent):
        count, children = struct.unpack_from("<II", raw, pos)
        pos += 8
        properties = {}
        for _ in range(count):
            key, size_flags = struct.unpack_from("<32sI", raw, pos)
            key = key.split(b"\0", 1)[0].decode("ascii")
            size = size_flags & 0x7fffffff
            pos += 36
            assert key not in properties and pos + size <= len(raw)
            properties[key] = (raw[pos:pos + size], size_flags >> 31)
            pos += (size + 3) & ~3
        name = properties["name"][0].split(b"\0", 1)[0].decode("ascii")
        path = parent.rstrip("/") + "/" + name if parent else "/"
        for key, value in properties.items():
            full = path.rstrip("/") + ":" + key
            assert full not in result
            result[full] = value
        for _ in range(children):
            pos = node(pos, path)
        return pos
    end = node(0, "")
    assert not any(raw[end:])
    return result


def main():
    images = {"enuma": ENUMA, "nuwa": NUWA}
    data, configs = {}, {}
    for name, image in images.items():
        raw = member(image, "Payloads/kernel.macho.adt")
        data[name] = parse(raw)
        cfg = tomllib.loads(member(image, "unixnu.toml").decode())
        configs[name] = next(e["args"].split() for e in cfg["entry"] if e["id"] == "xnu")
        print(name, "sha256", hashlib.sha256(raw).hexdigest(), "properties", len(data[name]))
        path = Path("docs") / (name + "-adt-properties-20261123.txt")
        path.write_text("".join(f"{k}\tlength={len(v)}\tflag={flag}\n"
                                for k, (v, flag) in sorted(data[name].items())), encoding="utf-8")
    e, n = data["enuma"], data["nuwa"]
    for label, keys in (("nuwa-only", n.keys() - e.keys()), ("different", n.keys() & e.keys()),
                        ("enuma-only", e.keys() - n.keys())):
        print("\nADT", label)
        for k in sorted(keys):
            if FAMILIES.search(k) and (label != "different" or e[k] != n[k]):
                def value(d):
                    if k not in d:
                        return "-"
                    raw, flag = d[k]
                    return f"hex={raw.hex()} length={len(raw)} flag={flag}"
                print(k, "enuma", value(e), "nuwa", value(n))
    print("\nADT common-equal")
    for k in sorted(n.keys() & e.keys()):
        if FAMILIES.search(k) and e[k] == n[k]:
            raw, flag = e[k]
            print(k, f"hex={raw.hex()} length={len(raw)} flag={flag}")
    args = {name: {x.split("=", 1)[0]: x for x in values if ARGS.search(x.split("=", 1)[0])}
            for name, values in configs.items()}
    e, n = args["enuma"], args["nuwa"]
    for label, keys in (("nuwa-only", n.keys() - e.keys()), ("different", n.keys() & e.keys()),
                        ("enuma-only", e.keys() - n.keys())):
        print("\nARGS", label)
        for k in sorted(keys):
            if label != "different" or e[k] != n[k]:
                print(k, "enuma", e.get(k, "-"), "nuwa", n.get(k, "-"))
    print("\nARGS common-equal")
    for k in sorted(n.keys() & e.keys()):
        if e[k] == n[k]:
            print(e[k])


if __name__ == "__main__":
    main()
