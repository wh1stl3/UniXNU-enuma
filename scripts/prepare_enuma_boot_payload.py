"""Reuse UniXNU's checked BootShim compiler with the built enuma FD; no device action."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unixnu', type=Path, required=True)
    args = parser.parse_args()
    # Compatibility for the host's Python 3.10; do not alter the pinned upstream.
    if sys.version_info < (3, 11):
        import tomli
        sys.modules['tomllib'] = tomli
    sys.path.insert(0, str(args.unixnu / 'scripts'))
    from unixnu.bootimg import compile_shim
    build = json.loads((ROOT / 'reports/enuma-firmware-build.json').read_text())
    audit = json.loads((ROOT / 'reports/enuma-fd-audit.json').read_text())
    fd = (ROOT / build['fd']).read_bytes()
    if not build['complete'] or hashlib.sha256(fd).hexdigest() != audit['fd_sha256']:
        raise ValueError('FD build and audit must agree')
    out = ROOT / 'out/boot-candidate'; out.mkdir(parents=True, exist_ok=True)
    shim = compile_shim(ROOT / 'out/firmware-build/uefi', 0x9fc00000, 0x300000, True, out)
    (out / 'enuma-uefi.raw').write_bytes(shim + fd)
    (out / 'empty-ramdisk').write_bytes(b'')
    report = {'scope': 'BootShim assembly and header checks; no execution', 'shim_bytes': len(shim),
              'fd_sha256': audit['fd_sha256'], 'raw_sha256': hashlib.sha256(shim + fd).hexdigest(),
              'compiler_source_sha256': hashlib.sha256((args.unixnu / 'scripts/unixnu/bootimg.py').read_bytes()).hexdigest(),
              'shim_source_sha256': hashlib.sha256((ROOT / 'out/firmware-build/uefi/BootShim/BootShim.S').read_bytes()).hexdigest()}
    (ROOT / 'reports/enuma-boot-payload.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: {len(shim)}-byte upstream BootShim plus audited 3 MiB FD')


if __name__ == '__main__': main()
