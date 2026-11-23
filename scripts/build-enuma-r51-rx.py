#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Rebuild only mach_msg and kern_exec from r49, retaining its package inputs."""
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
text = (here / 'build-enuma-r49-bp2.py').read_text()

def replace(old, new):
    global text
    assert text.count(old) == 1, (old, text.count(old))
    text = text.replace(old, new)

replace("parser_args.add_argument('--r49', action='store_true', required=True)",
        "parser_args.add_argument('--r51', action='store_true', required=True)")
replace("out = (opts.out or device / 'out/ufs-sm8250-bp2-20261123-r49').resolve()",
        "r49 = device / 'out/ufs-sm8250-bp2-20261123-r49'\n"
        "out = (opts.out or device / 'out/ufs-sm8250-rx-20261123-r51').resolve()")
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
        """assert text.count('#include "EnumaBootProgress2.inc"') == 1
assert text.count('enuma_bp_start();') == 1
text = text.replace('#include "EnumaBootProgress2.inc"', '#include "EnumaBootProgress51.inc"')
fb.write_text(text)
for inc in ('EnumaBootProgress51.inc', 'EnumaRx.inc'):
    shutil.copyfile(device / 'package' / inc, source / inc)""")
replace("assert digest(old_exec) != digest(obj)\n",
        """assert digest(old_exec) != digest(obj)
old_msg, = (p for p in paths if p.name == 'mach_msg.o')
original, = (Path(x) for x in (device / 'out/ufs-sm8250-launchd-attempt-20261123-r32/link.filelist').read_text().splitlines() if Path(x).name == 'mach_msg.o')
cc = json.loads(original.with_suffix('.o.json').read_text().rstrip().removesuffix(','))
msg = out / 'source/osfmk/ipc/mach_msg.c'
msg.parent.mkdir(parents=True)
code = (device / 'out/ufs-sm8250-launchd-ipc-20261123-r34/source/osfmk/ipc/mach_msg.c').read_text()
start = code.index('mach_msg_return_t\\nmach_msg2_trap(')
end = code.index('\\n}\\n', start) + 3
func = code[start:end]
assert func.count('return mr;') == 1 and func.count('return ') == 1
func = func.replace('{\\n', '{\\n\\tunsigned int enuma_rx_slot = enuma_rx_enter();\\n', 1)
func = func.replace('\\treturn mr;', '\\tenuma_rx_exit(enuma_rx_slot);\\n\\treturn mr;')
code = code[:start] + 'extern unsigned int enuma_rx_enter(void);\\nextern void enuma_rx_exit(unsigned int);\\n\\n' + func + code[end:]
msg.write_text(code)
msg_obj = out / 'objects/mach_msg.o'
argv = cc['arguments'].copy()
assert argv[1] == '-xc' and argv[2] == cc['file'] and argv[3] == '-o'
argv[2], argv[4] = str(msg), str(msg_obj)
call('compile-mach_msg.o', argv, cc['directory'])
assert digest(old_msg) != digest(msg_obj)
""")
replace("f'{obj if p == old_exec else p}\\n'",
        "f'{obj if p == old_exec else msg_obj if p == old_msg else p}\\n'")
replace("str(r47 / name)", "str(r49 / name)")
replace("b'enuma-bp\\0'):", "b'enuma-bp\\0', b'enuma-rx: sb5 in=%llu out=%llu\\n\\0', b'enuma-rx: bb34 in=%llu out=%llu\\n\\0'):")
replace("'_thread_call_enter1_delayed'):", "'_thread_call_enter1_delayed', '_enuma_rx_enter', '_enuma_rx_exit'):")
replace("'--disassemble-symbols=_enuma_fb_dump,_enuma_bp_start,_enuma_bp_print,_enuma_bp_repeat'",
        "'--disassemble-symbols=_enuma_fb_dump,_enuma_bp_start,_enuma_bp_print,_enuma_bp_repeat,_mach_msg2_trap'")
for old, new in [
    ("r48 / 'device'", "r49 / 'device'"),
    ("r48 / 'kernel.macho.adt'", "r49 / 'kernel.macho.adt'"),
    ("r48 / 'payload.img'", "r49 / 'payload.img'"),
    ("r48 / 'boot.img'", "r49 / 'boot.img'"),
    ("(r48 / n)", "(r49 / n)"),
    ("prior['args_after']", "prior['args']"),
    ("'r48_frozen'", "'r49_frozen'"),
    ("len(paths) - 1", "len(paths) - 2"),
]:
    text = text.replace(old, new)
replace("'object': {'name': 'kern_exec.o', 'before': digest(old_exec), 'after': digest(obj)},",
        "'objects': {'kern_exec.o': [digest(old_exec), digest(obj)], 'mach_msg.o': [digest(old_msg), digest(msg_obj)]},")
exec(compile(text, str(here / 'build-enuma-r49-bp2.py'), 'exec'))
