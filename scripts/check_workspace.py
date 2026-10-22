"""Check pinned inputs and exercise the upstream defconfig/example guard only."""
import hashlib
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    audit = json.loads((ROOT / 'reports/input-audit.json').read_text('utf-8'))
    pins = json.loads((ROOT / 'config/sources.lock.json').read_text('utf-8'))
    board = tomllib.loads((ROOT / 'board.toml').read_text('utf-8'))
    if board['board'] != {'name': 'enuma', 'soc': 'SM8250',
                          'description': 'Xiaomi Pad 5 Pro 5G / iPadOS 17.7.11 bring-up', 'example': True}:
        raise ValueError('board contract changed; review before updating the guard')
    if board.get('payload') != {'adt': {'ipad_identity': True, 'owned_memory_size': '0x20000000'}}:
        raise ValueError('payload contract differs from R-001: only the approved 512 MiB request is allowed')
    for name, source in pins['sources'].items():
        path = Path(source['path'])
        revision = subprocess.check_output(['git', '-c', f'safe.directory={path.as_posix()}', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
        if revision != source['commit']:
            raise ValueError(f'{name}: source revision changed')
        for relative, expected in source['file_sha256'].items():
            if hashlib.sha256((path / relative).read_bytes()).hexdigest() != expected:
                raise ValueError(f'{name}/{relative}: source content changed')
    base = Path(pins['sources']['UniXNU']['path'])
    from upstream_source import qualify
    qualify(base, pins['sources']['UniXNU'])
    feeds = tomllib.loads((base / 'feeds.toml').read_text('utf-8'))
    xnu = next(x for x in feeds['source'] if x['name'] == 'xnu')
    if xnu['commit'] != pins['sources']['xnu-ios17-full']['commit'] or xnu['version'] != '10063.141.1':
        raise ValueError('kernel feed mismatch')
    donor = audit['donor']
    for key in ('product', 'version', 'build', 'device_class'):
        if board['ipsw'][key] != donor[key]:
            raise ValueError(f'donor audit mismatch: {key}')
    for component in donor['components'].values():
        if component['digest_match'] is not True:
            raise ValueError('unmatched donor component')
    commands = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    # Never invoke build/bootimg: call their exact shared guard in-process,
    # so a future upstream change cannot accidentally produce an image.
    sys.path.insert(0, str(base / 'scripts'))
    from unixnu.config import Context, parse_config
    from unixnu.cli import parser
    from unixnu.util import Error
    args = parser().parse_args(['defconfig', '-D', str(ROOT), '--out', str(ROOT / 'out/upstream-check'), 'enuma_defconfig'])
    ctx = Context(args)
    try:
        ctx.refuse_example()
    except Error as error:
        guard = str(error)
    else:
        raise ValueError('upstream example guard did not reject this board')
    config = parse_config((ROOT / 'configs/enuma_defconfig').read_text('utf-8'))
    for name in ('XNU_SHENG_PMGR', 'XNU_NATIVE_ADRENO', 'XNU_NATIVE_UFS'):
        if config[name] is not False:
            raise ValueError(f'unreviewed hardware driver enabled: {name}')
    command = [sys.executable, '-B', str(base / 'unixnu'), 'defconfig', '-D', str(ROOT),
               '--out', str(ROOT / 'out/upstream-check'), 'enuma_defconfig']
    run = subprocess.run(command, capture_output=True, text=True, env=env)
    if run.returncode:
        raise RuntimeError(run.stderr)
    commands.append({'argv': command, 'exit_code': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr})
    result = {'evidence_level': 'static_only', 'source_pins_checked': len(pins['sources']),
              'example_guard': guard, 'defconfig': commands, 'build_performed': False,
              'owned_memory_request': {'review': 'R-001', 'bytes': 0x20000000,
                                       'physical_allocation_observed': False},
              'hardware_executed': False, 'donor_note': 'uses saved audit; rerun audit_inputs.py for complete content hashing'}
    (ROOT / 'reports/workspace-check.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('PASS: source pins, donor identity, upstream defconfig and example guard; no build performed')


if __name__ == '__main__':
    main()
