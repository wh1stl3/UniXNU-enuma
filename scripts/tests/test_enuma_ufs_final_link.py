#!/usr/bin/env python3
"""Negative injections for the final-link gate's stricter predicates.

Builds synthetic instruction bodies only; never reads or writes a kernel image.
Covers an extra call, a wrong refusal constant, a write side effect, a missing
wfe backedge, a wrong backedge target, a mis-resolved call target, a PMGR call
from the wrong caller, a PMGR target that does not match the defined symbol, and
a non-empty undefined set.
"""
import importlib.util
from pathlib import Path
import sys


def load():
    path = Path(__file__).resolve().parents[1] / 'audit-enuma-ufs-final-link.py'
    spec = importlib.util.spec_from_file_location('final_link', path)
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
    raise AssertionError(f'{getattr(function, "__name__", function)} accepted an injected negative')


def main():
    gate = load()
    cases = 0

    refusal = [line(0x1000, 'mov\tw0, #0'), line(0x1004, 'ret')]
    gate.check_constant_body('refusal', refusal, gate.REFUSAL_BODY)
    cases += 1
    expect_error(gate.check_constant_body, 'refusal',
                 refusal + [line(0x1008, 'bl\t0x900 <_IOLog>')], gate.REFUSAL_BODY)
    cases += 1
    expect_error(gate.check_constant_body, 'refusal',
                 refusal + [line(0x1008, 'str\tw0, [x1]')], gate.REFUSAL_BODY)
    cases += 1
    expect_error(gate.check_constant_body, 'refusal',
                 [line(0x1000, 'mov\tw0, #1'), line(0x1004, 'ret')], gate.REFUSAL_BODY)
    cases += 1

    async_body = [line(0x2000, 'mov\tw0, #728'), line(0x2004, 'movk\tw0, #57344, lsl #16'),
                  line(0x2008, 'ret')]
    gate.check_constant_body('async', async_body, gate.ASYNC_BODY)
    cases += 1
    expect_error(gate.check_constant_body, 'async',
                 async_body + [line(0x200c, 'bl\t0x900 <_complete>')], gate.ASYNC_BODY)
    cases += 1

    finish = [line(0x3000, 'wfe'), line(0x3004, 'b\t0x3000 <finish+0x0>')]
    gate.check_wfe_terminal('finish', finish)
    cases += 1
    expect_error(gate.check_wfe_terminal, 'finish',
                 [line(0x3000, 'wfe'), line(0x3004, 'ret')])
    cases += 1
    expect_error(gate.check_wfe_terminal, 'finish',
                 [line(0x3000, 'wfe'), line(0x3004, 'b\t0x2ffc <finish-0x4>')])
    cases += 1
    expect_error(gate.check_wfe_terminal, 'finish',
                 [line(0x3000, 'wfe'), line(0x3004, 'b\t0x3008 <finish+0x8>'),
                  line(0x3008, 'ret')])
    cases += 1

    body = [line(0x4000, 'bl\t0x4400 <ufsReuseFinish(char const*)>')]
    gate.check_calls_to('diagnostic', body, 'ufsReuseFinish(', 0x4400)
    cases += 1
    expect_error(gate.check_calls_to, 'diagnostic', body, 'ufsReuseFinish(', 0x4404)
    cases += 1
    expect_error(gate.check_calls_to, 'diagnostic',
                 [line(0x4000, 'b\t0x4400 <ufsReuseFinish(char const*)>')],
                 'ufsReuseFinish(', 0x4400, ('bl',))
    cases += 1

    functions = {'_bsd_init': [line(0x5000, 'bl\t0x6000 <_sheng_pmgr_run>')],
                 '_sheng_pmgr_run': [line(0x6000, 'b.ne\t0x6040 <_sheng_pmgr_run+0x40>')]}
    gate.check_pmgr(functions, {'_sheng_pmgr_run': 0x6000})
    cases += 1
    expect_error(gate.check_pmgr,
                 {'_other': [line(0x5000, 'bl\t0x6000 <_sheng_pmgr_run>')]},
                 {'_sheng_pmgr_run': 0x6000})
    cases += 1
    expect_error(gate.check_pmgr, functions, {'_sheng_pmgr_run': 0x6008})
    cases += 1

    gate.check_undefined({'native': [], 'prelink': []})
    cases += 1
    expect_error(gate.check_undefined, {'native': ['_missing'], 'prelink': []})
    cases += 1
    expect_error(gate.check_undefined, {'native': [], 'prelink': ['_missing']})
    cases += 1

    print(f'self-checked final-link negative injections: {cases} cases')
    return 0


if __name__ == '__main__':
    sys.exit(main())
