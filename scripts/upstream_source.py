"""Validate pinned UniXNU modules and apply the device's reviewed patch series."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(source, *args, check=True):
    return subprocess.run(['git', '-c', 'safe.directory=' + source.as_posix(),
                           '-C', str(source), *args], check=check,
                          capture_output=True, text=True)


def qualify(source, lock=None):
    source = Path(source).resolve()
    lock = lock or json.loads((ROOT / 'config/sources.lock.json').read_text())['sources']['UniXNU']
    if git(source, 'rev-parse', 'HEAD').stdout.strip() != lock['commit']:
        raise ValueError('UniXNU base revision mismatch')
    actual = {}
    for line in git(source, 'ls-tree', '-r', 'HEAD').stdout.splitlines():
        mode, _, revision, name = line.split(None, 3)
        if mode == '160000':
            actual[name] = revision
    if actual != lock['gitlinks']:
        raise ValueError('UniXNU gitlink lock differs from base tree')
    for name, revision in actual.items():
        if git(source / name, 'rev-parse', 'HEAD').stdout.strip() != revision:
            raise ValueError('Module revision mismatch: ' + name)
        if git(source / name, 'status', '--porcelain').stdout.strip():
            raise ValueError('Module must be clean: ' + name)
    for name, wanted in lock['file_sha256'].items():
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != wanted:
            raise ValueError('UniXNU input hash mismatch: ' + name)
    # Compare the complete tracked diff after applying; unrelated local changes
    # must never silently become part of the qualified build.
    for item in lock.get('patches', []):
        patch = ROOT / item['path']
        if hashlib.sha256(patch.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Device patch hash mismatch: ' + item['path'])
        if git(source, 'apply', '--reverse', '--check', str(patch), check=False).returncode:
            git(source, 'apply', '--check', str(patch))
            git(source, 'apply', str(patch))
    expected = ''.join((ROOT / item['path']).read_text() for item in lock.get('patches', []))
    # Check paths first, then compare the complete patch effect against HEAD.
    changed = git(source, 'diff', '--name-only', 'HEAD').stdout.splitlines()
    permitted = [line[6:] for line in expected.splitlines() if line.startswith('+++ b/')]
    if sorted(changed) != sorted(permitted):
        raise ValueError('Unexpected upstream tracked changes: ' + repr(changed))
    # Reversing all approved patches must exactly restore the pinned tree.
    for item in reversed(lock.get('patches', [])):
        git(source, 'apply', '--reverse', str(ROOT / item['path']))
    try:
        if git(source, 'diff', 'HEAD', '--exit-code', check=False).returncode:
            raise ValueError('Unreviewed changes within patched upstream files')
    finally:
        for item in lock.get('patches', []):
            git(source, 'apply', str(ROOT / item['path']))
    return {'base': lock['commit'], 'modules': actual, 'patches': lock.get('patches', [])}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    print(json.dumps(qualify(parser.parse_args().source), indent=2))
