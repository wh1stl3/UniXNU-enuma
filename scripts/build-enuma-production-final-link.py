#!/usr/bin/env python3
"""Isolated production-input link experiment. No package or runtime admission.

Replays the prepared non-LTO final link, not the source-mutating full recipe.
All prepared inputs are read-only; every new output lives in a fresh device out/.
Stops at the first failed command; never substitutes unresolved-symbol stubs.
"""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tomllib
from types import SimpleNamespace

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parents[1] / 'UniXNU'
PIN = '693f5d9cae8a408dd18b39f3f9fdc4228c934241'
PREPARED = Path('/root/enuma-step10/UniXNU/out/enuma-ufs-version-diagnostic-20261112-python311')
SOURCE = ROOT / '.cache/ufs-observation-output-20261112/source'
PROVIDER = ROOT / 'out/provider-rebuild-20261113'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    out = a.output.resolve()
    require(out.is_relative_to((ROOT / 'out').resolve()), 'output must be under device out/')
    require(not out.exists(), 'output must be new')
    require(subprocess.check_output(['git', '-C', BASE, 'rev-parse', 'HEAD'], text=True).strip() == PIN,
            'base HEAD changed')
    subprocess.run(['git', '-C', ROOT, 'check-ignore', str(out)], check=True, capture_output=True)
    out.mkdir(parents=True)
    report = {'status': 'self-checked in progress', 'commands': [], 'base_head': PIN,
              'deployment': False, 'runtime_qualified': False, 'GR0': 'NO-GO',
              'admission': 'unchanged NoAccessPolicy/NoContract', 'inputs': {},
              'scope': 'isolated native/prelink and embedded-byte audit; never deployment',
              'native_linked': False, 'prelinked': False}
    def save():
        (out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    def record(path):
        path = Path(path).resolve()
        report['inputs'][str(path)] = {'sha256': sha(path), 'bytes': path.stat().st_size}
        return path
    tree = PREPARED / 'out/enuma/ipados-17.7.11-21H461/enuma/tree'
    objroot = tree / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837'
    sys.path.insert(0, str(BASE / 'scripts'))
    from unixnu.kernel import linux_env
    env = dict(os.environ, **linux_env(SimpleNamespace(tree=tree)))
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['PATH'] = '/home/wh1stl3/.local/bin:' + env['PATH']
    def run(argv, cwd=out):
        argv = list(map(str, argv))
        log = out / ('command-%02d.log' % len(report['commands']))
        with log.open('w') as stream:
            p = subprocess.run(argv, cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT)
        report['commands'].append({'argv': argv, 'cwd': str(cwd), 'exit': p.returncode,
                                   'log': str(log), 'log_sha256': sha(log)})
        save()
        require(p.returncode == 0, f'command failed exit {p.returncode}: {log}')
        return log.read_text()
    try:
        report['upstream_head_at_start'] = run(['git', '-C', BASE, 'ls-remote', 'origin', 'HEAD']).strip()
        for path in (BASE / 'scripts/build-xnu-4k-baseline.sh',
                     BASE / 'scripts/check-boot-progress-code.py',
                     BASE / 'patches/xnu/zzz-boot-progress.patch',
                     tree / '.cache/xnu-work/makedefs/MakeInc.kernel'):
            record(path)
        mode = record(objroot / '.boot-progress-mode').read_text()
        require(mode == '0:disabled', 'prepared boot-progress mode must be exactly 0:disabled')
        require(re.findall(r'^CONFIG_XNU_BOOT_PROGRESS=(.*)$', record(ROOT / 'configs/enuma_defconfig').read_text(), re.M) == ['n'],
                'device defconfig must explicitly disable boot progress')
        require(not (tree / 'build/boot-progress/libBootProgress.a').exists(), 'unexpected boot-progress archive')
        report['deep_approval'] = 'ses_e2ceb5e16ffe14gJgp6R14HmOM; exact two-hunk guard only'
        provider_record = json.loads(record(PROVIDER / 'result.json').read_text())
        require(provider_record['mode'] == 'production', 'not real production provider')
        policies = []
        for label in ('os', 'systemos'):
            verified = json.loads(record(ROOT / f'out/verify-fresh-20261113/{label}/result.json').read_text())
            policy, anchor = record(verified['policy_path']), record(verified['anchor_path'])
            require(sha(policy) == verified['policy_sha256'] and sha(anchor) == verified['anchor_sha256'],
                    'verified policy/anchor binding changed')
            require(verified['vr_open_exit'] == 0 and verified['blocks_verified'] == (verified['raw_bytes'] + 4095) // 4096,
                    'incomplete inherited full-block verification')
            policies.append((policy, verified))
        report['signature_validation'] = 'inherited independent full-block results; not rerun'
        report['envelope_bytes'] = sum(p.stat().st_size for p, _ in policies)
        require(report['envelope_bytes'] == 73287008, 'unexpected envelope total')
        # Exact latest source, compiled without observer/external-store substitutions.
        snapshot = out / 'source'
        snapshot.mkdir()
        for p in SOURCE.iterdir():
            if p.suffix in ('.cpp', '.h'):
                record(p)
                shutil.copy2(p, snapshot / p.name)
        patch = record(ROOT / 'patches/isolated/sheng-ufs-boot-progress-guard.patch')
        require(sha(patch) == '31f5e2c2dba7f803b9ba71ebaa5de86ad1992e2749bcf63e4853b8b097838eb5',
                'patch differs from exact deep-approved two hunks')
        report['consumer_patch_sha256'] = sha(patch)
        run(['patch', '--batch', '--fuzz=0', '-p1', '-i', patch], snapshot)
        report['patched_source_sha256'] = sha(snapshot / 'NativeUfs.cpp')
        recpath = record(ROOT / '.cache/ufs-observation-output-20261112/target2/diag-0-layout-0/compile-command.json')
        argv = json.loads(recpath.read_text())
        abi_record = record(Path('/root/enuma-step10/UniXNU/out/enuma/ipados-17.7.11-21H461/enuma/tree/build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/iokit/DEVELOPMENT/IOPlatformExpert.cpo.json'))
        compile_cwd = Path(json.loads(abi_record.read_text().strip().rstrip(','))['directory'])
        oldsource = next(v for v in argv if v.endswith('/NativeUfs.cpp'))
        argv[argv.index(oldsource)] = str(snapshot / 'NativeUfs.cpp')
        consumer = out / 'NativeUfs.o'
        argv[argv.index('-o') + 1] = str(consumer)
        defines = {'NATIVE_UFS_OBSERVATION_ONLY': 0, 'NATIVE_UFS_EXTERNAL_STORE_PROVIDER': 0,
                   'NATIVE_UFS_REUSE_DIAGNOSTIC': 0, 'NATIVE_UFS_VERSION_DIAGNOSTIC': 0,
                   'NATIVE_UFS_ENUMA_READ_DIAGNOSTIC': 0, 'NATIVE_UFS_SMMU_REVIEW_CANDIDATE': 0}
        require(not any(any(v.startswith('-D' + k) for k in defines) for v in argv),
                'unexpected diagnostic flags in replay command')
        env['CCC_OVERRIDE_OPTIONS'] += ''.join(f' +-D{k}={v}' for k, v in defines.items())
        report['consumer_defines'] = defines
        def effective_defines(command):
            trace = run(command + ['-###'], compile_cwd)
            cc1 = [shlex.split(line) for line in trace.splitlines() if '"-cc1"' in line]
            require(len(cc1) == 1, 'expected exactly one effective compiler argv')
            values = [cc1[0][i + 1] for i, value in enumerate(cc1[0][:-1]) if value == '-D']
            return trace, values
        effective, values = effective_defines(argv)
        require([v for v in values if v.split('=')[0] == 'XNU_BOOT_PROGRESS'] == ['XNU_BOOT_PROGRESS=0'],
                'missing/conflicting effective XNU_BOOT_PROGRESS=0')
        for name, value in dict(defines, NATIVE_VERIFIED_BLOCK=1, NATIVE_VERIFIED_BLOCK_MULTI_POLICY=1).items():
            require([v for v in values if v.split('=')[0] == name] == [f'{name}={value}'],
                    f'effective macro mismatch: {name}')
        run(argv, compile_cwd)
        (out / 'effective-compile.txt').write_text(effective)
        pp = argv.copy()
        pp[pp.index('-c')] = '-E'
        pp[pp.index('-o') + 1] = str(out / 'consumer-off.ii')
        run(pp, compile_cwd)
        require('boot_progress_poll' not in (out / 'consumer-off.ii').read_text(), 'disabled hook remains preprocessed')
        off_nm = run(['llvm-nm', '-m', consumer])
        off_reloc = run(['llvm-objdump', '--reloc', consumer])
        require('boot_progress_poll' not in off_nm + off_reloc, 'disabled hook import/relocation remains')
        # Replace the existing macro; never append a conflicting -D.
        on = argv.copy()
        require(on.count('XNU_BOOT_PROGRESS=0') == 1, 'cannot uniquely replace boot-progress macro')
        on[on.index('XNU_BOOT_PROGRESS=0')] = 'XNU_BOOT_PROGRESS=1'
        on_obj = out / 'NativeUfs-progress-on.o'
        on[on.index('-o') + 1] = str(on_obj)
        trace_on, values_on = effective_defines(on)
        require([v for v in values_on if v.split('=')[0] == 'XNU_BOOT_PROGRESS'] == ['XNU_BOOT_PROGRESS=1'],
                'conflicting enabled hook macro')
        (out / 'effective-compile-on.txt').write_text(trace_on)
        run(on, compile_cwd)
        on_nm = run(['llvm-nm', '-m', on_obj])
        require(re.search(r'\(undefined\) weak external _boot_progress_poll\b', on_nm), 'enabled hook not weak C import')
        on_dis = run(['llvm-objdump', '--disassemble', '--reloc', '--demangle', on_obj])
        require('ARM64_RELOC_BRANCH26\t_boot_progress_poll' in on_dis or
                re.search(r'ARM64_RELOC_BRANCH26\s+_boot_progress_poll', on_dis), 'enabled hook has no direct call relocation')
        loads = re.findall(r'([0-9a-f]+):\s+ARM64_RELOC_GOT_LOAD_PAGEOFF12\s+_boot_progress_poll', on_dis)
        calls = re.findall(r'([0-9a-f]+):\s+ARM64_RELOC_BRANCH26\s+_boot_progress_poll', on_dis)
        require(len(loads) == len(calls) == 1, 'expected one enabled hook address load and call')
        load_at, call_at = int(loads[0], 16), int(calls[0], 16)
        instructions = {int(m[0], 16): m[1] for m in re.findall(
            r'^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2} ){4}\s*(.+)$', on_dis, re.M)}
        register = re.match(r'ldr\s+(x\d+),', instructions[load_at])
        guard = re.match(r'cbz\s+(x\d+),\s+0x([0-9a-f]+)', instructions[load_at + 4])
        require(register and guard and register[1] == guard[1] and call_at == load_at + 8 and
                instructions[call_at].startswith('bl') and not load_at <= int(guard[2], 16) <= call_at,
                'enabled weak-hook load/null-branch/call sequence changed')
        report['boot_progress_checks'] = {'off_pp_import_reloc_absent': True,
                                          'on_weak_C_import_guard_call_present': True,
                                          'on_guard_sequence': {hex(at): instructions[at] for at in (load_at, load_at + 4, call_at)},
                                          'enabled_object_not_executed_or_linked': True}
        report['consumer_sha256'] = sha(consumer)
        report['old_partial_consumer'] = {'path': '.cache/native-read-adapter-20261112/macro-1/NativeUfs.o',
                                         'sha256': sha(ROOT / '.cache/native-read-adapter-20261112/macro-1/NativeUfs.o'),
                                         'reused': False}
        dis = run(['llvm-objdump', '--disassemble', '--demangle', consumer])
        body = dis.split('<NativeUfsBlock::configureVerification()>:', 1)[1].split('\n\n', 1)[0]
        require(len(body.splitlines()) > 20, 'configureVerification is a refusal-only observer')
        require('_vr_open' in run(['llvm-nm', '-u', consumer]), 'consumer lost verification imports')
        run(['llvm-ar', 'rcs', out / 'libShengUfs.a', consumer])
        objects = []
        for name in ('verified_root.o', 'xnu_crypto.o', 'provider.o'):
            p = record(PROVIDER / name)
            require(sha(p) == provider_record['object_sha256'][str(p)], 'provider object hash changed')
            objects.append(p)
        run(['llvm-ar', 'rcs', out / 'libVerifiedRootProduction.a', *objects])
        record(out / 'libVerifiedRootProduction.a')
        record(out / 'libShengUfs.a')
        # Remove only the observation provider from a private RAM archive copy.
        ram = record(tree / 'build/ram-block/libRamBlock.a')
        require(run(['llvm-ar', 't', ram]).splitlines() ==
                ['NativeRamBlock.o', 'original-bindings.o', 'EnumaRamBlockStore.o'], 'RAM member set changed')
        ram_copy = out / 'libRamBlock.a'
        shutil.copy2(ram, ram_copy)
        run(['llvm-ar', 'd', ram_copy, 'EnumaRamBlockStore.o'])
        record(ram_copy)
        # Replay MakeInc.kernel's BUILD_LTO=0 link with read-only prepared objects.
        flags = shlex.split(record(objroot / '.LDFLAGS').read_text().replace('\0', ''))
        archives_file = record(objroot / 'mach.development.bcm2837.link/mach.development.bcm2837.linkarchives')
        archives = shlex.split(archives_file.read_text())
        replacements = {str(tree / 'build/sheng-ufs/libShengUfs.a'): str(out / 'libShengUfs.a'),
                        str(ram): str(ram_copy), str(PREPARED / 'native-link.map'): str(out / 'native-link.map')}
        archives = [next((v.replace(old, new) for old, new in replacements.items() if old in v), v)
                    for v in archives]
        filelist = record(objroot / 'link.filelist')
        for p in filelist.read_text().splitlines():
            record(p)
        for name in ('version.o', 'lastkerneldataconst.o', 'lastkernelconstructor.o'):
            record(objroot / name)
        for v in flags + archives:
            p = Path(v.removeprefix('-Wl,-force_load,'))
            if p.is_file():
                record(p)
        # Resolve implicit -l inputs from the already qualified prepared map.
        prepared_map = record(PREPARED / 'native-link.map')
        for path in sorted(set(re.findall(r'^\[\s*\d+\]\s+(.+\.a)\(', prepared_map.read_text(errors='replace'), re.M))):
            record(path)
        record(Path(__file__))
        record(ROOT / 'scripts/audit-enuma-production-final-link.py')
        native = out / 'native.macho'
        command = flags + ['-filelist', str(filelist)] + [str(objroot / n) for n in
                  ('version.o', 'lastkerneldataconst.o', 'lastkernelconstructor.o')]
        command += ['-o', str(native), *archives, '-Wl,-force_load,' + str(out / 'libVerifiedRootProduction.a')]
        report['XNU_EXTRA_LD_ARCHIVES_equivalent'] = command[-1]
        report['extra_archive_dependency_caveat'] = 'official extra argv not in external dependency stamp; explicit isolated relink'
        run(command, objroot)
        report['native_linked'] = True
        report['native_sha256'] = sha(native)
        undefined = run(['llvm-nm', '-u', native]).splitlines()
        report['native_undefined'] = undefined
        require(not undefined, 'final native violates zero-undefined policy (including weak imports)')
        # Match the actual prepared crypto mode, not the recipe's default.
        crypto_mode = record(objroot / 'osfmk/DEVELOPMENT/.crypto-bootstrap-mode').read_text().strip()
        require(crypto_mode in ('source', 'prelinked'), 'unknown prepared crypto mode')
        report['crypto_bootstrap_mode'] = crypto_mode
        if crypto_mode == 'source':
            run([sys.executable, record(BASE / 'scripts/seal-source-crypto-kernel.py'), native])
        report['native_sha256'] = sha(native)
        profile = record(BASE / 'profiles/os/ipados-17.7.11-21H461/profile.toml')
        spec = tomllib.loads(profile.read_text())['kernel']['prelink']
        donor = record(Path('/root/enuma-step10/UniXNU/out/ipsw/21H461/kernelcache.decompressed'))
        require(sha(donor) == spec['kernelcache_sha256'], 'donor kernelcache mismatch')
        prelink = out / 'prelink.macho'
        emit = record(BASE / spec['tool'])
        for name in ('native_prelink.py', 'emit_prelink.py'):
            record(emit.parent / name)
        pre_cmd = [sys.executable, emit, '--kernel', native, '--prelinked', donor,
                   '--slide=' + spec['slide'], '--early-security-init', spec['early_security_init']]
        for name in spec['roots']:
            pre_cmd += ['--root', name]
        pre_cmd += ['--output', prelink]
        run(pre_cmd)
        report['prelinked'] = True
        report['prelink_sha256'] = sha(prelink)
        save()
        run([sys.executable, ROOT / 'scripts/audit-enuma-production-final-link.py',
             '--build-json', out / 'result.json', '--output', out / 'audit.json'])
        report['audit_sha256'] = sha(out / 'audit.json')
        report['upstream_head_at_end'] = run(['git', '-C', BASE, 'ls-remote', 'origin', 'HEAD']).strip()
        require(subprocess.check_output(['git', '-C', BASE, 'rev-parse', 'HEAD'], text=True).strip() == PIN,
                'base changed during link')
        report['status'] = 'self-checked native/prelink byte binding and budget; runtime unqualified'
        save()
    except Exception as e:
        report['status'] = 'self-checked BLOCKED'
        report['first_error'] = str(e)
        raise
    finally:
        save()


if __name__ == '__main__':
    main()
