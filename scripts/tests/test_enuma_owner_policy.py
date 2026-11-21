#!/usr/bin/env python3
"""Small host-only C consumer check for the window signer."""
import ctypes
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

BASE = Path('/mnt/d/Code/PortingiOS/UniXNU/kits/VerifiedRoot')
SIGNER = Path(__file__).resolve().parents[1] / 'enuma-owner-policy.py'
VERIFY = SIGNER.with_name('verify-enuma-owner-policy.py')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class View(ctypes.Structure):
    _fields_ = [('hashes', ctypes.c_void_p), ('image_bytes', ctypes.c_uint64),
                ('block_count', ctypes.c_uint64), ('generation', ctypes.c_uint64),
                ('volume_uuid', ctypes.c_uint8 * 16), ('image_sha256', ctypes.c_uint8 * 32)]


with tempfile.TemporaryDirectory(prefix='enuma-vr-fixture-') as temp:
    d = Path(temp)
    subprocess.run(['openssl', 'genpkey', '-algorithm', 'RSA', '-pkeyopt', 'rsa_keygen_bits:3072', '-out', str(d / 'fixture.pem')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    subprocess.run(['openssl', 'pkey', '-in', str(d / 'fixture.pem'), '-pubout', '-out', str(d / 'public.pem')], check=True)
    data = bytes(i % 251 for i in range(8704))
    (d / 'raw').write_bytes(b'prefix' + data + b'suffix')
    args = [sys.executable, str(SIGNER), '--image', str(d / 'raw'), '--offset', '6', '--size', str(len(data)), '--expected-sha256', hashlib.sha256(data).hexdigest(), '--uuid', '04769D26-2CA0-4825-B443-E2E5F88300F2', '--generation', '1', '--private-key', str(d / 'fixture.pem'), '--public-key', str(d / 'public.pem'), '--output', str(d / 'signed')]
    subprocess.run(args, stdout=subprocess.DEVNULL, check=True)
    subprocess.run(['cc', '-shared', '-fPIC', '-I', str(BASE / 'include'), str(BASE / 'src/verified_root.c'), str(BASE / 'tests/openssl_provider.c'), '-lcrypto', '-o', str(d / 'vr.so')], check=True)
    c = ctypes.CDLL(str(d / 'vr.so'))
    c.vr_host_open.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_uint64, ctypes.POINTER(View)]
    c.vr_host_block.argtypes = [ctypes.POINTER(View), ctypes.c_uint64, ctypes.c_void_p, ctypes.c_size_t]
    policy = (d / 'signed/manifest.bin').read_bytes()
    anchor = (d / 'signed/anchor.bin').read_bytes()
    def opening(blob, key=anchor):
        b, k, v = ctypes.create_string_buffer(blob), ctypes.create_string_buffer(key), View()
        return c.vr_host_open(b, len(blob), k, 1, ctypes.byref(v)), v, b, k
    status, view, keep, key = opening(policy)
    assert status == 0 and view.image_bytes == len(data)
    for i in range(view.block_count):
        block = data[i * 4096:(i + 1) * 4096]
        assert c.vr_host_block(ctypes.byref(view), i, block, len(block)) == 0
    assert c.vr_host_block(ctypes.byref(view), 0, b'X' * 4096, 4096) != 0
    bad = bytearray(policy); bad[160] ^= 1
    assert opening(bytes(bad))[0] != 0
    bad_key = bytearray(anchor); bad_key[8] ^= 1
    assert opening(policy, bytes(bad_key))[0] != 0
    assert opening(policy[:-1])[0] != 0
    mismatch = args.copy(); mismatch[mismatch.index('--offset') + 1] = '7'; mismatch[mismatch.index('--output') + 1] = str(d / 'mismatch')
    assert subprocess.run(mismatch, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0
    assert not (d / 'mismatch').exists()
    verifier = load('verify_fixture', VERIFY)
    pp, ap = d / 'policy-input', d / 'anchor-input'
    pp.write_bytes(policy); ap.write_bytes(anchor)
    pb, ab, ph, ah = verifier.input_buffers(pp, ap)
    pp.write_bytes(b'replaced'); ap.write_bytes(b'replaced')
    v = View()
    assert c.vr_host_open(pb, len(pb), ab, 1, ctypes.byref(v)) == 0
    assert ph == hashlib.sha256(policy).hexdigest() and ah == hashlib.sha256(anchor).hexdigest()
    assert ph != hashlib.sha256(pp.read_bytes()).hexdigest()
    assert ah != hashlib.sha256(ap.read_bytes()).hexdigest()
    verify_cmd = [sys.executable, str(VERIFY), '--policy', str(d / 'signed/manifest.bin'), '--anchor', str(d / 'signed/anchor.bin'), '--image', str(d / 'raw'), '--offset', '6', '--output', str(d / 'verification')]
    subprocess.run(verify_cmd, stdout=subprocess.DEVNULL, check=True)
    report = json.loads((d / 'verification/result.json').read_text())
    assert report['policy_sha256'] == ph and report['anchor_sha256'] == ah
    assert report['volume_uuid'] == '04769D26-2CA0-4825-B443-E2E5F88300F2'
    signer = load('signer_fixture', SIGNER)
    original_run, original_open = signer.subprocess.run, Path.open
    def failed_sign(command, *a, **kw):
        if '-sign' in command:
            raise OSError('injected signature failure')
        return original_run(command, *a, **kw)
    def failed_write(path, *a, **kw):
        if path.name == 'hashes.bin' and a and a[0] == 'xb':
            raise OSError('injected write failure')
        return original_open(path, *a, **kw)
    for name, patcher in [('sign-fail', mock.patch.object(signer.subprocess, 'run', side_effect=failed_sign)),
                          ('write-fail', mock.patch.object(Path, 'open', failed_write))]:
        cmd = args[1:].copy(); cmd[cmd.index('--output') + 1] = str(d / name)
        with mock.patch.object(sys, 'argv', cmd), patcher:
            try:
                signer.main()
                raise AssertionError('injected failure did not fail')
            except OSError:
                pass
        assert not (d / name).exists()
        assert list(d.glob('.' + name + '.staging-*'))
    old = (d / 'signed/manifest.bin').read_bytes()
    assert subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0
    assert (d / 'signed/manifest.bin').read_bytes() == old
    source, existing = d / 'rename-source', d / 'rename-existing'
    source.mkdir(); existing.mkdir()
    try:
        signer.publish_no_replace(source, existing)
        raise AssertionError('existing empty directory replaced')
    except FileExistsError:
        pass
    assert source.is_dir() and existing.is_dir()
    print('PASS: C/OpenSSL, input snapshot binding, staged write/sign failures and no-replace publication')
