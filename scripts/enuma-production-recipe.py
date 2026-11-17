#!/usr/bin/env python3
"""Generate an incomplete, offline-only enuma production recipe; never package it."""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    from pip._vendor import tomli as tomllib

PIN = '693f5d9cae8a408dd18b39f3f9fdc4228c934241'
OS_UUID = '04769D26-2CA0-4825-B443-E2E5F88300F2'
SYS_UUID = '8846FE78-2910-4297-AF97-D59BB6F8FC16'
GIB, MIB = 1 << 30, 1 << 20
WINDOWS = [('OS', 1048576, 6077580800, OS_UUID),
           ('SystemOS', 6079643648, 3303014400, SYS_UUID)]
BLOCKERS = ['OS and SystemOS owner policies not supplied or authenticated',
            'owner anchor not supplied or authenticated', 'Apple OS trust bundle not established',
            'Data seed and Data UUID not supplied', 'Data packed seed/nonzero-page residency and payload budgets unknown',
            'arm64 static two-policy provider and linking not implemented',
            'current GPT, UFS ownership and hardware access gates not established (GR0 NO-GO)']
ARCHIVES = ['build-corecrypto-14.py', 'build-corecrypto-14.py --namespace',
            'component:ArmDTPlatform', 'component:ArmCpu', 'component:SoftwareAES',
            'build-software-aes-bindings.py', 'build-mockfs-fixture.py', 'build-libpthread-kernel.py',
            'component:RamBlock', 'prepare-ram-block-audit.py',
            'build-virtio-mmio-bindings.py --component RamBlock --directory build/ram-block',
            'component:ShengUfs', 'build-enuma-platform-power.py --inputs build/sheng-platform-power/inputs.json']
TARGET_ARGS = ['-v', 'serial=3', 'native-ufs-root=1', 'sheng-pmgr=2', 'sheng-data-persist=2']
REQUIRED_CONFIG = {'SOURCE_CORECRYPTO14': 'y', 'SOURCE_PTHREAD': 'y', 'ARM_DT_PLATFORM': 'y',
                   'ARMCPU': 'y', 'NATIVE_ARCH_TIMER': 'y', 'NATIVE_PAN': 'y', 'DT_PANIC_REGION': 'y',
                   'BOOT_PROGRESS': 'n', 'ARMVIRT_PLATFORM': 'n', 'SHENG_PMGR': 'y', 'NATIVE_UFS': 'y',
                   'NATIVE_ADRENO': 'n', 'NATIVE_MOBILE_DISPLAY': 'n', 'NATIVE_LEGACY_DISPLAY': 'n',
                   'NATIVE_RAM_BLOCK': 'y', 'TRUST_CACHE_RUNTIME': 'y', 'NATIVE_CS_HASH_CACHE': 'y',
                   'VERIFIED_ROOT_PROBE': 'y', 'OWNER_ROOT_AUDIT': 'y', 'OWNER_ROOT_TRUST': 'y',
                   'OWNER_CACHE_MOUNT': 'y', 'OWNER_CACHE_STARTUP': 'y', 'OWNER_BOOT_MANIFEST': 'y',
                   'OWNER_DATA_MOUNT': 'y', 'OWNER_UNION_SYSTEMOS': 'y'}


def auto(capacity, root, reserve):
    available = capacity - ((root + 4095) // 4096 * 4096) - 4 * MIB - reserve * MIB
    if available <= 0:
        raise ValueError('partition too small for root, guard and reserve')
    gib = available // GIB
    while gib > 0:
        pages = gib * GIB // 4096
        if (1 + (pages + 32767) // 32768 + pages) * 4096 <= available:
            break
        gib -= 1
    if gib <= 1:
        raise ValueError('partition too small for Data and one GiB margin')
    return gib - 1, available


def replace_once(text, pattern, replacement):
    result, count = re.subn(pattern, lambda _: replacement, text, flags=re.M | re.S)
    if count != 1:
        raise ValueError('diagnostic source no longer matches expected configuration: ' + pattern)
    return result


def generate(args):
    if args.reserve_mib != 1024:
        raise ValueError('reserve_mib must be 1024 for this fixed snapshot')
    source, base, output = (p.resolve() for p in (args.device, args.unixnu, args.output))
    report, provenance, image = (p.resolve() for p in (args.report, args.provenance, args.image))
    if output.exists() or source == output or source in output.parents and output.parent != source / 'out':
        raise ValueError('output must be a new direct child of device/out')
    if output.parent != source / 'out':
        raise ValueError('output must be a new direct child of device/out')
    head = subprocess.check_output(['git', '-C', str(base), 'rev-parse', 'HEAD'], text=True).strip()
    if head != PIN:
        raise ValueError('unexpected UniXNU HEAD: ' + head)
    info = json.loads(report.read_text())
    prov = json.loads(provenance.read_text())
    if prov['base_commit'] != PIN or info['image_bytes'] != image.stat().st_size:
        raise ValueError('intermediate provenance or image size mismatch')
    if [(w['name'], w['offset'], w['size']) for w in info['windows']] != [w[:3] for w in WINDOWS]:
        raise ValueError('unexpected raw window layout')
    root = info['image_bytes']
    if any(start < 0 or size <= 0 or start + size > root for _, start, size, _ in WINDOWS):
        raise ValueError('window outside intermediate image')
    if WINDOWS[0][1] + WINDOWS[0][2] > WINDOWS[1][1]:
        raise ValueError('overlapping windows')
    if args.capacity != (61880314 - 2686976 + 1) * 4096:
        raise ValueError('capacity differs from historical-primary-GPT geometry')
    gib, available = auto(args.capacity, root, args.reserve_mib)
    pages = gib * GIB // 4096
    store_bytes = (1 + (pages + 32767) // 32768 + pages) * 4096
    store_start = args.capacity - args.reserve_mib * MIB - store_bytes
    if store_start < (root + 4095) // 4096 * 4096 + 4 * MIB:
        raise ValueError('Data store overlaps root or guard')
    text = (source / 'board.toml').read_text()
    archives = tomllib.loads(text)['kernel']['archives']
    archives = [a for a in archives if a not in ('build-enuma-ram-block-store.py', 'build-enuma-ufs-observe.py')]
    if archives != ARCHIVES:
        raise ValueError('diagnostic source archives differ from fixed expected archives')
    text = replace_once(text, r'^archives = \[.*?^\]', 'archives = [\n' + ''.join('  ' + json.dumps(a) + ',\n' for a in archives) + ']')
    text = replace_once(text, r'^kernel_args = \[.*?\]$', 'kernel_args = ["-v", "serial=3", "native-ufs-root=1", "sheng-pmgr=2", "sheng-data-persist=2"]')
    text = replace_once(text, r'^root_match_volume_uuid = ".*?"$', 'root_match_volume_uuid = "' + OS_UUID + '"')
    # Diagnostic restore-only trust adapter is not part of the Apple OS trust bundle.
    text = replace_once(text, r'^trust_cache_sha256 = \[.*?\]$', 'trust_cache_sha256 = ["7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7", "8900d6a93d7a59ce1a872a5c081e559f4240a218f97e12d44d22dda46644d68f"]')
    text = text.replace('defconfig = "enuma_defconfig"', 'defconfig = "enuma_production_defconfig"')
    text = text.replace('= "enuma_defconfig"', '= "enuma_production_defconfig"')
    text = text.replace('unixnu = "../../UniXNU"', 'unixnu = ' + json.dumps(str(base)))
    text = '\n'.join(line for line in text.split('\n') if not line.startswith('#'))
    text = '# INCOMPLETE OFFLINE PLAN: NOT BUILDABLE OR DEPLOYABLE.\n' + text
    tomllib.loads(text)
    output.mkdir()
    device = output / 'device'
    device.mkdir()
    for name in ('configs', 'dts', 'patches', 'package', 'scripts'):
        shutil.copytree(source / name, device / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for name in ('feeds.toml', 'unixnu.lock', 'proprietary-files.txt'):
        if (source / name).is_file():
            shutil.copy2(source / name, device / name)
    (device / 'board.toml').write_text(text)
    defconfig = (source / 'configs/enuma_defconfig').read_text()
    defconfig += '\n# Offline target selections; provider/link inputs and Data UUID are missing.\n'
    for name in ('TRUST_CACHE_RUNTIME', 'NATIVE_CS_HASH_CACHE', 'VERIFIED_ROOT_PROBE', 'OWNER_ROOT_AUDIT',
                 'OWNER_ROOT_TRUST', 'OWNER_CACHE_MOUNT', 'OWNER_CACHE_STARTUP', 'OWNER_BOOT_MANIFEST',
                 'OWNER_DATA_MOUNT', 'OWNER_UNION_SYSTEMOS'):
        defconfig += 'CONFIG_XNU_' + name + '=y\n'
    (device / 'configs/enuma_production_defconfig').write_text(defconfig)
    (output / 'build.toml').write_text('[build]\ndevice = "device"\nout = "build-output"\n')
    manifest = {'status': 'blocked-incomplete-offline-only', 'base_commit': PIN,
                'intermediate': {'image': str(image), 'report': str(report), 'provenance': str(provenance),
                                 'image_sha256_prior_record_not_rehashed': info['image_sha256']},
                'geometry': {'basis': 'historical-primary-GPT; not current GPT verification', 'first_lba': 2686976,
                             'last_lba': 61880314, 'lba_bytes': 4096, 'capacity_bytes': args.capacity},
                'windows': [dict(name=n, offset=o, bytes=s, volume_uuid=u, policy='complete raw window; no SHNGROOT header or padding') for n, o, s, u in WINDOWS],
                'data_plan': {'reserve_mib': args.reserve_mib, 'available_bytes': available, 'auto_gib': gib,
                              'store_start_bytes': store_start, 'store_bytes': store_bytes,
                              'guard_bytes': 4 * MIB, 'packed_seed_bytes': None, 'nonzero_pages_resident_bytes': None,
                              'payload_budget_bytes': None, 'data_uuid': None},
                'policy_plan': 'arm64 static two-policy plus VROOTKEY RSA-3072 owner anchor; no arm64e VROOTB01 handoff',
                'trust': 'Apple trust bundle and owner policy anchor are distinct; existence is not signature verification',
                'dependencies': ['device-relative configs, dts, patches, package, scripts and feeds copied',
                                 'external SoC feed, official profiles, toolchain, firmware and build inputs still required'],
                'blockers': BLOCKERS}
    (output / 'inputs.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('BLOCKED: generated incomplete offline recipe at', output)


def check_plan(path):
    plan = json.loads((path / 'inputs.json').read_text())
    if plan['status'] != 'blocked-incomplete-offline-only':
        raise ValueError('snapshot status must remain blocked-incomplete-offline-only')
    if plan['blockers'] != BLOCKERS:
        raise ValueError('snapshot blockers differ from fixed complete list')
    board = tomllib.loads((path / 'device/board.toml').read_text())
    build = tomllib.loads((path / 'build.toml').read_text())
    if set(build) != {'build'} or build['build'] != {'device': 'device', 'out': 'build-output'}:
        raise ValueError('invalid build-only configuration')
    kernel = board['kernel']
    if kernel['defconfig'] != 'enuma_production_defconfig':
        raise ValueError('defconfig name differs from fixed snapshot')
    if kernel['archives'] != ARCHIVES:
        raise ValueError('archives differ from fixed expected list')
    args = board['payload']['kernel_args']
    if args != TARGET_ARGS:
        raise ValueError('kernel arguments differ from fixed target or contain duplicates/conflicts')
    if board['payload']['adt']['root_match_volume_uuid'] != OS_UUID:
        raise ValueError('incorrect root UUID')
    if [(w['name'], w['offset'], w['bytes'], w['volume_uuid']) for w in plan['windows']] != WINDOWS:
        raise ValueError('incorrect policy windows')
    g, data = plan['geometry'], plan['data_plan']
    if type(data['reserve_mib']) is not int or data['reserve_mib'] != 1024:
        raise ValueError('reserve_mib must be 1024 for this fixed snapshot')
    if (g['first_lba'], g['last_lba'], g['lba_bytes']) != (2686976, 61880314, 4096):
        raise ValueError('incorrect historical geometry')
    capacity = (g['last_lba'] - g['first_lba'] + 1) * g['lba_bytes']
    root = WINDOWS[-1][1] + WINDOWS[-1][2]
    gib, available = auto(capacity, root, data['reserve_mib'])
    pages = gib * GIB // 4096
    size = (1 + (pages + 32767) // 32768 + pages) * 4096
    start = capacity - data['reserve_mib'] * MIB - size
    if (g['capacity_bytes'], data['auto_gib'], data['available_bytes'], data['store_start_bytes'], data['store_bytes']) != (capacity, gib, available, start, size) or start < root + 4 * MIB:
        raise ValueError('incorrect Data layout')
    for name in ('configs/' + kernel['defconfig'], 'dts/enuma.dts', 'patches/xnu/series',
                 'patches/xnu/os-series', 'scripts/prepare-ram-block-audit.py', 'scripts/build-enuma-platform-power.py'):
        if not (path / 'device' / name).is_file():
            raise ValueError('missing device dependency: ' + name)
    config_text = (path / 'device/configs' / kernel['defconfig']).read_text()
    for name, expected in REQUIRED_CONFIG.items():
        values = re.findall(r'^CONFIG_XNU_' + re.escape(name) + r'=(\S+)\s*$', config_text, re.M)
        unset = re.search(r'^\s*#\s*CONFIG_XNU_' + re.escape(name) + r'\s+is not set\s*$', config_text, re.M)
        if values != [expected] or unset:
            raise ValueError('defconfig CONFIG_XNU_' + name + ' must occur once as ' + expected)
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    gen = sub.add_parser('generate')
    for name in ('device', 'unixnu', 'output', 'image', 'report', 'provenance'):
        gen.add_argument('--' + name, type=Path, required=True)
    gen.add_argument('--capacity', type=int, required=True)
    gen.add_argument('--reserve-mib', type=int, default=1024)
    check = sub.add_parser('check')
    check.add_argument('--recipe', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'generate':
            generate(args)
            return 0
        plan = check_plan(args.recipe)
        print('BLOCKED: fixed planning snapshot; input readiness not authenticated; no packaging supported')
        for item in plan['blockers']:
            print('-', item)
        return 2
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print('error:', error, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
