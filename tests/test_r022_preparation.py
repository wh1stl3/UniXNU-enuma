"""No device calls: migration, local binding and fail-closed one-shot release."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import r022_preparation as prep
from enuma_paths import evidence_path
from native_pixel_scope import LONG_LOG_SCOPE
import run_system_transport_trial as runner
import run_enuma_entry_probe as entry


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'out')
        self.root=Path(self.temp.name).resolve();(self.root/'out/device-tests').mkdir(parents=True)
        self.meta=dict(image_sha256=prep.IMAGE,hardware_review='R-022',pixel_scope=LONG_LOG_SCOPE)
        self.q=dict(**self.meta,firmware_commit=prep.FIRMWARE,archive=prep.ARCHIVE,boot_log_hold_seconds=8)
    def tearDown(self):self.temp.cleanup()

    def test_migration_resolves_only_enuma_out(self):
        for value in ('D:\\Code\\UniXNU-enuma\\out\\backup','/mnt/d/Code/UniXNU-enuma/out/backup',
                      'D:/Code/PortingiOS/enuma/UniXNU-enuma/out/backup','out/backup',str(self.root/'out/backup')):
            self.assertEqual(evidence_path(value,self.root),self.root/'out/backup')
        for value in ('D:/Code/UniXNU-nuwa/out/backup','out/../outside','D:/Code/UniXNU-enuma-other/out/a',
                      '../out/a','out//a','out/a/../../escape'):
            with self.subTest(value=value),self.assertRaises(ValueError):evidence_path(value,self.root)

    def fixture_binding(self):
        for name in prep.BINDINGS:
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture '+name)
        data=dict(schema=1,image_sha256=prep.IMAGE,trial='S-050',authorizes_execution=False,
                  publication='local-bound-no-commit',bindings={n:prep.sha(self.root/n) for n in prep.BINDINGS})
        target=self.root/'out/preparation.json';target.write_text(json.dumps(data))
        return target,data

    def test_binding_rejects_drift_other_image_and_incomplete_manifest(self):
        target,data=self.fixture_binding()
        with patch.object(prep,'QUALIFICATION',prep.sha(self.root/prep.ARCHIVE/'qualification.json')):
            prep.require_local_preparation(target,self.q,self.root)
            for key,value in [('image_sha256','0'*64),('hardware_review','R-021'),('boot_log_hold_seconds',2)]:
                with self.assertRaises(ValueError):prep.require_local_preparation(target,{**self.q,key:value},self.root)
            (self.root/'scripts/run_enuma_entry_probe.py').write_text('changed runner')
            with self.assertRaisesRegex(ValueError,'stale'):prep.require_local_preparation(target,self.q,self.root)
            data['bindings'].pop('scripts/run_enuma_entry_probe.py');target.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'incomplete'):prep.require_local_preparation(target,self.q,self.root)

    def test_preparation_is_not_hardware_approval(self):
        with self.assertRaisesRegex(ValueError,'not approved'):
            entry.require_hardware_review(self.meta,{'R-022':dict(status='pending',image_sha256=[prep.IMAGE],pixel_scope=LONG_LOG_SCOPE)})

    def test_readiness_identity_and_exact_scope_before_claim(self):
        for meta,identity,ready in ((self.meta,str(uuid4()),False),(self.meta,None,True),
                                    ({**self.meta,'image_sha256':'0'*64},str(uuid4()),True),
                                    ({**self.meta,'pixel_scope':{}},str(uuid4()),True)):
            with self.assertRaises((ValueError,AttributeError)):
                prep.require_attempt(self.root,meta,identity,ready,claim=True)
            self.assertFalse((self.root/'out/device-tests/claimed-R-022.local.json').exists())

    def test_claim_is_atomic_and_survives_missing_consumed_marker(self):
        def attempt(_):
            try:prep.require_attempt(self.root,self.meta,str(uuid4()),True,claim=True);return True
            except (ValueError,FileExistsError):return False
        with ThreadPoolExecutor(max_workers=2) as pool:self.assertEqual(sum(pool.map(attempt,range(2))),1)
        with self.assertRaises(ValueError):prep.require_attempt(self.root,self.meta,str(uuid4()),True)

    def test_old_issue_record_blocks_reissue_without_claim_file(self):
        old=self.root/'out/device-tests/previous';old.mkdir()
        (old/'result.json').write_text(json.dumps(dict(candidate_sha256=prep.IMAGE,issued_at='historical')))
        with self.assertRaisesRegex(ValueError,'already issued'):prep.require_attempt(self.root,self.meta,str(uuid4()),True)

    def test_new_capture_failure_does_not_attribute_stale_attempt(self):
        (self.root/'config').mkdir();(self.root/'reports').mkdir()
        (self.root/'config/hardware-review-approvals.json').write_text(json.dumps({'R-022':dict(
            status='approved',image_sha256=[prep.IMAGE],pixel_scope=LONG_LOG_SCOPE,capture_mode='human-primary-only')}))
        image=self.root/'out/image.img';image.with_suffix('.json').write_text(json.dumps(self.meta))
        state=dict(candidate_sha256=prep.IMAGE,issued_at='prior',execution_id=str(uuid4()),hardware_review='R-022')
        (self.root/'out/device-tests/current.local.json').write_text(json.dumps(state))
        q={**self.q,'boot_log_replay':True,'trial_kind':'native-video-route'}
        with patch.object(runner,'ROOT',self.root),patch.object(entry,'ROOT',self.root),\
             patch.object(runner.subprocess,'run',return_value=type('Result',(),{'returncode':1})()),\
             self.assertRaises(RuntimeError):runner.run_with_human_capture(q,image,None,str(uuid4()),True)
        report=json.loads((self.root/'reports/enuma-system-trial-observation.json').read_text())
        self.assertFalse(report['boot_issued'])
        self.assertFalse((self.root/'out/device-tests'/('consumed-'+prep.IMAGE+'.local.json')).exists())


if __name__=='__main__':unittest.main()
