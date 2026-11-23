#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Rebuild r53 with at most one framebuffer row per console call."""
from pathlib import Path

here = Path(__file__).resolve().parent
wrapper = (here / 'build-enuma-r53-fbfill2.py').read_text()
marker = "''' + '\\n' + marker"
assert wrapper.count(marker) == 1
extra = r'''
one("parser_args.add_argument('--r53'", "parser_args.add_argument('--r54'")
one("r49 = device / 'out/ufs-sm8250-fbfill-20261123-r52'",
    "r49 = device / 'out/ufs-sm8250-fbfill2-20261123-r53'")
one("out/ufs-sm8250-fbfill2-20261123-r53').resolve()",
    "out/ufs-sm8250-fbfill3-20261123-r54').resolve()")
one('96b8c8981b2b191af4faa5c75d5bfc49c0287cf42e4184b5ecfef7589d5a2ef2',
    '8256c160561ecf427f73c3105b1790915c13df925ccb7c70fe536061e0924137')
start = text.index("bp = source / 'EnumaBootProgress2.inc'")
end = text.index("\nobj = out / 'objects/kern_exec.o'", start)
text = text[:start] + """bp = source / 'EnumaBootProgress2.inc'
bptext = bp.read_text()
old = 'if (g_enuma_fbfill_state == -1) {\\n\\t\\tprintf("enuma-fbfill: never-gated\\\\n");\\n\\t}'
assert bptext.count(old) == 1
bptext = bptext.replace(old, '')
old = 'enuma-fbfill: st=%d w=%u h=%u d=%u rb=%u avail=%u'
new = 'enuma-fbfill: st=%d rows=%u w=%u h=%u d=%u rb=%u avail=%u'
assert bptext.count(old) == 1
bptext = bptext.replace(old, new)
bptext = bptext.replace('g_enuma_fbfill_state, g_enuma_fbfill_w,',
                        'g_enuma_fbfill_state, g_enuma_fbfill_rows, g_enuma_fbfill_w,')
bp.write_text('extern volatile unsigned g_enuma_fbfill_rows;\\n' + bptext)
""" + text[end:]
one("shutil.copyfile(r49 / 'source/osfmk/console/video_console.c', video)",
    "code = (r49 / 'source/osfmk/console/video_console.c').read_text()\n"
    "assert code.count('enuma_fb_fill_once();') == 1\n"
    "video.write_text(code.replace('enuma_fb_fill_once();', 'enuma_fb_fill_step();'))")
one("device / 'package/EnumaFbFill52.inc'", "device / 'package/EnumaFbFill54.inc'")
one("b'enuma-fbfill: never-gated\\n\\0', ", "")
one("b'enuma-fbfill: st=%d w=%u h=%u d=%u rb=%u avail=%u",
    "b'enuma-fbfill: st=%d rows=%u w=%u h=%u d=%u rb=%u avail=%u")
'''
wrapper = wrapper.replace(marker, extra + "\n" + marker)
exec(compile(wrapper, str(here / 'build-enuma-r53-fbfill2.py'), 'exec'))
