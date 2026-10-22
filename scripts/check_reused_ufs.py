"""Compile and execute pinned upstream pure UFS helpers on a Linux host, no MMIO."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    pins = json.loads((ROOT / 'config/sources.lock.json').read_text())
    commit = subprocess.check_output(['git', '-c', f'safe.directory={source}', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    if commit != pins['sources']['UniXNU']['commit']:
        raise ValueError('UniXNU source revision mismatch')
    out = ROOT / 'out/ufs-host'
    out.mkdir(parents=True, exist_ok=True)
    records = []
    # These tests use memory-backed fake ports, never open a physical device.
    for name in ('TransferPoll', 'RootDiagnostics', 'RootPublication', 'SmmuTakeover'):
        cpp = source / f'drivers/NativeUfs/tests/{name}.cpp'
        header = cpp.parent.parent / f'{name}.h'
        command = ['clang++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined', '-fno-pie', '-no-pie',
                   '-fno-omit-frame-pointer', str(cpp), '-o', str(out / name)]
        compile_run = subprocess.run(command, capture_output=True, text=True, timeout=60)
        if compile_run.returncode:
            raise RuntimeError(compile_run.stderr)
        run = subprocess.run([str(out / name)], capture_output=True, text=True, timeout=30)
        if run.returncode:
            failure = {'name': name, 'exit_code': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr}
            (out / 'failure.json').write_text(json.dumps(failure, indent=2) + '\n')
            raise RuntimeError(json.dumps(failure))
        records.append({'name': name, 'source_sha256': hashlib.sha256(cpp.read_bytes()).hexdigest(),
                        'header_sha256': hashlib.sha256(header.read_bytes()).hexdigest(),
                        'compile_argv': command, 'compile_stderr': compile_run.stderr,
                        'exit_code': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr})
    report = {'scope': 'host ASan/UBSan execution of pure upstream helper tests; no QEMU, MMIO, real UFS or enuma boot',
              'source_commit': commit, 'compiler': subprocess.check_output(['clang++', '--version'], text=True), 'tests': records}
    (ROOT / 'reports/ufs-host-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: four upstream UFS helper suites with ASan/UBSan (host only)')


if __name__ == '__main__':
    main()
