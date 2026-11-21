#!/usr/bin/env python3
"""Bounded, hash-specific UFSDxe static evidence; never executes firmware/hardware."""
import argparse
from collections import deque
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[1]
PIN = 'ffeaed467f8251b7e30a45075da84a1c563e2bac7dc4be0f79f0ed49a88b8dc9'
HEADER_PIN = 'cfb93724a06ff86ff5ba971413368a7809ee42a5'
PROVIDER_PIN = '36a5adbe91a796940f4c09eb53ae4ffb1632ef20d8c3085f7cceb2a706c1e306'


def check(ok, why):
    if not ok:
        raise ValueError(why)


def run(argv, **kwargs):
    return subprocess.run(argv, capture_output=True, text=True, check=True, timeout=30, **kwargs).stdout


class PE:
    def __init__(self, data):
        self.data = data
        check(len(data) >= 64 and data[:2] == b'MZ', 'invalid DOS header')
        pe = struct.unpack_from('<I', data, 60)[0]
        check(pe + 24 <= len(data) and data[pe:pe + 4] == b'PE\0\0', 'invalid PE header boundary')
        machine, count = struct.unpack_from('<HH', data, pe + 4)
        optsize = struct.unpack_from('<H', data, pe + 20)[0]
        opt = pe + 24
        check(machine == 0xaa64 and 0 < count <= 16 and optsize >= 112,
              'expected bounded AArch64 PE32+')
        check(opt + optsize + count * 40 <= len(data), 'truncated PE sections')
        check(struct.unpack_from('<H', data, opt)[0] == 0x20b, 'not PE32+')
        self.entry = struct.unpack_from('<I', data, opt + 16)[0]
        self.base = struct.unpack_from('<Q', data, opt + 24)[0]
        self.image_size = struct.unpack_from('<I', data, opt + 56)[0]
        self.subsystem = struct.unpack_from('<H', data, opt + 68)[0]
        self.sections = []
        for i in range(count):
            at = opt + optsize + i * 40
            name = data[at:at + 8].rstrip(b'\0').decode('ascii')
            vs, va, rs, raw = struct.unpack_from('<IIII', data, at + 8)
            flags = struct.unpack_from('<I', data, at + 36)[0]
            check(raw + rs <= len(data) and va + max(vs, rs) <= self.image_size,
                  'section outside file/image')
            self.sections.append(dict(name=name, rva=va, virtual_size=vs, raw=raw,
                                      raw_size=rs, executable=bool(flags & 0x20000000)))
        for a, b in zip(sorted(self.sections, key=lambda s: s['rva']),
                        sorted(self.sections, key=lambda s: s['rva'])[1:]):
            check(a['rva'] + max(a['virtual_size'], a['raw_size']) <= b['rva'], 'overlapping RVA sections')
        self.offset(self.entry, 4, executable=True)

    def offset(self, rva, size=1, executable=False):
        check(0 <= rva < 1 << 32 and 0 < size <= (1 << 32) - rva, 'invalid RVA/size')
        matches = [s for s in self.sections if s['rva'] <= rva and
                   rva + size <= s['rva'] + s['raw_size'] and
                   (not executable or s['executable'])]
        check(len(matches) == 1, 'RVA not uniquely file-backed with requested permissions')
        return matches[0]['raw'] + rva - matches[0]['rva']

    def rva(self, offset, size=1):
        matches = [s for s in self.sections if s['raw'] <= offset and
                   offset + size <= s['raw'] + s['raw_size']]
        check(len(matches) == 1, 'file offset not uniquely section-backed')
        return matches[0]['rva'] + offset - matches[0]['raw']

    def read(self, rva, size):
        at = self.offset(rva, size)
        return self.data[at:at + size]


def disassemble(tool, path, pe):
    text = next(s for s in pe.sections if s['name'] == '.text')
    check(text['executable'] and text['raw_size'] <= 0x20000, 'unexpected text extent')
    raw = run([tool, '-d', '--no-show-raw-insn', '--print-imm-hex',
               '--start-address=' + hex(text['rva'] + pe.base),
               '--stop-address=' + hex(text['rva'] + pe.base + text['raw_size']), str(path)])
    instructions = {}
    for line in raw.splitlines():
        match = re.match(r'^\s*([0-9a-f]+):\s+([a-z.][a-z0-9.]*)\s*(.*?)\s*$', line)
        if match:
            address = int(match[1], 16) - pe.base
            pe.offset(address, 4, executable=True)
            operands = re.sub(r'\s*<.*', '', match[3]).strip()
            instructions[address] = (match[2], operands)
    check(pe.entry in instructions and len(instructions) > 100, 'disassembler returned no usable instructions')
    return raw, instructions


def header_layout(headers, clang):
    check(run(['git', '-C', str(headers), 'rev-parse', 'HEAD']).strip() == HEADER_PIN, 'UEFI header pin mismatch')
    run(['git', '-C', str(headers), 'diff', '--exit-code', 'HEAD', '--', 'MdePkg/Include'])
    firmware = ROOT.parent / 'uefi-enuma'
    shim = firmware / 'Silicon/Qualcomm/QcomPkg/Library/PlatformPeiLib/ShimLibraries'
    source = '#include <Uefi.h>\n#include <Guid/EventGroup.h>\n'
    # Only an unused pointer-pointee in EFIUefiConfig.h; no descriptor layout/value
    # is instantiated. Relevant UINT32 output and all actual Shim struct fields
    # come from the local headers, not from a hand-recreated interface struct.
    source += 'typedef struct AuditUnusedMemoryRegion EFI_MEMORY_REGION_DESCRIPTOR;\n'
    source += f'#include "{shim / "EFIShim.h"}"\n#include "{shim / "EFIUefiConfig.h"}"\n'
    fields = {'st_bs': ('EFI_SYSTEM_TABLE', 'BootServices'),
              'create_event': ('EFI_BOOT_SERVICES', 'CreateEvent'),
              'create_event_ex': ('EFI_BOOT_SERVICES', 'CreateEventEx'),
              'locate_protocol': ('EFI_BOOT_SERVICES', 'LocateProtocol'),
              'install_multiple': ('EFI_BOOT_SERVICES', 'InstallMultipleProtocolInterfaces'),
              'shim_load_lib': ('EFI_SHIM_LIBRARY_LOADER', 'LoadLib'),
              'shim_get_uint32': ('EFI_UEFI_CONFIG_LIBRARY', 'GetCfgInfoVal')}
    for name, (typ, member) in fields.items():
        source += f'const unsigned long {name} = __builtin_offsetof({typ}, {member});\n'
    source += 'const unsigned long exit_type = EVT_SIGNAL_EXIT_BOOT_SERVICES;\n'
    source += 'const unsigned long pointer_bytes = sizeof(void*);\n'
    source += 'const EFI_GUID exit_guid = EFI_EVENT_GROUP_EXIT_BOOT_SERVICES;\n'
    source += ('EFI_STATUS abi_probe(EFI_CREATE_EVENT_EX f, UINT32 type, EFI_TPL tpl, '
               'EFI_EVENT_NOTIFY cb, CONST VOID *ctx, CONST EFI_GUID *guid, EFI_EVENT *event) '
               '{ return f(type, tpl, cb, ctx, guid, event); }\n')
    # Compiler-only layout/ABI probe: no firmware build, link or binary execution.
    compiler = [clang, '-target', 'aarch64-none-elf', '-ffreestanding', '-fshort-wchar', '-O1', '-S',
                '-I' + str(headers / 'MdePkg/Include'),
                '-I' + str(headers / 'MdePkg/Include/AArch64'), '-x', 'c', '-', '-o', '-']
    ir = run(compiler + ['-emit-llvm'], input=source)
    assembly = run(compiler, input=source)
    result = {}
    for name in [*fields, 'exit_type', 'pointer_bytes']:
        match = re.search(r'@' + name + r' = .*?constant i64 ([0-9]+)', ir)
        check(match is not None, 'missing clang layout constant ' + name)
        result[name] = int(match[1])
    check(result['pointer_bytes'] == 8, 'unexpected AArch64 pointer width')
    # GUID byte order is EFI_GUID's UINT32/UINT16/UINT16/UINT8[8], not a guessed integer.
    header = (headers / 'MdePkg/Include/Guid/EventGroup.h').read_text()
    definition = re.search(r'#define EFI_EVENT_GROUP_EXIT_BOOT_SERVICES\s*\\\s*\{([^}]+)\}', header)
    check(definition is not None, 'missing exact EBS GUID definition')
    values = [int(n, 16) for n in re.findall(r'0x[0-9a-fA-F]+', definition[1])]
    check(len(values) == 11, 'invalid GUID field count')
    result['exit_guid'] = str(uuid.UUID(bytes_le=struct.pack('<IHH8B', *values)))
    result['abi'] = 'clang target aarch64-none-elf; pinned AArch64 ProcessorBind.h EFIAPI empty; AAPCS64 x0-x7 integer/pointer arguments, x0-x18 call-clobbered'
    result['pin'] = HEADER_PIN
    result['header_sha256'] = {str(p.relative_to(headers)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in [headers / 'MdePkg/Include/Uefi/UefiSpec.h',
                                         headers / 'MdePkg/Include/Guid/EventGroup.h',
                                         headers / 'MdePkg/Include/Protocol/StatusCode.h',
                                         headers / 'MdePkg/Include/AArch64/ProcessorBind.h']}
    return result, ir, assembly


def edges(instructions, at, calls=True):
    op, args = instructions[at]
    target = re.search(r'(?:^|,\s*)(0x[0-9a-f]+)$', args)
    dest = int(target[1], 16) if target else None
    if op in ('ret', 'br', 'udf'):
        return []
    if op == 'b':
        return [dest] if dest is not None else []
    result = [at + 4]
    if dest is not None and (op.startswith('b.') or op in ('cbz', 'cbnz', 'tbz', 'tbnz') or (calls and op == 'bl')):
        result.append(dest)
    return [x for x in result if x in instructions]


def path_to(instructions, start, goal, budget=12000):
    todo = deque([start]); parents = {start: None}
    while todo and len(parents) <= budget:
        at = todo.popleft()
        if at == goal:
            chain = []
            while at is not None:
                chain.append(at); at = parents[at]
            chain.reverse()
            # Retain exact direct CFG edges; sequential runs compressed for review.
            return {'status': 'syntactic direct CFG path, conditions/call returns not proven',
                    'start': start, 'goal': goal,
                    'nonsequential_edges': [[a, b] for a, b in zip(chain, chain[1:]) if b != a + 4]}
        for nxt in edges(instructions, at):
            if nxt not in parents:
                parents[nxt] = at; todo.append(nxt)
    return {'status': 'UNKNOWN: no direct path established within bound; indirect calls not followed', 'budget': budget}


def register(name):
    return 'x' + name[1:] if name.startswith('w') else name


def trace(instructions, start, end, bs_slot, layout):
    """Local fallthrough evidence only; unknown operations/loads never become constants."""
    regs = {'xzr': 0}; events = []; refs = []
    def value(reg):
        return regs.get(register(reg))
    for at in range(start, end, 4):
        check(at in instructions, 'missing bounded instruction ' + hex(at))
        op, args = instructions[at]
        parts = args.split(', ')
        dest = register(parts[0])
        old = value(parts[0])
        v = None
        if op in ('adr', 'adrp') and len(parts) == 2:
            v = int(parts[1], 0)
        elif op in ('add', 'sub') and len(parts) == 3 and parts[2].startswith('#'):
            base = value(parts[1])
            if isinstance(base, int):
                v = base + (1 if op == 'add' else -1) * int(parts[2][1:], 0)
        elif op == 'mov' and len(parts) == 2:
            v = int(parts[1][1:], 0) if parts[1].startswith('#') else value(parts[1])
        elif op == 'orr' and len(parts) == 3 and parts[1] in ('wzr', 'xzr') and parts[2].startswith('#'):
            v = int(parts[2][1:], 0)
        elif op == 'ldr':
            mem = re.fullmatch(r'([xw]\d+), \[(x\d+)(?:, #(0x[0-9a-f]+|[0-9]+))?\]', args)
            if mem:
                base = value(mem[2]); off = int(mem[3] or '0', 0)
                if isinstance(base, int) and base + off == bs_slot:
                    v = ('BootServices',)
                elif base == ('BootServices',):
                    v = ('BS_member', off)
        if op in ('bl', 'blr'):
            callee = value(parts[0]) if op == 'blr' else ('direct', int(parts[0], 0))
            if callee in [('BS_member', layout['create_event']), ('BS_member', layout['create_event_ex'])]:
                events.append({'call_rva': at, 'service': 'CreateEventEx' if callee[1] == layout['create_event_ex'] else 'CreateEvent',
                               'service_offset': callee[1],
                               'arguments_x0_x5': [value('x' + str(i)) for i in range(6)],
                               'window': [start, end], 'execution': 'conditional static call site, not observed registration success'})
            for i in range(19):
                regs.pop('x' + str(i), None)
        elif op not in ('str', 'strb', 'strh', 'stur', 'stp', 'cmp', 'cbz', 'cbnz', 'tbz', 'tbnz', 'ret', 'b') and not op.startswith('b.'):
            # Kill all destinations we do not model, including the second LDP output.
            if dest != 'xzr':
                regs[dest] = v
                if op == 'ldp' and len(parts) > 1:
                    regs.pop(register(parts[1]), None)
            if isinstance(v, int) and op in ('add', 'adr', 'adrp'):
                refs.append({'instruction_rva': at, 'target_rva': v})
        if op in ('adr', 'adrp', 'add', 'sub', 'mov', 'orr', 'ldr') and parts[0].startswith('w') and isinstance(regs.get(dest), int):
            regs[dest] &= 0xffffffff
    return events, refs


def callback_table(instructions, start, pe):
    pe.offset(start, 4, executable=True)
    todo = [start]; seen = set(); direct = []; indirect = []
    while todo and len(seen) < 128:
        at = todo.pop()
        if at in seen or at not in instructions:
            continue
        seen.add(at)
        op, args = instructions[at]
        if op == 'bl' or op == 'b':
            direct.append({'instruction_rva': at, 'target_rva': int(args, 0), 'kind': op})
        if op in ('blr', 'br'):
            indirect.append({'instruction_rva': at, 'register': args, 'target': 'UNKNOWN'})
        # Tail branches outside this 0x100-byte window are targets, not decoded functions.
        todo += [x for x in edges(instructions, at, calls=False) if start <= x < start + 0x100]
    return {'callback_rva': start, 'visited_instruction_rvas': sorted(seen),
            'direct_targets': direct, 'indirect_calls': indirect,
            'queue_operations': 'UNKNOWN', 'completion_conditions': 'UNKNOWN',
            'limit': 'bounded callback CFG only; direct callees are not assumed to stop DMA'}


def source_guid(path, name):
    text = path.read_text()
    match = re.search(r'\b' + re.escape(name) + r'\s*(?:\\\s*)?(?:=\s*)?\{([^}]+)\}', text)
    check(match is not None, 'GUID source definition missing: ' + name)
    values = [int(x, 16) for x in re.findall(r'0x[0-9a-fA-F]+', match[1])]
    check(len(values) == 11, 'GUID source field count: ' + name)
    return str(uuid.UUID(bytes_le=struct.pack('<IHH8B', *values)))


def require_guid(pe, rva, expected, name):
    actual = str(uuid.UUID(bytes_le=pe.read(rva, 16)))
    check(actual == expected, name + ' GUID mismatch at ' + hex(rva))
    return actual


def require_members(ins, proof, name):
    for at, expected in proof.items():
        check(ins.get(at) == expected, name + ' member/source mismatch at ' + hex(at))


def interface_evidence(pe, ins, layout, headers):
    """Fixed local anchors, NOT a branch-merge/general dataflow proof."""
    firmware = ROOT.parent / 'uefi-enuma'
    qcom = firmware / 'Silicon/Qualcomm/QcomPkg'
    status_guid = require_guid(pe, 0x192a8, source_guid(headers / 'MdePkg/Include/Protocol/StatusCode.h',
                               'EFI_STATUS_CODE_RUNTIME_PROTOCOL_GUID'), 'StatusCode')
    hob_guid = require_guid(pe, 0x19098, source_guid(qcom / 'QcomPkg.dec', 'gEfiShimLibraryHobGuid'), 'Shim HOB')
    # Match both the source global and member, rather than naming a call by offset alone.
    status_proof = {0x6060: ('adrp', 'x10, 0x1a000'), 0x6064: ('ldr', 'x8, [x10, #0x8e0]'),
                    0x606c: ('ldr', f"x8, [x8, #{hex(layout['locate_protocol'])}]"),
                    0x6074: ('adrp', 'x0, 0x19000'), 0x607c: ('add', 'x0, x0, #0x2a8'),
                    0x6078: ('adrp', 'x2, 0x1a000'),
                    0x6080: ('add', 'x2, x2, #0x910'), 0x6088: ('blr', 'x8'),
                    0x60c8: ('bl', '0x603c'), 0x60d4: ('strb', 'w9, [x8, #0x918]'),
                    0x5df0: ('strb', 'w9, [x8, #0x8f1]')}
    require_members(ins, status_proof, 'StatusCode LocateProtocol/flag')
    shim_proof = {0x4cc8: ('ldr', 'x8, [x21, #0x8c8]'), 0x4cd0: ('bl', '0x4bfc'),
                  0x4cdc: ('ldr', f"x2, [x8, #{hex(layout['shim_get_uint32'])}]"),
                  0x4cf4: ('br', 'x2'), 0x4c04: ('bl', '0x104a0'),
                  0x4c10: ('ldr', f"x3, [x8, #{hex(layout['shim_load_lib'])}]"),
                  0x4c1c: ('add', 'x0, x0, #0xf31'), 0x4c20: ('add', 'x2, x2, #0x8c8'),
                  0x4c24: ('mov', 'w1, wzr'), 0x4c2c: ('br', 'x3'),
                  0x104ac: ('add', 'x0, x0, #0x98'), 0x104b0: ('bl', '0x67a8'),
                  0x104b8: ('ldr', 'x0, [x0, #0x18]')}
    require_members(ins, shim_proof, 'Shim config library')
    check(pe.read(0x14f31, 16) == b'UEFI Config Lib\0', 'Shim library name mismatch')
    # Only this finite next-step region, including the acquisition branch needed
    # to bind the otherwise-unknown cached object; do not follow external methods.
    smmu_proof = {0x2798: ('cbz', 'x0, 0x27c0'), 0x27c0: ('ldr', 'w8, [sp, #0x64]'),
                  0x27c4: ('cbz', 'w8, 0x27d0'), 0x27c8: ('bl', '0x9548'),
                  0x27d8: ('bl', '0x9548'), 0x9550: ('bl', '0x14088'),
                  0x140a4: ('ldrb', 'w8, [x19, #0x958]'), 0x140a8: ('tbz', 'w8, #0x0, 0x140b4'),
                  0x140b8: ('add', 'x20, x20, #0x958'), 0x140bc: ('ldr', 'x9, [x20, #0x8]'),
                  0x140c0: ('cbz', 'x9, 0x1411c'), 0x140e4: ('bl', '0x4cac'),
                  0x140f0: ('ldr', 'x11, [x20, #0x8]'), 0x140f8: ('ldr', 'x12, [x11]'),
                  0x140fc: ('blr', 'x12'), 0x14124: ('add', 'x0, x0, #0x248'),
                  0x14128: ('ldr', 'x9, [x8, #0x8e0]'),
                  0x14134: ('ldr', f"x10, [x9, #{hex(layout['locate_protocol'])}]"),
                  0x14138: ('blr', 'x10'), 0x141a4: ('add', 'x0, x20, #0x8'),
                  0x141a8: ('ldr', 'x11, [x10, #0x8]'), 0x141ac: ('blr', 'x11')}
    require_members(ins, smmu_proof, 'bounded SMMU interface')
    check(pe.read(0x18644, 13) == b'EnableUfsIOC\0', 'secondary config string mismatch')
    # Source references/hashes bind static implementations and board selections,
    # not proof that the current boot created/loaded any of these objects.
    refs = {
        'Silicon/Qualcomm/QcomPkg/QcomPkg.dec': [13],
        'Silicon/Qualcomm/QcomPkg/Library/PlatformPeiLib/PlatformPei.c': [25, 30, 80, 97],
        'Silicon/Qualcomm/QcomPkg/Library/PlatformPeiLib/ShimLoader.c': [15, 23, 49, 53, 57, 77],
        'Silicon/Qualcomm/QcomPkg/Library/PlatformPeiLib/ShimLibraries/EFIShim.h': [32, 47],
        'Silicon/Qualcomm/QcomPkg/Library/PlatformPeiLib/ShimLibraries/EFIUefiConfig.h': [33, 38, 94, 101],
        'Silicon/Qualcomm/QcomPkg/Library/ConfigurationMapHelperLib/ConfigurationMapHelperLib.c': [7, 35],
        'Platforms/Xiaomi/enumaPkg/enuma.dsc': [95],
        'Platforms/Xiaomi/enumaPkg/Library/ConfigurationMapLib/ConfigurationMapLib.c': [34, 35],
        'Platforms/Xiaomi/enumaPkg/Include/DXE.inc': [70, 73, 80],
    }
    sources = [{'path': p, 'lines': lines, 'sha256': hashlib.sha256((firmware / p).read_bytes()).hexdigest()}
               for p, lines in refs.items()]
    bindings = {
        'Silicon/Qualcomm/QcomPkg/Library/PlatformPeiLib/PlatformPei.c':
            ['0x00010001,ShimInstallLib,ShimLoadLib', 'BuildGuidDataHob(&gEfiShimLibraryHobGuid,&ShimLibLoaderAddress,sizeof(ShimLibLoaderAddress))'],
        'Silicon/Qualcomm/QcomPkg/Library/PlatformPeiLib/ShimLoader.c':
            ['0x10002,LocateMemoryRegionByName,LocateConfigurationEntryString,LocateConfigurationEntry32,',
             '{"UEFIConfigLib",&ConfigLib}', '*LibIntf=gShimLibraryInstanceData[i].LibIntf;'],
        'Silicon/Qualcomm/QcomPkg/Library/ConfigurationMapHelperLib/ConfigurationMapHelperLib.c':
            ['GetConfigurationMap(&ConfigurationDescriptor,&ConfigurationDescriptorCount);',
             '*EntryValue=(UINT32)(ConfigurationDescriptor[i].Value&0xFFFFFFFF);'],
        'Platforms/Xiaomi/enumaPkg/enuma.dsc':
            ['ConfigurationMapLib|enumaPkg/Library/ConfigurationMapLib/ConfigurationMapLib.inf'],
    }
    for path, fragments in bindings.items():
        normalized = re.sub(r'\s+', '', (firmware / path).read_text())
        check(all(fragment in normalized for fragment in fragments), 'local source binding changed: ' + path)
    return {
        'input_sha256': PIN,
        'status_code_callback': {'call_rva': 0x6088, 'service': 'BootServices.LocateProtocol',
            'bs_global_rva': 0x1a8e0, 'member_offset': layout['locate_protocol'],
            'guid_rva': 0x192a8, 'guid': status_guid, 'output_global_rva': 0x1a910,
            'exit_flag_rva': 0x1a918, 'other_callback_flag_rva': 0x1a8f1,
            'anchors': sorted(status_proof), 'protocol_method_invoked_in_these_callback_bodies': False,
            'scope': 'these bounded callback bodies only, not absence of other module exit paths'},
        'shim_config': {'call_rva': 0x4cf4, 'interface': 'EFI_UEFI_CONFIG_LIBRARY.GetCfgInfoVal',
            'member_offset': layout['shim_get_uint32'], 'output_type': 'UINT32*',
            'library_global_rva': 0x1a8c8, 'library_name_rva': 0x14f31, 'name': 'UEFI Config Lib',
            'loader_function_rva': 0x104a0, 'hob_guid_rva': 0x19098, 'hob_guid': hob_guid,
            'loader_loadlib_offset': layout['shim_load_lib'], 'version_argument': 0,
            'static_board_target': 'ShimLoadLib -> ConfigLib -> LocateConfigurationEntry32 -> board ConfigurationMapLib',
            'anchors': sorted(shim_proof), 'runtime_HOB_load_config_success': 'UNKNOWN'},
        'smmu_next_step': {'bounds_rva': [[0x277c, 0x27f8], [0x9548, 0x9568], [0x14088, 0x141b4]],
            'config_gate': 'on the lookup path:2798 requires EFI_SUCCESS x0=0,27c4 requires UINT32[sp+0x64]!=0 before27c8; alternate27d8 also calls9548 without this lookup gate',
            'wrapper': '9548 passes no explicit new arguments;9550 calls14088,9554-955c maps nonzero result to -100',
            'cached_flag': 'bit0 of global1b958 returns zero early when set; not a runtime completion proof',
            'interface_table_global_rva': 0x1b960,
            'secondary_config': 'if UINT32[19fa8]==2, read EnableUfsIOC via4cac; lookup failure resets it0; no effective SMMU ownership inferred',
            'acquisition': {'locate_call_rva': 0x14138, 'service': 'BootServices.LocateProtocol',
                'guid_rva': 0x19248, 'guid': str(uuid.UUID(bytes_le=pe.read(0x19248, 16))),
                'factory_method_call_rva': 0x141ac, 'factory_member_offset': 8,
                'x0': '&global1b960 (interface table output)', 'interface_type': 'UNKNOWN until provider audit'},
            'first_operation': {'call_rva': 0x140fc, 'interface_table_global_rva': 0x1b960,
                'member_offset': 0, 'client_context_output': '&stack[sp+0x18]', 'target': 'UNKNOWN until provider audit'},
            'board_provider_binding': 'UNKNOWN: enuma includes DALSys/HALIOMMU/UFSDxe; inclusion alone does not bind GUID19248 or object1b960 to a provider',
            'anchors': sorted(smmu_proof),
            'next_question': 'Which enuma-selected provider installs GUID54b6d3b4-5d33-4f91-8600-6c41d5deb19a, and what object does factory+8 return at1b960? Stop before resolving/executing external methods.'},
        'source_inputs': sources,
        'limits': 'fixed local anchors plus source review; linear trace is not a branch-merge proof; runtime registration/config/interfaces and all DMA safety obligations UNKNOWN',
    }


def provider_evidence(pe, ins, ufs_pe, ufs_ins, layout):
    """Only the pinned HAL install/table/parameters and resource lookup boundary."""
    guid = require_guid(pe, 0x9048, str(uuid.UUID(bytes_le=ufs_pe.read(0x19248, 16))), 'provider')
    factory = struct.unpack('<Q', pe.read(0x90a0, 8))[0]
    check(factory == 0x14cc, 'provider factory member mismatch')
    table = {off: struct.unpack('<Q', pe.read(0x90b0 + off, 8))[0] for off in (0, 0x10, 0x40)}
    check(table == {0: 0x16b4, 0x10: 0x1920, 0x40: 0x2f10}, 'provider interface table member mismatch')
    install = {0x1210: ('bl', '0x1488'), 0x14a4: ('bl', '0x1504'),
        0x42f4: ('ldr', f"x8, [x1, #{hex(layout['st_bs'])}]"), 0x42f8: ('adrp', 'x10, 0x9000'),
        0x42fc: ('str', 'x8, [x10, #0x168]'), 0x1524: ('ldr', 'x1, [x1, #0x168]'),
        0x1528: ('ldr', f"x1, [x1, #{hex(layout['install_multiple'])}]"),
        0x1530: ('add', 'x8, x8, #0x48'), 0x1538: ('add', 'x2, x2, #0x98'),
        0x1518: ('mov', 'x0, xzr'), 0x1540: ('str', 'x0, [sp, #0x20]'),
        0x1550: ('ldr', 'x3, [sp, #0x20]'), 0x1558: ('blr', 'x8'),
        0x14e8: ('add', 'x9, x9, #0xb0'), 0x14ec: ('str', 'x9, [x0]'),
        0x16e8: ('orr', 'w8, wzr, #0x38'), 0x16f0: ('bl', '0x3c48'),
        0x172c: ('bl', '0x4f28'), 0x1738: ('str', 'w8, [x2]'),
        0x2fb4: ('orr', 'w10, wzr, #0xe0'), 0x2fb8: ('str', 'w10, [x8, #0x20]'),
        0x2fe4: ('movk', 'w10, #0x9f, lsl #16'), 0x2fe8: ('str', 'w10, [x8, #0x20]'),
        0x3018: ('bl', '0x2d98')}
    require_members(ins, install, 'provider install/context')
    params = {0x1416c: ('ldr', 'x13, [x12, #0x40]'), 0x14170: ('blr', 'x13'),
        0x141c0: ('add', 'x1, x1, #0x70f'), 0x141c4: ('mov', 'w2, wzr'), 0x141c8: ('mov', 'w3, wzr'),
        0x141cc: ('ldr', 'x14, [x13, #0x10]'), 0x141d0: ('blr', 'x14'),
        0x141f0: ('blr', 'x15'), 0x14210: ('ldr', 'x16, [x15, #0x40]'), 0x14214: ('blr', 'x16'),
        0x14234: ('add', 'x1, x1, #0x70f'), 0x14238: ('orr', 'w2, wzr, #0x10'),
        0x1423c: ('mov', 'w3, wzr'), 0x14240: ('ldr', 'x17, [x16, #0x10]'),
        0x14244: ('blr', 'x17'), 0x1425c: ('strb', 'w9, [x19, #0x958]')}
    require_members(ufs_ins, params, 'UFSDxe provider parameters')
    check(ufs_pe.read(0x1870f, 11) == b'\\_SB_.UFS0\0', 'UFS device name mismatch')
    resource = {0x19cc: ('bl', '0x48a8'), 0x48b8: ('bl', '0x4934'),
        0x4948: ('bl', '0x4e14'), 0x4968: ('add', 'x1, x19, #0x1d'), 0x4970: ('bl', '0x50dc'),
        0x1aac: ('bl', '0x49a8'), 0x1af0: ('lsl', 'x9, x9, #5'),
        0x1af4: ('ldr', 'w10, [x8, x9]'), 0x1af8: ('ldur', 'w11, [x29, #-0x2c]'),
        0x1afc: ('cmp', 'w10, w11'), 0x1b68: ('ldr', 'x8, [x8, #0x10]'),
        0x2e08: ('ldr', 'w9, [x8, #0x20]'), 0x2e2c: ('mov', 'w2, w9'), 0x2e30: ('bl', '0x34a4'),
        0x4e4c: ('bl', '0x6ab0'), 0x4e68: ('bl', '0x6ad0'),
        0x6a30: ('ldr', 'x9, [x8, #0x168]'),
        0x6a44: ('ldr', f"x9, [x9, #{hex(layout['locate_protocol'])}]"), 0x6a48: ('blr', 'x9'),
        0x6ac0: ('ldr', 'x2, [x8, #0xc0]'), 0x6ac4: ('br', 'x2'),
        0x6ae0: ('ldr', 'x4, [x8, #0xf8]'), 0x6ae4: ('br', 'x4')}
    require_members(ins, resource, 'HAL resource/field')
    check(pe.read(0x7afe, 10) == b'SMMU\0IORT\0', 'resource property names mismatch')
    firmware = ROOT.parent / 'uefi-enuma'
    selections = []
    for name, line in [('Vendor.dsc.inc', 17), ('Vendor.fdf.inc', 16), ('Vendor.apriori.inc', 7)]:
        path = firmware / 'Platforms/Xiaomi/enumaPkg/EnumaInputs' / name
        check('Binaries/enuma/HALIOMMU/HALIOMMU.inf' in path.read_text().splitlines()[line - 1], 'provider board selection mismatch')
        selections.append({'path': str(path.relative_to(firmware)), 'line': line,
                           'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    return {'input_sha256': PROVIDER_PIN, 'ufsdxe_sha256': PIN, 'guid': guid,
        'selection': selections, 'installation': {'chain_rvas': [0x1210, 0x1488, 0x1504],
            'call_rva': 0x1558, 'bs_global_rva': 0x9168, 'member': layout['install_multiple'],
            'guid_rva': 0x9048, 'factory_table_rva': 0x9098, 'terminator_x3': 0, 'anchors': sorted(install)},
        'factory': {'member_offset': 8, 'target_rva': factory, 'shared_table_rva': 0x90b0,
            'allocation': 'none in factory body; returns shared function table, not client context'},
        'table_targets': table, 'client_context': {'create_rva': 0x16b4, 'bytes': 0x38,
            'initial_word': 1, 'meaning': 'zeroed software allocation with initial marker; not hardware bank or exclusivity'},
        'ufsdxe_calls': {'device_name_rva': 0x1870f, 'device_name': '\\_SB_.UFS0',
            'groups': [{'create_call': 0x140fc, 'mode_call': 0x14170, 'attach_call': 0x141d0, 'w2': 0, 'w3': 0},
                       {'create_call': 0x141f0, 'mode_call': 0x14214, 'attach_call': 0x14244, 'w2': 0x10, 'w3': 0}],
            'completion_store_rva': 0x1425c, 'execution_and_success': 'UNKNOWN', 'anchors': sorted(params)},
        'resource_selection': {'bounds': [[0x1920, 0x1b7c], [0x48a8, 0x4b70], [0x4e14, 0x4f28], [0x6958, 0x6af0]],
            'name_lookup': '1920->48a8->4934: walk external table nodes; type byte1, name at node+0x1d compared via50dc',
            'record_lookup': '49a8 decodes count records (wire stride0x14) into software stride0x20;1920 compares first UINT32 to caller w2 (0 or0x10), selected+0x10 used next; not proven SID/bank/index',
            'actual_UFS_records': 'UNKNOWN: runtime IORT property bytes not provided',
            'boundary': {'locate_call_rva': 0x6a48, 'guid_rva': 0x9078,
                'guid': str(uuid.UUID(bytes_le=pe.read(0x9078, 16))),
                'protocol_global_rva': 0x94e8, 'returned_function_table_global_rva': 0x94f0,
                'factory_member': 8, 'property_members': [0xc0, 0xf8],
                'properties': ['SMMU', 'IORT'], 'implementation_board_binding': 'UNKNOWN; not expanded to another module'},
            'anchors': sorted(resource)},
        'context_field_20': {'bounds': [0x2d98, 0x3038], 'mode_values': [0xe0, 0x009f00e0],
            'consumer': '2d98 walks ctx+0x28 list; when ctx first word0, forwards ctx+0x20 as w2 to34a4 at2e30 with record fields w0/w1',
            'hardware_field_meaning': 'UNKNOWN; no register layout, SID/context ownership or readback/completion inferred'},
        'next_boundary': 'External property protocol GUIDae37b942-457f-4c91-a196-d9669fd347a3 -> returned function table+0xc0/+0xf8 and actual board IORT/UFS records. Stop; no other provider code decoded.',
        'unknown': 'runtime installation/config/resource records, UTRL/UTMRL, SID/context exclusivity, DMA ownership, PA/IOVA/coherence/timeout buffers/LUN all UNKNOWN'}


def audit_provider(binary, ufs_pe, ufs_ins, layout, tool, output):
    data = binary.read_bytes()
    check(hashlib.sha256(data).hexdigest() == PROVIDER_PIN, 'HALIOMMU input hash mismatch')
    pe = PE(data)
    check((pe.entry, pe.base, pe.subsystem) == (0x1000, 0, 11), 'HALIOMMU PE identity mismatch')
    bounds = [(0x1208, 0x1224), (0x1488, 0x1560), (0x16b4, 0x1768),
              (0x1920, 0x1b7c), (0x2d98, 0x3038), (0x42d4, 0x4304),
              (0x48a8, 0x4b70), (0x4e14, 0x4f28), (0x6958, 0x6af0)]
    instructions = {}; raw = []
    for start, end in bounds:
        dump = run([tool, '-d', '--no-show-raw-insn', '--print-imm-hex',
                    '--start-address=' + hex(start), '--stop-address=' + hex(end), str(binary)])
        raw.append(dump)
        for line in dump.splitlines():
            match = re.match(r'^\s*([0-9a-f]+):\s+([a-z.][a-z0-9.]*)\s*(.*?)\s*$', line)
            if match:
                at = int(match[1], 16)
                pe.offset(at, 4, executable=True)
                instructions[at] = (match[2], re.sub(r'\s*<.*', '', match[3]).strip())
    report = provider_evidence(pe, instructions, ufs_pe, ufs_ins, layout)
    report['pe'] = {'entry': pe.entry, 'subsystem': pe.subsystem, 'sections': pe.sections}
    report['disassembly_bounds'] = bounds
    (output / 'haliommu-bounded.txt').write_text('\n'.join(raw))
    return report


def audit(binary, headers, objdump, clang, output):
    data = binary.read_bytes()
    check(hashlib.sha256(data).hexdigest() == PIN, 'UFSDxe input hash mismatch; no address reuse')
    pe = PE(data)
    check(pe.entry == 0x1000 and pe.subsystem == 12 and pe.base == 0, 'unexpected PE identity')
    layout, ir, assembly = header_layout(headers, clang)
    raw, ins = disassemble(objdump, binary, pe)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'disassembly.txt').write_text(raw)
    (output / 'header-layout.ll').write_text(ir)
    (output / 'header-abi.s').write_text(assembly)
    # Bind the BS global to a system-table constructor, not offset coincidence.
    proof = {0x5d38: ('ldr', f"x8, [x1, #{hex(layout['st_bs'])}]"),
             0x5d3c: ('adrp', 'x10, 0x1a000'), 0x5d40: ('str', 'x8, [x10, #0x8e0]')}
    for at, expected in proof.items():
        check(ins.get(at) == expected, 'BootServices constructor proof mismatch ' + hex(at))
    argument_proof = {0x1160: ('mov', 'x19, x1'), 0x118c: ('mov', 'x1, x19'),
                      0x1190: ('bl', '0x123c'), 0x1248: ('mov', 'x19, x1'),
                      0x1250: ('bl', '0x5d18'), 0x2794: ('bl', '0x4cac'),
                      0x4cf4: ('br', 'x2'), 0x27c8: ('bl', '0x9548'),
                      0x9550: ('bl', '0x14088')}
    for at, expected in argument_proof.items():
        check(ins.get(at) == expected, 'argument/xref instruction mismatch ' + hex(at))
    events = []; references = []
    # Hash-specific finite windows: constructors, UFS config lookup and event helper.
    for start, end in [(0x5e34, 0x5f24), (0x60e0, 0x61bc), (0xe674, 0xe6f8), (0x277c, 0x27f8)]:
        ev, ref = trace(ins, start, end, 0x1a8e0, layout)
        events += ev; references += ref
    strings = []
    for offset, text in [(0x14912, 'UfsSmmuConfigForOtherBootDev'), (0x1492f, 'UFSSmmuConfig failed\n')]:
        expected = text.encode() + b'\0'
        check(data[offset:offset + len(expected)] == expected, 'string bytes differ')
        rva = pe.rva(offset, len(expected))
        xrefs = [r for r in references if r['target_rva'] == rva]
        check(xrefs, 'required config/error xref not established')
        strings.append({'text': text, 'file_offset': offset, 'rva': rva, 'xrefs': xrefs, 'input_sha256': PIN,
                        'entry_path': path_to(ins, pe.entry, xrefs[0]['instruction_rva'])})
    for event in events:
        args = event['arguments_x0_x5']
        callback = args[2]
        event['entry_path'] = path_to(ins, pe.entry, event['call_rva'])
        event['guid'] = str(uuid.UUID(bytes_le=pe.read(args[4], 16))) if event['service'] == 'CreateEventEx' and isinstance(args[4], int) else 'UNKNOWN'
        event['is_exit_event'] = event['guid'] == layout['exit_guid'] or args[0] == layout['exit_type']
        event['callback'] = callback_table(ins, callback, pe) if isinstance(callback, int) else {'callback_rva': 'UNKNOWN'}
        event['direct_callee_tables'] = [callback_table(ins, target['target_rva'], pe)
                                         for target in event['callback'].get('direct_targets', [])]
        # Every item binds back to the whole input, including those unrelated to EBS.
        event['input_sha256'] = PIN
    interfaces = interface_evidence(pe, ins, layout, headers)
    provider = audit_provider(ROOT.parent / 'uefi-enuma/Binaries/enuma/HALIOMMU/HALIOMMU.efi', pe, ins, layout, objdump, output)
    interfaces['smmu_next_step']['board_provider_binding'] = {'provider': 'HALIOMMU', 'sha256': PROVIDER_PIN, 'guid_match': True}
    interfaces['smmu_next_step']['acquisition']['interface_type'] = 'shared HAL function table, not software client context'
    interfaces['smmu_next_step']['first_operation']['target'] = 'HALIOMMU16b4, client context creation'
    interfaces['smmu_next_step']['next_question'] = provider['next_boundary']
    for event in events:
        for table in event['direct_callee_tables']:
            for call in table['indirect_calls']:
                if call['instruction_rva'] == 0x6088:
                    call['target'] = 'BootServices.LocateProtocol (runtime implementation not resolved)'
    config = ROOT.parent / 'uefi-enuma/Platforms/Xiaomi/enumaPkg/Library/ConfigurationMapLib/ConfigurationMapLib.c'
    cfg = config.read_text()
    values = {}
    for key in ('EnableUfsIOC', 'UfsSmmuConfigForOtherBootDev'):
        found = re.findall(r'\{\s*"' + key + r'"\s*,\s*(0x[0-9a-fA-F]+|[0-9]+)\s*\}', cfg)
        check(len(found) == 1, 'ambiguous config ' + key)
        values[key] = int(found[0], 0)
    return {'validation': 'self-checked static evidence only', 'input_sha256': PIN,
            'pe': {'entry_rva': pe.entry, 'subsystem': pe.subsystem, 'image_base': pe.base, 'sections': pe.sections},
            'headers': layout, 'config': {'values': values, 'sha256': hashlib.sha256(config.read_bytes()).hexdigest()},
            'boot_services_proof': {'slot_rva': 0x1a8e0, 'constructor_instructions': sorted(proof),
                'argument_xref_instructions': sorted(argument_proof),
                'entry_path': path_to(ins, pe.entry, 0x5d38),
                'argument_proof': 'entry saves/restores x1 before tail114c;1160 saves ST x1 in x19;118c forwards x19 to123c;1248 saves x1;1250 calls5d18 without changing x1'},
            'strings': strings, 'event_sites': events, 'interfaces': interfaces, 'provider': provider,
            'config_xref_calls': [{'instruction_rva': 0x2794, 'target_rva': 0x4cac, 'role': 'string in x0, output pointer x1'},
                                  {'instruction_rva': 0x4cf4, 'target': 'Shim EFI_UEFI_CONFIG_LIBRARY.GetCfgInfoVal via x2; runtime loading UNKNOWN'},
                                  {'instruction_rva': 0x27c8, 'target_rva': 0x9548, 'role': 'conditional branch after stack value check; not proof of effective SMMU state'},
                                  {'instruction_rva': 0x9550, 'target_rva': 0x14088}],
            'unknown': {k: 'UNKNOWN' for k in ('runtime_registration_success', 'callback_invocation', 'UTRL_UTMRL', 'SID_context_exclusivity',
                         'DMA_ownership', 'PA_IOVA', 'cache_coherence', 'timeout_buffer_lifetime', 'LUN')},
            'limits': ['finite pinned windows, no claim that other registration sites do not exist',
                       'syntactic direct CFG paths ignore feasibility, indirect calls and termination; not runtime reachability',
                       'no MMIO/queue semantics assigned from numeric constants or runtime subsystem attribute',
                       'CreateEventEx existence, callback body, and queue/completion proof are separate',
                       'no FlushBlocks invocation, hardware execution, firmware build or activation change']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--headers', type=Path, default=Path('/home/wh1stl3/enuma-fw/mu_basecore'))
    parser.add_argument('--objdump', default='/usr/bin/llvm-objdump')
    parser.add_argument('--clang', default='/usr/bin/clang')
    args = parser.parse_args()
    output = ROOT / '.cache/ufs-exit-audit'
    run(['git', '-C', str(ROOT), 'check-ignore', '-q', str(output / 'report.json')])
    output.mkdir(parents=True, exist_ok=True)
    try:
        report = audit(ROOT.parent / 'uefi-enuma/Binaries/enuma/UFSDxe/UFSDxe.efi', args.headers, args.objdump, args.clang, output)
    except (ValueError, OSError, subprocess.SubprocessError, struct.error) as exc:
        (output / 'report.json').write_text(json.dumps({'validation': 'REJECTED', 'error': str(exc)}, indent=2) + '\n')
        print('REJECTED:', exc)
        return 1
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('self-checked static audit:', len(report['event_sites']), 'bounded event sites;',
          sum(e['is_exit_event'] for e in report['event_sites']), 'EBS group matches; runtime/queue state UNKNOWN')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
