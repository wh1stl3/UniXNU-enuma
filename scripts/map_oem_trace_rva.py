"""Map trace return RVAs to verified ARM64 call instructions in the exact OEM PE.

Static attribution only: this does not establish execution, a callee symbol,
or a missing return's cause. No third-party disassembler is required.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

OEM_SHA256 = '6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425'
OEM_SIZE = 315392


def sections(data):
    def unpack(fmt, offset):
        try:
            return struct.unpack_from(fmt, data, offset)
        except struct.error as exc:
            raise ValueError('truncated PE') from exc
    if data[:2] != b'MZ':
        raise ValueError('missing DOS header')
    pe, = unpack('<I', 60)
    if data[pe:pe + 4] != b'PE\0\0':
        raise ValueError('missing PE signature')
    machine, count = unpack('<HH', pe + 4)
    optional, = unpack('<H', pe + 20)
    magic, = unpack('<H', pe + 24)
    if machine != 0xaa64 or magic != 0x20b or optional < 112:
        raise ValueError('expected ARM64 PE32+')
    result = []
    for i in range(count):
        pos = pe + 24 + optional + 40 * i
        name, virtual, rva, size, raw = unpack('<8sIIII', pos)
        flags, = unpack('<I', pos + 36)
        if raw + size > len(data):
            raise ValueError('section raw range outside PE')
        result.append((name.rstrip(b'\0').decode('ascii'), rva, size, raw, flags))
    return result


def map_return(data, return_rva):
    if not isinstance(return_rva, int) or return_rva < 4 or return_rva % 4:
        raise ValueError('return RVA must be aligned and at least four')
    site = return_rva - 4
    matches = [s for s in sections(data) if s[1] <= site and site + 4 <= s[1] + s[2]]
    if len(matches) != 1 or not matches[0][4] & 0x20000000:
        raise ValueError('call site is not uniquely file-backed executable code')
    name, start, _, raw, _ = matches[0]
    offset = raw + site - start
    word, = struct.unpack_from('<I', data, offset)
    result = dict(return_rva=hex(return_rva), call_rva=hex(site), section=name,
                  file_offset=hex(offset), instruction_word=hex(word),
                  execution_proven=False, function_symbol=None)
    if word & 0xfc000000 == 0x94000000:
        immediate = word & 0x3ffffff
        if immediate & 0x2000000:
            immediate -= 0x4000000
        result.update(instruction='BL', static_target_rva=hex(site + immediate * 4))
    elif word & 0xfffffc1f == 0xd63f0000:
        result.update(instruction='BLR', target_register='x' + str((word >> 5) & 31),
                      static_target_rva=None)
    else:
        raise ValueError('preceding instruction is not BL or BLR; do not infer a call site')
    return result


def identify(data):
    digest = hashlib.sha256(data).hexdigest()
    if len(data) != OEM_SIZE or digest != OEM_SHA256:
        raise ValueError('wrong OEM PE bytes or size')
    return digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pe', type=Path, required=True)
    parser.add_argument('--return-rva', type=lambda value: int(value, 0), action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = args.pe.read_bytes()
    digest = identify(data)
    report = dict(pe_sha256=digest, pe_bytes=len(data),
                  mappings=[map_return(data, rva) for rva in args.return_rva],
                  deadlock_established=False, hardware_executed=False)
    output = args.output.resolve()
    output.relative_to(Path(__file__).resolve().parents[1] / 'out')
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
