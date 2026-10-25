"""Static constructor ordering in the pinned OEM PE; never drives hardware."""
import hashlib
import json
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]


def inspect(blob):
    import capstone
    import pefile
    pe = pefile.PE(data=blob)
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_LITTLE_ENDIAN)
    md.detail = True
    def code(start, end):
        return list(md.disasm(pe.get_data(start, end-start), start))
    wrapper = code(0x114c, 0x1238)
    if [(i.address, i.operands[0].imm) for i in wrapper if i.mnemonic == 'bl' and i.address in [0x1190, 0x120c]] != [(0x1190,0x123c),(0x120c,0x1508)]:
        raise ValueError('constructor-before-main wrapper changed')
    chain = code(0x123c, 0x14bc)
    calls = [(i.address, i.operands[0].imm) for i in chain if i.mnemonic == 'bl' and i.operands[0].imm not in [0x3df0,0x3ef4]]
    expected = [(0x1250,0x5848),(0x1290,0x5888),(0x12d0,0x5918),(0x1310,0x59f8),
                (0x1350,0x5b60),(0x1390,0x5d70),(0x13c8,0x5e5c),(0x1400,0x612c),
                (0x1438,0x6628),(0x1470,0x6ffc)]
    if calls != expected:
        raise ValueError('ordered constructor call list changed')
    guids = {hex(rva):str(uuid.UUID(bytes_le=pe.get_data(rva,16))) for rva in [0x3e0f8,0x3e108]}
    if list(guids.values()) != ['05ad34ba-6f02-4214-952e-4da0398e2bb9','7739f24c-93d7-11d4-9a3a-0090273fc14d']:
        raise ValueError('DXE services/HOB table GUID changed')
    if [(i.mnemonic,i.op_str) for i in code(0x1508,0x150c)] != [('b','#0x16e8')]:
        raise ValueError('main trampoline changed')
    return dict(constructor_calls=[dict(call_rva=hex(a),target_rva=hex(b)) for a,b in calls],
                configuration_table_guids=guids,
                main_trampoline_rva='0x1508', main_target_rva='0x16e8',
                instructions=[dict(rva=hex(i.address),mnemonic=i.mnemonic,operands=i.op_str) for i in wrapper+chain])


def main():
    sys.path.insert(0,str(ROOT/'out/reverse-tools'))
    from audit_display_handoff import named_pe, DISPLAY_SHA, pinned
    import pefile
    blob = named_pe(pinned('out/device/xbl_a.bin'),'DisplayDxe',DISPLAY_SHA)
    report = inspect(blob)
    pe = pefile.PE(data=blob)
    bad = bytearray(blob)
    offset = pe.get_offset_from_rva(0x1310)
    bad[offset:offset+4] = bytes.fromhex('1f2003d5')
    try:
        inspect(bytes(bad))
    except ValueError:
        pass
    else:
        raise ValueError('removed constructor call accepted')
    report.update(scope='hash-pinned OEM PE static path only; does not prove any constructor ran or failed',
                  pe_sha256=hashlib.sha256(blob).hexdigest(), removed_constructor_rejected=True,
                  interpretation='Display thread configuration is consumed later in main and cannot bypass this constructor chain',
                  limits=['linear call-list and wrapper review, not a complete call graph or runtime root cause',
                          'DXE services/HOB tables are normal UEFI requirements; presence at the actual call remains unobserved'])
    (ROOT/'reports/enuma-display-constructor-path.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: pinned wrapper has ten ordered constructor calls before main; mutation rejected; static only')


if __name__ == '__main__':
    main()
