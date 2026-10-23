"""Build and read back a configuration-only FAT volume; no boot image or USB calls."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

if sys.version_info < (3, 11):
    import tomli as tomllib
    sys.modules['tomllib'] = tomllib
else:
    import tomllib

ROOT = Path(__file__).resolve().parents[1]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def clear_free_clusters(image):
    """Remove formatter residue only from FAT32 clusters marked free in both FATs."""
    data = bytearray(image.read_bytes())
    bps = struct.unpack_from('<H', data, 11)[0]
    spc = data[13]
    reserved = struct.unpack_from('<H', data, 14)[0]
    fats = data[16]
    sectors = struct.unpack_from('<I', data, 32)[0]
    fat_sectors = struct.unpack_from('<I', data, 36)[0]
    if bps != 512 or spc == 0 or spc & (spc - 1) or fats != 2 or reserved == 0:
        raise ValueError('Unsupported FAT32 geometry')
    if data[82:90] != b'FAT32   ' or data[510:512] != b'\x55\xaa' or sectors * bps != len(data):
        raise ValueError('FAT32 size/type/signature mismatch')
    fat_start = reserved * bps
    fat_bytes = fat_sectors * bps
    data_start = fat_start + fats * fat_bytes
    cluster_bytes = spc * bps
    count = (len(data) - data_start) // cluster_bytes
    if data_start >= len(data) or (count + 2) * 4 > fat_bytes:
        raise ValueError('FAT does not cover data clusters')
    if data[fat_start:fat_start + fat_bytes] != data[fat_start + fat_bytes:data_start]:
        raise ValueError('FAT copies disagree')
    cleared = 0
    for cluster in range(2, count + 2):
        entry = struct.unpack_from('<I', data, fat_start + cluster * 4)[0] & 0x0fffffff
        if entry == 0:
            offset = data_start + (cluster - 2) * cluster_bytes
            if any(data[offset:offset + cluster_bytes]):
                cleared += 1
                data[offset:offset + cluster_bytes] = bytes(cluster_bytes)
    # Bytes after the last complete cluster are outside the allocation space.
    tail = data_start + count * cluster_bytes
    data[tail:] = bytes(len(data) - tail)
    image.write_bytes(data)
    return cleared


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unixnu', type=Path, required=True)
    args = parser.parse_args()
    source = args.unixnu.resolve()
    lock = json.loads((ROOT / 'config/sources.lock.json').read_text())['sources']['UniXNU']
    revision = subprocess.check_output(['git', '-c', f'safe.directory={source.as_posix()}',
                                        '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != lock['commit']:
        raise ValueError('Unexpected UniXNU source revision')
    paths = ['scripts/unixnu/payload.py', 'scripts/unixnu/util.py',
             'package/UniXNUPkg/Library/UniXNULib/Config.c',
             'package/UniXNUPkg/Library/UniXNULib/Menu.c']
    inputs = {}
    for relative in paths:
        raw = (source / relative).read_bytes()
        original = subprocess.check_output(['git', '-c', f'safe.directory={source.as_posix()}',
                                            '-C', str(source), 'show', f'{revision}:{relative}'])
        if raw != original:
            raise ValueError(f'Modified source: {relative}')
        inputs[relative] = digest(raw)
    raw = (ROOT / 'config/discovery-volume.toml').read_bytes()
    config = tomllib.loads(raw.decode())
    expected_entry = {'id': 'enuma-fat-discovery-01', 'title': 'ENUMA FAT DISCOVERY 01 - Restart',
                      'type': 'action', 'action': 'reset'}
    if config != {'version': 1, 'boot': {'timeout': 10, 'fallback_timeout': 10,
                                        'default': 'enuma-fat-discovery-01'},
                  'ui': {'title': 'ENUMA FAT DISCOVERY 01'}, 'kits': {'autoload': False},
                  'entry': [expected_entry]}:
        raise ValueError('Configuration-only discovery contract changed')
    sys.path.insert(0, str(source / 'scripts'))
    from unixnu.payload import EPOCH, write_volume
    out = ROOT / 'out/payload-discovery'
    out.mkdir(parents=True, exist_ok=True)
    # mformat's volume metadata also needs an epoch; fixing input mtimes alone
    # does not make two invocations reproducible on the installed mtools.
    os.environ['SOURCE_DATE_EPOCH'] = str(EPOCH)
    env = dict(os.environ, MTOOLS_SKIP_CHECK='1', TZ='UTC')
    with tempfile.TemporaryDirectory(dir=out, prefix='stage-') as scratch:
        stage = Path(scratch) / 'volume'
        config_path = stage / 'EFI/UniXNU/unixnu.toml'
        config_path.parent.mkdir(parents=True)
        config_path.write_bytes(raw)
        for path in [stage, *stage.rglob('*')]:
            os.utime(path, (EPOCH, EPOCH))
        images = [out / 'enuma-fat-discovery-01.img', Path(scratch) / 'repeat.img']
        cleared = []
        for image in images:
            write_volume(stage, image, 'ENUMAPROBE', 64)
            cleared.append(clear_free_clusters(image))
        first = images[0].read_bytes()
        second = images[1].read_bytes()
        if first != second:
            differences = [hex(i) for i, (a, b) in enumerate(zip(first, second)) if a != b]
            raise ValueError(f'Repeated FAT builds differ: {differences[:24]}')
        listing = subprocess.check_output(['mdir', '-i', str(images[0]), '-b', '-s', '::/'],
                                           env=env, text=True)
        files = [line.strip() for line in listing.splitlines() if line.strip() and not line.endswith('/')]
        if files != ['::/EFI/UniXNU/unixnu.toml']:
            raise ValueError(f'Unexpected FAT files: {files}')
        extracted = Path(scratch) / 'readback.toml'
        subprocess.run(['mcopy', '-i', str(images[0]), '::/EFI/UniXNU/unixnu.toml', str(extracted)],
                       env=env, check=True)
        if extracted.read_bytes() != raw:
            raise ValueError('FAT config readback differs')
        bps = struct.unpack_from('<H', first, 11)[0]
        sectors = struct.unpack_from('<I', first, 32)[0]
        if first[510:512] != b'\x55\xaa' or bps != 512 or sectors * bps != len(first):
            raise ValueError('FAT boot-sector size/signature mismatch')
        if first[82:90] != b'FAT32   ':
            raise ValueError('Expected FAT32')
        report = {'scope': 'offline mtools FAT build/readback, not UEFI discovery or a boot candidate',
                  'unixnu_commit': revision, 'source_sha256': inputs,
                  'config_sha256': digest(raw), 'image': str(images[0].relative_to(ROOT)),
                  'image_bytes': len(first), 'image_sha256': digest(first),
                  'logical_sector_bytes': bps, 'fat_type': 'FAT32', 'volume_label': 'ENUMAPROBE',
                  'source_date_epoch': EPOCH,
                  'free_cluster_normalization': 'Only FAT32 free clusters and post-cluster padding; identical FAT copies required',
                  'nonzero_free_clusters_cleared': cleared,
                  'files': files, 'repeat_build_identical': True, 'mcopy_readback_identical': True,
                  'contains_kernel_or_efi': False, 'boot_image_packaged': False,
                  'firmware_publisher_integrated': False, 'new_device_trials': 0,
                  'reset_limit': 'Menu countdown only; input cancels countdown; not a watchdog'}
        (ROOT / 'reports/enuma-discovery-volume.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: 64 MiB configuration-only FAT32; deterministic rebuild and exact mcopy readback')


if __name__ == '__main__':
    main()
