"""Pure parameter negatives, not simulated device or ABI evidence."""
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('pmgr_prelink', Path(__file__).parents[1] / 'audit-enuma-pmgr-prelink.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Parameters(unittest.TestCase):
    def test_exact_mode_two(self):
        MODULE.check_args('-v serial=3 rd=md0-ramblock pmgr=2')
        MODULE.check_args(['-v', 'pmgr=2'])

    def test_reject_missing_duplicate_wrong_alias(self):
        for args in ('-v', 'pmgr', 'pmgr 2', 'pmgr=1', 'pmgr=0', 'pmgr=3', 'pmgr=02',
                     'pmgr=2 pmgr=2', 'pmgr=1 pmgr=2', '-pmgr=2', '--pmgr=2',
                     'pmgr=2 sheng-pmgr=2', 'sheng-pmgr=2', 'pmgr=2 -sheng-pmgr'):
            with self.subTest(args=args), self.assertRaises(ValueError):
                MODULE.check_args(args)


if __name__ == '__main__':
    unittest.main()
