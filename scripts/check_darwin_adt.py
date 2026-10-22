"""Run the pinned DarwinBoot ADT parser on host memory buffers; emit no ADT/image."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from check_enuma_drivers import run

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unixnu', type=Path, required=True)
    args = parser.parse_args()
    if sys.byteorder != 'little':
        raise ValueError('the host unaligned-read adapters require little endian')
    plan = json.loads((ROOT / 'reports/enuma-adt-plan.json').read_text())['loader_memory']
    if plan['request_bytes'] != 0x20000000 or plan['value_hex'] != '0000002000000000':
        raise ValueError('plan differs from approved R-001')
    if digest(ROOT / 'board.toml') != plan['board_input']['sha256']:
        raise ValueError('stale ADT plan: board changed')
    lock = json.loads((ROOT / 'config/porting-sources.lock.json').read_text())
    relative = 'drivers/DarwinBoot/DarwinBootPkg/Driver/'
    paths = [relative + 'DarwinBoot.c', relative + 'WindowSize.h', 'drivers/DarwinBoot/Test/window-size.c']
    sources = {}
    for name in paths:
        actual = digest(args.unixnu / name)
        if actual != lock['unixnu_interface_sha256'][name]:
            raise ValueError(f'source pin mismatch: {name}')
        sources[name] = actual
    original = (args.unixnu / paths[0]).read_text()
    start = original.index('STATIC\nBOOLEAN\nAdtNode (')
    end = original.index('STATIC\nBOOLEAN\nValidTrustCaches (', start)
    fragment = original[start:end]
    out = ROOT / 'out/darwin-adt-contract'; out.mkdir(parents=True, exist_ok=True)
    include = out / 'AdtNode.inc'; include.write_text(fragment)
    flags = ['clang', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined',
             '-fno-omit-frame-pointer', '-fno-pie', '-no-pie', '-I' + str(args.unixnu / relative)]
    records = [run([*flags, '-DDARWIN_ADT_SOURCE="' + str(include) + '"',
                    ROOT / 'tests/darwin_adt_contract.c', '-o', out / 'adt-test'])]
    records.append(run([out / 'adt-test', hex(plan['request_bytes'])]))
    records.append(run([*flags, args.unixnu / paths[2], '-o', out / 'window-size-test']))
    records.append(run([out / 'window-size-test']))
    run_start = original.index('STATIC\nUINT64\nRunEnd (')
    run_end = original.index('// Large diagnostic text', run_start)
    alloc_start = original.index('STATIC\nEFI_STATUS\nAllocateWindow (')
    alloc_end = original.index('STATIC\nEFI_STATUS\nEFIAPI\nBoot (', alloc_start)
    window_include = out / 'AllocateWindow.inc'
    window_include.write_text(original[run_start:run_end] + original[alloc_start:alloc_end])
    records.append(run([*flags, '-fshort-wchar', '-DDARWIN_WINDOW_SOURCE="' + str(window_include) + '"',
                        ROOT / 'tests/darwin_window_contract.c', '-o', out / 'allocation-test']))
    records.append(run([out / 'allocation-test']))
    report = {'scope': 'real source function with host adapters and in-memory synthetic inputs; no UEFI allocation or hardware',
              'request_bytes': plan['request_bytes'], 'property_path': '/chosen/darwinboot-memory-size',
              'property_value_hex': plan['value_hex'], 'sources': sources,
              'extracted_function_sha256': digest(include), 'harness_sha256': digest(ROOT / 'tests/darwin_adt_contract.c'),
              'allocation_functions_sha256': digest(window_include),
              'allocation_harness_sha256': digest(ROOT / 'tests/darwin_window_contract.c'),
              'checks': records, 'image_generated': False, 'runtime_allocation_observed': False}
    (ROOT / 'reports/darwin-adt-contract.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: pinned DarwinBoot ADT and window-size host checks; no image emitted')


if __name__ == '__main__':
    main()
