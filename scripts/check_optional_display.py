"""Compile the actual patched BSD probe with legacy display disabled/enabled."""
import argparse
import hashlib
import json
from pathlib import Path
from check_enuma_drivers import run
from upstream_source import qualify

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unixnu', type=Path, required=True)
    args = parser.parse_args()
    qualification = qualify(args.unixnu)
    patch = args.unixnu / 'patches/xnu/offline-component-load-probes.patch'
    # Extract exactly the added C function, retaining its real preprocessor gates.
    added = '\n'.join(line[1:] for line in patch.read_text().splitlines()
                      if line.startswith('+') and not line.startswith('+++'))
    begin = added.index('static void\nnative_mobile_graphics_load_probe(void)')
    end = added.index('\n}\n#endif', begin) + 2
    out = ROOT / 'out/optional-display'; out.mkdir(parents=True, exist_ok=True)
    source = out / 'probe.c'
    source.write_text('''typedef unsigned long size_t;
extern int PE_parse_boot_argn(const char *, void *, int);
extern int OSKextLoadKextWithIdentifier(const char *);
extern void native_mobile_graphics_probe_checkpoint(void);
int native_mobile_graphics_load_status;
''' + added[begin:end] + '\nvoid exercise(void) { native_mobile_graphics_load_probe(); }\n')
    checks = []
    for value in (0, 1):
        obj = out / ('probe-' + str(value) + '.o')
        checks.append(run(['clang', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                           '-DXNU_NATIVE_LEGACY_DISPLAY=' + str(value), '-c', source, '-o', obj]))
        symbols = run(['nm', '-u', obj]); checks.append(symbols)
        if ('native_legacy_display_probe' in symbols['stdout']) != bool(value):
            raise ValueError('Optional legacy reference is not gated at compile time')
    (ROOT / 'reports/enuma-optional-display-check.json').write_text(json.dumps({
        'scope': 'actual probe compiled on host; final XNU link requires macOS CI',
        'qualification': qualification, 'checks': checks,
        'extracted_source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()
    }, indent=2) + '\n')
    print('PASS: no legacy symbol when disabled; real legacy reference retained when enabled')


if __name__ == '__main__': main()
