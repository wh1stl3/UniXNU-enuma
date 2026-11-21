#!/usr/bin/env python3
"""Read-only checker for the clean 24r observation package.

Binds the frozen native/prelink/metadata, the single actual contained `xnu` boot
entry, the actual ADT delta/address translation used by the UFS consumer, the
inherited firmware DTB/RAM-root/trust inputs, the actual boot ramdisk extent and
the per-file ext4/Windows copies. It never writes to the candidate.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

FROZEN = {
    'native_sha256': 'f5c372beab9bd7fbb420b533582c27a95dacb81f816e78d4efc18f5a8e5bd597',
    'prelink_sha256': 'f30a36862a796bdbf45dd55c4a1a60b9d0cec6dde68bcb3fe315c7b11b86ea18',
    'metadata_sha256': '3c94f5bce228ac50c9ff7126aa1caebd1c8df9a60b9c6cf82556173173983232',
}
ALLOWED_ADT_DELTA = {
    '/device-tree/chosen:random-seed',
    '/device-tree/arm-io/intc:reg',
    '/device-tree/arm-io/ufshc:compatible',
    '/device-tree/arm-io/ufshc:name',
    '/device-tree/arm-io/ufshc:reg',
    '/device-tree/arm-io:ranges',
}
UFSHC_ADDRESS = 0x01d84000
UFSHC_LENGTH = 0x3000


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def load(name, filename):
    path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def adt_properties(blob):
    result = {}

    def node(at, prefix):
        count, children = struct.unpack_from('<II', blob, at)
        at += 8
        own = {}
        for _ in range(count):
            key, size = struct.unpack_from('<32sI', blob, at)
            at += 36
            require(at + size <= len(blob), 'truncated ADT property')
            own[key.rstrip(b'\0').decode()] = blob[at:at + size]
            at += (size + 3) & ~3
        name = own.get('name', b'unknown\0').rstrip(b'\0').decode()
        path = prefix + '/' + name
        for key, value in own.items():
            result[path + ':' + key] = value
        for _ in range(children):
            at = node(at, path)
        return at

    require(node(0, '') == len(blob), 'trailing ADT bytes')
    return result


def adt_delta(old, new):
    return sorted(key for key in set(old) | set(new) if old.get(key) != new.get(key))


def translate_ufshc(reg, ranges):
    """The exact consumer arithmetic in UfsPlatformResources.h select()."""
    require(isinstance(reg, (bytes, bytearray)) and len(reg) == 16, 'ufshc reg must be 16 bytes')
    require(isinstance(ranges, (bytes, bytearray)) and len(ranges) == 24, 'arm-io ranges must be 24 bytes')
    def little(data, count):
        return int.from_bytes(bytes(data[:count]), 'little')
    offset = little(reg, 8)
    length = little(reg[8:], 8)
    child = little(ranges, 8)
    parent = little(ranges[8:], 8)
    span = little(ranges[16:], 8)
    require(length and span and child <= 2**64 - span and parent <= 2**64 - span,
            'range/reg overflow or zero length')
    require(offset >= child and offset - child <= span and length <= span - (offset - child),
            'reg is outside the arm-io range')
    address = parent + (offset - child)
    require(address == UFSHC_ADDRESS and length == UFSHC_LENGTH,
            f'translated address differs: {address:#x}/{length:#x}')
    return {'address': address, 'length': length,
            'offset': offset, 'child': child, 'parent': parent, 'span': span}


def contained(payload, member):
    return subprocess.check_output(['mtype', '-i', str(payload), member], timeout=120)


def check(candidate, baseline, manifest_sha, fd, dtb, data, trust, tree):
    manifest_path = candidate / 'manifest.json'
    require(sha(manifest_path) == manifest_sha, 'manifest SHA256 differs')
    manifest = json.loads(manifest_path.read_text())
    require(manifest['frozen'] == FROZEN, 'frozen binding differs')
    validation = json.loads((candidate / 'copy-validation.json').read_text())
    windows = Path(validation['copied_to'])
    require(candidate.resolve() != windows.resolve(),
            'candidate and copy resolve to the same path')
    candidate_device = os.stat(candidate).st_dev
    windows_device = os.stat(windows).st_dev
    require(candidate_device != windows_device,
            'candidate and copy are on the same filesystem; not a cross-system check')
    for name, item in manifest['files'].items():
        require(Path(name).name == name, 'unsafe manifest path')
        for root in (candidate, windows):
            path = root / name
            require(path.is_file(), f'missing copy: {path}')
            require(path.stat().st_size == item['bytes'] and sha(path) == item['sha256'],
                    f'file binding differs: {path}')
    require(validation['manifest_sha256'] == manifest_sha, 'copy-validation manifest hash differs')
    require(validation['all_copy_hashes_match'] is True, 'copy-validation flag false')
    require(sha(candidate / 'manifest.json') == sha(windows / 'manifest.json'),
            'manifest copies differ')
    require(sha(candidate / 'copy-validation.json') == sha(windows / 'copy-validation.json'),
            'copy-validation copies differ')
    require(validation['boot_sha256'] == sha(candidate / 'boot.img'), 'boot binding differs')
    require(validation['payload_sha256'] == sha(candidate / 'payload.img'), 'payload binding differs')

    payload = json.loads((candidate / 'payload.json').read_text())
    boot = json.loads((candidate / 'boot.json').read_text())
    base_payload = json.loads((baseline / 'payload.json').read_text())
    base_boot = json.loads((baseline / 'boot.json').read_text())
    require(payload['kernel_sha256'] == payload['payload_kernel_sha256'] == FROZEN['prelink_sha256'],
            'payload kernel metadata differs')
    require(sha(candidate / 'payload.img') == payload['payload_sha256'], 'payload hash differs')
    require(sha(candidate / 'boot.img') == boot['image_sha256'], 'boot hash differs')
    for key in ('trust_cache_sha256', 'data_ramdisk_sha256', 'payload_bytes', 'panic_screen',
                'skip_setup', 'gpu_addon_sha256'):
        require(payload.get(key) == base_payload.get(key), f'inherited payload input differs: {key}')
    for key in ('header_version', 'fd_sha256', 'dtb_sha256', 'shim_bytes', 'ramdisk_bytes'):
        require(boot.get(key) == base_boot.get(key), f'inherited firmware input differs: {key}')
    require(sha(fd) == base_boot['fd_sha256'], 'actual firmware volume differs')
    require(sha(dtb) == base_boot['dtb_sha256'], 'actual firmware DTB differs')
    require(sha(data) == base_payload['data_ramdisk_sha256'], 'actual RAM-root image differs')
    require(sha(trust) == base_payload['trust_cache_sha256'], 'actual trust cache differs')

    admission = load('admission', 'audit-enuma-ufs-final-admission.py')
    entry = admission.select_boot_entry(
        contained(candidate / 'payload.img', '::/EFI/UniXNU/unixnu.toml').decode(errors='replace'))
    contained_kernel = hashlib.sha256(
        contained(candidate / 'payload.img', '::/EFI/UniXNU/Payloads/kernel.macho')).hexdigest()
    require(contained_kernel == FROZEN['prelink_sha256'], 'contained kernel differs')

    old_adt = adt_properties(contained(baseline / 'payload.img',
                                       '::/EFI/UniXNU/Payloads/kernel.macho.adt'))
    new_adt = adt_properties(contained(candidate / 'payload.img',
                                       '::/EFI/UniXNU/Payloads/kernel.macho.adt'))
    delta = adt_delta(old_adt, new_adt)
    require(set(delta) <= ALLOWED_ADT_DELTA, f'unexpected ADT property change: {delta}')
    for key in set(old_adt) & set(new_adt):
        if key not in ALLOWED_ADT_DELTA:
            require(old_adt[key] == new_adt[key], f'ADT bytes differ outside the allowed delta: {key}')
    translation = translate_ufshc(new_adt['/device-tree/arm-io/ufshc:reg'],
                                  new_adt['/device-tree/arm-io:ranges'])
    consumer = Path(tree) / 'drivers/ShengUfs/UfsPlatformResources.h'
    consumer_text = consumer.read_text()
    require('address != 0x01d84000ULL || length != 0x3000' in consumer_text,
            'consumer address check not present')
    require('parent + (offset - child)' in consumer_text, 'consumer ranges arithmetic not present')

    with (candidate / 'boot.img').open('rb') as stream:
        header = stream.read(4096)
    require(header[:8] == b'ANDROID!', 'boot header absent')
    kernel_size, _, ramdisk_size = struct.unpack_from('<3I', header, 8)
    page = struct.unpack_from('<I', header, 36)[0]
    require(page == manifest['constraints']['boot_pagesize'] and
            ramdisk_size == payload['payload_bytes'], 'boot ramdisk extent differs')
    with (candidate / 'boot.img').open('rb') as stream:
        stream.seek(page * (1 + (kernel_size + page - 1) // page))
        digest = hashlib.sha256()
        remaining = ramdisk_size
        while remaining:
            chunk = stream.read(min(1024 * 1024, remaining))
            require(chunk, 'truncated boot ramdisk')
            digest.update(chunk)
            remaining -= len(chunk)
    require(digest.hexdigest() == payload['payload_sha256'], 'boot-contained payload differs')

    return {
        'status': 'self-checked', 'candidate': str(candidate), 'windows': str(windows),
        'candidate_device': candidate_device, 'windows_device': windows_device,
        'cross_system_check': True,
        'manifest_sha256': manifest_sha, 'boot_sha256': sha(candidate / 'boot.img'),
        'payload_sha256': sha(candidate / 'payload.img'),
        'contained_kernel_sha256': contained_kernel,
        'boot_entry': entry, 'adt_delta_properties': delta,
        'ufshc_translation': translation, 'consumer_source': str(consumer),
        'consumer_source_sha256': sha(consumer),
        'firmware_inputs_inherited': True, 'copies_verified_per_file': True,
        'device_authorized': False, 'release_allowed': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--tree', type=Path, required=True)
    parser.add_argument('--fd', type=Path, required=True)
    parser.add_argument('--dtb', type=Path, required=True)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--trust', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = check(args.candidate.resolve(), args.baseline.resolve(), args.manifest_sha256,
                       args.fd, args.dtb, args.data, args.trust, args.tree)
        print(json.dumps(result, indent=2))
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f'24r package rejected: {error}\n')


if __name__ == '__main__':
    main()
