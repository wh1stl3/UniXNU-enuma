"""Policy unit negatives, not synthetic-image or actual-target verification."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('audit', Path(__file__).resolve().parents[1] / 'audit-enuma-pid1.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AuditNegatives(unittest.TestCase):
    def test_mismatched_or_stale_artifact(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'artifact'
            path.write_bytes(b'old build bytes, not a Mach-O fixture')
            with self.assertRaisesRegex(ValueError, 'stale/mismatched'):
                audit.bound_file({'native': str(path), 'native_sha256': '0' * 64}, 'native')

    def test_missing_actual_hook(self):
        with self.assertRaisesRegex(ValueError, 'missing actual collector hook'):
            audit.require_hooks({'_enuma_pid1_begin': [1], '_enuma_pid1_svc': [1]})

    def test_changed_artifact_after_record(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'artifact'
            path.write_bytes(b'current bound bytes')
            record = {'prelink': str(path), 'prelink_sha256': audit.digest(path)}
            self.assertEqual(audit.bound_file(record, 'prelink'), path)
            path.write_bytes(b'stale bytes substituted after recording')
            with self.assertRaisesRegex(ValueError, 'stale/mismatched'):
                audit.bound_file(record, 'prelink')

    def test_atomic_load_then_external_tail(self):
        # Real A64 encodings: LDAR X0,[X0]; B +0x100. Never package a fake image.
        with self.assertRaisesRegex(ValueError, 'external branch/tail'):
            audit.check_leaf([0xc8dffc00, 0x14000040], 0x1000, 0x1008)

    def test_indirect_tail(self):
        with self.assertRaisesRegex(ValueError, 'indirect transfer'):
            audit.check_leaf([0xc8dffc00, 0xd61f0000], 0x1000, 0x1008)

    def test_local_retry_and_return(self):
        audit.check_leaf([0xc8dffc00, 0x17ffffff, 0xd65f03c0], 0x1000, 0x100c)


if __name__ == '__main__':
    unittest.main()
