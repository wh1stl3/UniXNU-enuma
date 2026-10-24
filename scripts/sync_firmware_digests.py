"""Resync the firmware digest lists after editing a locked firmware input.

The firmware repository keeps two independent digest lists: Resources/Enuma/
migration.json (values are objects with a destination and a sha256) and
Resources/Enuma/extensions.json (values are the sha256 string itself). Both
are checked by the preflight before any build, so a content change has to be
reflected in both. The device repository keeps a third list,
config/uefi-source.lock.json, which pins the firmware commit and the same file
digests.

Usage: python scripts/sync_firmware_digests.py [--write]

Without --write it only reports what would change. It also refuses to record a
digest for a file that is missing, so a renamed input cannot silently keep an
old hash.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIRMWARE = ROOT / 'firmware'
META = FIRMWARE / 'Resources/Enuma'
LOCK = ROOT / 'config/uefi-source.lock.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--device-only', action='store_true',
                        help='only update the device lock; use after the firmware '
                             'repository has already committed its own digests')
    args = parser.parse_args()

    changed = []
    missing = []

    migration_path = META / 'migration.json'
    migration = json.loads(migration_path.read_text())
    for item in migration['files'].values():
        target = FIRMWARE / item['destination']
        if not target.exists():
            missing.append(item['destination'])
            continue
        want = digest(target)
        if item['sha256'] != want:
            changed.append(('migration', item['destination']))
            item['sha256'] = want

    extensions_path = META / 'extensions.json'
    extensions = json.loads(extensions_path.read_text())
    for relative, value in extensions['files'].items():
        target = FIRMWARE / relative
        if not target.exists():
            missing.append(relative)
            continue
        want = digest(target)
        if value != want:
            changed.append(('extensions', relative))
            extensions['files'][relative] = want

    commit = subprocess.check_output(['git', '-C', str(FIRMWARE), 'rev-parse', 'HEAD'], text=True).strip()
    lock = json.loads(LOCK.read_text())
    if lock['commit'] != commit:
        changed.append(('lock', 'commit'))
        lock['commit'] = commit
    for relative in list(lock['file_sha256']):
        target = FIRMWARE / relative
        if not target.exists():
            missing.append(relative)
            continue
        want = digest(target)
        if lock['file_sha256'][relative] != want:
            changed.append(('lock', relative))
            lock['file_sha256'][relative] = want

    if missing:
        raise SystemExit('missing inputs: ' + ', '.join(sorted(set(missing))))
    if not changed:
        print('nothing to sync')
        return
    for where, what in changed:
        print(where, what)
    if not args.write:
        print('dry run; pass --write to apply')
        return
    if not args.device_only:
        migration_path.write_text(json.dumps(migration, indent=2) + '\n')
        extensions_path.write_text(json.dumps(extensions, indent=2) + '\n')
    LOCK.write_text(json.dumps(lock, indent=2) + '\n')
    print('written')


if __name__ == '__main__':
    main()
