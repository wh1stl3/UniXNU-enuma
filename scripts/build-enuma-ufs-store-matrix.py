#!/usr/bin/env python3
"""Own-source-only four-archive build; uses existing official prepared ABI/tools.

No kernel/prelink/package/device work. Output must be a NEW ignored ext4 directory.
"""
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


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--archives-from', type=Path,
                        help='Reuse four completed source-matched cells after a host-runner-only fix')
    args = parser.parse_args()
    source, out = args.source.resolve(), args.output.resolve()
    reuse = args.archives_from.resolve() if args.archives_from else None
    base = Path('/mnt/d/Code/PortingiOS/UniXNU')
    device = Path(__file__).resolve().parents[1]
    prepared = Path('/root/enuma-step10/UniXNU/out/enuma/ipados-17.7.11-21H461/enuma/tree')
    ram = prepared / 'build/ram-block/libRamBlock.a'
    old = Path('/root/enuma-step10/UniXNU-enuma/.cache/sheng-ufs-reuse-diagnostic-fix1-20261111')
    assert not out.exists(), 'Use a new output path: never overwrite evidence'
    assert subprocess.check_output(['git', '-C', str(base), 'rev-parse', 'HEAD'], text=True).strip() == '693f5d9cae8a408dd18b39f3f9fdc4228c934241'
    assert subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip() == 'e2b32cc429e8cf1501161c1d8c517f8994ceb9b2'
    subprocess.run(['git', '-C', '/root/enuma-step10/UniXNU-enuma', 'check-ignore', str(out)], check=True, capture_output=True)
    tree = out / 'tree'
    (tree / 'scripts').mkdir(parents=True)
    for name in ('build-arm-driver.py', 'kernel_target.py'):
        shutil.copy2(base / 'scripts' / name, tree / 'scripts' / name)
    shutil.copy2(base / 'components.toml', tree / 'components.toml')
    for original, destination in ((prepared/'build/xnu', tree/'build/xnu'),
        (prepared/'build/storage-abi', tree/'build/storage-abi'),
        (prepared/'.cache/xnu-work', tree/'.cache/xnu-work'),
        (base/'kits/VerifiedRoot', tree/'kits/VerifiedRoot'),
        (base/'drivers/VirtioMmioBlock', tree/'drivers/VirtioMmioBlock')):
        assert original.exists()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.symlink_to(original, target_is_directory=True)
    shutil.copytree(source, tree/'drivers/ShengUfs', ignore=shutil.ignore_patterns('.git', '__pycache__'))
    if reuse:
        # Reuse only when all production source inputs still match the built tree.
        for pattern in ('*.cpp', '*.h'):
            for path in source.glob(pattern):
                assert path.read_bytes() == (reuse/'tree/drivers/ShengUfs'/path.name).read_bytes(), path
        assert (reuse/'tree/scripts/build-arm-driver.py').read_bytes() == (tree/'scripts/build-arm-driver.py').read_bytes()
        shutil.copy2(reuse/'commands.json',out/'reused-archive-commands.json')
    # Preserve fix1 BEFORE any build; runner's tree/build output is reused internally.
    for diagnostic in (0, 1):
        dst = out / ('fix1-before-' + str(diagnostic))
        shutil.copytree(old / ('archive-' + str(diagnostic)), dst)
    sys.path.insert(0, str(base/'scripts'))
    from unixnu.kernel import linux_env
    env = dict(os.environ, **linux_env(SimpleNamespace(tree=prepared)))
    env.update(UNIXNU_XNU_ARCH='arm64', UNIXNU_IOS_VERSION='17.0')
    env['PATH'] = '/home/wh1stl3/.local/bin:' + env['PATH']
    records = []

    def run(command, name, environment=env, cwd=None):
        command = [str(x) for x in command]
        cwd = str(cwd or tree)
        child = subprocess.run(command, cwd=cwd, env=environment, capture_output=True, text=True)
        (out/(name+'.log')).write_text(child.stdout+child.stderr)
        records.append({'command': command, 'cwd': cwd, 'exit': child.returncode,
                        'CCC_OVERRIDE_OPTIONS': environment.get('CCC_OVERRIDE_OPTIONS')})
        (out/'commands.json').write_text(json.dumps(records, indent=2)+'\n')
        if child.returncode:
            print(child.stdout+child.stderr, flush=True)
            raise SystemExit(child.returncode)
        return child.stdout

    spec = importlib.util.spec_from_file_location('symbols', device/'scripts/check-enuma-ufs-store-symbols.py')
    symbols = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(symbols)
    spec = importlib.util.spec_from_file_location('identity', device/'scripts/audit-enuma-ufs-object-identity.py')
    identity = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(identity)
    ram_before = sha(ram)
    variants = []
    for external in (0, 1):
        for diagnostic in (0, 1):
            tag = f'external-{external}-diagnostic-{diagnostic}'
            dst = out/tag
            dst.mkdir()
            buildenv = dict(env)
            buildenv['CCC_OVERRIDE_OPTIONS'] += f' +-DNATIVE_UFS_REUSE_DIAGNOSTIC={diagnostic}'
            # Default cells deliberately omit the new define, testing its default=0.
            if external:
                buildenv['CCC_OVERRIDE_OPTIONS'] += ' +-DNATIVE_UFS_EXTERNAL_STORE_PROVIDER=1'
            if not reuse:
                run([sys.executable, tree/'scripts/build-arm-driver.py', 'ShengUfs'], tag, buildenv)
            for name in ('NativeUfs.o', 'libShengUfs.a', 'compile-command.json', 'compile.log'):
                original = reuse/tag/name if reuse else tree/'build/sheng-ufs'/name
                shutil.copy2(original, dst/name)
            archive = dst/'libShengUfs.a'
            defs = symbols.definitions([archive])
            stores = set(defs) & symbols.STORE
            assert stores == (set() if external else symbols.STORE), stores
            olddefs = symbols.definitions([out/f'fix1-before-{diagnostic}/libShengUfs.a'])
            assert set(defs) == set(olddefs) - (symbols.STORE if external else set())
            if external:
                audit = symbols.audit([ram, archive])
                (dst/'symbols.json').write_text(json.dumps(audit, indent=2)+'\n')
            else:
                if reuse:
                    proof = json.loads((reuse/tag/'identity.json').read_text())
                    assert proof['object_after_sha256'] == sha(dst/'NativeUfs.o')
                    assert proof['object_before_sha256'] == sha(out/f'fix1-before-{diagnostic}/NativeUfs.o')
                    assert proof['default_preprocessor_equal_except_panic_source_lines']
                    shutil.copy2(reuse/tag/'identity.json',dst/'identity.json')
                else:
                    identity.explain_default(out/f'fix1-before-{diagnostic}', dst, diagnostic,
                                             dst/'identity.json', run)
                both = symbols.definitions([ram, archive])
                duplicates = {s for s, owners in both.items() if len(owners)>1}
                assert duplicates == symbols.STORE, duplicates
            (dst/'nm.txt').write_text(run(['llvm-nm','-A','-g','--defined-only',archive],tag+'-nm'))
            run(['xcrun','ar','t',archive],tag+'-members')
            dis = run(['llvm-objdump','--disassemble','--demangle',dst/'NativeUfs.o'],tag+'-disassembly')
            assert (b'UFS_REUSE ' in (dst/'NativeUfs.o').read_bytes()) == bool(diagnostic)
            if diagnostic: assert 'wfe' in dis
            variants.append({'external':external,'diagnostic':diagnostic,'archive':str(archive),
                             'archive_sha256':sha(archive),'object_sha256':sha(dst/'NativeUfs.o'),
                             'store_definitions':sorted(stores),'export_count':len(defs)})
            print(f'self-checked {tag}: {sha(archive)}',flush=True)
    assert sha(ram)==ram_before
    hostenv = dict(os.environ)
    hostenv['PATH'] = '/usr/bin:/bin:/home/wh1stl3/.local/bin'
    hostenv.pop('CCC_OVERRIDE_OPTIONS',None)
    run([sys.executable,source/'tests/reuse_admission_test.py','--output',out/'host',
         '--ramblock-source',prepared/'drivers/RamBlock/NativeRamBlock.cpp',
         '--store-provider',device/'package/EnumaRamBlockStore.cpp'],'host',hostenv)
    (out/'result.json').write_text(json.dumps({'validation':'self-checked','variants':variants,
        'ramblock_sha256_unchanged':ram_before,'candidate_final_link_checked':False,
        'reused_archive_source':str(reuse) if reuse else None},indent=2)+'\n')
    print('self-checked four archives and real-provider host matrix; no candidate/final-link claim')


if __name__ == '__main__':
    main()
