#!/usr/bin/env python3
"""Candidate-specific final ABI/admission audit for the 24r observation kernel.

Read-only: it never builds, links or edits the kernel, the metadata or the
package. It reuses the final-link disassembly/symbol helpers and the package
ADT reader. The audit separates mechanically closed facts from the
qualification flags that kernel.json still reports as false:

* metadata is bound to the actual native/prelink bytes (hashes, size, output,
  sparse ABI, coalesced extents, unmodified-image flags);
* the prelink contains exactly one NativeUfs nub personality and one
  NativeUfsRoot/IOPlatformExpertDevice personality;
* the contained payload ADT exposes the sm8250 UFSHCI node under arm-io;
* NativeUfs::probe and NativeUfs::start keep a narrow argument gate before the
  first resource call, and start calls the diagnostic only after the resource
  check;
* the single PMGR hook is _bsd_init -> _sheng_pmgr_run on this image and the
  _enuma_pid1_* observer symbols are image-resident.

The kernel.json abi_qualified/loadable/runtime_qualified/... flags are read as
reported; they are not rewritten and are not treated as qualified. ABI/load
admission therefore stays false even when the mechanical bindings pass.
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
import tomllib

CONDITIONAL = ('cbz', 'cbnz', 'tbz', 'tbnz', 'b.eq', 'b.ne', 'b.hs', 'b.lo',
               'b.hi', 'b.ls', 'b.mi', 'b.pl', 'b.vs', 'b.vc', 'b.gt', 'b.le',
               'b.ge', 'b.lt', 'b.al')
PERSONALITY_NUB = ("'IOClass' = NativeUfs; 'IOProviderClass' = IOPlatformDevice; "
                   "'IOProbeScore' = 1000:32;")
PERSONALITY_ROOT = ("'IOClass' = NativeUfs; 'IOMatchCategory' = NativeUfsRoot; "
                    "'IOProviderClass' = IOPlatformExpertDevice; 'IOProbeScore' = 500:32;")
OBSERVER = ('_enuma_pid1_begin', '_enuma_pid1_svc', '_enuma_pid1_exit')


def load(name, filename):
    path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(ok, message):
    if not ok:
        raise ValueError(message)


def condition_target(text):
    match = re.search(r'0x([0-9a-fA-F]+)', text)
    return int(match.group(1), 16) if match else None


def check_guard(link, name, body, limit_symbol, minimum, null_before):
    """Fail closed on a missing/shifted observation argument gate.

    Shape-only: requires at least `minimum` conditional branches *before the
    bounded call* to one shared forward refusal tail; the tail must end in ret
    without a call. `null_before` checks a null return register before the first
    gate (probe), otherwise the tail itself must start with the constant null.
    This does not prove CFG dominance or the success data-flow to the bounded
    call; those remain for human review of the hash-bound disassembly.
    """
    parsed = [link.instruction(line) for line in body]
    limit = None
    for address, text in parsed:
        if link.symbol_name(text).startswith(limit_symbol) and link.opcode(text) in ('bl', 'b'):
            limit = address
            break
    require(limit is not None, f'{name}: no direct call to {limit_symbol}')
    gates = []
    last = parsed[-1][0]
    for address, text in parsed:
        if link.opcode(text) not in CONDITIONAL:
            continue
        target = condition_target(text)
        if target is None or not (address < limit and address < target <= last):
            continue
        gates.append((address, target))
    require(gates, f'{name}: no forward conditional argument gate before {limit_symbol}')
    target = max({t for _, t in gates}, key=lambda t: sum(1 for _, x in gates if x == t))
    guards = [(a, t) for a, t in gates if t == target]
    require(len(guards) >= minimum,
            f'{name}: only {len(guards)} guard branches share the refusal tail; require {minimum}')
    tail = []
    for address, text in parsed:
        if address < target:
            continue
        tail.append((address, text))
        if link.opcode(text) == 'ret':
            break
    require(any(link.opcode(text) == 'ret' for _, text in tail),
            f'{name}: guard tail does not reach ret')
    require(not any(link.opcode(text) == 'bl' for _, text in tail),
            f'{name}: guard tail performs a call')
    if null_before:
        first = min(address for address, _ in guards)
        require(any(address < first and link.normalized(text) == 'mov x0, #0'
                    for address, text in parsed),
                f'{name}: no constant null x0 before the first guard branch')
    else:
        require(link.normalized(tail[0][1]) == 'mov w0, #0',
                f'{name}: guard tail does not begin with the constant false return')
    return {'guard_branches': len(guards), 'tail': target, 'bounded_call': limit,
            'tail_instructions': len(tail),
            'method': 'shape-only; gate-before-call to a shared refusal tail; '
                      'CFG dominance/success data-flow pending human review'}


def adt_properties(blob):
    result = {}

    def node(at, prefix):
        count, children = struct.unpack_from('<II', blob, at)
        at += 8
        own = {}
        for _ in range(count):
            key, size = struct.unpack_from('<32sI', blob, at)
            at += 36
            require(at + size <= len(blob), 'truncated ADT property')
            own[key.rstrip(b'\0').decode()] = blob[at:at + size]
            at += (size + 3) & ~3
        name = own.get('name', b'unknown\0').rstrip(b'\0').decode()
        path = prefix + '/' + name
        for key, value in own.items():
            result[path + ':' + key] = value
        for _ in range(children):
            at = node(at, path)
        return at

    require(node(0, '') == len(blob), 'trailing ADT bytes')
    return result


def contained(payload, member):
    return subprocess.check_output(['mtype', '-i', str(payload), member], timeout=120)


EXPECTED_ARGS = ('-v', 'serial=3', 'rd=md0-ramblock', 'pmgr=2',
                 'native-ufs-observe-reuse=1')


def select_boot_entry(config_text, expected=EXPECTED_ARGS, entry_id='xnu'):
    """Select the unique actual xnu entry and reject duplicate/alias/conflict args."""
    config = tomllib.loads(config_text)
    entries = config.get('entry', [])
    require(isinstance(entries, list), 'entry table is not a list')
    matching = [entry for entry in entries if entry.get('id') == entry_id]
    require(len(matching) == 1, f'expected exactly one {entry_id} entry, got {len(matching)}')
    args = matching[0].get('args', '')
    require(isinstance(args, str), f'entry args is not a string: {type(args)}')
    tokens = args.split()
    require(tokens == list(expected), f'entry args differ: {tokens}')
    names = {}
    for token in tokens:
        name, separator, value = token.partition('=')
        names.setdefault(name, []).append(value if separator else None)
    require(all(len(values) == 1 for values in names.values()), f'duplicate parameter: {names}')
    require('sheng-pmgr' not in names, 'sheng-pmgr alias forbidden')
    require(names.get('pmgr') == ['2'], f'pmgr token differs: {names.get("pmgr")}')
    require(names.get('native-ufs-observe-reuse') == ['1'],
            f'observation token differs: {names.get("native-ufs-observe-reuse")}')
    require('native-ufs-root' not in names and 'native-ufs-probe' not in names,
            f'conflicting legacy token: {names}')
    return {'entry_id': entry_id, 'entry_count': len(entries), 'args': tokens,
            'parameters': names}


def write_disassembly_evidence(evidence, prelink_sha, functions, names):
    evidence.mkdir(parents=True, exist_ok=True)
    dumped = {}
    for name in names:
        text = '\n'.join(functions[name]) + '\n'
        filename = re.sub(r'[^A-Za-z0-9_.-]+', '_', name) + '.asm'
        (evidence / filename).write_text(text)
        dumped[name] = {'file': filename, 'lines': len(functions[name]),
                        'sha256': hashlib.sha256(text.encode()).hexdigest()}
    payload = {'prelink_sha256': prelink_sha, 'functions': dumped,
               'scope': 'hash-bound disassembly for human CFG/dominance review'}
    (evidence / 'disassembly.json').write_text(json.dumps(payload, indent=2) + '\n')
    return payload


def read_segments(path):
    data = Path(path).read_bytes()
    require(data[:4] == b'\xcf\xfa\xed\xfe', 'prelink is not a thin 64-bit Mach-O')
    ncmds = struct.unpack_from('<I', data, 16)[0]
    offset = 32
    segments = []
    for _ in range(ncmds):
        command, size = struct.unpack_from('<II', data, offset)
        if command == 0x19:
            name = data[offset + 8:offset + 24].rstrip(b'\0').decode()
            vmaddr, vmsize, fileoff, filesize = struct.unpack_from('<QQQQ', data, offset + 24)
            segments.append({'name': name, 'va': vmaddr, 'size': vmsize,
                             'fileoff': fileoff, 'filesize': filesize})
        offset += size
    require(segments, 'prelink has no segments')
    return segments


def check_adt(payload, prelink):
    props = adt_properties(contained(payload, '::/EFI/UniXNU/Payloads/kernel.macho.adt'))
    require('/device-tree/arm-io/ufshc:compatible' in props, 'ADT has no arm-io/ufshc node')
    strings = [part for part in props['/device-tree/arm-io/ufshc:compatible'].split(b'\0') if part]
    require(strings == [b'qcom,sm8250-ufshc', b'qcom,ufshc'], strings)
    reg = props.get('/device-tree/arm-io/ufshc:reg', b'')
    require(len(reg) == 16, f'ufshc reg is not two 64-bit cells: {len(reg)} bytes')
    base, size = struct.unpack('<QQ', reg)
    require(size > 0 and base % 0x1000 == 0 and size % 0x1000 == 0, (hex(base), hex(size)))
    ranges = props.get('/device-tree/arm-io:ranges', b'')
    require(ranges, 'arm-io has no ranges property')
    compatible = props.get('/device-tree:compatible', b'')
    require(b'qcom,sm8250\0' in compatible, compatible)
    return {'ufshc_compatible': [part.decode() for part in strings],
            'ufshc_reg_base': base, 'ufshc_reg_size': size,
            'arm_io_ranges_bytes': len(ranges),
            'root_has_sm8250': True}


def check_personality(text):
    require(text.count("'IOClass' = NativeUfs;") == 2,
            'expected exactly two NativeUfs personalities')
    require(text.count(PERSONALITY_NUB) == 1, 'NativeUfs nub personality missing or duplicated')
    require(text.count(PERSONALITY_ROOT) == 1,
            'NativeUfsRoot/IOPlatformExpertDevice personality missing or duplicated')
    return {'NativeUfs_nub': True, 'NativeUfsRoot_expert': True,
            'source': 'KernelConfigTables strings in the audited prelink'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-json', type=Path, required=True)
    parser.add_argument('--payload', type=Path,
                        help='Retained candidate payload; ADT/personality binding is skipped when absent')
    parser.add_argument('--board', type=Path,
                        help='Device board.toml whose payload.kernel_args must equal the contained entry')
    parser.add_argument('--evidence', type=Path,
                        help='Directory for the hash-bound function disassembly used by human review')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    link = load('final_link', 'audit-enuma-ufs-final-link.py')
    record = json.loads(args.build_json.read_text())
    native, prelink = Path(record['native']), Path(record['prelink'])
    metadata = json.loads(Path(record['metadata']).read_text())
    prelink_bytes = prelink.read_bytes()

    require(link.sha(native) == record['native_sha256'], 'native hash differs from build record')
    require(link.sha(prelink) == record['prelink_sha256'], 'prelink hash differs from build record')
    require(metadata['candidate_sha256'] == record['prelink_sha256'],
            'kernel.json candidate hash differs from the prelink')
    require(metadata['candidate_bytes'] == len(prelink_bytes),
            'kernel.json candidate size differs from the prelink')
    require(Path(metadata['output']).resolve() == prelink.resolve(),
            'kernel.json output is not the audited prelink')
    require(metadata['sparse_index']['abi'] == 1, metadata['sparse_index'])
    segments = sorted(metadata['coalesced_segments'], key=lambda item: item['fileoff'])
    for segment in segments:
        require(segment['fileoff'] >= 0 and segment['filesize'] >= 0, segment)
        require(segment['fileoff'] + segment['filesize'] <= len(prelink_bytes), segment)
    for before, after in zip(segments, segments[1:]):
        require(before['fileoff'] + before['filesize'] <= after['fileoff'],
                f'coalesced extents overlap: {before} {after}')
    require(not metadata['images_modified'], 'kernel.json says images_modified')
    require(not metadata['source_inputs_modified'], 'kernel.json says source_inputs_modified')

    text = re.sub(r'[ ]+', ' ', prelink_bytes.decode('latin-1'))
    personality = check_personality(text)

    functions = link.disassembly(prelink)
    defined = link.nm_defined(prelink)
    probe_names = [name for name in functions if name.startswith('NativeUfs::probe(')]
    require(len(probe_names) == 1, probe_names)
    start_names = [name for name in functions if name.startswith('NativeUfs::start(')]
    require(len(start_names) == 1, start_names)
    probe = check_guard(link, probe_names[0], functions[probe_names[0]],
                        'ufsPlatformResources(', 4, True)
    start = check_guard(link, start_names[0], functions[start_names[0]],
                        'ufsReuseDiagnostic(', 3, False)
    diagnostic_names = [name for name in functions if name.startswith('ufsReuseDiagnostic(')]
    require(len(diagnostic_names) == 1, diagnostic_names)
    diagnostic_entry = link.entry_address(functions[diagnostic_names[0]])
    start_calls = link.check_calls_to(start_names[0], functions[start_names[0]],
                                      'ufsReuseDiagnostic(', diagnostic_entry, opcodes=('bl',))
    require(len(start_calls) == 1, 'start does not have exactly one diagnostic call')
    resources = link.call_sites(functions[start_names[0]], 'ufsPlatformResources(')
    require(resources and resources[0]['site'] < start_calls[0]['site'],
            'start calls the diagnostic before the resource check')

    pmgr = link.check_pmgr(functions, defined)
    image_segments = read_segments(prelink)
    observer = {name: defined.get(name) for name in OBSERVER}
    require(all(observer.values()), observer)
    require(len(set(observer.values())) == 3, observer)
    for name, address in observer.items():
        require(any(segment['size'] > 0 and
                    segment['va'] <= address < segment['va'] + segment['size']
                    for segment in image_segments), f'{name} is not inside a prelink segment')

    adt = None
    contained_kernel = None
    contained_entry = None
    if args.payload:
        adt = check_adt(args.payload, prelink)
        contained_kernel = link.sha_bytes(contained(args.payload, '::/EFI/UniXNU/Payloads/kernel.macho'))
        require(contained_kernel == record['prelink_sha256'],
                'contained kernel differs from the audited prelink')
        config_text = contained(args.payload, '::/EFI/UniXNU/unixnu.toml').decode(errors='replace')
        contained_entry = select_boot_entry(config_text)
        if args.board:
            board = tomllib.loads(args.board.read_text())
            board_args = board['payload']['kernel_args']
            require(list(board_args) == contained_entry['args'],
                    f'contained entry differs from board kernel_args: {board_args}')

    disassembly = None
    if args.evidence:
        names = [probe_names[0], start_names[0], diagnostic_names[0]]
        names += [name for name in functions if name.startswith('ufsReuseFinish(')]
        names += [key for key in functions if any(key.startswith(prefix + '(') for prefix in
                                                  ('NativeUfsBlock::configure',
                                                   'NativeUfsBlock::configureVerification',
                                                   'NativeUfsBlock::authenticatesVolume',
                                                   'NativeUfsBlock::signedVolumeUuid',
                                                   'NativeUfsBlock::start', 'NativeUfs::startRoot',
                                                   'NativeUfsBlock::doAsyncReadWrite'))]
        disassembly = write_disassembly_evidence(args.evidence, record['prelink_sha256'],
                                                 functions, names)

    flags = {key: metadata[key] for key in
             ('abi_qualified', 'loadable', 'runtime_qualified',
              'register_dataflow_qualified', 'instruction_relocation_complete')}
    reasons = [key for key, value in flags.items() if not value]
    if metadata['images_modified']:
        reasons.append('images_modified')
    pmgr_entry = metadata['module_entrypoints']['com.apple.driver.ApplePMGR']['start_va']
    require(any(segment['size'] > 0 and segment['va'] <= pmgr_entry < segment['va'] + segment['size']
                for segment in image_segments), 'PMGR module entrypoint is outside the image')

    result = {
        'validation': 'self-checked; static only',
        'candidate': {'native_sha256': record['native_sha256'],
                      'prelink_sha256': record['prelink_sha256'],
                      'metadata_sha256': link.sha(Path(record['metadata'])),
                      'metadata_candidate_sha256': metadata['candidate_sha256'],
                      'candidate_bytes': metadata['candidate_bytes']},
        'metadata_binding': {'hash': True, 'size': True, 'output': True, 'sparse_abi': 1,
                             'coalesced_segments': len(segments),
                             'images_modified': metadata['images_modified'],
                             'source_inputs_modified': metadata['source_inputs_modified']},
        'qualification_flags': flags,
        'abi_qualified': all(flags.values()),
        'admission_qualified': all(flags.values()),
        'admission_reasons_unqualified': reasons,
        'personality': personality,
        'adt': adt,
        'personality_adt_probe_chain': {
            'static_preconditions_met': bool(adt),
            'meaning': 'the prelink embeds the nub and NativeUfsRoot/IOPlatformExpertDevice '
                       'personalities, the retained payload ADT exposes the sm8250 ufshc node and '
                       'arm-io ranges, and start checks ufsPlatformResources before its single '
                       'diagnostic call',
            'runtime_unverified': True,
        },
        'probe_start': {'probe': probe, 'start': start,
                        'start_resource_call': resources[0]['site'],
                        'start_diagnostic_call': start_calls[0]['site']},
        'pmgr_observer': {'pmgr': pmgr, 'observer_symbols': {k: hex(v) for k, v in observer.items()},
                          'observer_image_resident': True, 'pmgr_entrypoint': pmgr_entry,
                          'reused_23r_conclusions': False},
        'contained_package': {'contained_kernel_sha256': contained_kernel,
                              'boot_entry': contained_entry},
        'disassembly_evidence': disassembly,
        'not_closed': ['kernel.json ABI/load/runtime/register/relocation flags remain false',
                       'no runtime/load test; hardware diagnostic behaviour is unverified',
                       'CFG dominance and success data-flow to the diagnostic call are not proven '
                       'by the shape check; hash-bound disassembly is provided for human review',
                       'static checks only; no device authorization'] + reasons,
        'device_authorized': False, 'release_allowed': False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'validation': 'self-checked', 'admission_qualified': False,
                      'unqualified': reasons, 'adt_checked': adt is not None,
                      'observer': result['pmgr_observer']['observer_symbols']}, indent=2))


if __name__ == '__main__':
    sys.exit(main())
