#!/usr/bin/env python3
"""Offline final-link gate for the selected observation-only 24r kernel.

Reads an already completed native/prelink build record and its linker map. It
does not build or link anything. Checks:

* the native/prelink hashes match the build record and neither final image has
  any undefined symbol (explicit zero-undefined policy, no allowlist);
* every archive that contributed an object to the final link has no duplicate
  strong definitions, and the six native_ufs_store_* symbols come only from
  EnumaRamBlockStore.o (native, prelink and map agree);
* the prelinked image's NativeUfs::start reaches the observation diagnostic
  (one call, resolved to the diagnostic entry) and the diagnostic reaches
  ufsReuseFinish, whose body ends in an unbounded wfe loop whose backedge
  targets that same wfe;
* the ordinary configure/configureVerification/authenticatesVolume/
  signedVolumeUuid/start/startRoot entry points are exactly a constant false
  return with no call, store or other side effect, and doAsyncReadWrite is
  exactly kIOReturnNotReady without invoking a completion;
* the single `bl` to _sheng_pmgr_run is issued by _bsd_init and resolves to the
  defined _sheng_pmgr_run symbol.

The check is static only; no device, load, or runtime claim.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

OLD_MISSING = {'_boot_progress_poll', '_verified_root_key', '_verified_root_policies',
               '_verified_root_policy_count', '_vr_open', '_vr_verify_block', '_vr_xnu_crypto'}
REFUSALS = ('NativeUfsBlock::configure', 'NativeUfsBlock::configureVerification',
            'NativeUfsBlock::authenticatesVolume', 'NativeUfsBlock::signedVolumeUuid',
            'NativeUfsBlock::start', 'NativeUfs::startRoot')
REFUSAL_BODY = ('mov w0, #0', 'ret')
ASYNC_BODY = ('mov w0, #728', 'movk w0, #57344, lsl #16', 'ret')
UNDEFINED_POLICY = ('final native and prelink images must define every symbol they use; '
                    'this gate has an empty undefined allowlist')
INSTRUCTION = re.compile(r'^\s*([0-9a-fA-F]+):\s+((?:[0-9a-f]{2} ){3}[0-9a-f]{2})\s+(.+)$')
NM_DEFINED = re.compile(r'^([0-9a-fA-F]+)\s+([A-Za-z])\s+(\S+)$')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def load(name, filename):
    path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def nm_undefined(image):
    out = subprocess.check_output(['llvm-nm', '-u', str(image)], text=True)
    return {line.split()[-1] for line in out.splitlines() if line.split()}


def nm_defined(image):
    out = subprocess.check_output(['llvm-nm', '-g', '--defined-only', str(image)], text=True)
    result = {}
    for line in out.splitlines():
        match = NM_DEFINED.match(line.strip())
        if match:
            result[match.group(3)] = int(match.group(1), 16)
    return result


def disassembly(image):
    out = subprocess.check_output(['llvm-objdump', '--disassemble', '--demangle', str(image)],
                                  text=True)
    functions = {}
    current = None
    for line in out.splitlines():
        match = re.match(r'^[0-9a-fA-F]+ <(.+)>:$', line)
        if match:
            current = match.group(1)
            functions[current] = []
        elif current is not None and re.match(r'^\s*[0-9a-fA-F]+:', line):
            functions[current].append(line.strip())
    return functions


def instruction(line):
    match = INSTRUCTION.match(line)
    require(match is not None, f'unparsed instruction line: {line!r}')
    return int(match.group(1), 16), match.group(3).strip()


def normalized(text):
    return ' '.join(text.split())


def opcode(text):
    parts = text.split(None, 1)
    return parts[0] if parts else ''


def branch_target(text):
    parts = text.split(None, 1)
    if len(parts) != 2:
        return None
    if not (parts[0] in ('b', 'bl') or parts[0].startswith('b.')):
        return None
    match = re.match(r'0x([0-9a-fA-F]+)', parts[1])
    return int(match.group(1), 16) if match else None


def entry_address(body):
    require(body, 'empty function body')
    return instruction(body[0])[0]


def check_constant_body(name, body, expected):
    parsed = [instruction(line) for line in body]
    actual = [normalized(text) for _, text in parsed]
    require(actual == list(expected),
            f'{name}: expected the exact body {list(expected)} with no call or side effect, '
            f'got {actual}')
    return {'instructions': actual}


def check_wfe_terminal(name, body):
    parsed = [instruction(line) for line in body]
    require(len(parsed) >= 2, f'{name}: body too short for a wfe terminal')
    wfe_address, wfe_text = parsed[-2]
    require(normalized(wfe_text) == 'wfe', f'{name}: second-to-last instruction is not wfe')
    branch_address, branch_text = parsed[-1]
    require(opcode(branch_text) == 'b', f'{name}: terminal wfe is not followed by an unconditional b')
    require(branch_target(branch_text) == wfe_address,
            f'{name}: terminal backedge does not target the wfe it follows')
    require(not any(normalized(text) == 'ret' for _, text in parsed),
            f'{name}: a return remains in the terminal function')
    return {'wfe': wfe_address, 'backedge': branch_address, 'target': wfe_address}


def symbol_name(text):
    match = re.search(r'<(.+)>$', text)
    return match.group(1) if match else ''


def call_sites(body, fragment, exact=False):
    sites = []
    for line in body:
        address, text = instruction(line)
        name = symbol_name(text)
        matched = name == fragment if exact else name.startswith(fragment)
        if not matched:
            continue
        target = branch_target(text)
        if target is None:
            continue
        sites.append({'site': address, 'target': target, 'opcode': opcode(text), 'text': text})
    return sites


def check_calls_to(name, body, fragment, target, opcodes=('bl', 'b')):
    sites = call_sites(body, fragment)
    require(sites, f'{name}: no direct branch to {fragment}')
    for site in sites:
        require(site['opcode'] in opcodes,
                f'{name}: branch to {fragment} uses {site["opcode"]}')
        require(site['target'] == target,
                f'{name}: branch to {fragment} at {site["site"]:#x} resolves to '
                f'{site["target"]:#x}, not the function entry {target:#x}')
    return sites


def check_pmgr(functions, defined):
    calls = []
    for caller, body in functions.items():
        for site in call_sites(body, '_sheng_pmgr_run', exact=True):
            calls.append(dict(site, caller=caller))
    require(len(calls) == 1, f'expected exactly one bl to _sheng_pmgr_run, got {calls}')
    call = calls[0]
    require(call['opcode'] == 'bl', f'PMGR hook is not a bl: {call["text"]}')
    require(call['caller'] == '_bsd_init',
            f'PMGR hook caller is {call["caller"]!r}, not _bsd_init')
    require('_sheng_pmgr_run' in defined, '_sheng_pmgr_run is not a defined prelink symbol')
    require(call['target'] == defined['_sheng_pmgr_run'],
            f'PMGR hook target {call["target"]:#x} differs from the defined '
            f'_sheng_pmgr_run {defined["_sheng_pmgr_run"]:#x}')
    return {'caller': call['caller'], 'call_site': call['text'],
            'target': call['target'], 'target_symbol_defined': True}


def check_undefined(undefined):
    require(not undefined['native'], f'native undefined symbols violate the policy '
            f'({UNDEFINED_POLICY}): {undefined["native"]}')
    require(not undefined['prelink'], f'prelink undefined symbols violate the policy '
            f'({UNDEFINED_POLICY}): {undefined["prelink"]}')
    return undefined


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-json', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    record = json.loads(args.build_json.read_text())
    native, prelink = Path(record['native']), Path(record['prelink'])
    link_map = Path(record['native_link_map'])
    symbols = load('store_symbols', 'check-enuma-ufs-store-symbols.py')

    require(sha(native) == record['native_sha256'], 'native hash differs from the build record')
    require(sha(prelink) == record['prelink_sha256'], 'prelink hash differs from the build record')

    undefined = {'native': sorted(nm_undefined(native)), 'prelink': sorted(nm_undefined(prelink))}
    leftover = sorted(OLD_MISSING & set(undefined['native']) | OLD_MISSING & set(undefined['prelink']))
    assert not leftover, leftover
    check_undefined(undefined)
    defined = nm_defined(prelink)

    text = link_map.read_text(errors='replace')
    owners = {}
    for index, name in re.findall(r'^\[\s*(\d+)\]\s+(.+)$', text, re.M):
        owners[index] = name
    archives = []
    for name in owners.values():
        match = re.match(r'(.+\.a)\(', name)
        if match and match.group(1) not in archives:
            archives.append(match.group(1))
    assert archives, 'no archive members in link map'
    report = symbols.audit([Path(p) for p in archives], native, prelink, link_map)
    report.update(build=record, undefined=undefined, leftover_old_missing=leftover,
                  link_archives=archives, undefined_policy=UNDEFINED_POLICY)

    functions = disassembly(prelink)
    start_name = 'NativeUfs::start(IOService*)'
    start = functions.get(start_name)
    require(start is not None, [name for name in functions if 'NativeUfs::start' in name])
    diagnostic_names = [name for name in functions if name.startswith('ufsReuseDiagnostic(')]
    require(len(diagnostic_names) == 1, diagnostic_names)
    diagnostic = functions[diagnostic_names[0]]
    finish_names = [name for name in functions if name.startswith('ufsReuseFinish(')]
    require(len(finish_names) == 1, finish_names)
    finish = functions[finish_names[0]]

    diagnostic_entry = entry_address(diagnostic)
    finish_entry = entry_address(finish)
    start_calls = check_calls_to(start_name, start, 'ufsReuseDiagnostic(',
                                 diagnostic_entry, opcodes=('bl',))
    require(len(start_calls) == 1,
            f'NativeUfs::start has {len(start_calls)} calls to the diagnostic')
    diagnostic_calls = check_calls_to(diagnostic_names[0], diagnostic, 'ufsReuseFinish(',
                                      finish_entry)
    require(len(diagnostic_calls) >= 1, 'diagnostic has no call to ufsReuseFinish')
    wfe_terminal = check_wfe_terminal(finish_names[0], finish)

    refusal_bodies = {}
    for name in REFUSALS:
        body = functions.get(name + '(IOService*)') or functions.get(name + '()')
        if body is None:
            candidates = [key for key in functions if key.startswith(name + '(')]
            require(len(candidates) == 1, f'{name}: ambiguous function {candidates}')
            body = functions[candidates[0]]
        refusal_bodies[name] = check_constant_body(name, body, REFUSAL_BODY)

    async_name = [key for key in functions if key.startswith('NativeUfsBlock::doAsyncReadWrite(')]
    require(len(async_name) == 1, async_name)
    async_body = check_constant_body(async_name[0], functions[async_name[0]], ASYNC_BODY)

    pmgr = check_pmgr(functions, defined)

    report['final_call_targets'] = {
        'NativeUfs::start_calls_ufsReuseDiagnostic': True,
        'NativeUfs::start_call_site': start_calls[0]['site'],
        'ufsReuseDiagnostic_entry': diagnostic_entry,
        'diagnostic_calls_ufsReuseFinish': True,
        'diagnostic_call_sites': [site['site'] for site in diagnostic_calls],
        'ufsReuseFinish_entry': finish_entry,
        'ufsReuseFinish_has_wfe_terminal': True,
        'refusing_entry_points': refusal_bodies,
        'doAsyncReadWrite_returns_kIOReturnNotReady': True,
    }
    report['refusal_exact_sequences'] = refusal_bodies
    report['wfe_terminal'] = wfe_terminal
    report['pmgr_hook'] = pmgr
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'validation': 'self-checked', 'archives': len(archives),
                      'leftover_old_missing': leftover,
                      'undefined_policy': 'zero undefined symbols',
                      'store_owners': sorted(set(report['store_owners']))}, indent=2))


if __name__ == '__main__':
    sys.exit(main())
