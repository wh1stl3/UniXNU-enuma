#!/usr/bin/env python3
"""Negative injections for the 24r package checker's pure helpers.

Synthetic ADT bytes only; no package, kernel or device is touched.
Covers the consumer range arithmetic (wrong parent/length/size/offset) and the
allowed ADT delta boundary.
"""
import importlib.util
from pathlib import Path
import sys


def load():
    path = Path(__file__).resolve().parents[1] / 'check-enuma-ufs-24r-package.py'
    spec = importlib.util.spec_from_file_location('ufs24_package', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reg(offset, length):
    return offset.to_bytes(8, 'little') + length.to_bytes(8, 'little')


def ranges(child, parent, span):
    return child.to_bytes(8, 'little') + parent.to_bytes(8, 'little') + span.to_bytes(8, 'little')


def expect_error(function, *args):
    try:
        function(*args)
    except (AssertionError, ValueError):
        return
    raise AssertionError('injected negative was accepted')


def main():
    package = load()
    cases = 0
    good_reg = reg(0x0d84000, 0x3000)
    good_ranges = ranges(0, 0x01000000, 0x17000000)
    result = package.translate_ufshc(good_reg, good_ranges)
    assert result['address'] == 0x01d84000 and result['length'] == 0x3000
    cases += 1
    expect_error(package.translate_ufshc, reg(0x0d84000, 0x2000), good_ranges)
    cases += 1
    expect_error(package.translate_ufshc, reg(0x0d84000, 0x3000), ranges(0, 0x02000000, 0x17000000))
    cases += 1
    expect_error(package.translate_ufshc, reg(0x0d84000, 0x3000), ranges(0, 0x01000000, 0x1000))
    cases += 1
    expect_error(package.translate_ufshc, b'', good_ranges)
    cases += 1
    expect_error(package.translate_ufshc, good_reg, b'')
    cases += 1
    expect_error(package.translate_ufshc, reg(0x0d84000, 0x3000), ranges(0x1000, 0x01000000, 0x17000000))
    cases += 1

    old = {'/device-tree/chosen:random-seed': b'a', '/device-tree/arm-io:ranges': b'r'}
    allowed = {'/device-tree/chosen:random-seed': b'b', '/device-tree/arm-io:ranges': b'r'}
    assert package.adt_delta(old, allowed) == ['/device-tree/chosen:random-seed']
    cases += 1
    unexpected = {'/device-tree/chosen:random-seed': b'b', '/device-tree/arm-io:ranges': b'q'}
    assert '/device-tree/arm-io:ranges' in package.adt_delta(old, unexpected)
    cases += 1

    print(f'self-checked 24r package negative injections: {cases} cases')
    return 0


if __name__ == '__main__':
    sys.exit(main())
