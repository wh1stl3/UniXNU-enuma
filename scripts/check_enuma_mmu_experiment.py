"""Offline regression and refusal checks for the exact-PE experiment generator."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import prepare_enuma_mmu_experiment as tool
from map_oem_trace_rva import identify
from plan_enuma_panel_handoff import contract


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pe', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    out = args.output.resolve()
    out.relative_to(tool.ROOT / 'out')
    out.mkdir(parents=True, exist_ok=False)
    original = args.pe.read_bytes()
    checks = []

    def rejects(name, fn):
        try:
            fn()
        except (ValueError, FileExistsError):
            checks.append(name)
        else:
            raise AssertionError(name + ' was accepted')

    candidate, report = tool.prepare(original)
    assert candidate[:0x1994] == original[:0x1994]
    assert candidate[0x1998:] == original[0x1998:]
    assert candidate[0x1994:0x1998] == bytes.fromhex('01008052')
    checks.append('only one instruction changes; all other bytes identical')
    rejects('reject truncated input', lambda: tool.prepare(original[:-1]))
    bad = bytearray(original); bad[-1] ^= 1
    rejects('reject wrong digest outside patch site', lambda: tool.prepare(bytes(bad)))
    rejects('reject already patched input', lambda: tool.prepare(candidate))
    rejects('original offline RVA mapper identity rejects patched PE', lambda: identify(candidate))
    # Independently exercise guards behind the digest barrier without weakening production checks.
    with patch.object(tool, 'identify', return_value=report['original_sha256']):
        bad = bytearray(original); bad[0x1994:0x1998] = bytes.fromhex('1f2003d5')
        rejects('reject wrong patch instruction after identity gate', lambda: tool.prepare(bytes(bad)))
        bad = bytearray(original); bad[0x1998:0x199c] = bytes.fromhex('1f2003d5')
        rejects('reject altered MDPInit call after identity gate', lambda: tool.prepare(bytes(bad)))
        bad = bytearray(original); bad[0x16b88:0x16b8c] = bytes.fromhex('1f2003d5')
        rejects('reject altered bit1 branch after identity gate', lambda: tool.prepare(bytes(bad)))
    dry = tool.write_result(args.pe, out/'inspect')
    assert not dry['emitted_pe'] and list((out/'inspect').iterdir()) == [out/'inspect/manifest.json']
    checks.append('default inspection emits no PE')
    emitted = tool.write_result(args.pe, out/'emit', True)
    pe = out/'emit/DisplayDxe.mmu-flag-only.efi'
    assert pe.read_bytes() == candidate and emitted['patched_sha256'] == hashlib.sha256(candidate).hexdigest()
    checks.append('explicit emission readback matches')
    rejects('refuse existing output directory', lambda: tool.write_result(args.pe, out/'emit', True))
    rejects('refuse output outside out', lambda: tool.write_result(args.pe, tool.ROOT/'forbidden-output', True))
    assert args.pe.read_bytes() == original
    asm = subprocess.check_output(['/usr/bin/llvm-objdump', '-d', '--start-address=0x1990',
                                   '--stop-address=0x19a0', str(pe)], text=True)
    assert 'mov\tw1, #0' in asm and 'bl\t0x167d8' in asm and 'cbz\tw0' in asm
    (out/'patched-site.txt').write_text(asm)
    checks.append('AArch64 disassembly confirms argument zero and retained call/error check')
    xml = (tool.ROOT/'out/firmware-vendor/raw/Panel_K81_42_02_0a_dualdsi_cphy_lcd_vid.xml').read_bytes()
    panel = contract(xml)
    expected_payloads = json.loads((tool.ROOT/'out/public-display-references-20261027-c999/phase2/semantic-comparison.json').read_text())
    assert expected_payloads['elish']['dt_command_count'] == len(panel['controller_streams'][0]) == 188
    assert panel['events'][-8:] == [
        dict(kind='select', mask=2), dict(kind='dcs', data_type=5, payload='11', mask=2),
        dict(kind='select', mask=1), dict(kind='dcs', data_type=5, payload='11', mask=1),
        dict(kind='select', mask=3), dict(kind='delay', ms=100),
        dict(kind='dcs', data_type=5, payload='29', mask=3), dict(kind='delay', ms=16)]
    checks.append('panel contract retains split links and native delay sequence')
    rejects('reject altered panel XML', lambda: contract(xml.replace(b'FD 02', b'FD 03')))
    rejects('reject truncated panel XML', lambda: contract(xml[:-1]))
    result = dict(passed=True, checks=checks, count=len(checks),
                  original_sha256=report['original_sha256'], patched_sha256=report['patched_sha256'],
                  hardware_executed=False, source_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in [Path(__file__), Path(tool.__file__), tool.ROOT/'scripts/map_oem_trace_rva.py',
                            tool.ROOT/'scripts/plan_enuma_panel_handoff.py']})
    (out/'result.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
