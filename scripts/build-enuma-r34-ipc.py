#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Replay r32 with isolated user Mach message entry counters."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
here = Path(__file__).resolve().parent
text = (here / "build-enuma-r32-attempt.py").read_text()
needle = "exec(compile(text, str(here / 'build-enuma-r30-control.py'), 'exec'))"
assert text.count(needle) == 1
extension = r'''
needle = "namespace = {'__name__': '__main__'"
extra = r"""
# Extend the r29 source generator before r30 invokes it.
needle = "    uc.write_text(s)\n"
addition = <Q>    old_msg, = [p for p in paths if p.name == 'mach_msg.o']
    msg_source = tree / '.cache/xnu-work/osfmk/ipc/mach_msg.c'
    msg = src / 'osfmk/ipc/mach_msg.c'
    msg.parent.mkdir(parents=True)
    code = msg_source.read_text()
    marker = 'static mach_msg_return_t\\\\nmach_msg_trap_send('
    assert code.count(marker) == 1
    code = code.replace(marker, 'extern void enuma_ipc_record(unsigned int);\\\\n\\\\n' + marker)
    for marker, kind in [('mach_msg_trap_send(', 0), ('mach_msg_trap_receive(', 1)]:
        start = code.index(marker)
        body = code.index('\\\\n{\\\\n', start) + len('\\\\n{\\\\n')
        code = code[:body] + '\\\\tenuma_ipc_record(' + str(kind) + ');\\\\n' + code[body:]
    msg.write_text(code)
    import json
    msg_cc = json.loads(old_msg.with_suffix('.o.json').read_text().rstrip().removesuffix(','))
    argv = msg_cc['arguments'].copy()
    new_msg = objects / 'mach_msg.o'
    assert argv[1] == '-xc' and argv[2] == msg_cc['file'] and argv[3] == '-o' and argv[4] == 'mach_msg.o'
    argv[2], argv[4] = msg, new_msg
    call('compile-mach-msg', argv, msg_cc['directory'])
    assert digest(new_msg) != digest(old_msg)

<Q>
assert text.count(needle) == 1
text = text.replace(needle, addition + needle)
needle = "    new_archive = BASE / 'objects/libEnumaGopLegacy.a'\n"
addition = <Q>    lines = filelist.read_text().splitlines()
    assert lines.count(str(old_msg)) == 1
    filelist.write_text(''.join(str(new_msg if p == str(old_msg) else p) + '\\\\n' for p in lines))
<Q>
assert text.count(needle) == 1
text = text.replace(needle, addition + needle)
needle = "    blob = path.read_bytes()\n"
addition = "    formats += ['enuma-ipc: begin send=%llu recv=%llu\\n', 'enuma-ipc: bb send=%llu recv=%llu\\n', 'enuma-ipc: sb send=%llu recv=%llu\\n', 'enuma-ipc: end\\n']\n"
assert text.count(needle) == 1
text = text.replace(needle, addition + needle)
"""
assert text.count(needle) == 1
text = text.replace(needle, extra + '\n' + needle)
text = text.replace("ufs-sm8250-launchd-attempt-20261123-r32'",
                    "ufs-sm8250-launchd-ipc-20261123-r34'")
'''
text = text.replace(needle, extension.replace('<Q>', "'''") + '\n' + needle)
text = text.replace("shutil.copyfile(DEVICE / 'package/EnumaAttempt.inc', bsd / 'EnumaAttempt.inc')",
    "shutil.copyfile(DEVICE / 'package/EnumaAttempt.inc', bsd / 'EnumaAttempt.inc')\n"
    "    shutil.copyfile(DEVICE / 'package/EnumaIpc.inc', bsd / 'EnumaIpc.inc')\n"
    "    inc.write_text(inc.read_text().replace('#include \"EnumaAttempt.inc\"', "
    "'#include \"EnumaAttempt.inc\"\\\\\\\\n#include \"EnumaIpc.inc\"').replace("
    "'enuma_att_dump();', 'enuma_att_dump();\\\\\\\\n\\\\\\\\tenuma_ipc_dump();'))")
exec(compile(text, str(here / "build-enuma-r32-attempt.py"), "exec"))
