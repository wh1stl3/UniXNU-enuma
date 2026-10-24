import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# WARNING: never patch `baseline.subprocess` to stub the device runner.
# run_next() binds invoke=subprocess.run as a DEFAULT ARGUMENT at import time, so
# patching the module attribute does not reach it and the real fastboot runner
# executes against the attached device. Always pass invoke= explicitly.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import run_hang_baseline as baseline


def plan(count=3, code=0, image_sha='same'):
    def trial(index):
        return dict(id=f'baseline{index+1}', role='constant', code=code,
                    image='out/value-transport/baseline/candidate.img',
                    raw='out/value-transport/baseline/candidate.raw',
                    build='out/value-transport/baseline/build.json',
                    audit='out/value-transport/baseline/audit.json',
                    package='out/value-transport/baseline/package.json',
                    sha256={'image': image_sha, 'raw': 'r', 'build': 'b', 'audit': 'a', 'package': 'p'})
    return {'schema': 1, 'seconds_per_code': 3, 'trials': [trial(i) for i in range(count)]}


class HangBaselineTests(unittest.TestCase):
    def test_rejects_non_zero_code(self):
        # R-009 is a zero-read measurement; a coded transport would reintroduce
        # the very timing the baseline is meant to be independent of.
        with self.assertRaisesRegex(ValueError, 'constant code 0'):
            baseline.check_baseline(plan(code=3))

    def test_rejects_mixed_candidates(self):
        candidate = plan(count=2)
        candidate['trials'][1]['sha256'] = dict(candidate['trials'][1]['sha256'], image='other')
        with self.assertRaisesRegex(ValueError, 'identical candidate'):
            baseline.check_baseline(candidate)

    def test_rejects_duplicate_ids(self):
        candidate = plan(count=2)
        candidate['trials'][1]['id'] = 'baseline1'
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            baseline.check_baseline(candidate)

    def test_rejects_over_budget(self):
        with self.assertRaisesRegex(ValueError, 'trial budget'):
            baseline.check_baseline(plan(count=17))

    def test_hang_does_not_freeze_the_plan(self):
        # The one deliberate difference from the value transport: a hang is a
        # measurement, so the following trial must remain runnable once the
        # device is verified back in Android.
        ledger = Path(tempfile.mkdtemp())/'ledger.json'
        recovered_state = {'candidate_sha256': plan()['trials'][0]['sha256']['image'],
                           'phase': 'manual-recovery-needed'}
        runner = Mock(return_value=_Result(2))
        with patch.object(baseline, 'validate_plan'), \
             patch.object(baseline, 'require_published'), \
             patch.object(baseline, 'device_recovered', return_value=True), \
             patch.object(baseline, 'read_state', return_value=recovered_state):
            first = baseline.run_next(ROOT, plan(), ledger, execute=True, invoke=runner)
        self.assertEqual(first['outcome'], 'hung')
        self.assertEqual(runner.call_count, 1)
        stored = json.loads(ledger.read_text())
        self.assertEqual(stored['summary'], {'issued': 1, 'returned': 0, 'hung': 1, 'hung_rate': 1.0})

    def test_unexpected_state_stops_the_baseline(self):
        ledger = Path(tempfile.mkdtemp())/'ledger.json'
        runner = Mock(return_value=_Result(0))
        with patch.object(baseline, 'validate_plan'), \
             patch.object(baseline, 'require_published'), \
             patch.object(baseline, 'device_recovered', return_value=True), \
             patch.object(baseline, 'read_state', return_value={'phase': 'fastboot-only'}):
            with self.assertRaisesRegex(ValueError, 'unexpected state'):
                baseline.run_next(ROOT, plan(), ledger, execute=True, invoke=runner)

    def test_refuses_next_trial_before_recovery(self):
        ledger = Path(tempfile.mkdtemp())/'ledger.json'
        runner = Mock(return_value=_Result(0))
        with patch.object(baseline, 'validate_plan'), \
             patch.object(baseline, 'require_published'), \
             patch.object(baseline, 'device_recovered', return_value=False):
            with self.assertRaisesRegex(ValueError, 'verified recovered state'):
                baseline.run_next(ROOT, plan(), ledger, execute=True, invoke=runner)
        runner.assert_not_called()

    def test_offline_validation_touches_nothing(self):
        ledger = Path(tempfile.mkdtemp())/'ledger.json'
        runner = Mock()
        with patch.object(baseline, 'validate_plan'):
            row = baseline.run_next(ROOT, plan(), ledger, execute=False, invoke=runner)
        self.assertFalse(row['device_action'])
        runner.assert_not_called()
        self.assertFalse(ledger.exists())


class _Result:
    def __init__(self, returncode):
        self.returncode = returncode
        self.stdout = ''
        self.stderr = ''


if __name__ == '__main__':
    unittest.main()
