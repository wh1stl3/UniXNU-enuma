"""Exercise real profile-tree corruption and collision refusal paths offline."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from stage_oem_display_profiles import ROOT, PE, XML, verify_pair, stage


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pair', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve(); out.relative_to(ROOT/'out')
    out.mkdir(parents=True, exist_ok=False)
    baseline = verify_pair(a.pair)
    passed = []
    with tempfile.TemporaryDirectory(dir=out, prefix='failure-cases-') as tmp:
        root = Path(tmp)/'pair'
        shutil.copytree(a.pair, root)

        def refused(name, fn):
            try:
                fn()
            except (ValueError, FileExistsError):
                passed.append(name)
            else:
                raise AssertionError(name+' accepted')

        for name, relative in [('control PE corruption', 'oem-control/vendor/'+PE),
                               ('experiment non-patch corruption', 'oem-mmu-only/vendor/'+PE),
                               ('experiment panel mutation', 'oem-mmu-only/vendor/'+XML)]:
            path = root/relative; original = path.read_bytes()
            path.write_bytes(original[:-1]+bytes([original[-1]^1]))
            refused(name, lambda: verify_pair(root))
            path.write_bytes(original)
        extra = root/'oem-mmu-only/vendor/unexpected.bin'; extra.write_bytes(b'extra')
        refused('unlisted extra module', lambda: verify_pair(root)); extra.unlink()
        manifest = root/'profiles.json'; original = manifest.read_bytes()
        m = json.loads(original); m['enabled'] = True
        manifest.write_text(json.dumps(m))
        refused('staging marked enabled', lambda: verify_pair(root)); manifest.write_bytes(original)
        m = json.loads(original); m['profiles']['oem-mmu-only'] = m['profiles']['oem-control']
        manifest.write_text(json.dumps(m))
        refused('swapped variant identity', lambda: verify_pair(root)); manifest.write_bytes(original)
        existing = Path(tmp)/'existing'; existing.mkdir()
        refused('existing output directory', lambda: stage(root/'oem-control/vendor', existing))
        refused('output outside worktree out', lambda: stage(root/'oem-control/vendor', ROOT/'forbidden'))
        assert verify_pair(root) == baseline
    assert verify_pair(a.pair) == baseline
    result = dict(passed=True, negative_checks=passed, count=len(passed), baseline=baseline,
                  source_sha256={name: hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest()
                                 for name in ['stage_oem_display_profiles.py','check_oem_display_profiles.py']})
    (out/'result.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
