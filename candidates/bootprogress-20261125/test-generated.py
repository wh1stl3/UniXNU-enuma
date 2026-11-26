#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Extract the actual staged screen functions into the host test translation unit."""
import hashlib
import json
from pathlib import Path
import re
import sys


def take(text, name):
    match, = list(re.finditer(rf"(?m)^{re.escape(name)}\(", text))
    start = text.rindex("\n", 0, match.start() - 1) + 1
    end = text.index("\n}", match.start()) + 2
    return text[start:end]


def main(out):
    paths = [out / "video_console.c", out / "pe_init.c", Path(__file__).with_name("renderer.inc")]
    vc, pe, renderer = [path.read_text() for path in paths]
    blit = vc[vc.index("enum {\n\tkSave"):vc.index("static void\nvc_clean_boot_graphics")]
    start = vc.index("static int8_t vc_rotate_matr")
    matrix = vc[start:vc.index("\n};", start) + 3]
    # Extract bodies unchanged. Only the low-level screen apply (pmap/VC),
    # OS scheduler/locks, and serial router are supplied by host fixtures.
    snippets = {
        "screen.inc": "\n\n".join(take(vc, name) for name in
                                   ("enuma_bp_screen_begin", "enuma_bp_screen_reserved",
                                    "enuma_bp_screen", "enuma_bp_pe_screen", "initialize_screen", "vcattach")),
        "pe.inc": "\n\n".join(take(pe, name) for name in
                              ("enuma_pe_before", "enuma_pe_after", "PE_initialize_console")),
        "blit.inc": matrix + "\n\n" + blit + take(vc, "vc_progress_task"),
        "bp-init.inc": "\n\n".join(take(renderer, name) for name in
                                   ("enuma_bp_initial_mapping", "enuma_bp_start")),
    }
    report = {}
    for name, text in snippets.items():
        dst = out / name
        dst.write_text(text + "\n")
        report[name] = hashlib.sha256(dst.read_bytes()).hexdigest()
    (out / "generated-test-inputs.json").write_text(json.dumps({
        "sources": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        "excerpts": report,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
