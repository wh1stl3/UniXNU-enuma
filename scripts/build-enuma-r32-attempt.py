#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Replay r30 with isolated pre-dispatch attempt and rejection counters."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
here = Path(__file__).resolve().parent
text = (here / 'build-enuma-r30-control.py').read_text()
anchor = 'needle = "text = text.replace(needle, replacement)\\n"'
assert text.count(anchor) == 1
text = text.replace(anchor, '''insert += """    inc = bsd / 'EnumaBbScan.inc'
    data = inc.read_text().replace('#include "EnumaControl.inc"', '#include "EnumaControl.inc"\\\\n#include "EnumaAttempt.inc"')
    data = data.replace('enuma_ctl_dump();', 'enuma_ctl_dump();\\\\n\\\\tenuma_att_dump();')
    inc.write_text(data)
    shutil.copyfile(DEVICE / 'package/EnumaAttempt.inc', bsd / 'EnumaAttempt.inc')
"""
''' + anchor)
needle = "namespace = {'__name__': '__main__'"
insert = r'''
# Modify the r29 program that r30 replayed, before it synthesizes its recipe.
needle = "    uc.write_text(s)\n"
extra = """    anchor = '#include "IOKitKernelInternal.h"'
    assert s.count(anchor) == 1
    s = s.replace(anchor, anchor + '\\nextern "C" void enuma_att_record(unsigned int);')
    anchor = 'io_object_t *connection )\\n{'
    assert s.count(anchor) == 1
    s = s.replace(anchor, anchor + '\\n\\tenuma_att_record(0);')
    anchor = '\\tif (!owningTask) {\\n\\t\\treturn kIOReturnBadArgument;'
    assert s.count(anchor) == 1
    s = s.replace(anchor, anchor.replace('return kIOReturnBadArgument;', 'enuma_att_record(2);\\n\\t\\treturn kIOReturnBadArgument;'))
    anchor = '\\tif (owningTask != current_task()) {\\n\\t\\treturn kIOReturnBadArgument;'
    assert s.count(anchor) == 1
    s = s.replace(anchor, anchor.replace('return kIOReturnBadArgument;', 'enuma_att_record(2);\\n\\t\\treturn kIOReturnBadArgument;'))
    anchor = 'mac_iokit_check_open_service(kauth_cred_get(), service, connect_type) != 0) {\\n\\t\\treturn kIOReturnNotPermitted;'
    assert s.count(anchor) == 1
    s = s.replace(anchor, anchor.replace('return kIOReturnNotPermitted;', 'enuma_att_record(1);\\n\\t\\treturn kIOReturnNotPermitted;'))
    anchor = '\\t\\tif (properties) {\\n\\t\\t\\treturn kIOReturnUnsupported;'
    assert s.count(anchor) == 1
    s = s.replace(anchor, anchor.replace('return kIOReturnUnsupported;', 'enuma_att_record(2);\\n\\t\\t\\treturn kIOReturnUnsupported;'))
"""
extra = extra.replace('\\', '\\\\')
assert text.count(needle) == 1
text = text.replace(needle, extra + needle)
needle = "    blob = path.read_bytes()\n"
assert text.count(needle) == 1
text = text.replace(needle, """    formats += ['enuma-att: begin entry=%llu entry_bb=%llu mac_rej=%llu mac_rej_bb=%llu early_rej=%llu early_rej_bb=%llu\\n', 'enuma-att: [com] %s=%llu\\n', 'enuma-att: end\\n']
""" + needle)
text = text.replace("ufs-sm8250-launchd-control-20261123-r30'", "ufs-sm8250-launchd-attempt-20261123-r32'")
'''
assert text.count(needle) == 1
text = text.replace(needle, insert + '\n' + needle)
exec(compile(text, str(here / 'build-enuma-r30-control.py'), 'exec'))
