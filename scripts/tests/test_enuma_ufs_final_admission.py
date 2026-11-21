#!/usr/bin/env python3
"""Negative injections for the candidate admission audit helpers.

Synthetic instruction/personality text only; no image is read or written.
Covers a missing shared argument gate, a call in the refusal tail, a tail that
does not return the constant false/null, a probe without a null register before
the gate, a missing root personality and a duplicated personality.
"""
import importlib.util
from pathlib import Path
import sys


def load(name, filename):
    path = Path(__file__).resolve().parents[1] / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def line(address, text):
    return f'{address:016x}: 00 00 00 00 \t{text}'


def expect_error(function, *args):
    try:
        function(*args)
    except (AssertionError, ValueError):
        return
    raise AssertionError('injected negative was accepted')


def main():
    link = load('final_link', 'audit-enuma-ufs-final-link.py')
    admission = load('admission', 'audit-enuma-ufs-final-admission.py')
    cases = 0

    probe = [line(0x1000, 'mov\tx0, #0'),
             line(0x1004, 'cbz\tw23, 0x1100 <f+0x100>'),
             line(0x1008, 'b.ne\t0x1100 <f+0x100>'),
             line(0x100c, 'cbnz\tw22, 0x1100 <f+0x100>'),
             line(0x1010, 'adrp\tx8, 0x9000 <limit()+0x10>'),
             line(0x1080, 'bl\t0x2000 <limit()>'),
             line(0x1100, 'ldp\tx29, x30, [sp, #16]'),
             line(0x1104, 'ret')]
    admission.check_guard(link, 'probe', probe, 'limit(', 3, True)
    cases += 1
    expect_error(admission.check_guard, link, 'probe', probe[:2] + probe[5:], 'limit(', 3, True)
    cases += 1
    expect_error(admission.check_guard, link, 'probe',
                 probe[:5] + [line(0x1080, 'bl\t0x2000 <limit()>'),
                              line(0x1100, 'bl\t0x3000 <other()>'), line(0x1104, 'ret')],
                 'limit(', 3, True)
    cases += 1

    start = [line(0x1000, 'cbz\tw21, 0x1100 <f+0x100>'),
             line(0x1004, 'b.ne\t0x1100 <f+0x100>'),
             line(0x1008, 'cbnz\tw20, 0x1100 <f+0x100>'),
             line(0x1080, 'bl\t0x2000 <limit()>'),
             line(0x1100, 'mov\tw0, #0'),
             line(0x1104, 'ret')]
    admission.check_guard(link, 'start', start, 'limit(', 3, False)
    cases += 1
    expect_error(admission.check_guard, link, 'start',
                 start[:-2] + [line(0x1100, 'mov\tw0, #1'), line(0x1104, 'ret')],
                 'limit(', 3, False)
    cases += 1
    expect_error(admission.check_guard, link, 'start',
                 start[:1] + start[2:], 'limit(', 3, False)
    cases += 1
    expect_error(admission.check_guard, link, 'start',
                 [line(0x1000, 'bl\t0x2000 <limit()>'),
                  line(0x1004, 'cbz\tw21, 0x1100 <f+0x100>'),
                  line(0x1008, 'b.ne\t0x1100 <f+0x100>'),
                  line(0x100c, 'cbnz\tw20, 0x1100 <f+0x100>'),
                  line(0x1100, 'mov\tw0, #0'), line(0x1104, 'ret')],
                 'limit(', 3, False)
    cases += 1

    def config(args, entries=1, entry_id='xnu'):
        body = 'version = 1\n[boot]\ntimeout = 3\ndefault = "xnu"\n'
        for _ in range(entries):
            body += f'[[entry]]\nid = "{entry_id}"\nargs = "{args}"\n'
        return body

    good = '-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-observe-reuse=1'
    admission.select_boot_entry(config(good))
    cases += 1
    expect_error(admission.select_boot_entry, config(good, entries=2))
    cases += 1
    expect_error(admission.select_boot_entry, config(good, entry_id='other'))
    cases += 1
    for bad in ('-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-observe-reuse=1 pmgr=2',
                '-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-observe-reuse=1 '
                'native-ufs-observe-reuse=1',
                '-v serial=3 rd=md0-ramblock sheng-pmgr=2 native-ufs-observe-reuse=1',
                '-v serial=3 rd=md0-ramblock pmgr=2 sheng-pmgr=2 native-ufs-observe-reuse=1',
                '-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-observe-reuse=1 native-ufs-root=0',
                '-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-observe-reuse=1 native-ufs-probe=0',
                '-v serial=3 rd=md0-ramblock pmgr=1 native-ufs-observe-reuse=1',
                '-v serial=3 rd=md0-ramblock pmgr=2'):
        expect_error(admission.select_boot_entry, config(bad))
        cases += 1

    valid = (admission.PERSONALITY_NUB + ' ' + admission.PERSONALITY_ROOT)
    admission.check_personality(valid)
    cases += 1
    expect_error(admission.check_personality,
                 admission.PERSONALITY_NUB + ' ' + admission.PERSONALITY_NUB)
    cases += 1
    expect_error(admission.check_personality, admission.PERSONALITY_NUB)
    cases += 1

    print(f'self-checked final-admission negative injections: {cases} cases')
    return 0


if __name__ == '__main__':
    sys.exit(main())
