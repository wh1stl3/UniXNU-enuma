#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Rebuild r52's two diagnostic units with bounded colour blocks."""
from pathlib import Path

here = Path(__file__).resolve().parent
wrapper = (here / 'build-enuma-r52-fbfill.py').read_text()
marker = "exec(compile(text, str(here / 'build-enuma-r49-bp2.py'), 'exec'))"
assert wrapper.count(marker) == 1
hook = r'''
def one(a, b):
    global text
    assert text.count(a) == 1, (a, text.count(a))
    text = text.replace(a, b)

one("parser_args.add_argument('--r52'", "parser_args.add_argument('--r53'")
one("r49 = device / 'out/ufs-sm8250-bp2-20261123-r49'",
    "r49 = device / 'out/ufs-sm8250-fbfill-20261123-r52'")
one("out/ufs-sm8250-fbfill-20261123-r52').resolve()",
    "out/ufs-sm8250-fbfill2-20261123-r53').resolve()")
one('1180a2c7b2c7f903cf412791a704a3051dbf6335f696f0183896a4c3b1f9d3f5',
    '96b8c8981b2b191af4faa5c75d5bfc49c0287cf42e4184b5ecfef7589d5a2ef2')
start = text.index("bp = source / 'EnumaBootProgress2.inc'")
end = text.index("\nobj = out / 'objects/kern_exec.o'", start)
text = text[:start] + """bp = source / 'EnumaBootProgress2.inc'
bptext = bp.read_text()
needle = '\\tenuma_matchcnt_dump();'
assert bptext.count(needle) == 1
bptext = bptext.replace(needle, '\\tif (g_enuma_fbfill_state == -1) {\\n\\t\\tprintf("enuma-fbfill: never-gated\\\\n");\\n\\t}\\n' + needle)
bp.write_text(bptext)
""" + text[end:]
start = text.index("cc = json.loads(old_video.with_suffix")
end = text.index("assert digest(old_video) != digest(video_obj)", start)
text = text[:start] + """cc = recipe['compile-video_console.o']
video = out / 'source/osfmk/console/video_console.c'
video.parent.mkdir(parents=True)
shutil.copyfile(r49 / 'source/osfmk/console/video_console.c', video)
shutil.copyfile(device / 'package/EnumaFbFill52.inc', video.parent / 'EnumaFbFill52.inc')
video_obj = out / 'objects/video_console.o'
argv = cc['argv'].copy()
argv[2], argv[4] = str(video), str(video_obj)
call('compile-video_console.o', argv, cc['cwd'])
""" + text[end:]
start = text.index("old_config = read_member(r49 / 'payload.img'")
end = text.index("old_tree = fat_tree(r49 / 'payload.img')", start)
text = text[:start] + """import tomllib
old_config = read_member(r49 / 'payload.img', 'unixnu.toml')
config = old_config
entry = lambda b: next(e for e in tomllib.loads(b.decode())['entry'] if e['id'] == 'xnu')['args']
args = entry(read_member(out / 'payload.img', 'unixnu.toml'))
assert args == entry(old_config)
""" + text[end:]
one("assert set(changed) == {'Payloads/kernel.macho', 'unixnu.toml'}, changed",
    "assert changed == ['Payloads/kernel.macho'], changed")
one("b'enuma-bp\\0', b'enuma-fbfill:",
    "b'enuma-bp\\0', b'enuma-fbfill: never-gated\\n\\0', b'enuma-fbfill:")
''' + '\n' + marker
wrapper = wrapper.replace(marker, hook)
exec(compile(wrapper, str(here / 'build-enuma-r52-fbfill.py'), 'exec'))
