#!/usr/bin/env python3
"""23r actual contained-parameter/kernel and boot/payload binding checks."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys

PRELINK = 'bf9f7e12bb05dc3a09f1a732fbcdb83d7729f6378f65ea7fbe77646514edc072'
NATIVE = '5b8fd1811e39d6415550786578c1fb96346df32a0ba2a35efbd3ff50a251a74f'


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def adt_properties(blob):
    """Property-byte comparison only; not a repeat hardware/ADT semantic audit."""
    result = {}
    def node(at, prefix):
        count, children = struct.unpack_from('<II', blob, at)
        at += 8
        own = {}
        for _ in range(count):
            key, size = struct.unpack_from('<32sI', blob, at)
            at += 36
            require(at + size <= len(blob), 'Truncated ADT property')
            own[key.rstrip(b'\0').decode()] = blob[at:at + size]
            at += (size + 3) & ~3
        name = own.get('name', b'unknown\0').rstrip(b'\0').decode()
        path = prefix + '/' + name
        result.update({path + ':' + key: value for key, value in own.items()})
        for _ in range(children):
            at = node(at, path)
        return at
    require(node(0, '') == len(blob), 'Trailing ADT bytes')
    return result


def check(candidate, expected_manifest=None):
    manifest_path = candidate / 'manifest.json'
    require(not expected_manifest or sha(manifest_path) == expected_manifest, 'Manifest SHA256 differs')
    manifest = json.loads(manifest_path.read_text())
    require(manifest['candidate'] == '23r-pmgr-publisher', 'Wrong candidate')
    require(manifest['frozen'] == {'native_sha256': NATIVE, 'prelink_sha256': PRELINK}, 'Frozen binding differs')
    for name, item in manifest['files'].items():
        require(Path(name).name == name, 'Unsafe manifest path')
        path = candidate / name
        require(path.stat().st_size == item['bytes'] and sha(path) == item['sha256'], f'File binding differs: {name}')
    payload = json.loads((candidate / 'payload.json').read_text())
    boot = json.loads((candidate / 'boot.json').read_text())
    require(payload['kernel_sha256'] == payload['payload_kernel_sha256'] == PRELINK, 'Payload kernel metadata differs')
    require(sha(candidate / 'payload.img') == payload['payload_sha256'], 'Payload SHA256 differs')
    require(sha(candidate / 'boot.img') == boot['image_sha256'], 'Boot SHA256 differs')
    baseline = manifest['reused_baseline']
    for key in ('trust_cache_sha256', 'data_ramdisk_sha256', 'payload_bytes', 'panic_screen', 'skip_setup', 'gpu_addon_sha256'):
        require(payload.get(key) == baseline['payload'].get(key), f'Unchanged payload input differs: {key}')
    for key in ('header_version', 'kernel_sha256', 'fd_sha256', 'dtb_sha256', 'shim_bytes', 'ramdisk_bytes'):
        require(boot[key] == baseline['boot'][key], f'Unchanged firmware/header input differs: {key}')
    require(payload['kernel_args'] == '-v serial=3 rd=md0-ramblock pmgr=2', 'Payload arguments differ')
    old_image = candidate.parent / baseline['candidate'] / 'payload.img'
    def contained_adt(image):
        return subprocess.check_output(['mtype', '-i', str(image), '::/EFI/UniXNU/Payloads/kernel.macho.adt'], timeout=60)
    old_adt = contained_adt(old_image)
    new_adt = contained_adt(candidate / 'payload.img')
    require(hashlib.sha256(old_adt).hexdigest() == baseline['payload']['adt_sha256'], 'Baseline ADT binding differs')
    require(hashlib.sha256(new_adt).hexdigest() == payload['adt_sha256'], 'Contained ADT binding differs')
    old_props, new_props = adt_properties(old_adt), adt_properties(new_adt)
    adt_delta = [key for key in sorted(set(old_props) | set(new_props)) if old_props.get(key) != new_props.get(key)]
    require(set(adt_delta) <= {'/device-tree/chosen:random-seed'}, 'Unexpected ADT property change')
    # Parse the real Android boot ramdisk extent; do not trust only boot.json.
    with (candidate / 'boot.img').open('rb') as stream:
        header = stream.read(4096)
        require(header[:8] == b'ANDROID!', 'Boot header absent')
        kernel_size, _, ramdisk_size = struct.unpack_from('<3I', header, 8)
        page = struct.unpack_from('<I', header, 36)[0]
        require(page == manifest['constraints']['boot_pagesize'] and ramdisk_size == payload['payload_bytes'],
                'Boot ramdisk extent differs')
        stream.seek(page * (1 + (kernel_size + page - 1) // page))
        digest = hashlib.sha256()
        remaining = ramdisk_size
        while remaining:
            chunk = stream.read(min(1024 * 1024, remaining))
            require(chunk, 'Truncated boot ramdisk')
            digest.update(chunk)
            remaining -= len(chunk)
        require(digest.hexdigest() == payload['payload_sha256'], 'Boot-contained payload differs')
    spec = importlib.util.spec_from_file_location('pmgr_prelink', Path(__file__).with_name('audit-enuma-pmgr-prelink.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # This reads actual contained unixnu.toml/kernel, archive report/hash, 340
    # linked pointers and hook instructions. 205 imports are presence checks only.
    bindings = manifest['audit_inputs']
    args = argparse.Namespace(**{k: Path(v) for k, v in bindings.items()}, payload=candidate / 'payload.img', require_package=True)
    result = module.audit(args)
    require(result['prelink_sha256'] == PRELINK and result['native_sha256'] == NATIVE, 'Actual audit image differs')
    return {'status': 'self-checked', 'candidate': str(candidate), 'manifest_sha256': sha(manifest_path),
            'boot_sha256': boot['image_sha256'], 'payload_sha256': payload['payload_sha256'],
            'contained_kernel_sha256': PRELINK, 'contained_args': result['contained_args'],
            'adt_delta_properties': adt_delta,
            'actual_archive_and_hook_checked': True, 'imports_checked_for_presence_only': result['imports_checked'],
            'package_checked': result['package_checked'], 'device_authorized': False, 'release_allowed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--manifest-sha256')
    args = parser.parse_args()
    try:
        print(json.dumps(check(args.candidate.resolve(), args.manifest_sha256), indent=2))
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f'PMGR package rejected: {error}\n')
