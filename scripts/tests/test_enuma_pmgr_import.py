"""Import-location tests only; fixtures do not stand in for donor ABI tests."""
import hashlib
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('pmgr_path_audit', Path(__file__).parents[1] / 'audit-enuma-pmgr-prelink.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ExplicitImport(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.helper = self.base / 'kits/XnuPrelink/native_prelink.py'
        self.helper.parent.mkdir(parents=True)
        self.helper.write_bytes(b'marker = "explicit pinned helper"\n')
        self.hash = hashlib.sha256(self.helper.read_bytes()).hexdigest()

    def test_other_cwd_and_cached_name_ignored(self):
        old_cwd = Path.cwd()
        try:
            os.chdir(self.base / 'kits')
            with patch.object(MODULE, 'PRELINK_LF_SHA256', self.hash), \
                 patch.object(MODULE.subprocess, 'check_output', return_value=MODULE.BASE_REVISION + '\n'), \
                 patch.dict(sys.modules, {'native_prelink': types.SimpleNamespace(marker='wrong cached helper')}):
                self.assertEqual(MODULE.load_native_prelink(self.base).marker, 'explicit pinned helper')
        finally:
            os.chdir(old_cwd)

    def test_hash_mismatch_rejected_before_execution(self):
        with self.assertRaisesRegex(ValueError, 'hash differs'):
            MODULE.load_native_prelink(self.base)

    def test_wrong_base_revision_rejected(self):
        with patch.object(MODULE, 'PRELINK_LF_SHA256', self.hash), \
             patch.object(MODULE.subprocess, 'check_output', return_value='wrong revision\n'), \
             self.assertRaisesRegex(ValueError, 'revision differs'):
            MODULE.load_native_prelink(self.base)

    def test_missing_file_never_imports_other_module(self):
        self.helper.unlink()
        with self.assertRaisesRegex(ValueError, 'no import fallback'):
            MODULE.load_native_prelink(self.base)

    def test_permission_error_is_explicit(self):
        with patch.object(Path, 'read_bytes', side_effect=PermissionError('fixture')), \
             self.assertRaisesRegex(ValueError, 'PYTHONPATH cannot repair filesystem permissions'):
            MODULE.load_native_prelink(self.base)


if __name__ == '__main__':
    unittest.main()
