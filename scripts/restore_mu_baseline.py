"""Restore the staged Mu tree to the baseline the preflight expects.

The preflight compares the staged Mu sources against the digests recorded in
Resources/Enuma/reset.json, and that baseline is the tree with every
diagnostic patch reversed. Hand-applied patches and removed patch files make
that state hard to reach by hand, so this script reverses the published
diagnostic patches until every baseline file matches again.

Usage: python scripts/restore_mu_baseline.py [--device-root PATH]
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def run(command, cwd):
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device-root', default=str(ROOT))
    args = parser.parse_args()
    root = Path(args.device_root)
    firmware = root / 'firmware'
    core = root / 'out/firmware-build/Mu_Basecore'
    reset = json.loads((firmware / 'Resources/Enuma/reset.json').read_text())
    baseline = {rel: want for rel, want in reset['diagnostic_baseline_lf_sha256'].items()
                if rel.startswith(('MdeModulePkg/', 'UefiCpuPkg/'))}
    patches = sorted((firmware / 'patches').glob('*.patch'))

    def mismatched():
        bad = []
        for rel, want in baseline.items():
            path = core / rel
            if not path.exists():
                bad.append(rel)
            elif digest(path) != want:
                bad.append(rel)
        return bad

    for _ in range(len(patches) + 1):
        bad = mismatched()
        if not bad:
            print('baseline restored')
            return
        changed = False
        for patch in patches:
            check = run(['git', 'apply', '--reverse', '--check', str(patch)], cwd=core)
            if check.returncode != 0:
                continue
            run(['git', 'apply', '--reverse', str(patch)], cwd=core)
            changed = True
            break
        if not changed:
            break
    bad = mismatched()
    if bad:
        raise SystemExit('could not restore baseline: ' + ', '.join(bad))
    print('baseline restored')


if __name__ == '__main__':
    main()
