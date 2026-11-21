#!/usr/bin/env python3
"""Compile actual extracted query/UFS/publication bodies against host dependency mocks."""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parents[1] / 'UniXNU'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def equivalence(tu, original):
    start = original.index('static int verifiedVolumeQuery(')
    end = original.index('\nbool NativeVirtioBlock::configureVerification()', start)
    expected = original[start:end]
    first = expected.index('      NativeVirtioBlock *block =')
    last = expected.index('\n    }\n  }\n  iterator->release();', first)
    retained = '''      if (native_ufs_block_authenticates) {
        int ufs = native_ufs_block_authenticates(provider, uuid->getCStringNoCopy(), manifestDigest);
        if (ufs >= 0) {
          authenticated = ufs == 1;
          native_verified_block_root_uuid_match = authenticated;
          native_verified_block_wrong_uuid_refused = 1;
          break;
        }
      }
      continue;'''
    expected = expected[:first] + retained + expected[last:]
    actual = tu[tu.index('static int verifiedVolumeQuery('):]
    require(actual.rstrip() == expected.rstrip(), 'query extraction differs beyond removal of the Virtio branch')
    return ''.join(difflib.unified_diff(original[start:end].splitlines(True), actual.splitlines(True),
                                      fromfile='pinned/NativeVirtioBlock.cpp:250-371', tofile='EnumaUfsOwnerQuery.cpp'))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build-output', type=Path, required=True)
    p.add_argument('--output', type=Path, help='Fresh host-test output; defaults to BUILD_OUTPUT/query-host')
    a = p.parse_args()
    out = a.build_output.resolve()
    require(out.is_relative_to((ROOT / 'out').resolve()), 'output outside device out/')
    test = a.output.resolve() if a.output else out / 'query-host'
    require(test.is_relative_to((ROOT / 'out').resolve()), 'host-test output outside device out/')
    require(not test.exists(), 'host test output must be new')
    test.mkdir()
    source = ROOT / 'package/EnumaUfsOwnerQuery.cpp'
    tu = source.read_text()
    original = (BASE / 'drivers/VirtioMmioBlock/NativeVirtioBlock.cpp').read_text()
    module = BASE / 'drivers/VirtioMmioBlock'
    revision = subprocess.check_output(['git', '-C', str(module), 'rev-parse', 'HEAD'], text=True).strip()
    require(revision == '4e1013eb8c45077b57f8d38d61b389fe899ea1c3', 'query reference module revision changed')
    pinned = subprocess.check_output(['git', '-C', str(module), 'show', revision + ':NativeVirtioBlock.cpp'])
    # The Windows submodule checkout uses CRLF; code must equal the pinned blob
    # after that deterministic newline conversion, with both hashes recorded.
    require(pinned.replace(b'\r\n', b'\n').decode() == original, 'query reference differs from pinned module source')
    delta = equivalence(tu, original)
    (test / 'extraction.diff').write_text(delta)
    ufs = (out / 'source-ufs/NativeUfs.cpp').read_text()
    auth = ufs[ufs.index('bool NativeUfsBlock::authenticatesVolume ('):ufs.index('\nbool NativeUfsBlock::signedVolumeUuid (')]
    hook = ufs[ufs.index('extern "C" int native_ufs_block_authenticates ('):ufs.index('\n#endif', ufs.index('extern "C" int native_ufs_block_authenticates ('))]
    bsd = (out / 'source-xnu/iokit/bsddev/IOKitBSDInit.cpp').read_text()
    at = bsd.index('extern "C" int\nnative_owner_publish_boot_manifest(')
    publish = bsd[at:bsd.index('\n#endif', at)]
    body = '\n'.join(line for line in tu.splitlines() if not line.startswith('#include'))
    # Forward weak declaration stays after the real hook's declaration but before
    # its definition, as on target. No algorithm or acceptance condition rewritten.
    implementation = body + '\n#define NATIVE_UFS_OBSERVATION_ONLY 0\n' + auth + '\n' + hook + '\n' + publish
    harness = (ROOT / 'scripts/tests/enuma_ufs_owner_query_host.cpp').read_text()
    (test / 'actual.cpp').write_text(harness.replace('// INSERT_ACTUAL_IMPLEMENTATIONS', implementation))
    reports = [json.loads((ROOT / f'out/verify-fresh-20261113/{label}/result.json').read_text()) for label in ('os', 'systemos')]
    expected = []
    for r, size in zip(reports, (47481664, 25805344)):
        blob = Path(r['policy_path']).read_bytes()
        require(len(blob) == size and sha(blob) == r['policy_sha256'], 'real verified policy envelope changed')
        expected.append(hashlib.sha384(blob).digest())
    combined = hashlib.sha384(b'VerifiedRoot.OwnerBootSet.v1\0' + b'\x01' + expected[0] + b'\x02' + expected[1]).hexdigest()
    commands = []
    # The parent target builder puts cctools/clang shims first in PATH. Host
    # fixtures must use the system compiler AND its system assembler/linker.
    host_env = dict(os.environ, PATH='/usr/bin:/bin')
    host_env.pop('CCC_OVERRIDE_OPTIONS', None)
    def run(argv):
        log = test / ('command-%02d.log' % len(commands))
        with log.open('w') as f:
            result = subprocess.run(list(map(str, argv)), env=host_env, stdout=f, stderr=subprocess.STDOUT)
        commands.append({'argv': list(map(str, argv)), 'exit': result.returncode, 'PATH': host_env['PATH'], 'log_sha256': sha(log.read_bytes())})
        require(result.returncode == 0, 'host actual-body test failed: ' + str(log))
        return log.read_text()
    run(['/usr/bin/c++', '-std=c++17', '-Wno-deprecated-declarations', '-I', BASE / 'kits/VerifiedRoot/include',
         test / 'actual.cpp', '-lcrypto', '-o', test / 'test'])
    output = run([test / 'test', *[r['policy_path'] for r in reports], *[r['volume_uuid'] for r in reports]])
    require('OS=' + expected[0].hex() in output and 'SYSTEMOS=' + expected[1].hex() in output and
            'BOOTSET=' + combined in output, 'independent Python SHA384 composition differs from actual C implementation')
    result = {'status': 'self-checked actual function bodies; mocked IOKit dependencies, no hardware',
              'build_output': str(out),
              'commands': commands, 'query_source_sha256': sha(source.read_bytes()),
              'reference_source_sha256': sha((module / 'NativeVirtioBlock.cpp').read_bytes()),
              'reference_normalized_sha256': sha(original.encode()), 'extraction_diff_sha256': sha(delta.encode()),
              'reference_module_revision': revision,
              'actual_ufs_auth_body_sha256': sha(auth.encode()), 'actual_ufs_hook_sha256': sha(hook.encode()),
              'actual_publish_body_sha256': sha(publish.encode()), 'policy_envelope_bytes': [47481664, 25805344],
              'sha384': {'OS': expected[0].hex(), 'SystemOS': expected[1].hex(), 'OwnerBootSet': combined},
              'padding_key_excluded': True, 'test_output': output}
    (test / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print('self-checked: actual query/UFS/publication bodies, rejection cases and independent SHA384 composition')


if __name__ == '__main__':
    main()
