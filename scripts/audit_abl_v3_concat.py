"""Bind enuma ABL's vendor/generic copy path to actual PE instructions."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from audit_display_handoff import named_pe, ABL_PE_SHA, PINS

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    0x16448: ('ldrb', 'w9, [x8, #0xc]!'),
    0x16468: ('stur', 'w9, [x24, #-0x38]'),
    0x16470: ('ldrb', 'w10, [x8, #0x18]!'),
    0x1648c: ('stur', 'w10, [x24, #-0x28]'),
    0x173a4: ('ldr', 'w8, [x20, #0x458]'),
    0x173a8: ('cmp', 'w8, #3'),
    0x173ac: ('b.lo', '#0x173dc'),
    0x173c0: ('ldur', 'w2, [x24, #-0x28]'),
    0x173cc: ('ldr', 'x8, [x8, #0x160]'),
    0x173d0: ('blr', 'x8'),
    0x173d4: ('ldur', 'w8, [x24, #-0x28]'),
    0x173d8: ('add', 'x21, x21, x8'),
    0x173e4: ('ldp', 'w2, w10, [x24, #-0x38]'),
    0x173e8: ('mov', 'x0, x21'),
    0x173f4: ('ldr', 'x8, [x8, #0x160]'),
    0x173f8: ('blr', 'x8'),
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-path', type=Path)
    a = p.parse_args()
    if a.tool_path: sys.path.insert(0, str(a.tool_path.resolve()))
    import capstone
    import pefile
    raw = (ROOT / 'out/device/abl_a.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest() != PINS['out/device/abl_a.bin']:
        raise ValueError('ABL backup changed')
    blob = named_pe(raw, 'LinuxLoader', ABL_PE_SHA)
    pe = pefile.PE(data=blob)
    decoder = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_LITTLE_ENDIAN)
    records = []
    def check(rva, code):
        ins = list(decoder.disasm(code, rva))
        if len(ins) != 1 or (ins[0].mnemonic, ins[0].op_str) != EXPECTED[rva]:
            raise ValueError('unexpected instruction at ' + hex(rva))
        return dict(rva=hex(rva), bytes=code.hex(), mnemonic=ins[0].mnemonic, operands=ins[0].op_str)
    for rva in EXPECTED:
        records.append(check(rva, pe.get_data(rva, 4)))
    try:
        check(0x173d8, b'\x1f\x20\x03\xd5')  # Replace exact byte advance with NOP.
    except ValueError:
        negative = 'rejected'
    else:
        raise ValueError('mutation accepted')
    report = dict(scope='actual saved ABL PE disassembly; no runtime execution',
                  abl_sha256=PINS['out/device/abl_a.bin'], linux_loader_sha256=ABL_PE_SHA,
                  instructions=records, mutation_negative=negative,
                  interpretation='v3 branch uses vendor size from header+0x18, copies via slot0x160, advances destination by that raw size without rounding, then copies generic size from boot header+0xc; slot0x160 is consistent with UEFI CopyMem',
                  runtime_layout_observed=False,
                  source_contract='https://android.googlesource.com/platform/system/tools/mkbootimg/+/808d42e197506319ee65eb078d3defd9602e2ac2/include/bootimg/bootimg.h',
                  limits=['complete allocation and selected DTB paths not proven by these slices',
                          'temporary-entry FDT/start/end and exact payload integrity still checked at runtime'])
    (ROOT / 'reports/enuma-abl-v3-concat.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: pinned enuma ABL raw vendor-size advance and subsequent generic copy; mutation rejected')


if __name__ == '__main__':
    main()
