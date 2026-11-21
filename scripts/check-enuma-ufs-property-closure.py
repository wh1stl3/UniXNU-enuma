#!/usr/bin/env python3
"""Pinned DALSys/HALIOMMU private property extraction, not runtime ACPI/DMA proof."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('enuma_exit_audit', ROOT / 'scripts/audit-enuma-ufsdxe-exit.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
DAL_PIN = 'e6b151c5506f52196e6ea687d15ffa074b7e3d518e8c52621ef62413000a8204'
HAL_PIN = base.PROVIDER_PIN


def pinned_bytes(data, expected):
    base.check(hashlib.sha256(data).hexdigest() == expected, 'fixed input hash mismatch')
    return data


def integer(pe, at, fmt):
    return struct.unpack(fmt, pe.read(at, struct.calcsize(fmt)))[0]


def name_at(pe, at, end):
    base.check(at < end, 'name pointer outside bound')
    data = pe.read(at, min(128, end - at))
    base.check(b'\0' in data, 'unterminated bounded name')
    return data.split(b'\0', 1)[0].decode('ascii')


def private_resources(pe):
    """Fixed database descriptor, typed pointer and consumer layout; no general DAL decoder."""
    base.check(integer(pe, 0x1d210, '<I') == 1, 'descriptor count changed')
    db = integer(pe, 0x1d220, '<Q')
    base.check(db == 0x7bc8, 'descriptor database pointer changed')
    properties, typed, name_count, names = struct.unpack('<QQQQ', pe.read(db, 32))
    base.check((properties, typed, name_count, names) == (0x1c208, 0x1bd98, 20, 0x1c618), 'database layout changed')
    property_bytes = integer(pe, properties, '<I')
    pool_start, pool_end = struct.unpack('<II', pe.read(properties + 4, 8))
    base.check(0 < pool_start < pool_end < property_bytes and properties + property_bytes <= names,
               'property/name pool boundary')
    entries = []
    for i in range(name_count):
        at = names + i * 40
        pointer = integer(pe, at, '<Q')
        label = name_at(pe, pointer, pointer + 128)
        if label == 'SMMU':
            entries.append(at)
    base.check(entries == [0x1c820], 'SMMU name missing/ambiguous or entry changed')
    entry = entries[0]
    prop_offset = integer(pe, entry + 12, '<I')
    collisions = integer(pe, entry + 16, '<I')
    base.check(collisions == 0 and prop_offset == 0x22c, 'property offset/collision changed')
    base.check(prop_offset + 8 <= property_bytes, 'property record outside database')
    word, index = struct.unpack('<II', pe.read(properties + prop_offset, 8))
    base.check(word >> 24 == 0x12 and word & 0x800000, 'property type/name flag changed')
    offset = word & 0x7fffff
    base.check(offset < pool_end - pool_start, 'property name index outside pool')
    base.check(name_at(pe, properties + pool_start + offset, properties + pool_end) == 'IORT', 'IORT property name mismatch')
    # The adjacent property base provides a physical upper bound, not a claimed
    # semantic typed-array element count. Fixed input additionally requires index f.
    base.check(index < (properties - typed) // 16, 'typed index outside physical span')
    base.check(index == 0xf, 'typed property index changed')
    item = typed + index * 16
    raw_item, table = struct.unpack('<QQ', pe.read(item, 16))
    base.check(table == 0x2bf80, 'typed property pointer changed')
    header = pe.read(table, 48)
    base.check(header[:4] == b'IORT', 'private table signature mismatch')
    length = struct.unpack_from('<I', header, 4)[0]
    count, first = struct.unpack_from('<II', header, 36)
    base.check((length, count, first) == (0x1174, 25, 0x30), 'private table header changed')
    pe.read(table, length)
    nodes = {}; selected = []; at = first
    for _ in range(count):
        base.check(at + 16 <= length, 'node header outside private table')
        kind, size = struct.unpack('<BH', pe.read(table + at, 3))
        base.check(size >= 16 and at + size <= length, 'node length outside private table')
        node = {'rva': table + at, 'kind': kind, 'length': size}
        nodes[at] = node
        if kind == 1:
            base.check(size > 0x1d, 'named node too short')
            label = name_at(pe, table + at + 0x1d, table + at + size)
            if label == '\\_SB_.UFS0':
                selected.append(node)
        at += size
    base.check(at == length, 'node count/length does not consume private table')
    base.check(len(selected) == 1, 'UFS name missing/ambiguous')
    node = selected[0]
    base.check(node['rva'] == 0x2c6e0 and node['length'] == 0x65, 'UFS node location/length changed')
    mappings, offset = struct.unpack('<II', pe.read(node['rva'] + 8, 8))
    base.check(offset >= 0x1d and offset + mappings * 20 <= node['length'], 'record range outside node')
    base.check((mappings, offset) == (2, 0x3d), 'UFS record count/offset changed')
    records = []
    for i in range(mappings):
        rva = node['rva'] + offset + i * 20
        raw = list(struct.unpack('<5I', pe.read(rva, 20)))
        reference = raw[3]
        base.check(reference in nodes and nodes[reference]['length'] >= 24, 'reference is not a bounded node')
        records.append({'rva': rva, 'raw_uint32': raw, 'selection_argument_equal_raw0': raw[0],
                        'referenced_node_rva': table + reference,
                        'referenced_node_raw_uint64_at_0x10': integer(pe, table + reference + 0x10, '<Q')})
    base.check([r['raw_uint32'] for r in records] == [[0, 1, 0x4e0, 0x30, 0], [0x10, 1, 0xe0, 0x30, 0]], 'raw UFS records changed')
    return {'descriptor_count': 1, 'descriptor_rva': 0x1d218, 'database_rva': db,
            'property_base': properties, 'name_entry_rva': entry, 'name': 'SMMU',
            'property_rva': properties + prop_offset, 'property_name': 'IORT', 'raw_type': 0x12,
            'typed_index': index, 'typed_item_rva': item, 'typed_raw_word0': raw_item,
            'table_rva': table, 'length': length, 'node_count': count, 'first_node_offset': first,
            'ufs_node': node, 'records': records,
            'scope': 'private board property bytes, not proof of installed system ACPI IORT or runtime selection',
            'unknown': 'runtime SID/context exclusivity, UTRL/UTMRL quiescence, PA/IOVA/coherence and timeout buffer lifetime UNKNOWN'}


def bounded_instructions(path, bounds, output):
    lines = []; instructions = {}
    for start, end in bounds:
        text = base.run(['/usr/bin/llvm-objdump', '-d', '--no-show-raw-insn', '--print-imm-hex',
                         '--start-address=' + hex(start), '--stop-address=' + hex(end), str(path)])
        lines.append(text)
        for line in text.splitlines():
            match = re.match(r'^\s*([0-9a-f]+):\s+([a-z.][a-z0-9.]*)\s*(.*?)\s*$', line)
            if match:
                instructions[int(match[1], 16)] = (match[2], re.sub(r'\s*<.*', '', match[3]).strip())
    output.write_text('\n'.join(lines))
    return instructions


def audit(output):
    firmware = ROOT.parent / 'uefi-enuma'
    dal = firmware / 'Binaries/enuma/DALSys/DALSys.efi'
    hal = firmware / 'Binaries/enuma/HALIOMMU/HALIOMMU.efi'
    dp = base.PE(pinned_bytes(dal.read_bytes(), DAL_PIN))
    hp = base.PE(pinned_bytes(hal.read_bytes(), HAL_PIN))
    base.check((dp.entry, dp.base, dp.subsystem) == (0x1000, 0, 11), 'DAL PE identity mismatch')
    layout, _, _ = base.header_layout(Path('/home/wh1stl3/enuma-fw/mu_basecore'), '/usr/bin/clang')
    di = bounded_instructions(dal, [(0x141c, 0x1454), (0x14d0, 0x14fc), (0x19c8, 0x19d4), (0x3c0c, 0x3c8c)], output / 'dal-bounded.txt')
    hi = bounded_instructions(hal, [(0x48a8, 0x4b70), (0x4e14, 0x4f28)], output / 'hal-consumer-bounded.txt')
    guid = base.require_guid(dp, 0x1d058, str(base.uuid.UUID(bytes_le=hp.read(0x9078, 16))), 'DAL/HAL interface')
    base.check([integer(dp, at, '<Q') for at in (0x1d0b0, 0x1d180, 0x1d1b8)] == [0x141c, 0x2ca4, 0x2eb4], 'DAL factory/property table members changed')
    base.require_members(di, {0x19c8: ('ldr', f"x8, [x1, #{hex(layout['st_bs'])}]"),
        0x19d0: ('str', 'x8, [x10, #0x138]'), 0x14dc: ('ldr', 'x9, [x8, #0x138]'),
        0x14f0: ('ldr', f"x8, [x9, #{hex(layout['install_multiple'])}]"),
        0x14e0: ('add', 'x1, x1, #0x58'), 0x14e4: ('add', 'x2, x2, #0xa8'),
        0x14ec: ('mov', 'x3, xzr'), 0x14f8: ('blr', 'x8'),
        0x1440: ('add', 'x9, x9, #0xc0'), 0x1444: ('str', 'x9, [x2]'),
        0x1450: ('bl', '0x3c0c'), 0x3c20: ('add', 'x8, x8, #0x218'),
        0x3c64: ('ldrsw', 'x8, [x22, #0x210]')}, 'DAL install/factory/init')
    base.require_members(hi, {0x4e4c: ('bl', '0x6ab0'), 0x4e68: ('bl', '0x6ad0'),
        0x4950: ('ldr', 'x19, [x0, #0x10]'), 0x4968: ('add', 'x1, x19, #0x1d'),
        0x4978: ('ldrb', 'w8, [x19, #0x2]'), 0x4980: ('ldrb', 'w9, [x19, #0x1]'),
        0x4a28: ('mov', 'w14, #0x14'), 0x4b4c: ('add', 'x19, x19, #0x20')}, 'HAL property consumer')
    selection = []
    for file, line in [('Vendor.dsc.inc', 10), ('Vendor.fdf.inc', 9), ('Vendor.apriori.inc', 3)]:
        path = firmware / 'Platforms/Xiaomi/enumaPkg/EnumaInputs' / file
        base.check('Binaries/enuma/DALSys/DALSys.inf' in path.read_text().splitlines()[line - 1], 'DAL board selection changed')
        selection.append({'path': str(path.relative_to(firmware)), 'line': line})
    return {'validation': 'self-checked static private property only', 'inputs': {'DALSys': DAL_PIN, 'HALIOMMU': HAL_PIN},
            'pe': {'DALSys': dp.sections, 'HALIOMMU': hp.sections}, 'selection': selection,
            'installation': {'call': 0x14f8, 'bs_global': 0x4d138, 'guid_rva': 0x1d058, 'guid': guid, 'interface_rva': 0x1d0a8},
            'factory': {'target': 0x141c, 'output_argument': 'x2', 'output_table': 0x1d0c0,
                        'warning': 'not HAL factory x0 convention', 'c0_target': 0x2ca4, 'f8_target': 0x2eb4},
            'property': private_resources(dp), 'runtime_selected_database': 'UNKNOWN',
            'limits': 'No vendor execution/MMIO/device access. Raw selection association only, not SID/context/bank/exclusivity or PA=IOVA.'}


def main():
    output = ROOT / '.cache/ufs-property-closure'
    subprocess.run(['git', '-C', str(ROOT), 'check-ignore', '-q', str(output / 'report.json')], check=True)
    output.mkdir(parents=True, exist_ok=True)
    try:
        report = audit(output)
    except (ValueError, OSError, struct.error, subprocess.SubprocessError) as exc:
        (output / 'report.json').write_text(json.dumps({'validation': 'REJECTED', 'reason': str(exc)}) + '\n')
        print('REJECTED fixed property input/boundary')
        return 1
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('self-checked private property closure;2 raw UFS records; runtime/ownership UNKNOWN')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
