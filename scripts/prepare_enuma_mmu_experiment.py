"""Prepare an offline, exact-PE experiment; never package or deploy firmware.

Changes only MDPInit's MMU/SID flag from 2 to 0. This is not a proven fix,
and deliberately does not bypass MDPSetupPipe or MDPPanelInit.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from map_oem_trace_rva import identify, sections, map_return

ROOT = Path(__file__).resolve().parents[1]
PATCH_RVA = 0x1994
BEFORE = bytes.fromhex('e1031f32')  # orr w1, wzr, #2
AFTER = bytes.fromhex('01008052')   # mov w1, #0


def file_offset(data, rva, length=4):
    hits = [s for s in sections(data)
            if s[1] <= rva and rva + length <= s[1] + s[2]]
    if len(hits) != 1 or not hits[0][4] & 0x20000000:
        raise ValueError('RVA is not uniquely file-backed executable code')
    s = hits[0]
    return s[3] + rva - s[1]


def prepare(data):
    original = identify(data)
    expected = {PATCH_RVA: BEFORE, 0x16800: bytes.fromhex('f403012a'),
                0x16b88: bytes.fromhex('f4020836')}
    for rva, word in expected.items():
        off = file_offset(data, rva)
        if data[off:off+4] != word:
            raise ValueError('instruction guard mismatch')
    calls = {0x199c: '0x167d8', 0x176c8: '0x18884', 0x176ec: '0x18700'}
    for ret, target in calls.items():
        if map_return(data, ret).get('static_target_rva') != target:
            raise ValueError('call target guard mismatch')
    pe = struct.unpack_from('<I', data, 60)[0] + 24
    # Keep all headers unchanged; only this exact unsigned/checksum-zero PE is accepted.
    if struct.unpack_from('<I', data, pe+64)[0] or any(struct.unpack_from('<II', data, pe+144)):
        raise ValueError('unexpected checksum or certificate directory')
    off = file_offset(data, PATCH_RVA)
    patched = data[:off] + AFTER + data[off+4:]
    changed = [i for i, (a, b) in enumerate(zip(data, patched)) if a != b]
    if len(patched) != len(data) or not changed or any(not off <= i < off+4 for i in changed):
        raise ValueError('change escaped the one-instruction patch')
    report = dict(schema=1, experiment='enuma-mdpinit-mmu-flag-only',
                  original_sha256=original, patched_sha256=hashlib.sha256(patched).hexdigest(),
                  pe_bytes=len(data), patch_rva=hex(PATCH_RVA), file_offset=hex(off),
                  before=BEFORE.hex(), after=AFTER.hex(), changed_bytes=len(changed),
                  retained_calls={hex(k-4): v for k, v in calls.items()},
                  hypothesis='Avoid repeating the MMU/SID setup after predecessor firmware handoff',
                  hardware_executed=False, firmware_packaged=False, deployment_qualified=False,
                  driver_return_fabricated=False, panel_init_bypassed=False,
                  limitations=['Does not skip constructors or earlier MDP initialization',
                               'Does not prove inherited MMU/SID state is suitable',
                               'Old original-PE trace identity must reject this new digest',
                               'Requires a separate profile, exact packaged identity and reliable capture before a trial'],
                  emitted_pe=False)
    return patched, report


def write_result(source, output, emit=False):
    source, output = Path(source).resolve(), Path(output).resolve()
    out_root = (ROOT / 'out').resolve()
    output.relative_to(out_root)
    if output == out_root:
        raise ValueError('use a new child directory under out')
    data = source.read_bytes()
    patched, report = prepare(data)
    output.mkdir(parents=True, exist_ok=False)
    if emit:
        dest = output / 'DisplayDxe.mmu-flag-only.efi'
        with dest.open('xb') as stream:
            stream.write(patched)
        if dest.read_bytes() != patched:
            raise ValueError('output readback failed')
        report['emitted_pe'] = True
    with (output / 'manifest.json').open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pe', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--emit-pe', action='store_true', help='emit an unqualified PE in a new out directory')
    args = parser.parse_args()
    print(json.dumps(write_result(args.pe, args.output, args.emit_pe), indent=2))


if __name__ == '__main__':
    main()
