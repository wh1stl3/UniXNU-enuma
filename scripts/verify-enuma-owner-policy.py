#!/usr/bin/env python3
"""Verify a signed bounded window with the pinned C consumer and OpenSSL."""
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import subprocess
import uuid

BASE = Path('/mnt/d/Code/PortingiOS/UniXNU')
PIN = '693f5d9cae8a408dd18b39f3f9fdc4228c934241'


class View(ctypes.Structure):
    _fields_ = [('hashes', ctypes.c_void_p), ('image_bytes', ctypes.c_uint64),
                ('block_count', ctypes.c_uint64), ('generation', ctypes.c_uint64),
                ('volume_uuid', ctypes.c_uint8 * 16), ('image_sha256', ctypes.c_uint8 * 32)]


def input_buffers(policy_path, anchor_path):
    """Snapshot once; the hashes describe exactly the buffers supplied to C."""
    policy_bytes = policy_path.read_bytes()
    anchor_bytes = anchor_path.read_bytes()
    if len(anchor_bytes) != 395:
        raise ValueError('invalid anchor length')
    policy = ctypes.create_string_buffer(policy_bytes, len(policy_bytes))
    anchor = ctypes.create_string_buffer(anchor_bytes, len(anchor_bytes))
    return policy, anchor, hashlib.sha256(policy.raw).hexdigest(), hashlib.sha256(anchor.raw).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--policy', type=Path, required=True)
    p.add_argument('--anchor', type=Path, required=True)
    p.add_argument('--image', type=Path, required=True)
    p.add_argument('--offset', type=int, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.policy, a.anchor, a.image = a.policy.resolve(), a.anchor.resolve(), a.image.resolve()
    if subprocess.check_output(['git', '-C', str(BASE), 'rev-parse', 'HEAD'], text=True).strip() != PIN:
        raise ValueError('base pin mismatch')
    a.output.mkdir(parents=True, exist_ok=False)
    vr = BASE / 'kits/VerifiedRoot'
    lib = a.output / 'verified-root.so'
    cmd = ['cc', '-shared', '-fPIC', '-I', str(vr / 'include'), str(vr / 'src/verified_root.c'), str(vr / 'tests/openssl_provider.c'), '-lcrypto', '-o', str(lib)]
    subprocess.run(cmd, check=True)
    c = ctypes.CDLL(str(lib.resolve()))
    c.vr_host_open.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_uint64, ctypes.POINTER(View)]
    c.vr_host_block.argtypes = [ctypes.POINTER(View), ctypes.c_uint64, ctypes.c_void_p, ctypes.c_size_t]
    policy, anchor, policy_sha256, anchor_sha256 = input_buffers(a.policy, a.anchor)
    view = View()
    status = c.vr_host_open(policy, len(policy), anchor, 1, ctypes.byref(view))
    if status:
        raise ValueError(f'vr_open status {status}')
    if a.offset < 0 or a.offset + view.image_bytes > a.image.stat().st_size:
        raise ValueError('window outside image')
    with a.image.open('rb') as image:
        image.seek(a.offset)
        remaining = view.image_bytes
        for index in range(view.block_count):
            n = min(4096, remaining)
            data = image.read(n)
            if len(data) != n or c.vr_host_block(ctypes.byref(view), index, data, n):
                raise ValueError(f'vr_verify_block failed at {index}')
            remaining -= n
    if remaining:
        raise ValueError('block count mismatch')
    report = {'base_commit': PIN, 'compiler_command': cmd, 'compile_exit': 0,
              'vr_open_exit': status, 'blocks_verified': view.block_count,
              'policy_path': str(a.policy.resolve()), 'policy_sha256': policy_sha256,
              'anchor_path': str(a.anchor.resolve()), 'anchor_sha256': anchor_sha256,
              'image_path': str(a.image.resolve()),
              'raw_offset': a.offset, 'raw_bytes': view.image_bytes,
              'generation': view.generation, 'image_sha256_signed': bytes(view.image_sha256).hex(),
              'volume_uuid': str(uuid.UUID(bytes=bytes(view.volume_uuid))).upper(),
              'hardware_tested': False}
    (a.output / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
