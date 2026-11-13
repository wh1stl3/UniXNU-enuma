#!/usr/bin/env python3
"""Offline tests only; no Apple downloads or APFS creation."""
import importlib.util
import io
import json
import os
from pathlib import Path
import ssl
import stat
import struct
import subprocess
import sys
import tarfile
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

HERE = Path(__file__).resolve().parent
BASE = Path(os.environ.get('UNIXNU_ROOT', HERE.parents[3] / 'UniXNU'))


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build, receive = load('build'), load('receive')


class ToolsTests(unittest.TestCase):
    def test_actual_seed_fill_under_private_umask(self):
        official = build.load('fixture_official_make_data_seed', BASE / 'scripts/make-data-seed.py')
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            os_mount, work = root / 'os', root / 'work'
            source = os_mount / 'private/var'
            source.mkdir(parents=True)
            source.chmod(0o755)
            (source / 'special').mkdir()
            (source / 'special').chmod(0o710)
            (source / 'special/value').write_bytes(b'fixture')
            (source / 'special/value').chmod(0o640)
            (source / 'link').symlink_to('special', target_is_directory=True)
            work.mkdir()
            self.assertFalse((source / 'mobile').exists())
            self.assertFalse((source / 'containers').exists())
            def command(*args, **kwargs):
                if args[:2] == ('hdiutil', 'create'):
                    header = bytearray(4096)
                    header[32:36] = b'NXSB'
                    struct.pack_into('<IQ', header, 36, 4096, build.PIN['seed_bytes'] // 4096)
                    with Path(args[-1]).open('xb') as raw:
                        raw.write(header)
                        raw.truncate(build.PIN['seed_bytes'])
                return b''
            mask = os.umask(0o077)
            try:
                with patch.object(build, 'load', return_value=official), \
                     patch.object(build, 'run', side_effect=command), \
                     patch.object(build, 'attach', return_value=('fixture-disk', 'fixture-volume', {'VolumeUUID': 'fixture'})), \
                     patch.object(official.packed_ramdisk, 'pack', return_value={'bytes': build.PIN['seed_bytes'], 'packed': True}) as pack:
                    build.make_seed(BASE, work, os_mount)
                    pack.assert_called_once()
                self.assertEqual(os.umask(0o077), 0o077)
                mount = work / 'data-mount'
                for name in ('mobile', 'mobile/tmp', 'root', 'run', 'keybags', 'containers',
                             'containers/Bundle', 'containers/Data', 'containers/Data/System',
                             'containers/Shared', 'containers/Shared/SystemGroup', 'containers/Temp',
                             'mobile/Library', 'mobile/Library/Preferences',
                             'root/Library', 'root/Library/Preferences'):
                    self.assertEqual(stat.S_IMODE((mount / name).stat().st_mode), 0o755, name)
                self.assertEqual(stat.S_IMODE((mount / 'tmp').stat().st_mode), 0o1777)
                self.assertEqual(stat.S_IMODE((mount / 'special').stat().st_mode), 0o710)
                self.assertEqual(stat.S_IMODE((mount / 'special/value').stat().st_mode), 0o640)
                self.assertEqual(os.readlink(mount / 'link'), 'special')
                self.assertTrue((mount / 'mobile/Library/Preferences/backboardd.plist').is_file())
                # The actual official merge path fails: restoration is still mandatory.
                mount2 = work / 'failure-mount'
                mount2.mkdir()
                with patch.object(official, 'merge', side_effect=RuntimeError('fixture merge failure')):
                    with self.assertRaisesRegex(RuntimeError, 'merge failure'):
                        build.populate_seed(official, source, mount2)
                self.assertEqual(os.umask(0o077), 0o077)
            finally:
                os.umask(mask)

    def test_tool_failure_reasons_are_bounded_and_redacted(self):
        for tool, operation, reason in (
                ('hdiutil', 'create', 'hdiutil: create failed - No space left on device'),
                ('diskutil', 'verifyVolume', 'Error: File system verify or repair failed'),
                ('openssl', 'cms', 'Error: unable to load recipient certificate')):
            stdout = (b'non-diagnostic plaintext fixture\n'
                      b'Error /private/sensitive/seed.cdr 04769D26-2CA0-4825-B443-E2E5F88300F2\n')
            stderr = (reason + '\nError "C:\\Sensitive Folder\\key.pem" token=fixture-token '
                      'password="fixture password" Authorization: Bearer fixture-bearer '
                      'GH_TOKEN=fixture-gh-token\n' + 'Error x' * 300).encode()
            if tool == 'diskutil':
                # diskutil often puts its actual failure reason on stdout.
                stdout = reason.encode() + b'\n' + stdout
                stderr = b'Error token=fixture-token GH_TOKEN=fixture-gh-token\n'
            result = subprocess.CompletedProcess([], 1, stdout, stderr)
            with patch.object(build.subprocess, 'run', return_value=result):
                with self.assertRaises(RuntimeError) as caught:
                    build.run(tool, operation, stage='fixture stage')
            message = str(caught.exception)
            self.assertIn('fixture stage exited 1', message)
            self.assertIn(reason, message)
            self.assertLessEqual(len(message), 800)
            for value in ('sensitive', 'Sensitive Folder', '04769D26', 'fixture-token',
                          'fixture password', 'fixture-bearer', 'fixture-gh-token', 'plaintext fixture'):
                self.assertNotIn(value, message)

    def test_main_encryption_failure_has_no_upload(self):
        # Run the real main publish path; only platform tools and Apple inputs are mocked.
        der = ssl.PEM_cert_to_DER_cert((HERE / 'recipient.pem').read_text())
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            def command(args, **kwargs):
                if args[0] == 'git':
                    if 'hash-object' in args:
                        output = build.PIN['packed_ramdisk_git_blob']
                    else:
                        output = build.PIN['darwinboot_revision'] if args[2].endswith('DarwinBoot') else build.PIN['unixnu_revision']
                    return subprocess.CompletedProcess(args, 0, output.encode(), b'')
                if 'cms' in args:
                    return subprocess.CompletedProcess(args, 1, b'private fixture content',
                        b'Error: unable to load recipient certificate /private/hidden/recipient.pem')
                return subprocess.CompletedProcess(args, 0, der if '-outform' in args else b'', b'')
            def seed(base, work, mount):
                path = work / 'data.dbr'
                path.write_bytes(b'fixture')
                return path, {}
            with patch.object(sys, 'argv', ['build.py', '--unixnu', str(BASE), '--openssl', 'openssl']), \
                 patch.object(sys, 'platform', 'darwin'), \
                 patch.dict(os.environ, RUNNER_TEMP=td, GITHUB_SHA='fixture', GITHUB_RUN_ID='1'), \
                 patch.object(build.subprocess, 'run', side_effect=command), \
                 patch.object(build.shutil, 'disk_usage', return_value=SimpleNamespace(free=12 * build.GIB)), \
                 patch.object(build, 'fetch_os', side_effect=lambda base, work: work / 'fixture.dmg'), \
                 patch.object(build, 'attach', return_value=('fixture-disk', 'fixture-volume', {'VolumeUUID': '04769D26-2CA0-4825-B443-E2E5F88300F2'})), \
                 patch.object(build, 'make_seed', side_effect=seed), \
                 patch.object(build, 'load', return_value=SimpleNamespace(verify_seed=Mock())), \
                 patch.object(Path, 'is_file', return_value=True), \
                 patch.object(Path, 'is_dir', return_value=True):
                with self.assertRaisesRegex(RuntimeError, 'encrypt Data CMS.*unable to load recipient certificate') as caught:
                    build.main()
            self.assertNotIn('/private/hidden', str(caught.exception))
            self.assertNotIn('private fixture content', str(caught.exception))
            self.assertEqual(list((temp / 'enuma-seed-upload').iterdir()), [])

    def test_copy_policy(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source, dest = root / 'source', root / 'dest'
            source.mkdir()
            dest.mkdir()
            (source / 'tmp').mkdir(mode=0o700)
            (source / 'tmp/value').write_bytes(b'fixture')
            (source / 'staged_system_apps').mkdir()
            (source / 'staged_system_apps/excluded').write_bytes(b'not copied')
            (source / 'link').symlink_to('tmp', target_is_directory=True)
            build.copy_var(source, dest)
            self.assertEqual((dest / 'tmp/value').read_bytes(), b'fixture')
            self.assertTrue((dest / 'link').is_symlink())
            self.assertFalse((dest / 'staged_system_apps').exists())

    def test_archive_whitelist(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            archive = root / 'seed.tar'
            out = root / 'out'
            out.mkdir()
            with tarfile.open(archive, 'w') as tar:
                entry = tarfile.TarInfo('../escape')
                entry.size = 1
                tar.addfile(entry, io.BytesIO(b'x'))
            with self.assertRaises(ValueError):
                receive.unpack(archive, out)
            self.assertEqual(list(out.iterdir()), [])

    def test_archive_valid(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            archive = root / 'seed.tar'
            out = root / 'out'
            out.mkdir()
            with tarfile.open(archive, 'w') as tar:
                for name, value in [('data.dbr', b'fixture'), ('manifest.json', b'{}')]:
                    entry = tarfile.TarInfo(name)
                    entry.size = len(value)
                    tar.addfile(entry, io.BytesIO(value))
            receive.unpack(archive, out)
            self.assertEqual((out / 'data.dbr').read_bytes(), b'fixture')

    def test_bad_checksum(self):
        self.assertFalse(receive.apfs_checksum(bytes(4096)))

    def test_manifest_binding(self):
        report = dict(source={}, run_id='1', device_revision='a', first_install=True,
                      hardware_tested=False, data={'skip_setup': False})
        with self.assertRaisesRegex(ValueError, 'provenance'):
            receive.verify_seed(None, None, report, 1, 'a')

    def test_range_failures_no_retry(self):
        class Response:
            status = 200
            headers = {'Content-Length': str(build.PIN['archive_bytes'])}
            def __enter__(self): return self
            def __exit__(self, *args): pass
        # Reuse only the superclass contract; no real network call.
        class Ipsw:
            RangeFile = object
        cls = build.strict_ranges(Ipsw)
        with patch('urllib.request.urlopen', return_value=Response()) as urlopen:
            stream = cls('https://updates.cdn-apple.com/fixture')
            with self.assertRaisesRegex(ValueError, 'range response'):
                stream._block(0)
            self.assertEqual(urlopen.call_count, 2)  # HEAD, one failing GET.


if __name__ == '__main__':
    unittest.main()
