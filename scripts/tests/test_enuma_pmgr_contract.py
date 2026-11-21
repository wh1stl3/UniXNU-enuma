"""Host-only input gates; these are not donor ABI or runtime tests."""
import argparse
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('pmgr_contract', Path(__file__).parents[1] / 'audit-enuma-pmgr-contract.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class InputGates(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        (root / 'scripts').mkdir()
        (root / 'scripts/audit-amfi-pmgr-contract.py').write_text('pinned fixture')
        self.args = argparse.Namespace(base=root)
        for name in ('donor', 'candidate', 'manifest'):
            path = root / name
            path.write_text(name)
            setattr(self.args, name, path)
            setattr(self.args, name + '_sha256', MODULE.sha256(path))
        self.plan = {'original_sha256': self.args.donor_sha256, 'components': ['com.apple.driver.ApplePMGR']}
        self.save_plan()
        self.hash_patch = patch.object(MODULE, 'AUDIT_SHA256', MODULE.sha256(root / 'scripts/audit-amfi-pmgr-contract.py'))
        self.hash_patch.start()
        self.addCleanup(self.hash_patch.stop)
        self.git_patch = patch.object(MODULE.subprocess, 'check_output', side_effect=[MODULE.BASE_REVISION + '\n', ''])
        self.git_patch.start()
        self.addCleanup(self.git_patch.stop)

    def save_plan(self):
        self.args.manifest.write_text(json.dumps(self.plan))
        self.args.manifest_sha256 = MODULE.sha256(self.args.manifest)

    def test_valid_explicit_inputs(self):
        MODULE.validate(self.args)

    def test_missing_candidate_no_fallback(self):
        self.args.candidate.unlink()
        with self.assertRaisesRegex(ValueError, 'no fallback'):
            MODULE.validate(self.args)

    def test_wrong_input_hash(self):
        self.args.donor_sha256 = '0' * 64
        with self.assertRaisesRegex(ValueError, 'donor SHA256'):
            MODULE.validate(self.args)

    def test_manifest_donor_binding(self):
        self.plan['original_sha256'] = '0' * 64
        self.save_plan()
        with self.assertRaisesRegex(ValueError, 'donor binding'):
            MODULE.validate(self.args)

    def test_forbid_hardware_driver(self):
        self.plan['components'].append('com.apple.driver.AppleT8011PMGR')
        self.save_plan()
        with self.assertRaisesRegex(ValueError, 'Hardware PMGR'):
            MODULE.validate(self.args)


if __name__ == '__main__':
    unittest.main()
