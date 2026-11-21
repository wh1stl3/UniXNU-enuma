#!/usr/bin/env python3
"""Target archive matrix for the approved observation-only feature; no native link."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    source, out = a.source.resolve(), a.output.resolve()
    assert not out.exists(), 'Use NEW output'
    base = Path('/mnt/d/Code/PortingiOS/UniXNU')
    device = Path(__file__).resolve().parents[1]
    # Existing four-cell runner independently rebuilds normal/default-off cells,
    # explains source-coordinate changes and runs the existing real host guards.
    command = [sys.executable, str(device/'scripts/build-enuma-ufs-store-matrix.py'),
               '--source', str(source), '--output', str(out)]
    run = subprocess.run(command)
    assert run.returncode == 0, 'Normal four-cell matrix failed'
    sys.path.insert(0, str(base/'scripts'))
    from unixnu.kernel import linux_env
    tree = out/'tree'
    env = dict(os.environ, **linux_env(SimpleNamespace(tree=tree)))
    env.update(UNIXNU_XNU_ARCH='arm64', UNIXNU_IOS_VERSION='17.0')
    env['PATH'] = '/home/wh1stl3/.local/bin:' + env['PATH']
    spec = importlib.util.spec_from_file_location('symbols', device/'scripts/check-enuma-ufs-store-symbols.py')
    symbols = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(symbols)
    records = []
    old_missing = {'_boot_progress_poll', '_verified_root_key', '_verified_root_policies',
                   '_verified_root_policy_count', '_vr_open', '_vr_verify_block', '_vr_xnu_crypto'}
    cells = [(e,d,0,True) for e in (0,1) for d in (0,1)]
    cells += [(e,d,1,e==d==1) for e in (0,1) for d in (0,1)]
    cells += [(1,1,v,False) for v in (-1,2)]
    for e,d,o,success in cells:
        tag = f'explicit-observation-{o}-external-{e}-diagnostic-{d}'
        dst = out/tag
        dst.mkdir()
        buildenv = dict(env)
        buildenv['CCC_OVERRIDE_OPTIONS'] += f' +-DNATIVE_UFS_EXTERNAL_STORE_PROVIDER={e} +-DNATIVE_UFS_REUSE_DIAGNOSTIC={d} +-DNATIVE_UFS_OBSERVATION_ONLY={o}'
        argv = [sys.executable, str(tree/'scripts/build-arm-driver.py'), 'ShengUfs']
        run = subprocess.run(argv, cwd=tree, env=buildenv, capture_output=True)
        (dst/'build.log').write_bytes(run.stdout+run.stderr)
        record = {'argv': argv, 'cwd': str(tree), 'CCC_OVERRIDE_OPTIONS': buildenv['CCC_OVERRIDE_OPTIONS'],
                  'external':e, 'diagnostic':d, 'observation':o, 'returncode':run.returncode, 'expected_success':success}
        records.append(record)
        (out/'observation-commands.json').write_text(json.dumps(records, indent=2)+'\n')
        if not success:
            assert run.returncode != 0 and b'error:' in run.stdout+run.stderr, tag
            continue
        if run.returncode:
            print((run.stdout+run.stderr).decode(errors='replace'), flush=True)
            raise SystemExit(run.returncode)
        for name in ('NativeUfs.o','libShengUfs.a','compile-command.json','compile.log'):
            shutil.copy2(tree/'build/sheng-ufs'/name, dst/name)
        undefined = subprocess.check_output(['llvm-nm','-u',str(dst/'libShengUfs.a')],env=env,text=True)
        (dst/'undefined.txt').write_text(undefined)
        found = {v.split()[-1] for v in undefined.splitlines() if v.split() and v.split()[-1].startswith('_')}
        assert (old_missing.isdisjoint(found) if o else old_missing<=found), tag
        if o==0:
            prior = out/f'external-{e}-diagnostic-{d}'
            assert symbols.definitions([prior/'libShengUfs.a']).keys() == symbols.definitions([dst/'libShengUfs.a']).keys()
            prior_undefined = subprocess.check_output(['llvm-nm','-u',str(prior/'libShengUfs.a')],env=env,text=True)
            assert {v.split()[-1] for v in prior_undefined.splitlines() if v.split() and v.split()[-1].startswith('_')} == found
        record['archive_sha256'] = hashlib.sha256((dst/'libShengUfs.a').read_bytes()).hexdigest()
        print('self-checked',tag,flush=True)
    (out/'observation-result.json').write_text(json.dumps({'status':'self-checked target macro matrix', 'cells':records},indent=2)+'\n')

if __name__=='__main__':
    main()
