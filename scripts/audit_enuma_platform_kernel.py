"""Re-audit downloaded source-platform kernel evidence, without prelink or boot."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
from audit_enuma_kernel_baseline import inspect

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--run', type=int, required=True)
    parser.add_argument('--head', required=True)
    args = parser.parse_args()
    result = json.loads((args.evidence / 'result.json').read_text())
    lock = json.loads((ROOT / 'config/sources.lock.json').read_text())['sources']['UniXNU']
    if (result['status'] != 'passed' or result['mode'] != 'platform' or
            result['device_commit'] != args.head or int(result['run_id']) != args.run or
            result['unixnu_commit'] != lock['commit'] or result['sdk_version'] != '18.5' or
            not result['xcode'].startswith('Xcode 16.4\n') or
            result.get('platform_kernel_exit_code') != 0 or not result.get('platform_build_and_link_passed')):
        raise ValueError('Unqualified CI result or wrong provenance')
    recipe = json.loads((ROOT / 'config/kernel-archives.lock.json').read_text())
    if result['archive_recipe_lock'] != recipe or len(result['archive_steps']) != len(recipe['steps']):
        raise ValueError('CI archive recipe differs')
    for actual, expected in zip(result['archive_steps'], recipe['steps']):
        if actual['recipe'] != expected or actual['exit_code'] != 0:
            raise ValueError('Missing or failed archive step')
    source = ROOT / 'out/sources/UniXNU'
    kit = source / 'kits/NativePrelink'
    wanted = lock['gitlinks']['kits/NativePrelink']
    revision = subprocess.check_output(['git', '-C', str(kit), 'rev-parse', 'HEAD'], text=True).strip()
    raw = (kit / 'native_prelink.py').read_bytes()
    if revision != wanted or raw != subprocess.check_output(['git', '-C', str(kit), 'show', f'{wanted}:native_prelink.py']):
        raise ValueError('NativePrelink parser revision/content changed')
    spec = importlib.util.spec_from_file_location('enuma_platform_parser', kit / 'native_prelink.py')
    native = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native)
    data = (args.evidence / 'platform-kernel.macho').read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != result['platform_kernel_sha256']:
        raise ValueError('Downloaded kernel differs from CI hash')
    audit = inspect(data, native)
    if not all(audit['selected_platform_symbols'].values()):
        raise ValueError('Downloaded kernel lacks real platform/CPU/pthread providers')
    import sys
    sys.path.insert(0, str(source / 'scripts'))
    from unixnu.config import parse_config
    config = parse_config((ROOT / 'configs/enuma_defconfig').read_text())
    effective = result['effective_platform_switches']
    for key, value in config.items():
        if key.startswith('XNU_'):
            expected = '1' if value is True else '0' if value is False else str(value)
            if effective.get(key) != expected:
                raise ValueError('CI feature mismatch: ' + key)
    report = {'scope': 'actual macOS source-platform link and local Mach-O audit; no donor prelink/boot',
              'run_id': args.run, 'head_sha': args.head,
              'url': f'https://github.com/wh1stl3/UniXNU-enuma/actions/runs/{args.run}',
              'unixnu_commit': lock['commit'], 'kernel_bytes': len(data), 'kernel_sha256': sha,
              'native_prelink_parser_commit': wanted, 'parser_sha256': hashlib.sha256(raw).hexdigest(),
              'kernel_audit': audit, 'effective_platform_switches': effective,
              'ci_archive_sha256': result['platform_archive_sha256'],
              'archive_hashes_independently_recomputed_locally': False,
              'archive_steps_passed': len(recipe['steps']), 'sdk_version': result['sdk_version'],
              'xcode': result['xcode'], 'new_device_trials': 0,
              'donor_prelink_generated': False, 'complete_adt_generated': False,
              'boot_candidate_generated': False, 'ipados_userspace_observed': False}
    (ROOT / 'reports/enuma-platform-kernel-ci.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: actual platform link, fixed recipe and feature flags; downloaded ordinary ARM64/4K kernel with real providers')


if __name__ == '__main__':
    main()
