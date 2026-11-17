#!/usr/bin/env python3
"""Sign one bounded raw window using the pinned VerifiedRoot envelope format."""
import argparse
import base64
import ctypes
import errno
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import uuid

BASE = Path('/mnt/d/Code/PortingiOS/UniXNU')
PIN = '693f5d9cae8a408dd18b39f3f9fdc4228c934241'


def publish_no_replace(staging, target):
    # Linux renameat2 is atomic and refuses even an existing empty directory.
    libc = ctypes.CDLL(None, use_errno=True)
    rename = libc.renameat2
    rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    rename.restype = ctypes.c_int
    if rename(-100, os.fsencode(staging), -100, os.fsencode(target), 1):
        error = ctypes.get_errno()
        if error == errno.EINVAL and str(staging).startswith('/mnt/'):
            # DrvFS does not implement RENAME_NOREPLACE. Windows Directory.Move
            # refuses an existing destination, including an empty directory.
            paths = [subprocess.check_output(['wslpath', '-w', str(p)], text=True).strip() for p in (staging, target)]
            quote = lambda s: "'" + s.replace("'", "''") + "'"
            script = '$ErrorActionPreference="Stop"; [System.IO.Directory]::Move(' + ','.join(map(quote, paths)) + ')'
            encoded = base64.b64encode(script.encode('utf-16le')).decode('ascii')
            result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-EncodedCommand', encoded], capture_output=True)
            if result.returncode:
                if target.exists() or target.is_symlink():
                    raise FileExistsError(errno.EEXIST, 'output already exists', str(target))
                raise RuntimeError('Windows Directory.Move failed: ' + result.stderr.decode(errors='replace'))
            return
        raise OSError(error, os.strerror(error), str(target))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--image', type=Path, required=True)
    p.add_argument('--offset', type=int, required=True)
    p.add_argument('--size', type=int, required=True)
    p.add_argument('--expected-sha256', required=True)
    p.add_argument('--uuid', type=uuid.UUID, required=True)
    p.add_argument('--generation', type=int, required=True)
    p.add_argument('--private-key', type=Path, required=True)
    p.add_argument('--public-key', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.offset < 0 or a.size <= 0 or a.generation <= 0 or a.offset + a.size > a.image.stat().st_size:
        p.error('invalid window or generation')
    if subprocess.check_output(['git', '-C', str(BASE), 'rev-parse', 'HEAD'], text=True).strip() != PIN:
        raise ValueError('base pin mismatch')
    spec = importlib.util.spec_from_file_location('verified_root_manifest', BASE / 'kits/VerifiedRoot/tools/manifest.py')
    manifest = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(manifest)
    anchor = manifest.public_anchor(a.public_key)
    derived = subprocess.check_output(['openssl', 'pkey', '-in', str(a.private_key), '-pubout', '-outform', 'DER'])
    supplied = subprocess.check_output(['openssl', 'pkey', '-pubin', '-in', str(a.public_key), '-outform', 'DER'])
    if derived != supplied:
        raise ValueError('private/public key mismatch')
    target = a.output.absolute()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        raise FileExistsError(errno.EEXIST, 'output already exists', str(target))
    # Retained on failure for inspection; never remove files outside this new directory.
    a.output = Path(tempfile.mkdtemp(prefix='.' + target.name + '.staging-', dir=target.parent))
    print('staging:', a.output, flush=True)
    image_hash, table_hash = hashlib.sha256(), hashlib.sha256()
    count = 0
    with a.image.open('rb') as image, (a.output / 'hashes.bin').open('xb') as table:
        image.seek(a.offset)
        remaining = a.size
        while remaining:
            n = min(4096, remaining)
            block = image.read(n)
            if len(block) != n:
                raise ValueError('short raw window')
            h = hashlib.sha256(block).digest()
            image_hash.update(block)
            table_hash.update(h)
            table.write(h)
            count += 1
            remaining -= n
    if image_hash.hexdigest() != a.expected_sha256.lower():
        raise ValueError('raw window SHA256 does not match source report; not signing')
    header = struct.pack('<8s4I2Q16s32s32s32sQ', b'VROOT01\0', 1, 160, 4096, 0,
                         a.size, count, a.uuid.bytes, image_hash.digest(), table_hash.digest(),
                         hashlib.sha256(anchor).digest(), a.generation)
    (a.output / 'header.bin').write_bytes(header)
    (a.output / 'anchor.bin').write_bytes(anchor)
    signature = a.output / 'signature.bin'
    subprocess.run(['openssl', 'dgst', '-sha256', '-sign', str(a.private_key), '-out', str(signature), str(a.output / 'header.bin')], check=True)
    subprocess.run(['openssl', 'dgst', '-sha256', '-verify', str(a.public_key), '-signature', str(signature), str(a.output / 'header.bin')], check=True)
    sig = signature.read_bytes()
    if len(sig) != 384:
        raise ValueError('unexpected signature size')
    policy_hash = hashlib.sha256()
    with (a.output / 'manifest.bin').open('xb') as out:
        for data in (header, sig):
            out.write(data); policy_hash.update(data)
        with (a.output / 'hashes.bin').open('rb') as table:
            while data := table.read(1024 * 1024):
                out.write(data); policy_hash.update(data)
    record = {'base_commit': PIN, 'image': str(a.image.resolve()), 'offset': a.offset,
              'image_bytes': a.size, 'block_count': count, 'volume_uuid': str(a.uuid).upper(),
              'generation': a.generation, 'image_sha256': image_hash.hexdigest(),
              'hash_table_sha256': table_hash.hexdigest(), 'anchor_sha256': hashlib.sha256(anchor).hexdigest(),
              'policy_sha256': policy_hash.hexdigest(), 'policy_bytes': 544 + count * 32,
              'signature_algorithm': 'RSA3072-PKCS1v1.5-SHA256', 'hardware_tested': False}
    (a.output / 'manifest.json').write_text(json.dumps(record, indent=2) + '\n')
    # Verify the bytes actually persisted in the envelope, including its full table.
    with (a.output / 'manifest.bin').open('rb') as envelope:
        if envelope.read(160) != header or envelope.read(384) != sig:
            raise ValueError('persisted envelope header/signature mismatch')
        persisted_hash = hashlib.sha256()
        while data := envelope.read(1024 * 1024):
            persisted_hash.update(data)
        if persisted_hash.digest() != table_hash.digest():
            raise ValueError('persisted envelope table mismatch')
    if (a.output / 'manifest.bin').stat().st_size != record['policy_bytes']:
        raise ValueError('persisted envelope length mismatch')
    if (a.output / 'anchor.bin').read_bytes() != anchor:
        raise ValueError('persisted anchor mismatch')
    publish_no_replace(a.output, target)
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
