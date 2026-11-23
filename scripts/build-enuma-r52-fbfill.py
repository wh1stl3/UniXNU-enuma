#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Build the isolated r52 framebuffer diagnostic from the r49 recipe."""
from pathlib import Path

here = Path(__file__).resolve().parent
text = (here / 'build-enuma-r49-bp2.py').read_text()


def replace(old, new):
    global text
    assert text.count(old) == 1, (old, text.count(old))
    text = text.replace(old, new)


replace("parser_args.add_argument('--r49', action='store_true', required=True)",
        "parser_args.add_argument('--r52', action='store_true', required=True)")
replace("out = (opts.out or device / 'out/ufs-sm8250-bp2-20261123-r49').resolve()",
        "r49 = device / 'out/ufs-sm8250-bp2-20261123-r49'\n"
        "out = (opts.out or device / 'out/ufs-sm8250-fbfill-20261123-r52').resolve()")
replace("before = {n: digest(r48 / n) for n in names}", "before = {n: digest(r49 / n) for n in names}")
replace("prior = json.loads((r48 / 'candidate-manifest.json').read_text())",
        "prior = json.loads((r49 / 'candidate-manifest.json').read_text())")
replace("f0fa42d6330625919bb76827b9fcb2df62cefedfe8c3a84c3d5d098cb39adb2b",
        "1180a2c7b2c7f903cf412791a704a3051dbf6335f696f0183896a4c3b1f9d3f5")
replace("frozen_paths = [r48 / n for n in names]", "frozen_paths = [r49 / n for n in names]")
replace("recipe = json.loads((r47 / 'commands.json').read_text())",
        "recipe = json.loads((r49 / 'commands.json').read_text())")
replace("compile_recipe = json.loads((r46 / 'commands.json').read_text())['compile-kern_exec.o']",
        "compile_recipe = recipe['compile-kern_exec.o']")
replace("paths = [Path(x) for x in (r47 / 'link.filelist').read_text().splitlines()]",
        "paths = [Path(x) for x in (r49 / 'link.filelist').read_text().splitlines()]")
replace("assert old_exec == r46 / 'objects/kern_exec.o'",
        "assert old_exec == r49 / 'objects/kern_exec.o'")
replace("shutil.copytree(r47 / 'source/bsd/kern', source)",
        "shutil.copytree(r49 / 'source/bsd/kern', source)")
replace("""assert text.count('#include "EnumaBootProgress.inc"') == 1
assert text.count('enuma_bp_print();') == 1
text = text.replace('#include "EnumaBootProgress.inc"', '#include "EnumaBootProgress2.inc"')
text = text.replace('enuma_bp_print();', 'enuma_bp_start();')
fb.write_text(text)
shutil.copyfile(device / 'package/EnumaBootProgress2.inc', source / 'EnumaBootProgress2.inc')""",
        """bp = source / 'EnumaBootProgress2.inc'
bptext = bp.read_text()
needle = '\\tenuma_matchcnt_dump();'
assert bptext.count(needle) == 1
bptext = bptext.replace(needle, '\\tprintf("enuma-fbfill: st=%d w=%u h=%u d=%u rb=%u avail=%u\\\\n", g_enuma_fbfill_state, g_enuma_fbfill_w, g_enuma_fbfill_h, g_enuma_fbfill_d, g_enuma_fbfill_rb, g_enuma_fbfill_avail);\\n' + needle)
bp.write_text('extern volatile int g_enuma_fbfill_state;\\nextern volatile unsigned g_enuma_fbfill_w, g_enuma_fbfill_h, g_enuma_fbfill_d, g_enuma_fbfill_rb, g_enuma_fbfill_avail;\\n' + bptext)""")
replace("assert digest(old_exec) != digest(obj)\n",
        """assert digest(old_exec) != digest(obj)
old_video, = (p for p in paths if p.name == 'video_console.o')
cc = json.loads(old_video.with_suffix('.o.json').read_text().rstrip().removesuffix(','))
video = out / 'source/osfmk/console/video_console.c'
video.parent.mkdir(parents=True)
code = Path(cc['file']).read_text()
declarations = 'static vm_offset_t  lastVideoVirt    = 0;\\nstatic vm_size_t    lastVideoMapSize = 0;'
assert code.count(declarations) == 1
code = code.replace(declarations, '')
marker = 'void\\nvcputc_options(char c, __unused bool poll)'
assert code.count(marker) == 1
code = code.replace(marker, declarations + '\\n#include "EnumaFbFill52.inc"\\n\\n' + marker)
marker = '\\t\\tVCPUTC_LOCK_LOCK();\\n\\t\\tif (gc_enabled) {'
assert code.count(marker) == 1
code = code.replace(marker, '\\t\\tVCPUTC_LOCK_LOCK();\\n\\t\\tenuma_fb_fill_once();\\n\\t\\tif (gc_enabled) {')
video.write_text(code)
shutil.copyfile(device / 'package/EnumaFbFill52Full.inc', video.parent / 'EnumaFbFill52.inc')
video_obj = out / 'objects/video_console.o'
argv = cc['arguments'].copy()
assert argv[1] == '-xc' and argv[2] == cc['file'] and argv[3] == '-o'
argv[2], argv[4] = str(video), str(video_obj)
argv.extend(['-iquote', str(Path(cc['file']).parent)])
call('compile-video_console.o', argv, cc['directory'])
assert digest(old_video) != digest(video_obj)
""")
replace("f'{obj if p == old_exec else p}\\n'",
        "f'{obj if p == old_exec else video_obj if p == old_video else p}\\n'")
replace("str(r47 / name)", "str(r49 / name)")
replace("b'enuma-bp\\0'):", "b'enuma-bp\\0', b'enuma-fbfill: st=%d w=%u h=%u d=%u rb=%u avail=%u\\n\\0'):")
replace("'_thread_call_enter1_delayed'):", "'_thread_call_enter1_delayed', '_vcputc_options'):")
replace("'--disassemble-symbols=_enuma_fb_dump,_enuma_bp_start,_enuma_bp_print,_enuma_bp_repeat'",
        "'--disassemble-symbols=_enuma_fb_dump,_enuma_bp_start,_enuma_bp_print,_enuma_bp_repeat,_vcputc_options'")
for old, new in [
    ("r48 / 'device'", "r49 / 'device'"),
    ("r48 / 'kernel.macho.adt'", "r49 / 'kernel.macho.adt'"),
    ("r48 / 'payload.img'", "r49 / 'payload.img'"),
    ("r48 / 'boot.img'", "r49 / 'boot.img'"),
    ("(r48 / n)", "(r49 / n)"),
    ("prior['args_after']", "args"),
    ("'r48_frozen'", "'r49_frozen'"),
    ("len(paths) - 1", "len(paths) - 2"),
]:
    text = text.replace(old, new)
replace("old_tree = fat_tree(r49 / 'payload.img')",
        """old_config = read_member(r49 / 'payload.img', 'unixnu.toml')
needle = b'"\\n[[entry]]\\nid = "reset"'
assert old_config.count(needle) == 1
config = old_config.replace(needle, b' enuma-fb-fill=1' + needle)
tmp = out / 'unixnu.toml'
tmp.write_bytes(config)
os.utime(tmp, (payload_step.EPOCH, payload_step.EPOCH))
call('replace-config', ['env', 'MTOOLS_SKIP_CHECK=1', 'TZ=UTC', 'mcopy', '-o', '-m',
    '-i', out / 'payload.img', tmp, '::/EFI/UniXNU/unixnu.toml'])
import tomllib
entry = lambda b: next(e for e in tomllib.loads(b.decode())['entry'] if e['id'] == 'xnu')['args']
args = entry(read_member(out / 'payload.img', 'unixnu.toml'))
assert args == entry(old_config) + ' enuma-fb-fill=1'
old_tree = fat_tree(r49 / 'payload.img')""")
replace("assert changed == ['Payloads/kernel.macho'], changed",
        "assert set(changed) == {'Payloads/kernel.macho', 'unixnu.toml'}, changed")
replace("assert read_member(out / 'payload.img', changed[0]) == (out / 'prelink.macho').read_bytes()",
        "assert read_member(out / 'payload.img', 'Payloads/kernel.macho') == (out / 'prelink.macho').read_bytes()")
replace("assert read_member(out / 'payload.img', 'unixnu.toml') == read_member(r49 / 'payload.img', 'unixnu.toml')",
        "assert read_member(out / 'payload.img', 'unixnu.toml') == config")
replace("'object': {'name': 'kern_exec.o', 'before': digest(old_exec), 'after': digest(obj)},",
        "'objects': {'kern_exec.o': [digest(old_exec), digest(obj)], 'video_console.o': [digest(old_video), digest(video_obj)]},")
exec(compile(text, str(here / 'build-enuma-r49-bp2.py'), 'exec'))
