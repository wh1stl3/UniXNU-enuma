"""Corrupt real archived Core inputs to exercise the boundary auditor; no device I/O."""
import argparse
import json
from pathlib import Path
import struct
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--map', type=Path, required=True)
    parser.add_argument('--tool-path', type=Path)
    parser.add_argument('--compare-a', type=Path)
    args = parser.parse_args()
    if args.tool_path:
        sys.path.insert(0, str(args.tool_path.resolve()))
    import pefile
    from audit_display_boundary_core import code_review
    core = (args.archive / 'DxeCore.efi').read_bytes()
    map_text = args.map.read_text()
    point = json.loads((args.archive / 'qualification.json').read_text())['detail_point']
    valid = code_review(core, map_text, point)
    pe = pefile.PE(data=core)
    calls = valid['callsites'][0]
    start_address = (calls['setjump_call_rva'] if point == 22 else calls['entry_call_rva'] if point in (20, 21) else
                     (calls['CoreStartImage_calls_before'] if point == 13 else calls['CoreStartImage_calls_after'])[0])
    no_start = bytearray(core)
    offset = pe.get_offset_from_rva(int(start_address, 16))
    no_start[offset:offset + 4] = bytes.fromhex('1f2003d5')
    # Damage an actual GUID MOVK immediate, retaining the opcode and register.
    movk = next(i for i in valid['checkpoint_body'] if i['mnemonic'] == 'movk')
    wrong_guid = bytearray(core)
    offset = pe.get_offset_from_rva(int(movk['rva'], 16))
    instruction = struct.unpack_from('<I', wrong_guid, offset)[0]
    struct.pack_into('<I', wrong_guid, offset, instruction ^ (1 << 5))
    for name, payload, requested in [('removed StartImage call', bytes(no_start), point),
                                     ('corrupt GUID immediate', bytes(wrong_guid), point),
                                     ('wrong checkpoint point', core, 15 if point == 13 else 13)]:
        try:
            code_review(payload, map_text, requested)
        except ValueError:
            print('PASS rejection: ' + name)
        else:
            raise AssertionError('Accepted corrupted boundary input: ' + name)
    if point in (20, 21, 22):
        for label, instruction in [
                ('removed null-handle gate', next(i for i in valid['checkpoint_body'] if i['mnemonic'] == 'cbz')),
                ('removed scheduled-handle comparison', next(i for i in valid['checkpoint_body'] if i['mnemonic'] == 'cmp' and i['operands'] == 'x8, x1'))]:
            damaged = bytearray(core)
            offset = pe.get_offset_from_rva(int(instruction['rva'], 16))
            damaged[offset:offset+4] = bytes.fromhex('1f2003d5')
            try:
                code_review(bytes(damaged), map_text, point)
            except ValueError:
                print('PASS rejection: ' + label)
            else:
                raise AssertionError('Accepted corrupted entry bridge: ' + label)
    if point == 22:
        for label, address in [('removed CoreExit transfer', calls['exit_call_rva']),
                               ('removed SetJump return branch', hex(int(calls['setjump_call_rva'],16)+4))]:
            damaged = bytearray(core)
            offset = pe.get_offset_from_rva(int(address,16))
            damaged[offset:offset+4] = bytes.fromhex('1f2003d5')
            try:
                code_review(bytes(damaged),map_text,point)
            except ValueError:
                print('PASS rejection: '+label)
            else:
                raise AssertionError('Accepted corrupted Exit path: '+label)
    delay = valid.get('delay_contract', {})
    if delay.get('mode') == 'constant_specialized_2x1s':
        immediate = next(i for i in delay['callee_body'] if i['mnemonic'] == 'mov' and i['operands'].startswith('w0, #'))
        bad_delay = bytearray(core)
        offset = pe.get_offset_from_rva(int(immediate['rva'], 16))
        struct.pack_into('<I', bad_delay, offset, struct.unpack_from('<I', bad_delay, offset)[0] ^ (1 << 5))
        try:
            code_review(bytes(bad_delay), map_text, point)
        except ValueError:
            print('PASS rejection: altered specialized nanosecond delay')
        else:
            raise AssertionError('Accepted an altered specialized delay')
    if args.compare_a:
        from audit_display_handoff import firmware_files
        from audit_display_boundary_core import codeview_guid_only
        modules = [{m['name']: m['data'] for m in firmware_files((p / 'candidate.fd').read_bytes())}
                   for p in [args.compare_a, args.archive]]
        a, b = modules[0]['PcdDxe'], modules[1]['PcdDxe']
        codeview_guid_only(a, b)
        bad_code = bytearray(b)
        pc = pefile.PE(data=b)
        section = next(s for s in pc.sections if s.Name.rstrip(b'\0') == b'.text')
        bad_code[section.PointerToRawData] ^= 1
        try:
            codeview_guid_only(a, bytes(bad_code))
        except ValueError:
            print('PASS rejection: PcdDxe code change cannot hide behind debug GUID normalization')
        else:
            raise AssertionError('Accepted PcdDxe code modification')


if __name__ == '__main__':
    main()
