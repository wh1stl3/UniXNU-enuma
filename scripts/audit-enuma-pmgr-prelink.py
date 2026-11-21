#!/usr/bin/env python3
"""Read-only final-image PMGR link checks; lifecycle review remains mandatory."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tomllib

BASE_REVISION = '693f5d9cae8a408dd18b39f3f9fdc4228c934241'
PRELINK_LF_SHA256 = '5bd80b8c63deec29b747c28253e02308a56d5f8cdb37c9d315e7c8af7012d017'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_args(arguments):
    tokens = arguments.split() if isinstance(arguments, str) else list(arguments)
    require(not any(t.lstrip('-').split('=')[0] == 'sheng-pmgr' for t in tokens), 'sheng-pmgr alias forbidden')
    pmgr = [t for t in tokens if t.lstrip('-').split('=')[0] == 'pmgr']
    require(pmgr == ['pmgr=2'], 'Require exactly one literal pmgr=2')


def load_native_prelink(base):
    """Load the exact pinned base helper, never cwd/PYTHONPATH/cache fallback."""
    require(base.is_absolute(), 'Explicit base path must be absolute')
    helper = base / 'kits/XnuPrelink/native_prelink.py'
    try:
        raw = helper.read_bytes()
    except PermissionError as error:
        raise ValueError(f'Cannot read explicit pinned base helper: {helper}; run the checker as an account '
                         'with access to the manifest paths (WSL -u root for this local candidate); '
                         'PYTHONPATH cannot repair filesystem permissions') from error
    except FileNotFoundError as error:
        raise ValueError(f'Explicit pinned base helper missing: {helper}; no import fallback permitted') from error
    require(hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest() == PRELINK_LF_SHA256,
            'Pinned native_prelink hash differs')
    revision = subprocess.check_output(['git', '-C', str(base), 'rev-parse', 'HEAD'], text=True).strip()
    require(revision == BASE_REVISION, 'Explicit base revision differs')
    spec = importlib.util.spec_from_file_location('_enuma_pinned_native_prelink', helper)
    require(spec is not None and spec.loader is not None, 'Cannot create explicit helper loader')
    module = importlib.util.module_from_spec(spec)
    # Execute the verified bytes themselves; no re-read/cache shadowing and no
    # __pycache__ write into the read-only base dependency.
    exec(compile(raw, str(helper), 'exec'), module.__dict__)
    return module


def audit(args):
    helper = load_native_prelink(args.base)
    macho, backed_offset = helper.macho, helper.backed_offset
    raw = args.prelink.read_bytes()
    info = macho(raw)
    native_raw = args.native.read_bytes()
    native_info = macho(native_raw)
    def defined_symbols(blob, image):
        command = next(at for cmd, at, _ in image['commands'] if cmd == 2)
        offset, count, strings, size = struct.unpack_from('<4I', blob, command + 8)
        result = {}
        for index in range(count):
            string, kind, _, _, address = struct.unpack_from('<IBBHQ', blob, offset + index * 16)
            if kind & 0xe0 or not kind & 0x0e:
                continue
            require(string < size, 'Symbol string outside table')
            name = blob[strings + string:blob.index(b'\0', strings + string)].decode()
            result[name] = address
        return result
    names = defined_symbols(raw, info)
    native_names = defined_symbols(native_raw, native_info)
    report = json.loads((args.tree / 'build/sheng-platform-power/build-report.json').read_text())
    require(sha(args.tree / 'kits/enuma/ShengPlatformPower.cpp') == report['source_sha256'], 'Source/archive report differs')
    require(sha(args.tree / 'build/sheng-platform-power/libShengPlatformPower.a') == report['archive_sha256'], 'Archive hash differs')
    plan = json.loads(args.manifest.read_text())
    require(plan['native_sha256'] == sha(args.native), 'Manifest/native mismatch')
    require('com.apple.driver.AppleT8011PMGR' not in plan['components'], 'Hardware driver included')

    def read(va, size):
        return raw[backed_offset(info['segments'], va, size, len(raw)):][:size]

    def pointer(va):
        return struct.unpack('<Q', read(va, 8))[0]

    for module in ('com.apple.driver.ApplePMGR', 'com.apple.driver.AppleMobileFileIntegrity'):
        extent, = [e for e in plan['extents'] if e['module'] == module and e['segment'] == '__TEXT_EXEC']
        require(hashlib.sha256(read(extent['va'], extent['size'])).hexdigest() == plan['original_executable_sha256'][module],
                f'Original executable modified: {module}')
    bindings = {name: int(va, 16) for name, va in report['bindings'].items()}
    for name, va in bindings.items():
        require(names.get(name) == va and native_names.get(name) == va, f'Final absolute binding differs: {name}')
    for name in report['all_undefined_imports']:
        require(name in names and name in native_names, f'Final import missing: {name}')
    table = names['__ZTV18ShengPlatformPower'] + 16
    entries = report['virtual_entries']
    require(len(entries) == 340, 'Expected exactly 340 audited slots')
    for slot, name in enumerate(entries):
        require(pointer(table + slot * 8) == names[name], f'Final vtable slot {slot} differs')
        if slot not in (0, 1, 7) and slot < 168:
            require(pointer(table + slot * 8) == pointer(names['__ZTV6IOPMGR'] + 16 + slot * 8),
                    f'Final native low slot {slot} differs')
    meta = names['__ZN18ShengPlatformPower10gMetaClassE']
    meta_segment, = [s for s in info['segments'] if s['va'] <= meta < s['va'] + s['size']]
    require(meta_segment['initprot'] & 2, 'Late metaclass is not writable')
    initializer = names['__GLOBAL__sub_I_ShengPlatformPower.cpp']
    run = names['_sheng_pmgr_run']
    for address in (initializer, run):
        code_segment, = [s for s in info['segments'] if s['va'] <= address < s['va'] + s['size']]
        code_section, = [s for s in code_segment['sections'] if s['va'] <= address < s['va'] + s['size']]
        require(code_segment['initprot'] & 4 and code_section['name'] == '__text',
                'Late initializer and run code must remain executable resident text')
    calls = {run: [], initializer: []}
    for segment in native_info['segments']:
        for section in segment['sections']:
            if section['name'] == '__mod_init_func':
                for at in range(0, section['size'], 8):
                    value = struct.unpack_from('<Q', native_raw, section['fileoff'] + at)[0]
                    require(value != initializer, 'Automatic and manual initialization both remain')
            if section['name'] != '__text':
                continue
            for at in range(0, section['size'], 4):
                word = struct.unpack_from('<I', native_raw, section['fileoff'] + at)[0]
                if word & 0xfc000000 != 0x94000000:
                    continue
                immediate = word & 0x3ffffff
                if immediate & 0x2000000:
                    immediate -= 0x4000000
                pc = section['va'] + at
                target = pc + immediate * 4
                if target in calls:
                    calls[target].append(pc)
    require(len(calls[run]) == len(calls[initializer]) == 1, 'Require exactly one startup call and one manual initializer call')
    site = calls[run][0]
    previous = struct.unpack('<I', read(site - 4, 4))[0]
    immediate = previous & 0x3ffffff
    if immediate & 0x2000000:
        immediate -= 0x4000000
    require(previous & 0xfc000000 == 0x94000000 and site - 4 + immediate * 4 == names['_bsd_bufferinit'],
            'Publisher must be called immediately after bsd_bufferinit')
    require(names['_bsd_init'] <= site < names['_bsd_init'] + 0x10000, 'Publisher call outside bsd_init')
    observer = {n: hex(va) for n, va in names.items() if n.startswith('_enuma_pid1_')}
    require(observer, 'Existing observer missing')
    board = tomllib.loads(args.board.read_text())
    check_args(board['payload']['kernel_args'])
    require('build-enuma-platform-power.py --inputs build/sheng-platform-power/inputs.json' in board['kernel']['archives'],
            'Board does not build the audited archive')
    contained_args = None
    if args.payload:
        def contained(name):
            return subprocess.check_output(['mtype', '-i', str(args.payload), '::/EFI/UniXNU/' + name], timeout=60)
        require(hashlib.sha256(contained('Payloads/kernel.macho')).hexdigest() == sha(args.prelink),
                'Contained kernel differs from audited prelink')
        config = tomllib.loads(contained('unixnu.toml').decode())
        entry, = [e for e in config['entry'] if e['id'] == 'xnu']
        contained_args = entry['args']
        check_args(contained_args)
        require(contained_args.split() == board['payload']['kernel_args'], 'Contained arguments differ from board')
    require(not args.require_package or args.payload is not None, 'Actual contained package required')
    return {'status': 'self-checked', 'native_sha256': sha(args.native), 'prelink_sha256': sha(args.prelink),
            'archive_sha256': report['archive_sha256'], 'vtable_slots_checked': 340,
            'imports_checked': len(report['all_undefined_imports']), 'hook_call': hex(site),
            'run': hex(run), 'manual_initializer_call': hex(calls[initializer][0]),
            'initializer': hex(initializer), 'metaclass': hex(meta), 'metaclass_segment': meta_segment['name'],
            'observer_symbols_relocated': observer, 'contained_args': contained_args,
            'package_checked': args.payload is not None, 'ownership_closure_qualified': False, 'release_allowed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('base', 'tree', 'native', 'prelink', 'manifest', 'board', 'output'):
        parser.add_argument('--' + name, required=True, type=Path)
    parser.add_argument('--payload', type=Path)
    parser.add_argument('--require-package', action='store_true')
    args = parser.parse_args()
    result = audit(args)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
