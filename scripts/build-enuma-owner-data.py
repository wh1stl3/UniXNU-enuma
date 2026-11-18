#!/usr/bin/env python3
"""Offline owner/Data configuration, dependency rebuild and final-byte audit.

Run under WSL root with Python 3.11. Never opens a device or installs a store.
The prepared tree and r4 are read-only inputs; outputs must be new device out/.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tomllib
import uuid
from types import SimpleNamespace

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parents[1] / 'UniXNU'
PIN = '693f5d9cae8a408dd18b39f3f9fdc4228c934241'
R4 = ROOT / 'out/production-final-link-guard-20261113-r4'
TREE = Path('/root/enuma-step10/UniXNU/out/enuma-ufs-version-diagnostic-20261112-python311/out/enuma/ipados-17.7.11-21H461/enuma/tree')
OBJ = TREE / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837'
SEED = ROOT / 'out/data-seed-transfer-20261113/received-43379610501'
TRUST = ROOT / 'out/production-os-trust-20261113/original-static-system.bundle'
TRUST_SHA = '7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7'
ON = ('OWNER_ROOT_AUDIT', 'OWNER_ROOT_TRUST', 'OWNER_CACHE_MOUNT',
      'OWNER_CACHE_STARTUP', 'OWNER_BOOT_MANIFEST', 'OWNER_DATA_MOUNT',
      'OWNER_UNION_SYSTEMOS')
OFF = ('VERIFIED_ROOT_PROBE', 'OWNER_CRYPTEX_FILES', 'NATIVE_AIR_INIT',
       'OWNER_CACHE_CARRIER', 'OWNER_CACHE_CARRIER_WRONG_UUID')
UNITS = {'bsd/kern/bsd_init.c': ('bsd/DEVELOPMENT/bsd_init.o', ON[:2]),
         'iokit/bsddev/IOKitBSDInit.cpp': ('iokit/DEVELOPMENT/IOKitBSDInit.cpo', ('OWNER_BOOT_MANIFEST',)),
         'bsd/kern/kern_exec.c': ('bsd/DEVELOPMENT/kern_exec.o', ON[2:])}
STORE_NAMES = tuple('_native_ufs_store_' + s for s in ('mode', 'open', 'read', 'write', 'sync', 'gpt_check'))
QUERY_NAMES = tuple('_native_verified_block_' + s for s in ('root_authorized', 'volume_device', 'manifest_sha384'))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def data_binding(header, manifest):
    actual = re.findall(r'^#define XNU_OWNER_DATA_VOLUME_UUID "([^"]+)"$', header, re.M)
    require(actual == [str(uuid.UUID(manifest['data']['volume_uuid'])).upper()],
            'Data UUID mismatch against independently verified local seed manifest')


def audit(out):
    r = json.loads((out / 'result.json').read_text())
    for p, identity in r['inputs'].items():
        require(sha(p) == identity['sha256'], 'input changed: ' + p)
    data_binding((out / 'owner-data-volume.h').read_text(), json.loads((SEED / 'manifest.json').read_text()))
    old = load_module('owner_data_final_bytes', ROOT / 'scripts/audit-enuma-production-final-link.py')
    reports = [json.loads((ROOT / f'out/verify-fresh-20261113/{s}/result.json').read_text()) for s in ('os', 'systemos')]
    result = {'status': 'self-checked', 'hardware_admission': False,
              'native': old.audit_image(out / 'native.macho', r['native_sha256'], reports),
              'prelink': old.audit_image(out / 'prelink.macho', r['prelink_sha256'], reports)}
    text = (out / 'native-link.map').read_text(errors='replace')
    owners = dict(re.findall(r'^\[\s*(\d+)\]\s+(.+)$', text, re.M))
    active = text.split('# Symbols:', 1)[1].split('# Dead Stripped Symbols:', 1)[0]
    expected = dict(old.OWNERS, **{s: 'NativeUfs.o' for s in STORE_NAMES})
    expected.update({s: 'EnumaUfsOwnerQuery.o' for s in QUERY_NAMES})
    expected['_native_ufs_block_authenticates'] = 'NativeUfs.o'
    expected.update({'_native_owner_publish_boot_manifest': 'IOKitBSDInit.cpo',
                     '_native_owner_root_trust_enabled': 'bsd_init.o',
                     '_native_owner_data_status': 'kern_exec.o',
                     '_native_ram_block_volume_seed': 'NativeRamBlock.o'})
    attribution = {}
    for symbol, member in expected.items():
        matches = re.findall(r'^\s*(0x[0-9a-fA-F]+)\s+0x[0-9a-fA-F]+\s+\[\s*(\d+)\]\s+' + re.escape(symbol) + r'\s*$', active, re.M)
        require(len(matches) == 1, 'nonunique live symbol: ' + symbol)
        va, index = matches[0]
        owner = owners[index]
        if symbol in old.OWNERS:
            want = str(out / 'libVerifiedRootProduction.a') + '(' + member + ')'
        elif symbol in STORE_NAMES or symbol == '_native_ufs_block_authenticates':
            want = str(out / 'libShengUfs.a') + '(' + member + ')'
        elif member == 'NativeRamBlock.o':
            want = str(out / 'libRamBlock.a') + '(' + member + ')'
        else:
            want = str(out / 'objects' / member)
        require(owner == want, 'wrong symbol owner: ' + symbol + ': ' + owner)
        attribution[symbol] = {'va': int(va, 16), 'owner': owner}
    require('EnumaRamBlockStore' not in text, 'observation store unexpectedly linked')
    require('NativeVirtioBlock' not in text and 'libVirtioMmioBlock' not in text, 'unexpected Virtio transport in link map')
    query_nm = subprocess.check_output(['llvm-nm', '-m', str(out / 'objects/EnumaUfsOwnerQuery.o')], text=True)
    require('NativeVirtio' not in query_nm and 'native_virtio_' not in query_nm and
            'probe' not in query_nm and 'IOMemory' not in query_nm, 'query TU gained transport/probe imports')
    result['query_object_sha256'] = sha(out / 'objects/EnumaUfsOwnerQuery.o')
    result['query_host'] = json.loads((out / 'query-host/result.json').read_text())
    require(result['query_host']['query_source_sha256'] == sha(out / 'device/package/EnumaUfsOwnerQuery.cpp'),
            'tested query differs from target input')
    result['live_owners'] = attribution
    result['archives'] = {}
    for path in sorted({m[1] for owner in owners.values() if (m := re.match(r'(.+\.a)\(', owner))}):
        require(sha(path) == r['inputs'][path]['sha256'], 'unbound final archive: ' + path)
        result['archives'][path] = sha(path)
    for member in ('verified_root.o', 'xnu_crypto.o', 'provider.o'):
        blob = subprocess.check_output(['llvm-ar', 'p', str(out / 'libVerifiedRootProduction.a'), member])
        p = ROOT / 'out/provider-rebuild-20261113' / member
        require(hashlib.sha256(blob).hexdigest() == r['inputs'][str(p)]['sha256'], 'provider bytes changed')
    result['signature_validation'] = 'inherited independent full-block reports, not repeated'
    result['budget'] = r['budget']
    result['geometry'] = r['geometry']
    (out / 'audit.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def build(out):
    require(out.is_relative_to((ROOT / 'out').resolve()) and not out.exists(), 'output must be new device out/')
    require(subprocess.check_output(['git', '-C', BASE, 'rev-parse', 'HEAD'], text=True).strip() == PIN, 'base HEAD changed')
    subprocess.run(['git', '-C', ROOT, 'check-ignore', str(out)], check=True, capture_output=True)
    out.mkdir(parents=True)
    r = {'status': 'self-checked in progress', 'base_head': PIN, 'commands': [], 'inputs': {},
         'GR0': 'NO-GO', 'admission': 'NoAccessPolicy/NoContract unchanged',
         'deployment': False, 'runtime_qualified': False, 'native_linked': False, 'prelinked': False}
    def save():
        (out / 'result.json').write_text(json.dumps(r, indent=2) + '\n')
    def record(p):
        p = Path(p).resolve()
        r['inputs'][str(p)] = {'bytes': p.stat().st_size, 'sha256': sha(p)}
        return p
    sys.path.insert(0, str(BASE / 'scripts'))
    from unixnu.kernel import linux_env, xnu_env
    from unixnu.config import parse_config
    env = dict(os.environ, **linux_env(SimpleNamespace(tree=TREE)))
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['PATH'] = '/home/wh1stl3/.local/bin:' + env['PATH']
    def run(argv, cwd=out):
        argv = list(map(str, argv))
        log = out / ('command-%02d.log' % len(r['commands']))
        with log.open('w') as stream:
            p = subprocess.run(argv, cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT)
        r['commands'].append({'argv': argv, 'cwd': str(cwd), 'exit': p.returncode,
                              'log': str(log), 'log_sha256': sha(log)})
        save()
        require(p.returncode == 0, f'command failed exit {p.returncode}: {log}')
        return log.read_text()
    try:
        r['upstream_head_at_start'] = run(['git', '-C', BASE, 'ls-remote', 'origin', 'HEAD']).strip()
        baseline = json.loads(record(R4 / 'result.json').read_text())
        # Qualified inputs may be reused, not modified; never hash the 9 GB root image.
        for p, identity in baseline['inputs'].items():
            require(sha(p) == identity['sha256'], 'r4 input changed: ' + p)
            r['inputs'][p] = identity
        for p in (ROOT / 'board.toml', ROOT / 'configs/enuma_defconfig', ROOT / 'patches/xnu/series',
                  BASE / 'scripts/unixnu/kernel.py', BASE / 'scripts/unixnu/config.py', Path(__file__)):
            record(p)
        r['diagnostic_before'] = {str(p): sha(p) for p in (ROOT / 'board.toml', ROOT / 'configs/enuma_defconfig', ROOT / 'patches/xnu/series')}
        manifest = json.loads(record(SEED / 'manifest.json').read_text())
        data = manifest['data']
        require(data['bytes'] == 3 * 1024**3 and data['encoded_bytes'] == 1171584, 'not verified 3 GiB seed')
        require(sha(record(SEED / 'data.dbr')) == data['encoded_sha256'], 'packed seed changed')
        require(sha(record(TRUST)) == TRUST_SHA and TRUST.stat().st_size == 61356, 'production OS trust changed')
        record(ROOT / 'out/verify-data-seed-receipt-20261113/result.json')
        profile = tomllib.loads(record(BASE / 'profiles/os/ipados-17.7.11-21H461/profile.toml').read_text())
        root_uuid = profile['root']['os_volume_uuid']
        cache_report = json.loads(record(ROOT / 'out/verify-fresh-20261113/systemos/result.json').read_text())
        cache_uuid = cache_report['volume_uuid']
        r['uuids'] = {'root': root_uuid, 'cache': cache_uuid, 'data': data['volume_uuid']}
        for label, value in (('os', root_uuid), ('systemos', cache_uuid)):
            vr = json.loads(record(ROOT / f'out/verify-fresh-20261113/{label}/result.json').read_text())
            require(value == vr['volume_uuid'], 'profile/policy UUID mismatch: ' + label)
        # An isolated format-2 device copy; no mutation of the default restore board.
        dev = out / 'device'
        dev.mkdir()
        for name in ('configs', 'dts', 'patches', 'package'):
            shutil.copytree(ROOT / name, dev / name)
        shutil.copytree(ROOT / 'scripts', dev / 'scripts', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for name in ('feeds.toml', 'unixnu.lock', 'proprietary-files.txt'):
            if (ROOT / name).exists():
                shutil.copy2(ROOT / name, dev / name)
        board = (ROOT / 'board.toml').read_text()
        board = '\n'.join(line for line in board.splitlines() if not line.lstrip().startswith('#')) + '\n'
        for name in ('build-enuma-ram-block-store.py', 'build-enuma-ufs-observe.py'):
            board, n = re.subn(r'^\s*"' + re.escape(name) + r'",\n', '', board, flags=re.M)
            require(n == 1, 'unexpected archive recipe: ' + name)
        # Runtime enuma provider reads pmgr; unchanged host payload guard reads
        # sheng-pmgr. Both get exactly one value 2; neither name substitutes for
        # the other, and no new runtime alias is invented.
        args = ['-v', 'serial=3', 'native-ufs-root=1', 'pmgr=2', 'sheng-pmgr=2', 'sheng-data-persist=2', 'sheng-log-reserve=1024']
        runtime_pmgr = record(ROOT / 'package/ShengPlatformPower.cpp').read_text()
        host_payload = record(BASE / 'scripts/unixnu/payload.py').read_text()
        require('PE_parse_boot_argn("pmgr", &mode, sizeof(mode))' in runtime_pmgr and
                "values.get('sheng-pmgr') != ['2']" in host_payload, 'PMGR argument contracts changed')
        r['pmgr_argument_contract'] = {'pmgr=2': 'actual enuma runtime provider',
                                      'sheng-pmgr=2': 'unchanged official host payload guard; not runtime alias'}
        board = re.sub(r'^kernel_args = .*$', 'kernel_args = ' + json.dumps(args), board, flags=re.M)
        board = re.sub(r'^trust_cache_sha256 = .*$', 'trust_cache_sha256 = ["' + TRUST_SHA + '"]', board, flags=re.M)
        # The ADT root-match must name the media that carries the root. This build's root is the
        # signed OS window, whose IOMedia UUID is the UUID inside the OS VROOT01 policy, so the
        # restore ramdisk UUID on the default diagnostic board is not admissible here.
        board, replaces = re.subn(r'^root_match_volume_uuid = .*$',
                                  'root_match_volume_uuid = ' + json.dumps(root_uuid), board, flags=re.M)
        require(replaces == 1, 'root_match_volume_uuid must occur exactly once in board.toml')
        board = board.replace('enuma_defconfig', 'enuma_owner_data_defconfig')
        board = board.replace('unixnu = "../../UniXNU"', 'unixnu = ' + json.dumps(str(BASE)))
        board += '\n[root]\nos_volume_uuid = ' + json.dumps(root_uuid) + '\nsystemos_volume_uuid = ' + json.dumps(cache_uuid) + '\n'
        (dev / 'board.toml').write_text('# OFFLINE ONLY; no hardware admission, install or deployment.\n' + board)
        # Packaging-time gate: the official generator copies this option verbatim into
        # /chosen/root-matching (UniXNU/scripts/unixnu/devicetree.py:324-327), and the root media's
        # UUID is the one the OS policy signs (NativeUfsBlock::signedVolumeUuid). Declaring the
        # restore ramdisk UUID here would make the boot wait on a UUID this image cannot carry.
        written = tomllib.loads((dev / 'board.toml').read_text())
        require('native-ufs-root=1' in written['payload']['kernel_args'],
                'owner/Data build must select the native UFS root')
        require(written['payload']['adt']['root_match_volume_uuid'] == root_uuid,
                'board root_match_volume_uuid ' + str(written['payload']['adt']['root_match_volume_uuid']) +
                ' must be the signed OS window UUID ' + root_uuid)
        conf = (ROOT / 'configs/enuma_defconfig').read_text()
        conf += '\n# Actual owner/Data dependency closure; UUID only in this ignored candidate.\n'
        for name in ON:
            conf += 'CONFIG_XNU_' + name + '=y\n'
        for name in OFF:
            conf += 'CONFIG_XNU_' + name + '=n\n'
        conf += 'CONFIG_XNU_SOURCE_STORAGE=y\nCONFIG_XNU_OWNER_DATA_VOLUME_UUID=' + json.dumps(data['volume_uuid']) + '\n'
        crypto_mode = record(OBJ / 'osfmk/DEVELOPMENT/.crypto-bootstrap-mode').read_text().strip()
        require(crypto_mode == baseline['crypto_bootstrap_mode'] and crypto_mode in ('source', 'prelinked'),
                'actual r4/prepared crypto mode mismatch')
        conf += 'CONFIG_XNU_CRYPTO_BOOTSTRAP=' + json.dumps(crypto_mode) + '\n'
        r['crypto_bootstrap_mode'] = crypto_mode
        r['crypto_rebuilt'] = False
        # SOURCE_STORAGE suppresses the legacy auto-RamBlock link. Supply the real
        # built-in RAM consumer and the previously verified static owner provider.
        extra = ' '.join('-Wl,-force_load,' + str(out / name) for name in ('libRamBlock.a', 'libVerifiedRootProduction.a'))
        extra += ' ' + str(out / 'objects/EnumaUfsOwnerQuery.o')
        conf += 'CONFIG_XNU_EXTRA_LD_ARCHIVES=' + json.dumps(extra) + '\n'
        configpath = dev / 'configs/enuma_owner_data_defconfig'
        configpath.write_text(conf)
        values = {}
        for fragment in (BASE / 'profiles/arch/arm64/configs/common.config',
                         ROOT.parent / 'UniXNU-sm8250-common/configs/sm8250.config',
                         BASE / 'profiles/os/ipados-17.7.11-21H461/configs/ipados.config', configpath):
            values.update(parse_config(record(fragment).read_text()))
        (out / 'merged.config.json').write_text(json.dumps(values, indent=2) + '\n')
        r['config_environment'] = xnu_env(SimpleNamespace(need_config=lambda: values, tree=out))
        r['kernel_args'] = args
        header = out / 'owner-data-volume.h'
        # Execute the exact official generator, not a handwritten equivalent.
        official = record(BASE / 'scripts/build-xnu-4k-baseline.sh').read_text()
        generator = official.split("<<'PY_DATA_UUID'\n", 1)[1].split('\nPY_DATA_UUID', 1)[0]
        genpath = out / 'official-data-header.py'
        genpath.write_text(generator + '\n')
        run([sys.executable, genpath, header, '1', '1', data['volume_uuid'], cache_uuid, root_uuid, '1'])
        data_binding(header.read_text(), manifest)
        record(header)
        record(configpath)
        record(dev / 'board.toml')
        # Copy all source headers, not just .c bodies, and redirect both historical aliases.
        source = out / 'source-xnu'
        shutil.copytree(TREE / '.cache/xnu-work', source, ignore=shutil.ignore_patterns('.git'))
        aliases = (str(TREE / '.cache/xnu-work'),
                   '/root/enuma-step10/UniXNU/out/enuma/ipados-17.7.11-21H461/enuma/tree/.cache/xnu-work')
        # Use the official resolver's git-apply semantics, not GNU patch. Prevent
        # discovery of the containing device Git repository in these private copies.
        env['GIT_CEILING_DIRECTORIES'] = str(out)
        # Exact reverse checks show the two independent official patches are already applied.
        for name in ('offline-owner-root-binding-audit.patch', 'offline-owner-boot-manifest.patch'):
            patch = record(BASE / 'patches/xnu' / name)
            run(['git', 'apply', '--reverse', '--check', patch], source)
        # Verify the SystemOS patch with its existing official followups undone only in a check copy.
        check = out / 'patch-check'
        shutil.copytree(source, check)
        for name in ('zzyb-native-cryptex-os-view.patch',
                     'zzy-staged-system-apps.patch', 'zzy-native-gpu-addon-mount.patch',
                     'offline-owner-z-air-init.patch'):
            patch = record(BASE / 'patches/xnu' / name)
            run(['git', 'apply', '--reverse', patch], check)
        patch = record(BASE / 'patches/xnu/offline-owner-systemos-mount.patch')
        run(['git', 'apply', '--reverse', '--check', patch], check)
        r['patch_validation'] = 'official git-apply reverse checks; later official SystemOS followups reversed only in patch-check, never compiled source'
        objects = out / 'objects'
        objects.mkdir()
        replacements = {}
        r['recompiled_units'] = {}
        for relative, (obj, enabled) in UNITS.items():
            rec = json.loads(record(OBJ / (obj + '.json')).read_text().strip().rstrip(','))
            command = rec['arguments'].copy()
            command[command.index(rec['file'])] = str(record(source / relative))
            dest = objects / Path(obj).name
            command[command.index('-o') + 1] = str(dest)
            changes = {name: 1 for name in enabled}
            for i, value in enumerate(command):
                for name in changes:
                    if value.startswith('XNU_' + name + '='):
                        command[i] = 'XNU_' + name + '=1'
                if value.endswith('/build/xnu/owner-data-volume.h'):
                    command[i] = str(header)
            command = [next((v.replace(old, str(source)) for old in aliases if old in v), v) for v in command]
            # Compiler-record outputs are all redirected; includes remain read-only.
            require('-MJ' not in command and '-MF' not in command, 'unredirected dependency output in replay record')
            trace = run(command + ['-###'], rec['directory'])
            cc1 = [shlex.split(line) for line in trace.splitlines() if '"-cc1"' in line]
            require(len(cc1) == 1, 'unexpected compiler trace')
            defs = [cc1[0][i + 1] for i, v in enumerate(cc1[0][:-1]) if v == '-D']
            for name in changes:
                require([v for v in defs if v.split('=')[0] == 'XNU_' + name] == ['XNU_' + name + '=1'],
                        'conflicting/missing macro: ' + name)
            run(command, rec['directory'])
            pp = command.copy()
            pp[pp.index('-c')] = '-E'
            pp[pp.index('-o') + 1] = str(objects / (dest.name + '.i'))
            run(pp, rec['directory'])
            # Full macro dump includes forced header and generated configuration dependencies.
            pp += ['-dM']
            pp[pp.index('-o') + 1] = str(objects / (dest.name + '.macros'))
            run(pp, rec['directory'])
            if relative.endswith('kern_exec.c'):
                macros = (objects / (dest.name + '.macros')).read_text()
                require('#define CONFIG_UNION_MOUNTS 1' in macros, 'native union implementation disabled')
                for name in ('NATIVE_AIR_INIT', 'OWNER_CRYPTEX_FILES'):
                    require('#define XNU_' + name + ' 0' in macros, 'unrequested startup experiment')
                for name, value in r['uuids'].items():
                    require(value in macros, 'forced UUID header missing: ' + name)
            replacements[str(OBJ / obj)] = str(dest)
            r['recompiled_units'][relative] = {'object': str(dest), 'sha256': sha(dest), 'enabled': list(enabled)}
            record(dest)
        # Recompile the unmodified official big-seed/direct-store consumer too.
        ram_source = out / 'source-ram'
        shutil.copytree(BASE / 'drivers/RamBlock', ram_source)
        ram_command = json.loads(record(TREE / 'build/ram-block/compile-command.json').read_text())
        ram_command[next(i for i, v in enumerate(ram_command) if v.endswith('/NativeRamBlock.cpp'))] = str(ram_source / 'NativeRamBlock.cpp')
        ram_command[ram_command.index('-o') + 1] = str(out / 'NativeRamBlock.o')
        run(ram_command, json.loads((OBJ / 'iokit/DEVELOPMENT/IOPlatformExpert.cpo.json').read_text().strip().rstrip(','))['directory'])
        for p in ram_source.iterdir():
            if p.is_file():
                record(p)
        for name in ('libShengUfs.a', 'libVerifiedRootProduction.a', 'libRamBlock.a'):
            shutil.copy2(record(R4 / name), out / name)
        run(['llvm-ar', 'r', out / 'libRamBlock.a', out / 'NativeRamBlock.o'])
        require(run(['llvm-ar', 't', out / 'libRamBlock.a']).splitlines() == ['NativeRamBlock.o', 'original-bindings.o'], 'unexpected RAM provider')
        for name in ('libShengUfs.a', 'libVerifiedRootProduction.a', 'libRamBlock.a'):
            record(out / name)
        shutil.copytree(R4 / 'source', out / 'source-ufs')
        for p in (out / 'source-ufs').iterdir():
            if p.is_file():
                record(p)
        # Compile only the exact UFS-only query extraction, not a Virtio object.
        query_source = record(dev / 'package/EnumaUfsOwnerQuery.cpp')
        record(ROOT / 'package/UFS-OWNER-QUERY-LICENSE')
        record(BASE / 'drivers/VirtioMmioBlock/NativeVirtioBlock.cpp')
        record(BASE / 'drivers/VirtioMmioBlock/LICENSE')
        record(ROOT / 'scripts/check-enuma-ufs-owner-query.py')
        record(ROOT / 'scripts/tests/enuma_ufs_owner_query_host.cpp')
        run([sys.executable, ROOT / 'scripts/check-enuma-ufs-owner-query.py', '--build-output', out])
        query_recipe = json.loads(record(OBJ / 'iokit/DEVELOPMENT/IOPlatformExpert.cpo.json').read_text().strip().rstrip(','))
        query_command = query_recipe['arguments'].copy()
        query_command[query_command.index(query_recipe['file'])] = str(query_source)
        query_object = out / 'objects/EnumaUfsOwnerQuery.o'
        query_command[query_command.index('-o') + 1] = str(query_object)
        require('-MJ' not in query_command and '-MF' not in query_command, 'unredirected query compiler output')
        run(query_command, query_recipe['directory'])
        query_nm = run(['llvm-nm', '-m', query_object])
        require(not any(s in query_nm for s in ('NativeVirtio', 'native_virtio_', 'probe', 'IOMemory')),
                'query object contains transport/probe dependency')
        r['query_object_sha256'] = sha(record(query_object))
        r['query_source_sha256'] = sha(query_source)
        record(out / 'query-host/result.json')
        require(sha(out / 'libShengUfs.a') == sha(R4 / 'libShengUfs.a'), 'changed r4 ShengUfs bytes')
        r['consumer_sha256'] = baseline['consumer_sha256']
        r['consumer_patch_sha256'] = baseline['consumer_patch_sha256']
        r['consumer_defines'] = baseline['consumer_defines']
        require(r['consumer_defines']['NATIVE_UFS_EXTERNAL_STORE_PROVIDER'] == 0, 'not built-in store')
        filelist = out / 'link.filelist'
        oldlist = (OBJ / 'link.filelist').read_text().splitlines()
        require(all(oldlist.count(p) == 1 for p in replacements), 'changed object not uniquely in kernel filelist')
        filelist.write_text('\n'.join(replacements.get(p, p) for p in oldlist) + '\n')
        record(filelist)
        link = next(c for c in baseline['commands'] if c['argv'][0].endswith('/clang++') and '-filelist' in c['argv'])
        command = [v.replace(str(R4), str(out)) for v in link['argv']]
        command[command.index('-filelist') + 1] = str(filelist)
        command.append(str(query_object))
        run(command, link['cwd'])
        r['native_linked'] = True
        require(not run(['llvm-nm', '-u', out / 'native.macho']).strip(), 'undefined final native symbol')
        if baseline['crypto_bootstrap_mode'] == 'source':
            run([sys.executable, BASE / 'scripts/seal-source-crypto-kernel.py', out / 'native.macho'])
        r['native_sha256'] = sha(out / 'native.macho')
        pre = next(c for c in baseline['commands'] if '--prelinked' in c['argv'])
        run([v.replace(str(R4), str(out)) for v in pre['argv']])
        r['prelinked'] = True
        r['prelink_sha256'] = sha(out / 'prelink.macho')
        # Execute the actual unchanged native-root payload guard without building
        # a payload or replacing its tool/schema implementation.
        guard = 'import sys,json; from pathlib import Path; sys.path.insert(0,sys.argv[1]); from unixnu.payload import check_native_root; check_native_root(Path(sys.argv[2]),json.loads(sys.argv[3])); print("actual payload native-root guard: PASS")'
        run([sys.executable, '-c', guard, BASE / 'scripts', out / 'prelink.macho', json.dumps(args)])
        history = json.loads(record(ROOT / 'out/production-recipe-r3/inputs.json').read_text())
        info = json.loads(record(history['intermediate']['report']).read_text())
        require(Path(history['intermediate']['image']).stat().st_size == info['image_bytes'], 'historical root size changed')
        pages = data['bytes'] // 4096
        bitmap = (pages + 32767) // 32768
        blocks = 1 + bitmap + pages
        first, last = 2686976, 61880314
        reserve = 1024 * 256
        start = last + 1 - reserve - blocks
        image_blocks = (info['image_bytes'] + 4095) // 4096
        partition = last - first + 1
        require(start - first >= image_blocks + 1024 and blocks <= partition - reserve, 'store overlaps historical root/guard')
        require(start + blocks <= 0xffffffff, 'WRITE(10) LBA bound')
        r['geometry'] = {'basis': 'offline historical geometry only; current GPT not read/verified',
                         'partition_first_lba4k': first, 'partition_last_lba4k': last,
                         'partition_blocks': partition, 'logical_seed_bytes': data['bytes'], 'pages': pages,
                         'bitmap_blocks': bitmap, 'store_blocks': blocks, 'store_bytes': blocks * 4096,
                         'store_first_lba4k': start, 'store_end_lba4k_exclusive': start + blocks,
                         'root_image_bytes': info['image_bytes'], 'root_guard_blocks': 1024,
                         'reserve_blocks': reserve, 'gap_after_root_guard_blocks': start - first - image_blocks - 1024,
                         'under_partition_quarter': blocks <= partition // 4,
                         'quarter_note': 'comment says quarter; actual native_ufs_store_open/hostStoreOpen has no quarter test; size/overlap and UINT32 tests above are actual code',
                         'root_image_sha256_inherited_not_rehashed': info['image_sha256']}
        measured = (out / 'prelink.macho').stat().st_size + data['encoded_bytes'] + TRUST.stat().st_size
        limit = 192 * 1024**2
        r['budget'] = {'prelink_bytes': (out / 'prelink.macho').stat().st_size,
                       'native_bytes': (out / 'native.macho').stat().st_size,
                       'packed_seed_bytes': data['encoded_bytes'], 'production_os_trust_bytes': TRUST.stat().st_size,
                       'candidate_adt_bytes': None, 'candidate_adt_status': 'not generated; restore/diagnostic ADT not substituted',
                       'measured_subtotal_bytes': measured, 'limit_bytes': limit, 'limit_95_percent_bytes': limit * 95 // 100,
                       'raw_remaining_before_adt_packaging_bytes': limit - measured,
                       'remaining_95_before_adt_packaging_bytes': limit * 95 // 100 - measured,
                       'complete_payload_fits': None, 'payload_or_bootimg_generated': False}
        r['activated_high_impact_paths'] = [
            'bsd_init mounted readonly OS acceptance via real owner verified-block binding, not probe',
            'kern_exec readonly SystemOS union and dyld no-ignition startup after reauthentication',
            'IOKitBSDInit publishes owner-domain boot-manifest metadata (refuses preexisting identity)',
            'native_owner_data_prepare selects exact seed UUID and mounts APFS /private/var read-write',
            'NativeRamBlock >2GiB requires direct RW store; no volatile write fallback',
            'native_ufs_store_open -> hostStoreOpen -> bounded FUA WRITE(10)/SYNCHRONIZE CACHE',
            'PersistOverlay fresh bitmap/header writes require sheng-data-reset=1/2; intentionally absent; blank store will not boot Data']
        r['review_scope'] = 'UFS-only exact query extraction: ordinary review before any default/runtime integration; root acceptance, owner domain and chosen contracts unchanged. Runtime hardware/store admission not requested.'
        r['upstream_head_at_end'] = run(['git', '-C', BASE, 'ls-remote', 'origin', 'HEAD']).strip()
        require(subprocess.check_output(['git', '-C', BASE, 'rev-parse', 'HEAD'], text=True).strip() == PIN, 'base HEAD changed')
        require(all(sha(p) == digest for p, digest in r['diagnostic_before'].items()), 'default diagnostic changed')
        r['status'] = 'self-checked native/prelink; ADT/packaging and independent review/verification outstanding'
        save()
        audit(out)
        # One negative UUID control; do not change the actual config or build output.
        wrong = header.read_text().replace(data['volume_uuid'], str(uuid.UUID(int=0)).upper())
        try:
            data_binding(wrong, manifest)
        except ValueError as error:
            r['negative_uuid_control'] = {'expected_rejection': str(error), 'passed': True}
        else:
            raise ValueError('wrong Data UUID accepted')
        r['diagnostic_unchanged'] = True
        save()
    except Exception as error:
        r['status'] = 'self-checked STOPPED at first failure'
        r['first_error'] = str(error)
        raise
    finally:
        save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('build', 'audit'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    require(out.is_relative_to((ROOT / 'out').resolve()), 'output outside device out/')
    if args.mode == 'build':
        build(out)
    else:
        audit(out)


if __name__ == '__main__':
    main()
