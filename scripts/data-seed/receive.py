#!/usr/bin/env python3
"""Download this run's ciphertext, CMS-decrypt locally, verify, then delete artifact.

Run under WSL with OpenSSL 3; --output must be a NEW directory under the local
ACL-restricted out/data-seed-transfer-20261113 directory. Never supply owner keys.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tarfile
import uuid

HERE = Path(__file__).resolve().parent
PIN = json.loads((HERE / 'source.json').read_text())
REPO = 'wh1stl3/UniXNU-enuma'


def run(*args):
    return subprocess.check_output([str(a) for a in args])


def apfs_checksum(page):
    a = b = 0
    for value in struct.unpack('<1022I', page[8:]):
        a = (a + value) % 0xffffffff
        b = (b + a) % 0xffffffff
    low = 0xffffffff - ((a + b) % 0xffffffff)
    high = 0xffffffff - ((a + low) % 0xffffffff)
    return page[:8] == struct.pack('<II', low, high)


def verify_seed(packer, seed, report, run_id, commit):
    if (report['source'] != PIN or str(report['run_id']) != str(run_id)
            or report['device_revision'] != commit or not report['first_install']
            or report['hardware_tested'] or report['data']['skip_setup']):
        raise ValueError('manifest provenance differs')
    metadata, nx = packer.inspect(seed)
    if not metadata['packed'] or metadata['bytes'] != PIN['seed_bytes']:
        raise ValueError('not a packed 3 GiB seed')
    for name, value in metadata.items():
        if report['data'][name] != value:
            raise ValueError(f'seed {name} differs from encrypted manifest')
    if (nx[32:36] != b'NXSB' or not apfs_checksum(nx)
            or int.from_bytes(nx[36:40], 'little') != 4096
            or int.from_bytes(nx[40:48], 'little') * 4096 != PIN['seed_bytes']):
        raise ValueError('APFS container checksum/geometry differs')
    logical, extents = packer.regions(seed.read_bytes())
    wanted = uuid.UUID(report['data']['volume_uuid']).bytes
    found = False
    for _, data in extents:
        for at in range(0, len(data), 4096):
            page = bytes(data[at:at + 4096])
            if page[32:36] == b'APSB' and page[240:256] == wanted and apfs_checksum(page):
                found = True
    if not found:
        raise ValueError('no checksummed APFS volume superblock matches reported UUID')
    return metadata


def unpack(archive, output):
    with tarfile.open(archive, 'r:') as tar:
        members = tar.getmembers()
        if sorted(e.name for e in members) != ['data.dbr', 'manifest.json']:
            raise ValueError('unexpected encrypted archive whitelist')
        for entry in members:
            limit = 256 * 1024**2 if entry.name == 'data.dbr' else 65536
            if not entry.isfile() or entry.size > limit or entry.size <= 0:
                raise ValueError('unexpected archive type/size')
            with tar.extractfile(entry) as src, (output / entry.name).open('xb') as dst:
                while chunk := src.read(1024**2):
                    dst.write(chunk)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', required=True, type=int)
    p.add_argument('--commit', required=True)
    p.add_argument('--unixnu', type=Path, required=True)
    p.add_argument('--key', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--openssl', default='openssl')
    p.add_argument('--gh', default='gh', help='existing authenticated gh; WSL may use Windows gh.exe')
    args = p.parse_args()
    if not run(args.openssl, 'version').startswith(b'OpenSSL 3.'):
        p.error('OpenSSL 3 required for CMS authenticated encryption')
    # Use the independently pinned local writer, not code from the artifact.
    writer = args.unixnu.resolve() / 'drivers/DarwinBoot/Test/packed_ramdisk.py'
    if run('git', 'hash-object', writer).decode().strip() != PIN['packed_ramdisk_git_blob']:
        raise ValueError('local packed writer differs from source pin')
    sys.path.insert(0, str(writer.parent))
    import packed_ramdisk
    run_info = json.loads(run(args.gh, 'api', f'repos/{REPO}/actions/runs/{args.run}'))
    if (run_info['head_sha'] != args.commit or run_info['conclusion'] != 'success'
            or run_info['head_branch'] != 'ci/enuma-data-seed-20261113'):
        raise ValueError('run did not succeed at the expected branch/commit')
    listing = json.loads(run(args.gh, 'api', f'repos/{REPO}/actions/runs/{args.run}/artifacts'))
    expected_name = f'enuma-data-seed-encrypted-{args.run}'
    artifacts = listing['artifacts']
    if len(artifacts) != 1 or artifacts[0]['name'] != expected_name or artifacts[0]['expired']:
        raise ValueError('expected exactly one unexpired ciphertext artifact')
    artifact = artifacts[0]
    # Fresh directory only; private parent ACL is established before invocation.
    args.output.mkdir()
    download_dir = args.output.resolve()
    if args.gh.lower().endswith('.exe'):
        download_dir = run('wslpath', '-w', download_dir).decode().strip()
    run(args.gh, 'run', 'download', args.run, '--repo', REPO, '--name', expected_name,
        '--dir', download_dir)
    if sorted(e.name for e in args.output.iterdir()) != ['data-seed.cms']:
        raise ValueError('artifact contains unexpected files')
    archive = args.output / 'seed.tar'
    run(args.openssl, 'cms', '-decrypt', '-binary', '-inform', 'DER',
        '-in', args.output / 'data-seed.cms', '-recip', HERE / 'recipient.pem',
        '-inkey', args.key, '-out', archive)
    # CMS verifies its GCM tag before this returns successfully; don't parse on failure.
    unpack(archive, args.output)
    report = json.loads((args.output / 'manifest.json').read_text())
    metadata = verify_seed(packed_ramdisk, args.output / 'data.dbr', report, args.run, args.commit)
    receipt = dict(run_id=args.run, commit=args.commit, artifact_id=artifact['id'],
                   artifact_deleted=False, metadata=metadata, status='self-checked',
                   validation='CMS GCM tag, whitelist, DBR bounds/hashes/identity, NXSB checksum/size, APSB UUID/checksum; not a local filesystem mount')
    receipt_path = args.output / 'receipt.json'
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    run(args.gh, 'api', '--method', 'DELETE', f'repos/{REPO}/actions/artifacts/{artifact["id"]}')
    receipt['artifact_deleted'] = True
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    print('Seed verified locally; remote artifact deleted. self-checked; independent verifier pending.')


if __name__ == '__main__':
    main()
