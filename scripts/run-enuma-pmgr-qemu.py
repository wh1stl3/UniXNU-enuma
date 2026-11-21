#!/usr/bin/env python3
"""Isolated orchestration of the unchanged base real-kernel PMGR harness."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

FROZEN = 'bf9f7e12bb05dc3a09f1a732fbcdb83d7729f6378f65ea7fbe77646514edc072'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('base', 'kernel', 'manifest', 'loaders', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--firmware', type=Path, help='Existing UEFI FD forwarded to unchanged gdb-stop CLI')
    args = parser.parse_args()
    for name, path in vars(args).items():
        if isinstance(path, Path):
            setattr(args, name, path.resolve())
    if sha(args.kernel) != FROZEN:
        parser.error('Frozen prelink hash differs')
    # No reuse or overwrite of previous observations.
    args.output.mkdir(parents=True, exist_ok=False)
    view = args.output / 'view'
    scripts = view / 'scripts'
    scripts.mkdir(parents=True)
    for source in (args.base / 'scripts').iterdir():
        destination = scripts / source.name
        if source.name == 'qemu-entry' and args.firmware:
            destination.mkdir()
            for entry in source.iterdir():
                if entry.name == 'gdb-stop.py':
                    # The parent probe lacks a firmware option. Forward only the
                    # existing child CLI, preserving its code and QEMU behavior.
                    (destination / entry.name).write_text(
                        'import os, sys\n'
                        f'os.execv(sys.executable, [sys.executable, {str(entry)!r}, *sys.argv[1:], "--firmware", {str(args.firmware)!r}])\n')
                else:
                    (destination / entry.name).symlink_to(entry, target_is_directory=entry.is_dir())
        elif source.name == 'probe-darwinboot-xnu.py':
            shutil.copyfile(source, destination)  # unchanged bytes, isolated ROOT
        else:
            destination.symlink_to(source, target_is_directory=source.is_dir())
    (view / 'kits').symlink_to(args.base / 'kits', target_is_directory=True)
    darwin = view / 'build/DarwinBoot/DEBUG_CLANGPDB/AARCH64'
    darwin.mkdir(parents=True)
    (darwin / 'DarwinBoot.efi').symlink_to(args.loaders / 'DarwinBoot.efi')
    loader = view / 'package/Build/Out/AARCH64-DEBUG'
    loader.mkdir(parents=True)
    (loader / 'UniXNU.efi').symlink_to(args.loaders / 'UniXNU.efi')
    env = dict(os.environ)
    env['PATH'] = str(args.base / 'scripts/linux') + ':/home/wh1stl3/.local/bin:/usr/bin:/bin'
    env['XNU_TOOLCHAIN_BIN'] = '/opt/unixnu-linux/CommandLineTools/usr/bin'
    env['PYTHONPATH'] = str(args.base / 'scripts')
    record = {'status': 'self-checked', 'kernel': str(args.kernel), 'kernel_sha256': sha(args.kernel),
              'manifest_sha256': sha(args.manifest),
              'harness_sha256': sha(scripts / 'probe-darwinboot-xnu.py'),
              'firmware': str(args.firmware) if args.firmware else None,
              'firmware_sha256': sha(args.firmware) if args.firmware else None,
              'loader_sha256': {n: sha(args.loaders / n) for n in ('UniXNU.efi', 'DarwinBoot.efi')},
              'attempts': [], 'runtime_qualified': False, 'fault_injection_run': False}
    for mode in (1, 2, 3):
        output = args.output / f'mode{mode}'
        command = [sys.executable, str(scripts / 'probe-darwinboot-xnu.py'),
                   '--kernel', str(args.kernel), '--prelink-report', str(args.manifest),
                   '--output', str(output), '--timeout', '60', '--armvirt', '--armdt-platform', '--armcpu',
                   '--kernel-extra-args', f'pmgr={mode}', '--inspect-sheng-pmgr']
        result = subprocess.run(command, cwd=view, env=env, text=True, capture_output=True, timeout=150)
        (args.output / f'mode{mode}.stdout.txt').write_text(result.stdout)
        (args.output / f'mode{mode}.stderr.txt').write_text(result.stderr)
        attempt = {'mode': mode, 'command': command, 'cwd': str(view), 'returncode': result.returncode,
                   'environment': {k: env[k] for k in ('PATH', 'XNU_TOOLCHAIN_BIN', 'PYTHONPATH')}}
        # Record raw result files without assuming a successful hook or stage.
        attempt['json_outputs'] = [str(p) for p in output.rglob('*.json')] if output.exists() else []
        record['attempts'].append(attempt)
        record['kernel_after_sha256'] = sha(args.kernel)
        (args.output / 'result.json').write_text(json.dumps(record, indent=2) + '\n')
        print(f'mode{mode} real harness exit={result.returncode}', flush=True)
        if result.returncode:
            print(result.stderr[-4000:], file=sys.stderr)
            # A harness precondition failure does not justify more identical runs.
            return result.returncode
        # Do not label arbitrary harness exit0 as PMGR runtime qualification.
        # Stop for actual stage/field inspection before a later mode is authorized.
        return 0
    return 0


if __name__ == '__main__':
    sys.exit(main())
