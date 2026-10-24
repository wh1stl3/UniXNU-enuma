import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import run_value_probes as value


class ValueTransportTests(unittest.TestCase):
    def test_decode_zero_max_and_ambiguity(self):
        self.assertEqual(value.decode(16.7,16.7),0)
        self.assertEqual(value.decode(61.7,16.7),15)
        for seconds in (15.0,18.2,64.7,float('nan'),float('inf')):
            with self.assertRaises(ValueError):value.decode(seconds,16.7)
        # The historical extra 2 seconds is rejected instead of decoded as 2.
        with self.assertRaises(ValueError):value.decode(18.7,16.7)

    def controls(self):
        return [dict(role='constant',outcome='returned',code=c,seconds=t,metric='adb_return_seconds')
                for c,t in ((0,16.7),(3,25.8),(0,16.9))]

    def test_measured_controls_and_noise_rejection(self):
        zero,metric=value.calibration(self.controls())
        self.assertAlmostEqual(zero,16.8)
        rows=self.controls();rows[-1]['seconds']=18
        with self.assertRaisesRegex(ValueError,'drift'):value.calibration(rows)
        rows=self.controls();rows[1]['seconds']=26.9
        with self.assertRaises(ValueError):value.calibration(rows)
        rows=self.controls();rows[1]['metric']='fastboot_return_seconds'
        with self.assertRaises(ValueError):value.calibration(rows)

    def test_timeout_stops_and_freezes_plan_before_another_tool_call(self):
        plan={'trials':[dict(id='zero1',role='constant',code=0,image='out/control.img',sha256={'image':'test'}),
                        dict(id='known3',role='constant',code=3)]}
        with tempfile.TemporaryDirectory(dir=ROOT/'out') as folder:
            root=Path(folder);(root/'out/device-tests').mkdir(parents=True)
            (root/'out/device-tests/current.local.json').write_text(json.dumps({'phase':'manual-recovery-needed'}))
            ledger=root/'ledger.json'
            with patch.object(value,'validate_plan'),patch.object(value,'require_published'):
                calls=[]
                def invoke(*args,**kwargs):
                    calls.append(args)
                    return SimpleNamespace(returncode=2)
                with self.assertRaisesRegex(ValueError,'freeze plan'):
                    value.run_one(root,plan,'zero1',ledger,True,invoke)
                self.assertEqual(len(calls),1)
                self.assertEqual(json.loads(ledger.read_text())['trials'][0]['outcome'],'failed')
                with self.assertRaisesRegex(ValueError,'freeze this plan'):
                    value.run_one(root,plan,'known3',ledger,True,invoke)
                self.assertEqual(len(calls),1)

    def test_dry_run_never_calls_device_tools(self):
        with patch.object(value,'validate_plan'),patch.object(value,'require_published',side_effect=AssertionError):
            self.assertFalse(value.run_one(ROOT,{'trials':[{'id':'zero1'}]},'zero1',Path('unused'))['device_action'])

    def test_changed_artifact_is_rejected_before_execution(self):
        plan={'schema':1,'seconds_per_code':3,'trials':[{
            'id':'zero1','image':'out/nonexistent.img','sha256':{'image':'wrong'}}]}
        with self.assertRaises((ValueError,FileNotFoundError)):
            value.validate_plan(plan,ROOT)


if __name__=='__main__':unittest.main()
