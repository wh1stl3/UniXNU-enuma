"""Audit an archived Core checkpoint against its matching linker map; offline only."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
CORE_GUID = 'd6a2cb7f-6a18-4e2f-b43b-9920a733700a'
DISPLAY_GUID = '4138022f-06c7-4f79-9c94-7e33b511a4e7'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate_archive(path):
    q = json.loads((path / 'qualification.json').read_text())
    for name, item in q['files'].items():
        data = (path / name).read_bytes()
        if digest(data) != item['sha256'] or len(data) != item['bytes']:
            raise ValueError('Archived artifact changed: ' + name)
    return q


def code_review(core, map_text, point):
    import capstone
    import pefile
    pe = pefile.PE(data=core)
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_LITTLE_ENDIAN)
    md.detail = True
    md.skipdata = True
    symbols = {}
    for line in map_text.splitlines():
        match = re.fullmatch(r'\s*([0-9a-fA-F]{8,16})\s+[0-9a-fA-F]+\s+0\s+(\S+)\s*', line)
        if match:
            symbols[match[2]] = int(match[1], 16)
    if point not in (13, 15, 20, 21, 22):
        raise ValueError('Unsupported reviewed checkpoint')
    checkpoint = 'EnumaImageEntryCheckpoint' if point in (20, 21, 22) else 'EnumaDispatchDetailCheckpoint'
    required = ['CoreDispatcher', 'CoreStartImage', checkpoint,
                'ReadUnaligned64', 'MicroSecondDelay', 'ResetCold', 'CpuDeadLoop']
    if point in (21, 22):
        required.append('CoreExit')
    if point == 22:
        required.append('SetJump')
    if any(name not in symbols for name in required):
        raise ValueError('Required Core/map symbols missing')
    instructions = []
    for section in pe.sections:
        if section.Characteristics & 0x20000000:
            instructions.extend(md.disasm(section.get_data()[:section.Misc_VirtualSize], section.VirtualAddress))
    begin = symbols[checkpoint]
    end = min(address for address in symbols.values() if address > begin)
    body = [i for i in instructions if begin <= i.address < end and i.id]
    if not any(i.mnemonic in (['ccmp'] if point in (20, 21, 22) else ['cmp']) and len(i.operands) >= 2 and
               i.operands[0].type == capstone.arm64.ARM64_OP_REG and
               i.reg_name(i.operands[0].reg) == 'x0' and
               i.operands[1].type == capstone.arm64.ARM64_OP_IMM and
               i.operands[1].imm == point for i in body):
        raise ValueError('Checkpoint does not compare the requested point')
    calls = [(i.address, i.operands[0].imm) for i in body if i.mnemonic == 'bl']
    target_calls = [target for _, target in calls]
    expected_calls = [symbols['ReadUnaligned64'], symbols['ReadUnaligned64'],
                      symbols['MicroSecondDelay'], symbols['ResetCold']]
    if target_calls != expected_calls:
        raise ValueError('Checkpoint GUID read/delay/reset call sequence differs')
    if not any(i.mnemonic == 'b' and i.operands[0].imm == symbols['CpuDeadLoop'] for i in body):
        raise ValueError('Missing terminal dead loop')
    low, high = struct.unpack('<QQ', uuid.UUID(DISPLAY_GUID).bytes_le)
    # Check the intermediate completed constants immediately before both CMPs;
    # final register values alone would lose the first GUID half in a reused reg.
    values = []
    current = {}
    comparisons = []
    for ins in body:
        operands = ins.operands
        if ins.mnemonic in ['mov', 'movk'] and len(operands) == 2 and operands[1].type == capstone.arm64.ARM64_OP_IMM:
            reg = ins.reg_name(operands[0].reg)
            if ins.mnemonic == 'mov':
                current[reg] = operands[1].imm & ((1 << (32 if reg.startswith('w') else 64)) - 1)
            elif reg in current:
                shift = operands[1].shift.value
                current[reg] = (current[reg] & ~(0xffff << shift)) | ((operands[1].imm & 0xffff) << shift)
        if (ins.mnemonic == 'cmp' and len(operands) == 2 and operands[1].type == capstone.arm64.ARM64_OP_REG
                and (point not in (20, 21, 22) or ins.reg_name(operands[0].reg) == 'x0')):
            value = current.get(ins.reg_name(operands[1].reg))
            comparisons.append(value)
        if ins.mnemonic == 'bl':
            if operands[0].imm == symbols['MicroSecondDelay']:
                values.append(current.get('w0', current.get('x0')))
            current.clear()
    delay_contract = {'mode': 'explicit_microseconds', 'microseconds': 2000000}
    if comparisons != [low, high]:
        raise ValueError('Compared GUID halves mismatch')
    if values != [2000000]:
        # With the completion fallback removed, LTO can specialize the only
        # MicroSecondDelay call: two exact 1-second NanoSecondDelay calls.
        # Accept that concrete body only, never a missing immediate by itself.
        if values != [None] or 'NanoSecondDelay' not in symbols:
            raise ValueError('Target delay argument mismatch')
        callee_start = symbols['MicroSecondDelay']
        callee_end = min(v for v in symbols.values() if v > callee_start)
        callee = [i for i in instructions if callee_start <= i.address < callee_end and i.id]
        calls = []; constant = None
        for ins in callee:
            op = ins.operands
            if ins.mnemonic == 'mov' and len(op) == 2 and ins.reg_name(op[0].reg) in ['w0', 'x0'] and op[1].type == capstone.arm64.ARM64_OP_IMM:
                constant = op[1].imm & 0xffffffffffffffff
            elif ins.mnemonic == 'movk' and len(op) == 2 and ins.reg_name(op[0].reg) in ['w0', 'x0'] and op[1].type == capstone.arm64.ARM64_OP_IMM and constant is not None:
                shift = op[1].shift.value
                constant = (constant & ~(0xffff << shift)) | ((op[1].imm & 0xffff) << shift)
            elif ins.mnemonic in ['bl', 'b']:
                if op[0].type != capstone.arm64.ARM64_OP_IMM or op[0].imm != symbols['NanoSecondDelay']:
                    raise ValueError('Specialized delay calls an unexpected target')
                calls.append({'rva': hex(ins.address), 'branch': ins.mnemonic, 'nanoseconds': constant})
                constant = None
            elif ins.mnemonic in ['stp', 'ldp']:
                expected_frame = {'stp': 'x29, x30, [sp, #-0x10]!', 'ldp': 'x29, x30, [sp], #0x10'}
                if ins.op_str != expected_frame[ins.mnemonic]:
                    raise ValueError('Specialized delay uses an unexpected stack/memory operation')
            elif ins.mnemonic == 'mov' and len(op) == 2 and ins.reg_name(op[0].reg) in ['x29', 'fp'] and ins.reg_name(op[1].reg) == 'sp':
                pass
            else:
                raise ValueError('Unexpected specialized delay instruction: ' + ins.mnemonic + ' ' + ins.op_str)
        if [c['nanoseconds'] for c in calls] != [1000000000, 1000000000] or [c['branch'] for c in calls] != ['bl', 'b'] or callee[-1].mnemonic != 'b':
            raise ValueError('Specialized delay is not exactly two one-second calls')
        delay_contract = {'mode': 'constant_specialized_2x1s', 'microseconds': 2000000,
                          'nanosecond_calls': calls, 'callee_body': render(callee)}
    contexts = []
    if point in (20, 21, 22):
        return entry_review(core, instructions, symbols, body, delay_contract, required, point)
    for index, ins in enumerate(instructions):
        if not ins.id or ins.mnemonic != 'bl' or ins.operands[0].imm != begin:
            continue
        before = instructions[max(0, index - 12):index]
        after = instructions[index + 1:index + 15]
        earlier_start = [i.address for i in before if i.id and i.mnemonic == 'bl' and i.operands[0].imm == symbols['CoreStartImage']]
        later_start = [i.address for i in after if i.id and i.mnemonic == 'bl' and i.operands[0].imm == symbols['CoreStartImage']]
        point_load = any(i.id and i.mnemonic == 'mov' and len(i.operands) == 2 and
                         i.reg_name(i.operands[0].reg) in ['w0', 'x0'] and
                         i.operands[1].type == capstone.arm64.ARM64_OP_IMM and
                         i.operands[1].imm == point for i in before[-6:])
        if not point_load or (point == 15 and not later_start) or (point == 13 and not earlier_start):
            raise ValueError('Checkpoint call is not on the requested side of CoreStartImage')
        contexts.append({'checkpoint_call_rva': hex(ins.address),
                         'CoreStartImage_calls_before': [hex(x) for x in earlier_start],
                         'CoreStartImage_calls_after': [hex(x) for x in later_start],
                         'instructions': render(before[-8:] + [ins] + after)})
    if len(contexts) != 1:
        raise ValueError('Expected one concrete checkpoint call site')
    return {'core_sha256': digest(core), 'point': point,
            'delay_contract': delay_contract,
            'symbols': {name: hex(symbols[name]) for name in required},
            'checkpoint_body': render(body), 'callsites': contexts,
            'limits': ['fixed Core/map static checks only; no proof of hardware reaching or returning from the gate',
                       'detail13 is any CoreStartImage return, not an EFI_STATUS value or successful SetMode']}


def entry_review(core, instructions, symbols, body, delay, required, point=20):
    """Accept the concrete LTO bridge and entry-call shape, not arbitrary proximity."""
    for name in ['EnumaStartingImage', 'EnumaStartingFile']:
        if name not in symbols:
            raise ValueError('Scheduled image bridge symbols missing')
    if [(i.mnemonic, i.op_str) for i in body[-3:]] != [
            ('ldp', 'x29, x30, [sp, #8]'), ('ldr', 'x19, [sp], #0x20'), ('ret', '')]:
        raise ValueError('Bridge rejection exit differs')
    reject = body[-3].address
    image, file = symbols['EnumaStartingImage'], symbols['EnumaStartingFile']
    expected = [
        ('str', 'x19, [sp, #-0x20]!'), ('stp', 'x29, x30, [sp, #8]'),
        ('add', 'x29, sp, #8'), ('adrp', f'x8, #{hex(image & ~4095)}'),
        ('ldr', f'x8, [x8, #{hex(image & 4095)}]'), ('cbz', f'x8, #{hex(reject)}'),
        ('adrp', f'x9, #{hex(file & ~4095)}'), ('cmp', 'x8, x1'),
        ('ldr', f'x19, [x9, #{hex(file & 4095)}]'), ('ccmp', 'x19, #0, #4, eq'),
        ('ccmp', f'x0, #{hex(point)}, #0, ne'), ('b.ne', f'#{hex(reject)}')]
    if [(i.mnemonic, i.op_str) for i in body[:12]] != expected:
        raise ValueError('Scheduled handle/file/point bridge guard differs')
    start = symbols['CoreStartImage']
    end = min(v for v in symbols.values() if v > start)
    function = [i for i in instructions if start <= i.address < end and i.id]
    if not any(i.mnemonic == 'mov' and i.op_str == 'x22, x0' for i in function[:16]):
        raise ValueError('Entry handle is not the saved StartImage argument')
    contexts = []
    for index, ins in enumerate(function):
        if ins.mnemonic != 'bl' or ins.operands[0].imm != symbols['EnumaImageEntryCheckpoint']:
            continue
        if point == 22:
            before = function[max(0,index-4):index]
            if not any(i.mnemonic == 'mov' and i.op_str == 'w8, #0x16' for i in before):
                continue
            if [(i.mnemonic,i.op_str) for i in before] != [
                    ('bl',f'#{hex(symbols["CoreExit"])}'),('mov','w8, #0x16'),
                    ('mov','x1, x22'),('mov','w0, w8')]:
                raise ValueError('Point22 is not after CoreExit branch')
            jump = [(a,b) for a,b in zip(function,function[1:]) if a.mnemonic=='bl' and
                    a.operands[0].imm==symbols['SetJump'] and b.mnemonic=='cbnz' and
                    b.op_str==f'x0, #{hex(before[1].address)}']
            if len(jump)!=1:
                raise ValueError('SetJump nonzero path does not reach point22')
            after = function[index+1:index+4]
            if [(i.mnemonic,i.op_str) for i in after] != [
                    ('ldr','x8, [x19, #0xa0]'),('ldr','x9, [x25, #0x600]'),('cmp','x8, x9')]:
                raise ValueError('Point22 not before TPL cleanup')
            contexts.append(dict(checkpoint_call_rva=hex(ins.address),exit_call_rva=hex(before[0].address),
                                 setjump_call_rva=hex(jump[0][0].address),
                                 instructions=render([jump[0][0],jump[0][1]]+before+[ins]+after)))
            continue
        if point == 21:
            before = function[max(0,index-8):index]
            if not any(i.mnemonic == 'mov' and i.op_str == 'w8, #0x15' for i in before[-4:]):
                continue
            if [(i.mnemonic,i.op_str) for i in before] != [
                    ('ldr','x8, [x19, #0x20]'),('mov','x0, x22'),
                    ('ldr','x1, [x19, #0x38]'),('blr','x8'),('mov','w8, #0x15'),
                    ('str','x0, [x19, #0xa8]'),('mov','w0, w8'),('mov','x1, x22')]:
                raise ValueError('Direct PE return/point21 handle sequence differs')
            after = function[index+1:index+7]
            if [(i.mnemonic,i.op_str) for i in after[:5]] != [
                    ('ldr','x1, [x19, #0xa8]'),('mov','x2, xzr'),('mov','x0, x22'),
                    ('mov','x3, xzr'),('bl',f'#{hex(symbols["CoreExit"])}')]:
                raise ValueError('Point21 is not before CoreExit')
            contexts.append(dict(checkpoint_call_rva=hex(ins.address),entry_call_rva=hex(before[3].address),
                                 instructions=render(before+[ins]+after)))
            continue
        before = function[max(0, index-4):index]
        # Other bridge calls (21/22) must not be mistaken for point20.
        if not any(i.mnemonic == 'mov' and i.op_str == 'w8, #0x14' for i in before):
            continue
        if [(i.mnemonic, i.op_str) for i in before] != [
                ('mov', 'x1, x22'), ('strb', 'w8, [x19, #0x18]'),
                ('mov', 'w8, #0x14'), ('mov', 'w0, w8')]:
            raise ValueError('Point20/handle preparation differs')
        after = function[index+1:index+5]
        if [(i.mnemonic, i.op_str) for i in after] != [
                ('ldr', 'x8, [x19, #0x20]'), ('mov', 'x0, x22'),
                ('ldr', 'x1, [x19, #0x38]'), ('blr', 'x8')]:
            raise ValueError('PE entry indirect call/arguments differ')
        contexts.append(dict(checkpoint_call_rva=hex(ins.address), entry_call_rva=hex(after[-1].address),
                             instructions=render(before+[ins]+after)))
    if len(contexts) != 1:
        raise ValueError('Expected one exact PE-entry boundary')
    return dict(core_sha256=digest(core), point=point, delay_contract=delay,
                symbols={name:hex(symbols[name]) for name in required+['EnumaStartingImage','EnumaStartingFile']},
                checkpoint_body=render(body), callsites=contexts,
                limits=['Concrete fixed Core/map static shape only; no proof of gate execution or PE entry execution',
                        'point20 before PE; point21 direct return; point22 SetJump nonzero/post-CoreExit before TPL cleanup'])


def render(seq):
    return [{'rva': hex(i.address), 'mnemonic': i.mnemonic, 'operands': i.op_str} for i in seq]


def codeview_guid_only(a, b):
    """Permit only an RSDS GUID delta, not debug paths/age, code or other data."""
    import pefile
    if len(a) != len(b):
        raise ValueError('PE length changed')
    images = [pefile.PE(data=data) for data in [a, b]]
    directories = [[item.struct for item in getattr(image, 'DIRECTORY_ENTRY_DEBUG', [])]
                   for image in images]
    if len(directories[0]) != len(directories[1]) or not directories[0]:
        raise ValueError('Debug-directory inventory differs')
    normalized = [bytearray(a), bytearray(b)]
    fields = []
    for left, right in zip(*directories):
        if left.__pack__() != right.__pack__():
            raise ValueError('Debug-directory descriptors differ')
        offset, size = left.PointerToRawData, left.SizeOfData
        if left.Type != 2 or size < 24 or offset + size > len(a):
            raise ValueError('Unsupported debug record')
        if a[offset:offset + 4] != b'RSDS' or b[offset:offset + 4] != b'RSDS':
            raise ValueError('Not matching CodeView RSDS records')
        fields.append({'guid_file_offset': hex(offset + 4), 'bytes': 16})
        for data in normalized:
            data[offset + 4:offset + 20] = b'\0' * 16
    if normalized[0] != normalized[1]:
        raise ValueError('PE differs outside CodeView GUID fields')
    return {'allowed_fields': fields,
            'actual_changed_bytes': sum(x != y for x, y in zip(a, b)),
            'normalized_pe_sha256': digest(normalized[0]),
            'scope': 'all remaining PE bytes identical, including code, paths and debug age'}


def compare_pair(a, b):
    from audit_display_handoff import firmware_files
    if [validate_archive(p)['detail_point'] for p in [a, b]] != [15, 13]:
        raise ValueError('Expected archived A/detail15 and B/detail13')
    builds = [json.loads((p / 'build.json').read_text()) for p in [a, b]]
    if any(builds[0][name] != builds[1][name] for name in ['uefi_source_commit', 'source_inputs_sha256', 'unixnu_qualification']):
        raise ValueError('A/B source provenance mismatch')
    configs = [item['firmware_configuration'] for item in builds]
    diffs = {key: [configs[0]['defines'].get(key), configs[1]['defines'].get(key)]
             for key in configs[0]['defines'].keys() | configs[1]['defines'].keys()
             if configs[0]['defines'].get(key) != configs[1]['defines'].get(key)}
    if diffs != {'ENUMA_DIAG_DETAIL_POINT': ['15', '13']}:
        raise ValueError('A/B differ in more than detail point')
    if {k: v for k, v in configs[0].items() if k != 'defines'} != {k: v for k, v in configs[1].items() if k != 'defines'}:
        raise ValueError('A/B firmware profile differs')
    modules = [{m['guid']: m for m in firmware_files((p / 'candidate.fd').read_bytes())} for p in [a, b]]
    files = [{guid: {'name': m['name'], 'sha256': digest(m['data'])}
              for guid, m in inventory.items()} for inventory in modules]
    if files[0].keys() != files[1].keys():
        raise ValueError('A/B PE inventories differ')
    changed = [guid for guid in files[0] if files[0][guid] != files[1][guid]]
    if CORE_GUID not in changed:
        raise ValueError('DXE Core did not change')
    metadata = {}
    for guid in changed:
        if guid == CORE_GUID:
            continue
        if guid != '80cf7257-87ab-47f9-a3fe-d50b76d89541' or files[0][guid]['name'] != 'PcdDxe':
            raise ValueError('Unexpected additional PE change: ' + guid)
        metadata[guid] = codeview_guid_only(modules[0][guid]['data'], modules[1][guid]['data'])
    if (a / 'candidate.raw').read_bytes()[:192] != (b / 'candidate.raw').read_bytes()[:192]:
        raise ValueError('A/B BootShim differs')
    return {'source_pin': builds[0]['uefi_source_commit'], 'configuration_differences': diffs,
            'PE_count': len(files[0]), 'changed_PE': {guid: [files[0][guid], files[1][guid]] for guid in changed},
            'unchanged_PE_count': len(files[0]) - len(changed), 'debug_guid_only_PE': metadata,
            'runtime_PE_change': CORE_GUID, 'bootshim_bytes_identical': 192,
            'scope': 'decoded PE inventory and source/config equality; not a byte identity claim for recompressed FV envelopes'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--map', type=Path, required=True)
    parser.add_argument('--compare-a', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--tool-path', type=Path)
    args = parser.parse_args()
    if args.tool_path:
        sys.path.insert(0, str(args.tool_path.resolve()))
    output = args.output.resolve()
    if not any(output.is_relative_to(ROOT / name) for name in ['out', 'reports']):
        raise ValueError('Output must stay under out/ or reports/')
    q = validate_archive(args.archive)
    core = (args.archive / 'DxeCore.efi').read_bytes()
    if digest(core) != q['files']['DxeCore.efi']['sha256']:
        raise ValueError('Archived Core digest mismatch')
    map_data = args.map.read_bytes()
    result = code_review(core, map_data.decode(), q['detail_point'])
    result.update(scope='offline archived Core call boundary review', linker_map_sha256=digest(map_data))
    if args.compare_a:
        result['A_B_comparison'] = compare_pair(args.compare_a, args.archive)
    output.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: point/GUID/delay/reset and reviewed StartImage/PE-entry call order; ' +
          ('A/B config differs only in point; Core runtime change and PcdDxe debug ID separately audited'
           if args.compare_a else 'no device execution'))


if __name__ == '__main__':
    main()
