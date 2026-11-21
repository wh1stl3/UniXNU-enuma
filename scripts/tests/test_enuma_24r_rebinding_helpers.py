#!/usr/bin/env python3
"""Negative/incremental checks for the rebinding helper accuracy fixes.

Synthetic instruction/symbol data only; no image, package or device is touched.
Covers shape normalization, the ADRP register chain, the vtable next-symbol
boundary and the actual write-permission test.
"""
import importlib.util
from pathlib import Path
import sys


def load():
    path = Path(__file__).resolve().parents[1] / 'audit-enuma-24r-rebinding.py'
    spec = importlib.util.spec_from_file_location('rebinding', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def line(address, text):
    return f'{address:016x}: 00 00 00 00 \t{text}'


def main():
    module = load()
    link = module.load('final_link', 'audit-enuma-ufs-final-link.py')
    cases = 0

    body = [line(0x1000, 'mov\tw0, #1'), line(0x1004, 'ret')]
    other = [line(0x2000, 'mov\tw0, #2'), line(0x2004, 'ret')]
    assert module.instruction_shape(link, body) == module.instruction_shape(link, other)
    cases += 1
    assert module.instruction_shape(link, body) != module.instruction_shape(
        link, [line(0x1000, 'mov\tw1, #1'), line(0x1004, 'ret')])
    cases += 1

    def read_pointer(address):
        return {0x1030: 0xfeedface}.get(address)

    instructions = [link.instruction(item) for item in
                    [line(0x2000, 'adrp\tx8, 0x1000'),
                     line(0x2004, 'add\tx9, x8, #0x28')]]
    result = module.materialization_at(instructions, 0, read_pointer)
    assert len(result) == 1 and result[0]['value'] == 0x1028
    assert result[0]['register_chain'] == {'adrp_destination': 'x8', 'base': 'x8',
                                          'destination': 'x9'}
    cases += 1
    wrong_base = [link.instruction(item) for item in
                  [line(0x2000, 'adrp\tx8, 0x1000'),
                   line(0x2004, 'add\tx9, x10, #0x28')]]
    assert module.materialization_at(wrong_base, 0, read_pointer) == []
    cases += 1
    load_chain = [link.instruction(item) for item in
                  [line(0x2000, 'adrp\tx8, 0x1000'),
                   line(0x2004, 'ldr\tx9, [x8, #0x30]')]]
    loaded = module.materialization_at(load_chain, 0, read_pointer)
    assert len(loaded) == 1 and loaded[0]['value'] == 0xfeedface
    cases += 1
    assert module.materialization_at([link.instruction(item) for item in
                                      [line(0x2000, 'adrp\tx8, 0x1000'),
                                       line(0x2004, 'ldr\tx9, [x10, #0x30]')]],
                                     0, read_pointer) == []
    cases += 1

    section = {'va': 0x1000, 'size': 0x1000}
    slots, boundary, exact = module.vtable_slot_count({'a': 0x1000, 'b': 0x1100}, section, 0x1000)
    assert slots == 32 and boundary == 0x1100 and exact is True
    cases += 1
    slots, boundary, exact = module.vtable_slot_count({'a': 0x1000}, section, 0x1000)
    assert slots == 512 and boundary == 0x2000 and exact is False
    cases += 1

    assert module.writable_segment({'initprot': 3, 'maxprot': 3}) is True
    cases += 1
    assert module.writable_segment({'initprot': 3, 'maxprot': 1}) is False
    cases += 1
    assert module.writable_segment({'initprot': 1, 'maxprot': 3}) is False
    cases += 1
    assert module.writable_segment(None) is False
    cases += 1

    print(f'self-checked rebinding helper checks: {cases} cases')
    return 0


if __name__ == '__main__':
    sys.exit(main())
