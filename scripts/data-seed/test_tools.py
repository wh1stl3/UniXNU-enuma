#!/usr/bin/env python3
"""Offline tests only; no Apple downloads or APFS creation."""
import importlib.util
import io
import json
from pathlib import Path
import struct
import tarfile
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build, receive = load('build'), load('receive')


class ToolsTests(unittest.TestCase):
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
