#!/usr/bin/env python3
"""Candidate-specific rebinding evidence for the frozen 24r observation kernel.

Read-only. Reuses the accepted PMGR prelink audit method and the final-link
disassembly helpers, then adds:
* donor/slide/component equality and the source-site vs new-address diff vs 23r;
* the actual 340-slot landing map, provider storage size, lifecycle bindings and
  ADRP/ADD|LDR|BL materialization of the original functions;
* NativeUfs compile inputs, vtable/metaclass/initializer binding and isolation;
* observer source/disassembly evidence for the five reviewed gates;
* the actual ADT range translation used by the UFS consumer.

Every observer item is emitted as evidence with `human_gate: pending`; this
script does not self-certify the manual conclusions.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import subprocess
import sys

FROZEN = {
    'native_sha256': 'f5c372beab9bd7fbb420b533582c27a95dacb81f816e78d4efc18f5a8e5bd597',
    'prelink_sha256': 'f30a36862a796bdbf45dd55c4a1a60b9d0cec6dde68bcb3fe315c7b11b86ea18',
    'metadata_sha256': '3c94f5bce228ac50c9ff7126aa1caebd1c8df9a60b9c6cf82556173173983232',
}
OBSERVER_PATCH = 'a3c12c0f1d210bb2481ba83fa28023c91fad27ac346f992d7613de7e8ed12109'
ORIGINAL = ('__ZN9ApplePMGRC2EPK11OSMetaClass', '__ZN9ApplePMGRD2Ev',
            '__ZN9ApplePMGR10gMetaClassE')
NUB = ('_sheng_original_pmgr_nub_create', '_sheng_original_pmgr_nub_read',
       '_sheng_original_pmgr_nub_write')
OBSERVER_TEXT = ('_enuma_pid1_begin', '_enuma_pid1_svc', '_enuma_pid1_exit',
                 '_enuma_pid1_observer', '_enuma_pid1_write')
OBSERVER_DATA = ('_enuma_pid1_state', '_enuma_pid1_lock_ready')
OBSERVER_ROOT = 0xfffffff007000000


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(name, filename):
    path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def nm_all(path):
    out = subprocess.check_output(['llvm-nm', '--defined-only', str(path)], text=True)
    result = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 3 and re.fullmatch(r'[0-9a-fA-F]+', parts[0]):
            result.setdefault(parts[2], int(parts[0], 16))
    return result


def read_segments(path):
    data = Path(path).read_bytes()
    require(data[:4] == b'\xcf\xfa\xed\xfe', 'not a thin 64-bit Mach-O')
    ncmds = struct.unpack_from('<I', data, 16)[0]
    offset = 32
    segments = []
    for _ in range(ncmds):
        command, size = struct.unpack_from('<II', data, offset)
        if command == 0x19:
            name = data[offset + 8:offset + 24].rstrip(b'\0').decode()
            vmaddr, vmsize, fileoff, filesize = struct.unpack_from('<QQQQ', data, offset + 24)
            maxprot, initprot, nsects, _ = struct.unpack_from('<4I', data, offset + 56)
            sections = []
            for index in range(nsects):
                at = offset + 72 + index * 80
                sectname = data[at:at + 16].rstrip(b'\0').decode()
                segname = data[at + 16:at + 32].rstrip(b'\0').decode()
                addr, length, off, align, reloff, nreloc, flags = struct.unpack_from(
                    '<QQIIIII', data, at + 32)
                sections.append({'name': sectname, 'segment': segname, 'va': addr,
                                 'size': length, 'fileoff': off, 'flags': flags})
            segments.append({'name': name, 'va': vmaddr, 'size': vmsize, 'fileoff': fileoff,
                             'filesize': filesize, 'maxprot': maxprot, 'initprot': initprot,
                             'sections': sections})
        offset += size
    return segments


def segment_for(segments, address):
    hit = [segment for segment in segments
           if segment['size'] > 0 and segment['va'] <= address < segment['va'] + segment['size']]
    return hit[0] if hit else None


def section_for(segments, address):
    for segment in segments:
        for section in segment['sections']:
            if section['size'] > 0 and section['va'] <= address < section['va'] + section['size']:
                return section
    return None


def binding_set(metadata):
    return {(int(item['site']), int(item['target']), item['kind'], item['module'])
            for item in metadata['bindings']}


def compare_reference(metadata, reference):
    current = binding_set(metadata)
    prior = binding_set(reference)
    prior_new = {(int(item['site']), int(item['target'])): (int(item['new_site']), int(item['new_target']))
                 for item in reference['bindings']}
    moved = sum(1 for item in metadata['bindings']
                if (int(item['site']), int(item['target'])) in prior_new and
                prior_new[(int(item['site']), int(item['target']))] !=
                (int(item['new_site']), int(item['new_target'])))
    return {
        'slide_equal': metadata['slide'] == reference['slide'],
        'original_sha256_equal': metadata['original_sha256'] == reference['original_sha256'],
        'components_equal': metadata['components'] == reference['components'],
        'codeless_components_equal': metadata['codeless_components'] == reference['codeless_components'],
        'extents_equal': metadata['extents'] == reference['extents'],
        'original_executable_sha256_equal': (metadata['original_executable_sha256'] ==
                                             reference['original_executable_sha256']),
        'source_binding_set_equal': current == prior,
        'source_binding_count': len(current),
        'added_source_bindings': len(current - prior),
        'removed_source_bindings': len(prior - current),
        'pointer_counts': metadata['pointer_counts'],
        'moved_new_addresses': moved,
        'candidate_bytes_before': reference['candidate_bytes'],
        'candidate_bytes_after': metadata['candidate_bytes'],
    }


def vtable_targets(helper, raw, info, vtable, slots):
    result = []
    for index in range(slots):
        va = vtable + index * 8
        offset = helper.backed_offset(info['segments'], va, 8, len(raw))
        result.append(struct.unpack_from('<Q', raw, offset)[0])
    return result


def vtable_slot_count(defined, section, vtable):
    """Count slots to the next defined symbol, not to the section end."""
    inside = sorted(address for address in defined.values()
                    if section['va'] <= address < section['va'] + section['size']
                    and address > vtable)
    boundary = inside[0] if inside else section['va'] + section['size']
    require(boundary > vtable and (boundary - vtable) % 8 == 0,
            f'vtable boundary is not 8-byte aligned: {vtable:#x} -> {boundary:#x}')
    slots = (boundary - vtable) // 8
    require(0 < slots <= 512, f'implausible vtable slot count: {slots}')
    return slots, boundary, bool(inside)


def instruction_shape(link, body):
    """Normalized instruction form only.

    Every immediate, branch target and symbol annotation is erased, so equality
    of two shapes proves instruction-form equality only. It is not an operand,
    register or dataflow proof.
    """
    result = []
    for line in body:
        _, text = link.instruction(line)
        operation = link.opcode(text)
        rest = text[len(operation):].strip()
        rest = re.sub(r'<.*>', '<>', rest)
        rest = re.sub(r'0x[0-9a-fA-F]+', '<V>', rest)
        rest = re.sub(r'#-?\d+', '#<I>', rest)
        result.append(operation + ' ' + rest)
    return result


def materialization_at(parsed, index, read_pointer):
    """Instruction-form index of one ADRP and its ADD/LDR with a register chain.

    The chain requires the ADD/LDR base register to be the ADRP destination.
    This is existence and register-name association only; it does not prove the
    complete operand dataflow or that the value is used by the intended call.
    """
    address, text = parsed[index]
    match = re.match(r'adrp\s+(x\d+), 0x([0-9a-fA-F]+)', text)
    if not match:
        return []
    destination, page = match.group(1), int(match.group(2), 16) & ~0xfff
    results = []
    for offset in range(1, 4):
        if index + offset >= len(parsed):
            break
        next_address, next_text = parsed[index + offset]
        add = re.match(r'add\s+(x\d+), (x\d+), #(0x[0-9a-fA-F]+|\d+)', next_text)
        if add and add.group(2) == destination:
            results.append({'kind': 'adrp+add', 'site': address,
                            'materialize': next_address,
                            'value': page + int(add.group(3), 0),
                            'register_chain': {'adrp_destination': destination,
                                               'base': add.group(2),
                                               'destination': add.group(1)}})
        load = re.match(r'ldr\s+(x\d+), \[(x\d+), #(0x[0-9a-fA-F]+|\d+)\]', next_text)
        if load and load.group(2) == destination:
            try:
                value = read_pointer(page + int(load.group(3), 0))
            except ValueError:
                value = None
            if value is not None:
                results.append({'kind': 'adrp+ldr', 'site': address,
                                'materialize': next_address, 'value': value,
                                'register_chain': {'adrp_destination': destination,
                                                   'base': load.group(2),
                                                   'destination': load.group(1)}})
    return results


def build_reference_index(functions, link, read_pointer):
    """One pass: direct BL sites and ADRP+ADD/LDR instruction forms.

    This is a site index, not a dataflow proof. Materialization records carry
    only the register-name chain produced by `materialization_at`.
    """
    calls = {}
    materialized = {}
    for name, body in functions.items():
        for line in body:
            address, text = link.instruction(line)
            target = link.branch_target(text)
            if target is not None and link.opcode(text) == 'bl':
                calls.setdefault(target, []).append({'kind': 'bl', 'caller': name, 'site': address})
        parsed = [link.instruction(line) for line in body]
        for index, (address, text) in enumerate(parsed):
            if not text.startswith('adrp'):
                continue
            for item in materialization_at(parsed, index, read_pointer):
                item = dict(item)
                item['caller'] = name
                value = item.pop('value')
                materialized.setdefault(value, []).append(item)
    return calls, materialized


def writable_segment(segment):
    """Actual write permission (current and maximum), not merely non-executable."""
    return bool(segment and segment['initprot'] & 2 and segment['maxprot'] & 2)


def write_relocation_diff(metadata, reference, path):
    prior_new = {(int(item['site']), int(item['target'])):
                 (int(item['new_site']), int(item['new_target']))
                 for item in reference['bindings']}
    rows = []
    per_module = {}
    for item in metadata['bindings']:
        key = (int(item['site']), int(item['target']))
        current = (int(item['new_site']), int(item['new_target']))
        if key in prior_new and prior_new[key] == current:
            continue
        rows.append({'site': key[0], 'target': key[1], 'kind': item['kind'],
                     'module': item['module'],
                     'prior_new_site': prior_new.get(key, (None, None))[0],
                     'prior_new_target': prior_new.get(key, (None, None))[1],
                     'new_site': current[0], 'new_target': current[1]})
        per_module[(item['kind'], item['module'])] = \
            per_module.get((item['kind'], item['module']), 0) + 1
    path.write_text(json.dumps({'count': len(rows),
                                'per_kind_module': {f'{kind}/{module}': count
                                                    for (kind, module), count in
                                                    sorted(per_module.items())},
                                'rows': rows}, indent=2) + '\n')
    return {'path': str(path), 'count': len(rows),
            'per_kind_module': {f'{kind}/{module}': count
                                for (kind, module), count in sorted(per_module.items())}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-json', type=Path, required=True)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--tree', type=Path, required=True)
    parser.add_argument('--board', type=Path, required=True)
    parser.add_argument('--reference-metadata', type=Path, required=True)
    parser.add_argument('--payload', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    link = load('final_link', 'audit-enuma-ufs-final-link.py')
    pmgr_audit = load('pmgr_audit', 'audit-enuma-pmgr-prelink.py')
    package = load('package24', 'check-enuma-ufs-24r-package.py')
    record = json.loads(args.build_json.read_text())
    native, prelink = Path(record['native']), Path(record['prelink'])
    metadata = json.loads(Path(record['metadata']).read_text())
    reference = json.loads(args.reference_metadata.read_text())
    args.evidence.mkdir(parents=True, exist_ok=True)
    require(link.sha(native) == FROZEN['native_sha256'], 'native hash differs')
    require(link.sha(prelink) == FROZEN['prelink_sha256'], 'prelink hash differs')
    require(link.sha(Path(record['metadata'])) == FROZEN['metadata_sha256'], 'metadata hash differs')

    diff = compare_reference(metadata, reference)
    relocation_diff = write_relocation_diff(metadata, reference,
                                            args.evidence / 'relocation-diff-24r.json')
    require(diff['slide_equal'] and diff['original_sha256_equal'], 'donor/slide differ from 23r')
    require(diff['components_equal'] and diff['extents_equal'], 'donor components/extents differ')
    require(diff['original_executable_sha256_equal'], 'donor executable hashes differ')
    require(diff['source_binding_set_equal'], 'source binding set differs from 23r')

    helper = pmgr_audit.load_native_prelink(args.base)
    raw = prelink.read_bytes()
    info = helper.macho(raw)
    defined = nm_all(prelink)
    segments = read_segments(prelink)
    target_ok = 0
    for item in metadata['bindings']:
        target = int(item['new_target'])
        if segment_for(segments, target):
            target_ok += 1
    require(target_ok == len(metadata['bindings']), 'new relocation target outside the image')

    report = json.loads((args.tree / 'build/sheng-platform-power/build-report.json').read_text())
    require(report['source_sha256'] == sha(args.tree / 'kits/enuma/ShengPlatformPower.cpp'),
            'PMGR source/report differs')
    require(report['archive_sha256'] == sha(args.tree / 'build/sheng-platform-power/libShengPlatformPower.a'),
            'PMGR archive/report differs')
    namespace = argparse.Namespace(base=args.base, tree=args.tree, native=native, prelink=prelink,
                                   manifest=Path(record['metadata']), board=args.board,
                                   output=args.evidence / 'pmgr-prelink.json', payload=None,
                                   require_package=False)
    pmgr_result = pmgr_audit.audit(namespace)
    (args.evidence / 'pmgr-prelink.json').write_text(json.dumps(pmgr_result, indent=2) + '\n')
    require(pmgr_result['vtable_slots_checked'] == 340, pmgr_result)
    abi_header = (args.tree / 'build/sheng-platform-power/OriginalPMGRABI.h').read_text()
    require('static_assert(sizeof(ApplePMGR)==0x4b8a8,"Original provider storage");' in abi_header,
            'provider storage size differs')
    require('originalPrivate[0x4b8a8-sizeof(IOPMGR)]' in abi_header, 'provider private storage differs')
    late = read_segments(args.tree / 'build/sheng-platform-power/ShengPlatformPower.late.o')
    require(not any(section['name'] == '__mod_init_func' for segment in late
                    for section in segment['sections']), 'late PMGR initializer remains')

    bindings = {name: int(value, 16) for name, value in report['bindings'].items()}
    reference_tree = Path(args.reference_metadata).parent.parent / 'tree'
    reference_report_path = reference_tree / 'build/sheng-platform-power/build-report.json'
    reference_diff = None
    reference_linked = None
    if reference_report_path.is_file():
        reference_prelink = Path(args.reference_metadata).parent / 'kernel.macho'
        if reference_prelink.is_file():
            prior = nm_all(reference_prelink)
            names = ('_sheng_pmgr_run', '__ZN18ShengPlatformPower10gMetaClassE',
                     '__GLOBAL__sub_I_ShengPlatformPower.cpp', '_bsd_init',
                     '_enuma_pid1_begin', '_enuma_pid1_svc', '_enuma_pid1_exit')
            reference_linked = {name: {'prior': prior.get(name), 'current': defined.get(name),
                                       'equal': prior.get(name) == defined.get(name)}
                                for name in names}
        reference_report = json.loads(reference_report_path.read_text())
        require(report['virtual_entries'] == reference_report['virtual_entries'],
                'PMGR 340-slot entry list differs from 23r')
        require(report['all_undefined_imports'] == reference_report['all_undefined_imports'],
                'PMGR import list differs from 23r')
        require(set(report['bindings']) == set(reference_report['bindings']),
                'PMGR binding name set differs from 23r')
        reference_diff = {
            'reference_report': str(reference_report_path),
            'virtual_entries_equal': True,
            'imports_equal': True,
            'binding_names_equal': True,
            'moved_binding_addresses': sum(
                1 for name, value in report['bindings'].items()
                if reference_report['bindings'].get(name) != value),
            'source_sha256_equal': report['source_sha256'] == reference_report['source_sha256'],
            'archive_sha256_equal': report['archive_sha256'] == reference_report['archive_sha256'],
        }
    native_raw = native.read_bytes()
    native_info = helper.macho(native_raw)
    native_defined = nm_all(native)
    vtable = defined['__ZTV18ShengPlatformPower'] + 16
    native_vtable = native_defined['__ZTV6IOPMGR'] + 16

    def read_prelink(va, size):
        return raw[helper.backed_offset(info['segments'], va, size, len(raw)):][:size]

    def read_native(va, size):
        return native_raw[helper.backed_offset(native_info['segments'], va, size, len(native_raw)):][:size]

    landing = []
    counts = {}
    for slot, name in enumerate(report['virtual_entries']):
        target = struct.unpack('<Q', read_prelink(vtable + slot * 8, 8))[0]
        if 'ShengPlatformPower' in name:
            kind = 'own'
            expected = defined.get(name)
        elif '9ApplePMGR' in name:
            kind = 'original'
            expected = defined.get(name)
        else:
            kind = 'native'
            expected = struct.unpack('<Q', read_native(native_vtable + slot * 8, 8))[0]
        require(expected is not None and target == expected,
                f'vtable slot {slot} landing differs: {name} {target:#x} != {expected}')
        counts[kind] = counts.get(kind, 0) + 1
        landing.append({'slot': slot, 'target': target, 'symbol': name, 'class': kind})
    require(landing[320]['symbol'] and 'ApplePMGR' in landing[320]['symbol'], landing[320])
    require(landing[321]['symbol'] and 'ApplePMGR' in landing[321]['symbol'], landing[321])
    for slot in (0, 1, 7):
        require('ShengPlatformPower' in (landing[slot]['symbol'] or ''), landing[slot])
    (args.evidence / 'vtable-landing-24r.json').write_text(
        json.dumps(landing, indent=2) + '\n')

    def read_pointer(va):
        return struct.unpack('<Q', raw[helper.backed_offset(info['segments'], va, 8, len(raw)):][:8])[0]

    functions = link.disassembly(prelink)
    calls_index, materialized_index = build_reference_index(functions, link, read_pointer)
    materialization = {}
    for name in ORIGINAL + NUB:
        require(name in bindings, f'missing binding: {name}')
        value = bindings[name]
        if name.endswith('gMetaClassE'):
            pattern = value.to_bytes(8, 'little')
            offsets = []
            at = raw.find(pattern)
            while at != -1 and len(offsets) < 8:
                offsets.append(at)
                at = raw.find(pattern, at + 1)
            require(offsets, f'no materialized data pointer for {name}')
            evidence = [{'kind': 'data-pointer', 'file_offset': offset} for offset in offsets]
        else:
            evidence = calls_index.get(value, []) + materialized_index.get(value, [])
        require(evidence, f'no BL/ADRP materialization for {name}')
        extent = next((item for item in metadata['extents']
                       if item['va'] <= value < item['va'] + item['size']), None)
        require(extent is not None, f'binding outside donor extents: {name}')
        require(extent['module'] == 'com.apple.driver.ApplePMGR', f'binding module differs: {name}')
        materialization[name] = {'target': value, 'module': extent['module'],
                                 'evidence': evidence[:4], 'evidence_count': len(evidence)}
    (args.evidence / 'original-materialization-24r.json').write_text(
        json.dumps(materialization, indent=2) + '\n')

    argv_text = (args.tree / 'build/sheng-ufs/effective-compile-argv.json').read_text()
    for define in ('NATIVE_UFS_REUSE_DIAGNOSTIC=1', 'NATIVE_UFS_EXTERNAL_STORE_PROVIDER=1',
                   'NATIVE_UFS_OBSERVATION_ONLY=1'):
        require(define in argv_text, f'missing compile define: {define}')
    nativeufs_source = args.tree / 'drivers/ShengUfs/NativeUfs.cpp'
    require(sha(nativeufs_source) == '3fe914c0bb62d953e3d4a9e4131b0a7ab5f9189f8246f19446258d5295e4839a',
            'NativeUfs source differs')
    vtable_name = '__ZTV9NativeUfs'
    vtable = defined[vtable_name] + 16
    vtable_section = section_for(segments, vtable)
    require(vtable_section is not None, 'NativeUfs vtable section missing')
    slots, vtable_boundary, boundary_exact = vtable_slot_count(defined, vtable_section, vtable)
    require(boundary_exact, 'no next defined symbol to bound the NativeUfs vtable')
    vtable_boundary_symbol = next((name for name, address in defined.items()
                                   if address == vtable_boundary), None)
    native_targets = vtable_targets(helper, raw, info, vtable, slots)
    reverse = {}
    for name, address in defined.items():
        reverse.setdefault(address, name)
    by_symbol = {}
    for index, target in enumerate(native_targets):
        symbol = reverse.get(target)
        if symbol:
            by_symbol.setdefault(symbol, []).append(index)
    probe_slots = by_symbol.get('__ZN9NativeUfs5probeEP9IOServicePi', [])
    start_slots = by_symbol.get('__ZN9NativeUfs5startEP9IOService', [])
    require(len(probe_slots) == 1 and len(start_slots) == 1, (probe_slots, start_slots))
    require(defined['__ZN9NativeUfs10gMetaClassE'], 'NativeUfs metaclass missing')
    mod_init = next((s for segment in segments for s in segment['sections']
                     if s['name'] == '__mod_init_func'), None)
    require(mod_init is not None, 'no __mod_init_func section')
    entries = [struct.unpack_from('<Q', raw, mod_init['fileoff'] + index * 8)[0]
               for index in range(mod_init['size'] // 8)]
    require(defined['__GLOBAL__sub_I_NativeUfs.cpp'] in entries,
            'NativeUfs initializer is not registered')
    start_name = 'NativeUfs::start(IOService*)'
    diagnostic_names = [name for name in functions if name.startswith('ufsReuseDiagnostic(')]
    finish_names = [name for name in functions if name.startswith('ufsReuseFinish(')]
    require(len(diagnostic_names) == 1 and len(finish_names) == 1, (diagnostic_names, finish_names))
    start_body = functions[start_name]
    diagnostic_entry = link.entry_address(functions[diagnostic_names[0]])
    finish_entry = link.entry_address(functions[finish_names[0]])
    link.check_calls_to(start_name, start_body, 'ufsReuseDiagnostic(', diagnostic_entry, opcodes=('bl',))
    link.check_calls_to(diagnostic_names[0], functions[diagnostic_names[0]],
                        'ufsReuseFinish(', finish_entry)
    link.check_wfe_terminal(finish_names[0], functions[finish_names[0]])
    refusals = {}
    for prefix in ('NativeUfsBlock::configure', 'NativeUfsBlock::configureVerification',
                   'NativeUfsBlock::authenticatesVolume', 'NativeUfsBlock::signedVolumeUuid',
                   'NativeUfsBlock::start', 'NativeUfs::startRoot'):
        names = [name for name in functions if name.startswith(prefix + '(')]
        require(len(names) == 1, (prefix, names))
        refusals[prefix] = link.check_constant_body(prefix, functions[names[0]], link.REFUSAL_BODY)
    async_names = [name for name in functions if name.startswith('NativeUfsBlock::doAsyncReadWrite(')]
    require(len(async_names) == 1, async_names)
    async_body = link.check_constant_body(async_names[0], functions[async_names[0]], link.ASYNC_BODY)

    patch = Path(args.board).parent / 'patches/xnu/enuma-pid1-observer.patch'
    require(sha(patch) == OBSERVER_PATCH, 'observer patch hash differs')
    bsd_init = args.tree / '.cache/xnu-work/bsd/kern/bsd_init.c'
    lines = bsd_init.read_text().splitlines()
    pmgr_lines = [index + 1 for index, text in enumerate(lines) if 'sheng_pmgr_run()' in text]
    pid1_lines = [index + 1 for index, text in enumerate(lines) if 'enuma_pid1_begin(' in text]
    utask = [index + 1 for index, text in enumerate(lines) if text.startswith('bsd_utaskbootstrap(void)')]
    utask_call = [index + 1 for index, text in enumerate(lines) if 'bsd_utaskbootstrap();' in text]
    load_init = [index + 1 for index, text in enumerate(lines) if 'load_init_program(p)' in text]
    require(len(pmgr_lines) == 1 and len(pid1_lines) == 1, (pmgr_lines, pid1_lines))
    require(len(utask) == 1 and len(utask_call) == 1, (utask, utask_call))
    require(pmgr_lines[0] < utask_call[0] and pid1_lines[0] > utask[0],
            (pmgr_lines, pid1_lines, utask))
    require(load_init and load_init[0] > utask_call[0], load_init)

    observer = {}
    for name in OBSERVER_TEXT:
        address = defined.get(name)
        require(address is not None, f'missing observer symbol: {name}')
        segment = segment_for(segments, address)
        obs_section = section_for(segments, address)
        require(segment and obs_section and segment['initprot'] & 4 and
                obs_section['name'] == '__text',
                f'observer symbol not executable-resident: {name}')
        observer[name] = {'address': address, 'segment': segment['name'],
                          'section': obs_section['name'], 'initprot': segment['initprot']}
    for name in OBSERVER_DATA:
        address = defined.get(name)
        require(address is not None, f'missing observer data: {name}')
        segment = segment_for(segments, address)
        obs_section = section_for(segments, address)
        require(writable_segment(segment), f'observer data is not writable: {name}')
        observer[name] = {'address': address, 'segment': segment['name'],
                          'section': (obs_section or {}).get('name'),
                          'initprot': segment['initprot'], 'maxprot': segment['maxprot']}

    reference_prelink = Path(args.reference_metadata).parent / 'kernel.macho'
    reference_functions = link.disassembly(reference_prelink) if reference_prelink.is_file() else {}
    reference_bsd_init = reference_tree / '.cache/xnu-work/bsd/kern/bsd_init.c'
    observer_reuse = {}
    for name in OBSERVER_TEXT:
        current_text = '\n'.join(functions[name])
        prior = reference_functions.get(name)
        prior_text = '\n'.join(prior) if prior is not None else None
        current_shape = instruction_shape(link, functions[name])
        prior_shape = instruction_shape(link, prior) if prior is not None else None
        observer_reuse[name] = {
            'current_sha256': hashlib.sha256(current_text.encode()).hexdigest(),
            'prior_sha256': hashlib.sha256(prior_text.encode()).hexdigest() if prior_text else None,
            'shape_sha256': hashlib.sha256('\n'.join(current_shape).encode()).hexdigest(),
            'same_shape_as_23r': prior_shape == current_shape,
            'shape_difference_count': (sum(1 for a, b in zip(prior_shape, current_shape) if a != b)
                                       if prior_shape else None),
        }
        require(prior_shape == current_shape, f'observer instruction shape changed vs 23r: {name}')
        require(len(prior_shape) == len(current_shape), f'observer function length changed: {name}')
    bsd_same = reference_bsd_init.is_file() and sha(bsd_init) == sha(reference_bsd_init)

    def calls(body):
        result = []
        for site in link.call_sites(body, ''):
            if site['opcode'] != 'bl':
                continue
            result.append({'site': site['site'], 'target': site['target'],
                           'symbol': next((n for n, a in defined.items() if a == site['target']), None)})
        return result

    dumps = {}
    for name in OBSERVER_TEXT:
        body = functions.get(name)
        if body is None:
            body = [line for line in subprocess.check_output(
                ['llvm-objdump', '--disassemble', '--demangle', '--start-address', hex(defined[name]),
                 '--stop-address', hex(defined[name] + 0x200), str(prelink)], text=True).splitlines()
                if re.match(r'^\s*[0-9a-fA-F]+:', line)]
            body = [line.strip() for line in body]
        text = '\n'.join(body) + '\n'
        (args.evidence / (name + '.asm')).write_text(text)
        dumps[name] = {'sha256': hashlib.sha256(text.encode()).hexdigest(), 'lines': len(body)}
    begin_calls = calls(functions['_enuma_pid1_begin'])
    svc_calls = calls(functions['_enuma_pid1_svc'])
    exit_calls = calls(functions['_enuma_pid1_exit'])
    require(any(c['symbol'] == '_lck_ticket_lock' for c in begin_calls), begin_calls)
    require(any(c['symbol'] == '_kernel_thread_start' for c in begin_calls), begin_calls)
    require(any(c['symbol'] in ('_lck_ticket_unlock',) for c in begin_calls), begin_calls)
    lock_order = [c['symbol'] for c in begin_calls if c['symbol'] and 'lck_ticket' in c['symbol']]
    observer_gates = {
        'textmode_acquire_dominance': {
            'evidence': {'bsd_init_pmgr_line': pmgr_lines[0], 'bsd_init_pid1_line': pid1_lines[0],
                         'bsd_utaskbootstrap_definition': utask[0],
                         'bsd_utaskbootstrap_call': utask_call[0], 'load_init_program_line': load_init[0],
                         'observer_patch_sha256': sha(patch),
                         'bsd_init_source_identical_to_23r': bsd_same},
            'reuse_rationale': 'the observer patch hash and the assembled bsd_init.c are identical to '
                               'the independently reviewed 23r source; only the frozen image hash '
                               'changed, so the unchanged-source conclusion is reusable without '
                               'inheriting any old hash permission',
            'human_gate': 'pending independent review',
        },
        'svc_parameter_dispatch': {
            'evidence': {'call_sites': svc_calls[:8], 'disassembly': dumps['_enuma_pid1_svc'],
                         'instruction_sha256': observer_reuse['_enuma_pid1_svc']['current_sha256'],
                         'shape_sha256': observer_reuse['_enuma_pid1_svc']['shape_sha256']},
            'reuse_rationale': 'observer source patch unchanged; instruction shape is identical to '
                               '23r modulo candidate-specific data/string addresses, and the exact '
                               'candidate dump is hash-bound',
            'human_gate': 'pending independent review',
        },
        'begin_release_identity': {
            'evidence': {'calls': begin_calls[:8], 'lock_sequence': lock_order,
                         'disassembly': dumps['_enuma_pid1_begin'],
                         'instruction_sha256': observer_reuse['_enuma_pid1_begin']['current_sha256'],
                         'shape_sha256': observer_reuse['_enuma_pid1_begin']['shape_sha256'],
                         'state_symbol': observer.get('_enuma_pid1_state')},
            'reuse_rationale': 'observer source patch unchanged; instruction shape is identical to '
                               '23r with relocated data addresses; lock/thread-start ordering is '
                               'visible in the hash-bound dump',
            'human_gate': 'pending independent review',
        },
        'exit_lock_ordering': {
            'evidence': {'calls': exit_calls, 'disassembly': dumps['_enuma_pid1_exit'],
                         'instruction_sha256': observer_reuse['_enuma_pid1_exit']['current_sha256'],
                         'shape_sha256': observer_reuse['_enuma_pid1_exit']['shape_sha256']},
            'reuse_rationale': 'observer source patch unchanged; instruction shape is identical to '
                               '23r; the exit path publishes state without taking the ticket lock, '
                               'visible in the dump',
            'human_gate': 'pending independent review',
        },
        'normal_identity_lifecycle': {
            'evidence': {'writer': observer.get('_enuma_pid1_write'),
                         'observer_thread': observer.get('_enuma_pid1_observer'),
                         'data_symbols': {name: observer.get(name) for name in OBSERVER_DATA},
                         'svc_symbol': observer.get('_enuma_pid1_svc')},
            'reuse_rationale': 'observer source patch unchanged; writer/observer/svc instruction '
                               'shapes match 23r and the state symbols remain in writable __DATA; '
                               'no identity or lifecycle source changed',
            'human_gate': 'pending independent review',
        },
    }

    old_adt = package.adt_properties(subprocess.check_output(
        ['mtype', '-i', str(Path(args.payload).parent.parent / '22r-pid1-runtime-summary/payload.img'),
         '::/EFI/UniXNU/Payloads/kernel.macho.adt'], timeout=120))
    new_adt = package.adt_properties(subprocess.check_output(
        ['mtype', '-i', str(args.payload), '::/EFI/UniXNU/Payloads/kernel.macho.adt'], timeout=120))
    delta = package.adt_delta(old_adt, new_adt)
    require(set(delta) <= package.ALLOWED_ADT_DELTA, delta)
    translation = package.translate_ufshc(new_adt['/device-tree/arm-io/ufshc:reg'],
                                          new_adt['/device-tree/arm-io:ranges'])
    consumer = args.tree / 'drivers/ShengUfs/UfsPlatformResources.h'
    require('address != 0x01d84000ULL || length != 0x3000' in consumer.read_text(),
            'consumer address check missing')
    adt_equivalence = Path('/mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/.cache/'
                           'ufs-adt-equivalence-24r-20261111/result.json')

    result = {
        'validation': 'self-checked; static only; manual conclusions pending',
        'candidate': FROZEN,
        'donor_diff_vs_23r': diff,
        'relocation_diff_vs_23r': relocation_diff,
        'relocation_targets_in_image': target_ok,
        'binding_list_location': str(record['metadata']),
        'original_executable_modules_checked': ['com.apple.driver.ApplePMGR',
                                                'com.apple.driver.AppleMobileFileIntegrity'],
        'amfi_entrypoint': metadata['module_entrypoints']['com.apple.driver.AppleMobileFileIntegrity']['start_va'],
        'original_executable_sha256': {
            'ApplePMGR': metadata['original_executable_sha256']['com.apple.driver.ApplePMGR'],
            'AppleMobileFileIntegrity':
                metadata['original_executable_sha256']['com.apple.driver.AppleMobileFileIntegrity'],
        },
        'pmgr': {
            'reused_audit': {k: pmgr_result[k] for k in
                             ('vtable_slots_checked', 'imports_checked', 'hook_call', 'run',
                              'manual_initializer_call', 'initializer', 'metaclass',
                              'metaclass_segment')},
            'provider_storage': '0x4b8a8', 'vtable_slots': len(landing),
            'landing_classes': counts,
            'original_bindings': bindings,
            'materialization': {name: {'target': item['target'], 'module': item['module'],
                                       'evidence_count': item['evidence_count']}
                                for name, item in materialization.items()},
            'materialization_evidence': str(args.evidence / 'original-materialization-24r.json'),
            'materialization_method': 'BL and ADRP+ADD/LDR site index with register-name '
                                      'chain; existence and chain only, not a full dataflow proof',
            'late_initializer_removed': True,
            'reference_diff_vs_23r': reference_diff,
            'linked_address_diff_vs_23r': reference_linked,
        },
        'nativeufs': {
            'compile_defines_checked': True,
            'source_sha256': sha(nativeufs_source),
            'compile_argv_sha256': hashlib.sha256(argv_text.encode()).hexdigest(),
            'vtable_section': vtable_section['name'], 'vtable_slots': slots,
            'vtable_boundary': {'va': vtable_boundary, 'symbol': vtable_boundary_symbol,
                                'method': 'next defined symbol after the vtable, not section end'},
            'probe_slots': probe_slots, 'start_slots': start_slots,
            'metaclass': hex(defined['__ZN9NativeUfs10gMetaClassE']),
            'initializer': hex(defined['__GLOBAL__sub_I_NativeUfs.cpp']),
            'initializer_registered': True,
            'refusal_bodies': refusals,
            'doAsyncReadWrite_body': async_body,
            'diagnostic_isolation': True,
        },
        'observer': {'patch_sha256': sha(patch), 'symbols': observer,
                     'disassembly': dumps, 'gates': observer_gates,
                     'reuse_instruction_equality': observer_reuse,
                     'bsd_init_identical_to_23r': bsd_same},
        'adt': {'delta': delta, 'translation': translation,
                'consumer_sha256': sha(consumer),
                'original_equivalence_evidence': str(adt_equivalence),
                'original_equivalence_sha256': (sha(adt_equivalence)
                                                if adt_equivalence.is_file() else None)},
        'human_gates_pending': sorted(observer_gates),
        'evidence_semantics': {
            'instruction_shape': 'normalizes every immediate, branch target and symbol '
                                 'annotation; equality proves instruction form only, not operand '
                                 'or dataflow equality',
            'materialization_index': 'BL and ADRP+ADD/LDR site index with a register-name '
                                     'chain; existence and chain only, not a full dataflow proof',
            'vtable_slot_count': 'bounded by the next defined symbol after the vtable, not by '
                                 'the section end',
            'observer_gates': 'this audit still emits manual pending; the separate independent '
                              'deep manual conclusion does not rewrite these fields',
        },
        'not_claimed': ['ownership closure', 'runtime/load behaviour', 'AMFI/Matching runtime',
                        'device authorization'],
        'device_authorized': False, 'release_allowed': False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'validation': 'self-checked',
                      'landing': counts,
                      'materialization': {n: v['evidence_count'] for n, v in materialization.items()},
                      'observer_gates_pending': len(observer_gates)}, indent=2))


if __name__ == '__main__':
    sys.exit(main())
