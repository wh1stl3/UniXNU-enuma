#!/usr/bin/env python3
"""Read-only 22r packaging bindings, not a repeated FAT/trust/ADT hardware audit."""
import argparse
import hashlib
import json
from pathlib import Path
import plistlib
import struct
import subprocess
import tomllib

PRELINK = '48da518122894ba21344c016f09cbc62238848d83dd0ac32f97246c76795cb4d'
PATCH = 'a3c12c0f1d210bb2481ba83fa28023c91fad27ac346f992d7613de7e8ed12109'
NATIVE = '8c9dadc04f697c5d53e7421535552ff12840dabd1cfc85de2a9e2a1259a4d86e'
UUID = '9071148B-B025-402D-AD7A-48464D8B5FFF'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for data in iter(lambda: f.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def selected_adt(data):
    def node(at):
        count, children = struct.unpack_from('<II', data, at)
        at += 8
        props = {}
        for _ in range(count):
            key, size = struct.unpack_from('<32sI', data, at)
            at += 36
            if at + size > len(data):
                raise ValueError('truncated ADT property')
            props[key.rstrip(b'\0').decode()] = data[at:at + size]
            at += (size + 3) & ~3
        descendants = []
        for _ in range(children):
            child, at = node(at)
            descendants.append(child)
        return (props, descendants), at
    (_, children), end = node(0)
    assert end == len(data)
    chosen = next(p for p, _ in children if p['name'] == b'chosen\0')
    matching = plistlib.loads(b'<plist version="1.0">' + chosen['root-matching'].rstrip(b'\0') + b'</plist>')
    result = {'root_uuid': matching['IOPropertyMatch']['UUID'],
              'dram_bytes': struct.unpack('<Q', chosen['dram-size'])[0],
              'owned_memory_bytes': struct.unpack('<Q', chosen['darwinboot-memory-size'])[0]}
    assert result == {'root_uuid': UUID, 'dram_bytes': 8 * 1024**3, 'owned_memory_bytes': 512 * 1024**2}
    return result


def check(candidate):
    manifest = json.loads((candidate / 'manifest.json').read_text())
    assert manifest['candidate'] == '22r-pid1-runtime-summary'
    assert manifest['approved'] == {'patch_sha256': PATCH, 'native_sha256': NATIVE, 'prelink_sha256': PRELINK}
    for name, item in manifest['files'].items():
        assert Path(name).name == name
        path = candidate / name
        assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256'], name
    review = json.loads((candidate / 'review-bindings.json').read_text())
    assert review['approved'] == manifest['approved']
    assert review['automatic_audit_status'] == 'manual-review-required'
    assert review['deep']['result'] == 'PASS WITH CONDITIONS'
    assert review['verifier']['audit_child_returncode'] == 2 and review['verifier']['audit_stderr_bytes'] == 0
    payload = json.loads((candidate / 'payload.json').read_text())
    boot = json.loads((candidate / 'boot.json').read_text())
    assert payload['kernel_sha256'] == payload['payload_kernel_sha256'] == PRELINK
    assert payload['payload_sha256'] == sha(candidate / 'payload.img')
    assert boot['image_sha256'] == sha(candidate / 'boot.img')
    assert payload['payload_bytes'] == boot['ramdisk_bytes'] == 192 * 1024**2
    assert payload['kernel_args'] == '-v serial=3 rd=md0-ramblock'
    assert not payload['panic_screen'] and not payload['skip_setup'] and not payload['gpu_addon_sha256']
    for key in ('trust_cache_sha256', 'data_ramdisk_sha256', 'kernel_args', 'payload_bytes', 'panic_screen'):
        assert payload[key] == manifest['reused_baseline']['payload'][key], key
    for key in ('header_version', 'kernel_sha256', 'fd_sha256', 'dtb_sha256', 'shim_bytes', 'ramdisk_bytes'):
        assert boot[key] == manifest['reused_baseline']['boot'][key], key
    # Only inspect the changed kernel and the three requested ADT properties.
    def contained(name):
        return subprocess.check_output(['mtype', '-i', str(candidate / 'payload.img'), '::/EFI/UniXNU/' + name])
    kernel = contained('Payloads/kernel.macho')
    assert hashlib.sha256(kernel).hexdigest() == PRELINK
    config = tomllib.loads(contained('unixnu.toml').decode())
    entry = next(e for e in config['entry'] if e['id'] == 'xnu')
    assert entry['args'] == payload['kernel_args'] and entry['initrd'] == 'Payloads/scratch-data.img'
    adt = contained('Payloads/kernel.macho.adt')
    assert hashlib.sha256(adt).hexdigest() == payload['adt_sha256']
    constraints = selected_adt(adt)
    for site in manifest['svc_sites']:
        offset = site['file_offset']
        word = struct.unpack_from('<I', kernel, offset)[0]
        assert word == int(site['word'], 16) and word & 0xfc000000 == 0x94000000
        immediate = word & 0x3ffffff
        if immediate & 0x2000000:
            immediate -= 0x4000000
        assert int(site['pc'], 16) + immediate * 4 == int(site['target'], 16)
    assert {s['callee'] for s in manifest['svc_sites']} == {'_current_cached_proc_cred_update', '_enuma_pid1_svc'}
    assert next(s for s in manifest['svc_sites'] if s['callee'] == '_current_cached_proc_cred_update')['pc'] == '0xfffffff00741ff58'
    # Incremental boot->payload binding, without re-auditing unchanged firmware.
    with (candidate / 'boot.img').open('rb') as f:
        header = f.read(4096)
        assert header[:8] == b'ANDROID!' and struct.unpack_from('<I', header, 40)[0] == 1
        ks, _, rs = struct.unpack_from('<3I', header, 8)
        page = struct.unpack_from('<I', header, 36)[0]
        assert page == manifest['constraints']['boot_pagesize']
        f.seek(page * (1 + (ks + page - 1) // page))
        ramdisk = hashlib.sha256()
        remaining = rs
        while remaining:
            chunk = f.read(min(1024 * 1024, remaining))
            assert chunk
            ramdisk.update(chunk)
            remaining -= len(chunk)
        assert ramdisk.hexdigest() == payload['payload_sha256']
    return {'status': 'self-checked', 'candidate': str(candidate), 'boot_sha256': boot['image_sha256'],
            'payload_sha256': payload['payload_sha256'], 'contained_kernel_sha256': PRELINK,
            'manifest_sha256': sha(candidate / 'manifest.json'),
            'selected_adt': constraints, 'svc_sites': manifest['svc_sites'],
            'scope': 'packaging bindings only; no device visibility or repeated unchanged trust/FAT/ADT audit'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--manifest-sha256', help='externally pinned packaging manifest digest')
    args = parser.parse_args()
    if args.manifest_sha256:
        assert sha(args.candidate / 'manifest.json') == args.manifest_sha256
    print(json.dumps(check(args.candidate), indent=2))
