#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Replay r34 with isolated matching request/result counters."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
here = Path(__file__).resolve().parent
text = (here / "build-enuma-r34-ipc.py").read_text()
needle = 'exec(compile(text, str(here / "build-enuma-r32-attempt.py"), "exec"))'
assert text.count(needle) == 1
insert = r'''
needle = "exec(compile(text, str(here / 'build-enuma-r30-control.py'), 'exec'))"
assert text.count(needle) == 1
extension = r"""
needle = "namespace = {'__name__': '__main__'"
assert text.count(needle) == 1
extra = (
    'needle = "    uc.write_text(s)\\n"\n'
    'assert text.count(needle) == 1\n'
    'addition = "    s = __import__(\\x27runpy\\x27).run_path(str(DEVICE / \\x27scripts/enuma-r36-patch.py\\x27))[\\x27patch\\x27](s)\\n"\n'
    'text = text.replace(needle, addition + needle)\n'
    'needle = "    blob = path.read_bytes()\\n"\n'
    'assert text.count(needle) == 1\n'
    'text = text.replace(needle, "    formats += [\\x27enuma-match: begin all=%llu bb=%llu sb=%llu ok=%llu/%llu/%llu\\\\n\\x27, \\x27enuma-match: end\\\\n\\x27]\\n" + needle)\n'
)
assert text.count(needle) == 1
text = text.replace(needle, extra + '\n' + needle)
"""
text = text.replace(needle, extension + '\n' + needle)
text = text.replace("ufs-sm8250-launchd-ipc-20261123-r34'", "ufs-sm8250-launchd-match-20261123-r36'")
needle = "    shutil.copyfile(DEVICE / 'package/EnumaIpc.inc', bsd / 'EnumaIpc.inc')"
assert text.count(needle) == 1
text = text.replace(needle, needle + "\n    shutil.copyfile(DEVICE / 'package/EnumaMatch.inc', bsd / 'EnumaMatch.inc')")
text = text.replace("enuma_ipc_dump();", "enuma_ipc_dump();\\\\\\\\n\\\\\\\\tenuma_match_dump();")
text = text.replace('#include "EnumaIpc.inc"', '#include "EnumaIpc.inc"\\\\\\\\n#include "EnumaMatch.inc"')
'''
text = text.replace(needle, insert + '\n' + needle)
exec(compile(text, str(here / "build-enuma-r34-ipc.py"), "exec"))
