#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Extract named blocks of actual upstream draw(); supply captures, not pixels."""
import hashlib
import json
from pathlib import Path
import re
import sys

out = Path(sys.argv[1])
source = (out / "reference/BootProgress.c").read_text()


def between(text, a, b):
    start = text.index(a)
    return text[start:text.index(b, start)]


draw = between(source, "static void draw(unsigned now)", "\n// A framebuffer write")
blocks = [
    ("title", "  const char *title", "  snprintf(b,sizeof(b),\"time="),
    ("ufs", '  snprintf(b,sizeof(b),"%s requests=', '  snprintf(b,sizeof(b),"TCR='),
    ("registers", '  snprintf(b,sizeof(b),"TCR=', '  snprintf(b,sizeof(b),"last IRQ'),
    ("stage", "  unsigned latest", "  if(!__atomic_exchange"),
    ("history", "  unsigned first = visible->history_count", "  first = sample_count"),
    ("logs", '  bar(16," Kernel console', "  if(exit_snapshot.total)"),
    ("memory", '  snprintf(b,sizeof(b),"MEM totalMiB', "  if (visible->frozen)"),
]
sample = (out / "sample.inc").read_text()
registers = {"cntpct_el0", "cntfrq_el0", "tcr_el1", "ttbr0_el1", "ttbr1_el1",
             "sctlr_el1", "cntvct_el0", "cntv_cval_el0", "cntv_ctl_el0", "daif"}
if set(re.findall(r"PANEL_MRS\(\w+, (\w+)\);", sample)) != registers:
    raise ValueError("sample register fixture drift")
fixture = re.sub(r'^extern .*?\n', lambda m: "" if "bsd_log_" in m[0] else m[0][7:],
                 sample.split("/* Lock exists", 1)[0], flags=re.M)
fixture = re.sub(r"^#include <[^>]+>\n", "", fixture, flags=re.M)
fixture += sample[sample.index("#define PANEL_LOAD"):]
fixture = fixture.replace('__asm__ volatile("mrs %0, " #reg : "=r"(dst))', "(dst = reg)")
fixture = fixture.replace('\t__asm__ volatile("isb" ::: "memory");\n', "")
(out / "captured-sample.inc").write_text(fixture)
overlay = between(source, "static char ext_drawn[", "\n// Crash banner")
overlay = overlay.replace("  ext_data_rows();\n", "")
(out / "reference-draw.inc").write_text(
    "\n".join(between(draw, a, b) for _, a, b in blocks))
(out / "reference-side.inc").write_text(overlay)
report = {name: hashlib.sha256(between(draw, a, b).encode()).hexdigest() for name, a, b in blocks}
(out / "reference-blocks.json").write_text(json.dumps(report, indent=2) + "\n")
