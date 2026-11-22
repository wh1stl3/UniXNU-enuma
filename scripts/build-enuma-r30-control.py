#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Replay r29 with an isolated global control counter."""
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
here = Path(__file__).resolve().parent
text = (here / 'build-enuma-r29-bbscan.py').read_text()
insert = """    inc = bsd / 'EnumaBbScan.inc'
    data = inc.read_text()
    anchor = 'unsigned int\\nenuma_bb_record(const char *name, uint32_t type)'
    assert data.count(anchor) == 1
    data = data.replace(anchor, '#include "EnumaControl.inc"\\n\\n' + anchor)
    anchor = 'enuma_bb_record(const char *name, uint32_t type)\\n{'
    assert data.count(anchor) == 1
    data = data.replace(anchor, anchor + '\\n\\tenuma_ctl_record();')
    anchor = '\\tprintf("enuma-bb: end\\\\n");'
    assert data.count(anchor) == 1
    data = data.replace(anchor, anchor + '\\n\\tenuma_ctl_dump();')
    inc.write_text(data)
    shutil.copyfile(DEVICE / 'package/EnumaControl.inc', bsd / 'EnumaControl.inc')
"""
needle = "text = text.replace(needle, replacement)\n"
assert text.count(needle) == 4
text = text.replace(needle,
    "anchor = \"    exec_path = bsd / 'kern_exec.c'\\n\"\n"
    "assert replacement.count(anchor) == 1\n"
    "replacement = replacement.replace(anchor, " + repr(insert) + " + anchor)\n" + needle, 1)
needle = "    blob = path.read_bytes()\n"
insert = """    formats += ['enuma-ctl: begin all=%llu bb=%llu overflow=%llu\\n',
                'enuma-ctl: [com] %s=%llu\\n', 'enuma-ctl: end\\n']
"""
assert text.count(needle) == 1
text = text.replace(needle, insert + needle)
text = text.replace("blob.count(b'enuma-bb: ') == 3, counts",
                    "blob.count(b'enuma-bb: ') == 3 and blob.count(b'enuma-ctl: ') == 3, counts")
text = text.replace("ufs-sm8250-launchd-bbscan-20261123-r29'",
                    "ufs-sm8250-launchd-control-20261123-r30'")
namespace = {'__name__': '__main__', '__file__': str(here / 'build-enuma-r29-bbscan.py')}
exec(compile(text, namespace['__file__'], 'exec'), namespace)
