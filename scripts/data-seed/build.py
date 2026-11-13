#!/usr/bin/env python3
"""One-shot macOS Data creation; no device access, owner keys or plaintext upload."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import urllib.request
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
PIN = json.loads((HERE / 'source.json').read_text())
GIB = 1024**3


def run(*args):
    # hdiutil/diskutil output may contain UUIDs: keep it out of public logs.
    result = subprocess.run([str(a) for a in args], capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(f'{Path(str(args[0])).name} {args[1]} exited {result.returncode}')
    return result.stdout


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_var(source, mount):
    """Same copy/mode/symlink policy as pinned make-data-seed.py; no setup skip."""
    for current, dirs, files in os.walk(source, followlinks=False):
        dirs[:] = [n for n in dirs if n != 'staged_system_apps']
        dest = mount / Path(current).relative_to(source)
        dest.mkdir(exist_ok=True)
        dest.chmod(stat.S_IMODE(Path(current).stat().st_mode))
        for name in list(dirs) + files:
            src, dst = Path(current) / name, dest / name
            if src.is_symlink():
                dst.symlink_to(os.readlink(src))
                if name in dirs:
                    dirs.remove(name)
            elif src.is_file():
                shutil.copy2(src, dst)


def attach(image, mount, readonly=False):
    args = ['hdiutil', 'attach', '-nobrowse', '-owners', 'off', '-plist',
            '-mountpoint', mount]
    if readonly:
        args.append('-readonly')
    listing = plistlib.loads(run(*args, image))['system-entities']
    # Return the whole image device for detach, not just the APFS volume.
    device = listing[0]['dev-entry']
    try:
        volumes = [e for e in listing if e.get('mount-point') == str(mount)]
        if len(volumes) != 1:
            raise ValueError('expected one mounted volume')
        info = plistlib.loads(run('diskutil', 'info', '-plist', volumes[0]['dev-entry']))
        return device, volumes[0]['dev-entry'], info
    except BaseException:
        run('hdiutil', 'detach', device, '-force')
        raise


def strict_ranges(ipsw):
    class CheckedRange(ipsw.RangeFile):
        def __init__(self, url):
            self.url, self.block, self.position, self.cache = url, 8 << 20, 0, {}
            # Zero automatic retries, including permissions/region/quota failures.
            with urllib.request.urlopen(urllib.request.Request(url, method='HEAD'), timeout=60) as r:
                self.size = int(r.headers['Content-Length'])
            if self.size != PIN['archive_bytes']:
                raise ValueError('archive size differs from provenance')

        def _block(self, index):
            if index not in self.cache:
                start = index * self.block
                end = min(start + self.block, self.size) - 1
                req = urllib.request.Request(self.url, headers={
                    'Range': f'bytes={start}-{end}', 'Accept-Encoding': 'identity'})
                with urllib.request.urlopen(req, timeout=120) as r:
                    if r.status != 206 or r.headers.get('Content-Range') != f'bytes {start}-{end}/{self.size}':
                        raise ValueError('unexpected HTTP range response')
                    data = r.read(end - start + 2)
                if len(data) != end - start + 1:
                    raise ValueError('HTTP range length mismatch')
                if len(self.cache) >= 4:
                    self.cache.pop(next(iter(self.cache)))
                self.cache[index] = data
            return self.cache[index]
    return CheckedRange


def fetch_os(base, work):
    sys.path.insert(0, str(base / 'scripts'))
    from unixnu import ipsw
    ipsw.RangeFile = strict_ranges(ipsw)
    profile = tomllib.loads((base / 'profiles/os/ipados-17.7.11-21H461/profile.toml').read_text())
    c = profile['ipsw']
    if (c['product'], c['device_class'], c['build'], c['chip_id'], c['board_id']) != (
            'iPad7,1', 'j120ap', '21H461', 0x8011, 12):
        raise ValueError('unexpected profile identity')
    expected_url = ('https://updates.cdn-apple.com/2025SpringFCS/fullrestores/122-77166/'
                    'DCA6CFE8-90E9-4B92-880D-3DE171798E40/iPad_Pro_HFR_17.7.11_21H461_Restore.ipsw')
    if c['url'] != expected_url or c['sha256'][PIN['os_member']] != PIN['os_sha256']:
        raise ValueError('profile source/pin differs')
    ctx = SimpleNamespace(board=profile, out_root=work, option_text=lambda *args: None)
    source = ipsw.Ipsw(ctx)  # Official full manifest identity check.
    manifest = source.zip.read('BuildManifest.plist')
    if hashlib.sha256(manifest).hexdigest() != PIN['manifest_sha256']:
        raise ValueError('BuildManifest differs from local provenance')
    if source.member('OS') != PIN['os_member']:
        raise ValueError('OS manifest member differs')
    entry = source.zip.getinfo(PIN['os_member'])
    if (entry.header_offset, entry.file_size, entry.compress_size, entry.compress_type, entry.CRC) != (
            PIN['os_header_offset'], PIN['os_bytes'], PIN['os_bytes'], 0, int(PIN['os_crc32'], 16)):
        raise ValueError('OS ZIP metadata differs from provenance')
    path = work / PIN['os_member']
    digest = hashlib.sha256()
    with source.zip.open(entry) as src, path.open('xb') as dst:
        while chunk := src.read(8 << 20):
            digest.update(chunk)
            dst.write(chunk)
    source.zip.close()
    if path.stat().st_size != PIN['os_bytes'] or digest.hexdigest() != PIN['os_sha256']:
        raise ValueError('OS member SHA-256/size mismatch')
    return path


def make_seed(base, work, os_mount):
    official = load('official_make_data_seed', base / 'scripts/make-data-seed.py')
    packer = official.packed_ramdisk
    raw, mount = work / 'data.cdr', work / 'data-mount'
    mount.mkdir()
    # Final-size raw image, bounded at 3 GiB even on a non-sparse filesystem.
    run('hdiutil', 'create', '-size', '3g', '-layout', 'NONE', '-fs', 'APFS',
        '-volname', 'Data', '-type', 'UDTO', raw)
    device, volume, info = attach(raw, mount)
    try:
        copy_var(os_mount / 'private/var', mount)
        for name in ('keybags', 'mobile/tmp', 'tmp', 'run', 'containers/Bundle',
                     'containers/Data/System', 'containers/Shared/SystemGroup', 'containers/Temp'):
            (mount / name).mkdir(parents=True, exist_ok=True)
        (mount / 'tmp').chmod(0o1777)
        for home in ('root', 'mobile'):
            for name in ('backboardd', '.GlobalPreferences'):
                official.merge(mount, home, name, dict(CAEnableDeepFramebuffer=False,
                    CAEnableFramebufferCompression=False, CAEnableIOSurfaceCompression=False))
        run('diskutil', 'verifyVolume', volume)
    finally:
        run('hdiutil', 'detach', device, '-force')
    if raw.stat().st_size != PIN['seed_bytes']:
        raise ValueError('seed raw size differs')
    with raw.open('rb') as f:
        header = f.read(4096)
    if (header[32:36] != b'NXSB' or int.from_bytes(header[36:40], 'little') != 4096
            or int.from_bytes(header[40:48], 'little') * 4096 != PIN['seed_bytes']):
        raise ValueError('APFS container does not fill the 3 GiB raw image')
    output = work / 'data.dbr'
    metadata = packer.pack(raw, output)  # Official 256 MiB and extent bounds.
    if metadata['bytes'] != PIN['seed_bytes'] or not metadata['packed']:
        raise ValueError('invalid packed seed')
    return output, dict(**metadata, volume_uuid=info['VolumeUUID'],
                        filesystem_check='diskutil verifyVolume exit 0', skip_setup=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--unixnu', type=Path, required=True)
    p.add_argument('--openssl', required=True)
    args = p.parse_args()
    base = args.unixnu.resolve()
    if sys.platform != 'darwin':
        p.error('creation requires macOS')
    for root, revision in ((base, PIN['unixnu_revision']),
                           (base / 'drivers/DarwinBoot', PIN['darwinboot_revision'])):
        if run('git', '-C', root, 'rev-parse', 'HEAD').decode().strip() != revision:
            raise ValueError('source revision mismatch')
    packer_path = base / 'drivers/DarwinBoot/Test/packed_ramdisk.py'
    if run('git', 'hash-object', packer_path).decode().strip() != PIN['packed_ramdisk_git_blob']:
        raise ValueError('packed writer differs')
    cert = HERE / 'recipient.pem'
    fingerprint = run(args.openssl, 'x509', '-in', cert, '-outform', 'DER')
    if hashlib.sha256(fingerprint).hexdigest() != PIN['certificate_sha256']:
        raise ValueError('recipient fingerprint mismatch')
    run(args.openssl, 'x509', '-in', cert, '-checkend', '7200', '-noout')
    temp = Path(os.environ['RUNNER_TEMP'])
    if shutil.disk_usage(temp).free < 11 * GIB:
        raise ValueError('less than 11 GiB free; stop before Apple download')
    upload = temp / 'enuma-seed-upload'
    upload.mkdir()  # Never reuse an old upload directory.
    with tempfile.TemporaryDirectory(prefix='enuma-seed-', dir=temp) as td:
        work = Path(td)
        image = fetch_os(base, work)
        mount = work / 'os-mount'
        mount.mkdir()
        device, _, info = attach(image, mount, readonly=True)
        try:
            if info['VolumeUUID'].upper() != '04769D26-2CA0-4825-B443-E2E5F88300F2':
                raise ValueError('OS volume UUID differs')
            if not (mount / 'sbin/launchd').is_file() or not (mount / 'private/var').is_dir():
                raise ValueError('not an IPSW OS volume')
            output, metadata = make_seed(base, work, mount)
        finally:
            run('hdiutil', 'detach', device, '-force')
        report = dict(source=PIN, data=metadata, first_install=True, preserve_for_future_builds=True,
                      hardware_tested=False, device_revision=os.environ['GITHUB_SHA'],
                      run_id=os.environ['GITHUB_RUN_ID'])
        # Detect unsupported/broken SEEK_DATA as well as format/UUID mismatches
        # before encryption/upload, using the same checks as the local receiver.
        receiver = load('seed_receiver', HERE / 'receive.py')
        receiver.verify_seed(load('seed_packer', packer_path), output, report,
                             report['run_id'], report['device_revision'])
        manifest = work / 'manifest.json'
        manifest.write_text(json.dumps(report, indent=2) + '\n')
        archive = work / 'seed.tar'
        with tarfile.open(archive, 'x') as tar:
            # Explicit plaintext whitelist, never a directory glob.
            for path in (output, manifest):
                tar.add(path, arcname=path.name, recursive=False)
        ciphertext = work / 'data-seed.cms'
        run(args.openssl, 'cms', '-encrypt', '-aes-256-gcm', '-binary', '-outform', 'DER',
            '-in', archive, '-out', ciphertext, cert)
        # Publish only after CMS encryption completed; failures never upload.
        ciphertext.rename(upload / 'data-seed.cms')
    print('Pinned OS verified; 3 GiB first-install seed encrypted. No plaintext upload.')


if __name__ == '__main__':
    main()
