"""No device calls: one-shot R024, exact scope, stale bindings and policy rejection."""
import copy
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import r024_preparation as p
from native_pixel_scope import DIAGNOSTIC_LOG_SCOPE
from firmware_audit_policy import omitted_oem_modules
from run_enuma_entry_probe import require_hardware_review
from run_enuma_entry_probe import bound_android_online
import run_system_transport_trial as runner
import run_enuma_entry_probe as entry


class R024Tests(unittest.TestCase):
    def test_failed_new_capture_does_not_consume_stale_attempt(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for n in ('config','reports','out/device-tests'): (root/n).mkdir(parents=True)
            meta=dict(hardware_review='R-024',image_sha256='a'*64,pixel_scope=DIAGNOSTIC_LOG_SCOPE)
            (root/'config/hardware-review-approvals.json').write_text(json.dumps({'R-024':dict(status='approved',image_sha256=['a'*64],pixel_scope=DIAGNOSTIC_LOG_SCOPE,capture_mode='human-primary-only')}))
            image=root/'out/image.img';image.with_suffix('.json').write_text(json.dumps(meta))
            (root/'out/device-tests/current.local.json').write_text(json.dumps(dict(candidate_sha256='a'*64,issued_at='past',execution_id=str(uuid4()),hardware_review='R-024')))
            q=dict(meta,boot_log_replay=True,boot_log_hold_seconds=8,trial_kind='native-video-route')
            with patch.object(runner,'ROOT',root),patch.object(entry,'ROOT',root),patch.object(runner.subprocess,'run',return_value=type('Result',(),{'returncode':1})()),self.assertRaises(RuntimeError):
                runner.run_with_human_capture(q,image,None,str(uuid4()),True)
            self.assertFalse(json.loads((root/'reports/enuma-system-trial-observation.json').read_text())['boot_issued'])
            self.assertFalse((root/'out/device-tests'/('consumed-'+'a'*64+'.local.json')).exists())

    def test_only_bound_target_enumeration(self):
        self.assertTrue(bound_android_online(['List of devices attached','other device','bound device'],'bound'))
        for rows in (['other device'],['bound offline'],['bound unauthorized'],['bound device','bound device']):
            self.assertFalse(bound_android_online(['List of devices attached',*rows],'bound'))

    def test_pending_wrong_image_scope_and_consumed(self):
        meta=dict(hardware_review='R-024',image_sha256='a'*64,pixel_scope=DIAGNOSTIC_LOG_SCOPE)
        approval=dict(status='approved',image_sha256=['a'*64],pixel_scope=DIAGNOSTIC_LOG_SCOPE)
        require_hardware_review(meta,{'R-024':approval})
        for field,value in [('status','pending'),('status','consumed'),('image_sha256',['b'*64]),('pixel_scope',{})]:
            bad={**approval,field:value}
            with self.assertRaises(ValueError): require_hardware_review(meta,{'R-024':bad})

    def test_atomic_claim_and_stale_attempt(self):
        with tempfile.TemporaryDirectory() as td,patch.object(p,'IMAGE','a'*64):
            root=Path(td);(root/'out/device-tests').mkdir(parents=True)
            meta=dict(hardware_review='R-024',image_sha256=p.IMAGE,pixel_scope=DIAGNOSTIC_LOG_SCOPE)
            for ready,eid in [(False,str(uuid4())),(True,''),(True,'bad')]:
                with self.assertRaises(ValueError): p.require_attempt(root,meta,eid,ready)
            def claim(_):
                try: p.require_attempt(root,meta,str(uuid4()),True,True);return True
                except (ValueError,FileExistsError): return False
            with ThreadPoolExecutor(max_workers=2) as pool: self.assertEqual(sum(pool.map(claim,range(2))),1)
            with self.assertRaises(ValueError): p.require_attempt(root,meta,str(uuid4()),True)

    def test_historical_issue_blocks_without_marker(self):
        with tempfile.TemporaryDirectory() as td,patch.object(p,'IMAGE','a'*64):
            root=Path(td);d=root/'out/device-tests/history';d.mkdir(parents=True)
            (d/'result.json').write_text(json.dumps(dict(candidate_sha256=p.IMAGE,issued_at='past')))
            with self.assertRaises(ValueError): p.unused(root)

    def test_local_binding_tamper(self):
        with tempfile.TemporaryDirectory() as td,patch.object(p,'IMAGE','a'*64),patch.object(p,'BINDINGS',('source',)):
            root=Path(td);(root/'out').mkdir();(root/'source').write_text('before')
            data=dict(image_sha256=p.IMAGE,trial='S-052',authorizes_execution=False,publication='local-bound-no-commit',bindings={'source':p.sha(root/'source')})
            target=root/'out/preparation.json';target.write_text(json.dumps(data))
            p.require_local_preparation(target,{'image_sha256':p.IMAGE},root)
            (root/'source').write_text('after')
            with self.assertRaises(ValueError): p.require_local_preparation(target,{'image_sha256':p.IMAGE},root)

    def test_attributed_policy_rejects_old_budget_or_wrong_scope(self):
        root=Path(__file__).resolve().parents[1]
        b=json.loads((root/'out/inherited-gop/qualified-dxe-log-8s-8680ea7/firmware-build.json').read_text())
        b['firmware_configuration']['defines']['ENUMA_BOOT_LOG_REPLAY']='3'
        b['firmware_configuration']['defines']['ENUMA_PROBE_JOURNAL_REPLAY']='1'
        b.update(diagnostic_pixel_log=True,hardware_review_required='R-024',attributed_pixel_scope=dict(origin_x=64,origin_y=96,width=320,height=160,hold_us=8000000,barriers_max=3))
        b['inherited_video_compiled_contract'].update(maximum_framebuffer_reads=153600,framebuffer_writes=102400)
        omitted_oem_modules(b,b['fd_sha256'])
        for key,value in [('hardware_review_required','R-022'),('diagnostic_pixel_log',False),('attributed_pixel_scope',{})]:
            bad=copy.deepcopy(b);bad[key]=value
            with self.assertRaises(ValueError): omitted_oem_modules(bad,bad['fd_sha256'])
        for key,value in [('maximum_framebuffer_reads',73728),('framebuffer_writes',49152)]:
            bad=copy.deepcopy(b);bad['inherited_video_compiled_contract'][key]=value
            with self.assertRaises(ValueError): omitted_oem_modules(bad,bad['fd_sha256'])


if __name__=='__main__': unittest.main()
