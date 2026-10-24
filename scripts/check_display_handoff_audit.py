"""Negative-input checks for the offline ABI auditor; no device operations."""
import argparse
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool-path', type=Path)
    args = parser.parse_args()
    if args.tool_path:
        sys.path.insert(0, str(args.tool_path.resolve()))
    import pefile
    import audit_display_handoff as audit
    # Extract from the immutable saved image, independent of latest build output.
    image = audit.pinned('out/boot-candidate/vt-oemdisplay.img')
    source = audit.named_pe(image[4288:4288 + 0x300000], 'DisplayDxe', audit.DISPLAY_SHA)
    pe = pefile.PE(data=source)
    changed = bytearray(source)
    offset = pe.get_offset_from_rva(0x1be4)
    changed[offset:offset + 4] = bytes.fromhex('1f2003d5')  # Replace actual BL with NOP.
    checks = [
        ('changed call instruction', lambda: audit.pe_evidence(bytes(changed), [(0x1bd8, 0x1bec)],
                                                              {0x1be4: ('bl', '#0x3874')})),
        ('truncated firmware volume', lambda: audit.named_pe(b'\0' * 64, 'DisplayDxe', audit.DISPLAY_SHA)),
        ('truncated FDT', lambda: audit.dtb_evidence(bytes.fromhex('d00dfeed') + b'\0' * 8)),
    ]
    for name, run in checks:
        try:
            run()
        except ValueError:
            print('PASS rejection: ' + name)
        else:
            raise AssertionError('Auditor accepted ' + name)


if __name__ == '__main__':
    main()
