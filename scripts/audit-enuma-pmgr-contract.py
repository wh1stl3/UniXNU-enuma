#!/usr/bin/env python3
"""Run the pinned base AMFI/PMGR audit against explicit enuma inputs.

The base audit derives its donor and output paths from __file__.  An isolated
view preserves those semantics without changing the base or using its fallback.
This is static boundary evidence, NOT lifecycle or runtime qualification.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

BASE_REVISION = '693f5d9cae8a408dd18b39f3f9fdc4228c934241'
AUDIT_SHA256 = '19a0429a75341947b6908da69a26c2b9e686602e3b0f8795968009475fe5df08'
PRELINK_REVISION = 'f1d80d37528a33e24643583787123c652b70a268'
PRELINK_LF_SHA256 = '5bd80b8c63deec29b747c28253e02308a56d5f8cdb37c9d315e7c8af7012d017'


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate(args):
    script = args.base / 'scripts/audit-amfi-pmgr-contract.py'
    require(script.is_file(), f'Pinned base audit absent: {script}')
    require(sha256(script) == AUDIT_SHA256, 'Pinned base audit hash mismatch')
    head = subprocess.check_output(['git', '-C', str(args.base), 'rev-parse', 'HEAD'], text=True).strip()
    require(head == BASE_REVISION, f'Base revision differs: {head}')
    require(not subprocess.check_output(['git', '-C', str(args.base), 'status', '--porcelain', '--',
                                        'scripts/audit-amfi-pmgr-contract.py'], text=True).strip(),
            'Base audit has workspace changes; preserve and review its provenance')
    for name in ('donor', 'candidate', 'manifest'):
        path = getattr(args, name)
        require(path.is_file(), f'Explicit {name} absent: {path}; no fallback permitted')
        require(sha256(path) == getattr(args, name + '_sha256'), f'{name} SHA256 mismatch')
    plan = json.loads(args.manifest.read_text())
    require(plan['original_sha256'] == args.donor_sha256, 'Manifest donor binding differs')
    require('com.apple.driver.ApplePMGR' in plan['components'], 'Original ApplePMGR missing')
    require('com.apple.driver.AppleT8011PMGR' not in plan['components'], 'Hardware PMGR must not load')
    return script


def audit(args):
    script = validate(args)
    helper = args.base / 'kits/XnuPrelink/native_prelink.py'
    helper_head = subprocess.check_output(['git', '-C', str(helper.parent), 'rev-parse', 'HEAD'], text=True).strip()
    require(helper_head == PRELINK_REVISION, 'XnuPrelink revision differs')
    require(hashlib.sha256(helper.read_bytes().replace(b'\r\n', b'\n')).hexdigest() == PRELINK_LF_SHA256,
            'Pinned native_prelink implementation differs (beyond CRLF)')
    args.output.mkdir(parents=True, exist_ok=True)
    # Use links only in our newly created private view; never edit the inputs.
    with tempfile.TemporaryDirectory(prefix='contract-', dir=args.output) as temporary:
        view = Path(temporary)
        for directory in ('scripts', 'kits', '.cache/firmware/kernelcache.macho', 'inputs'):
            (view / directory).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(script, view / 'scripts' / script.name)
        (view / 'kits/XnuPrelink').symlink_to(args.base / 'kits/XnuPrelink', target_is_directory=True)
        (view / '.cache/firmware/kernelcache.macho/kernelcache.release.ipad7.decompressed').symlink_to(args.donor)
        candidate = view / 'inputs/reference.macho'
        candidate.symlink_to(args.candidate)
        candidate.with_suffix('.json').symlink_to(args.manifest)
        command = [sys.executable, str(view / 'scripts' / script.name), '--candidate', str(candidate)]
        result = subprocess.run(command, text=True, capture_output=True, timeout=120)
        (args.output / 'base-audit.stdout.txt').write_text(result.stdout)
        (args.output / 'base-audit.stderr.txt').write_text(result.stderr)
        print(result.stdout, end='')
        print(result.stderr, end='', file=sys.stderr)
        require(result.returncode == 0, f'Pinned base audit exited {result.returncode}')
        report = json.loads((view / 'build/amfi-pmgr-contract/report.json').read_text())
    report['enuma_dependency'] = {
        'base_revision': BASE_REVISION, 'base_audit_sha256': AUDIT_SHA256,
        'xnu_prelink_revision': helper_head, 'native_prelink_raw_sha256': sha256(helper),
        'native_prelink_lf_sha256': PRELINK_LF_SHA256,
        'inputs': {name: {'path': str(getattr(args, name)), 'sha256': getattr(args, name + '_sha256')}
                   for name in ('donor', 'candidate', 'manifest')},
        'status': 'self-checked', 'base_audit_exit': result.returncode,
        'ownership_closure_qualified': False,
    }
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True, type=Path)
    for name in ('donor', 'candidate', 'manifest'):
        parser.add_argument('--' + name, required=True, type=Path)
        parser.add_argument('--' + name + '-sha256', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    for name in ('base', 'donor', 'candidate', 'manifest', 'output'):
        setattr(args, name, getattr(args, name).resolve())
    try:
        audit(args)
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f'PMGR contract rejected: {error}\n')


if __name__ == '__main__':
    main()
