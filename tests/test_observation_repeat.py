"""No ADB/fastboot: exact one-shot exception and original evidence preservation."""
import copy,json,sys,tempfile,unittest,uuid
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import observation_repeat as repeat
from native_pixel_scope import LOG_SCOPE
import run_system_transport_trial as runner
import run_enuma_entry_probe as entry_probe

class ObservationRepeatTests(unittest.TestCase):
 def setUp(self):
  out=ROOT/'out/observation-repeat-tests';out.mkdir(exist_ok=True)
  self.temp=tempfile.TemporaryDirectory(dir=out);self.root=Path(self.temp.name).resolve();assert self.root.is_relative_to(out.resolve())
  for n in ('config','reports','out/device-tests'):(self.root/n).mkdir(parents=True)
  self.marker=self.root/'out/device-tests'/('consumed-'+repeat.IMAGE+'.local.json');self.marker.write_text('original S048 marker\n')
  self.result=self.root/'reports/enuma-native-route-S-048-result.json'
  self.prior=dict(trial='S-048',image_sha256=repeat.IMAGE,automatic_android_return=True,observation_valid=True,pixel_transaction_completion_supported=True,restoration_supported=True,device_recovery_failed=False,boot_clock_failed=False,result={'warning_code':5},exact_status_legibility=False)
  self.result.write_text(json.dumps(self.prior))
  (self.root/'config/uefi-source.lock.json').write_text(json.dumps(dict(commit=repeat.FIRMWARE)))
  self.meta=dict(hardware_review='R-020',image_sha256=repeat.IMAGE,pixel_scope=copy.deepcopy(LOG_SCOPE))
  self.authorization=dict(status='approved',mode='explicit-observation-repeat',base_review='R-020',base_trial='S-048',trial='S-049',allow_consumed_image=True,user_authorization=repeat.USER_WORDS,image_sha256=[repeat.IMAGE],firmware_commit=repeat.FIRMWARE,pixel_scope=copy.deepcopy(LOG_SCOPE),human_capture_required=True,base_consumed_marker_sha256=repeat.digest(self.marker),base_result_sha256=repeat.digest(self.result))
  self.approvals={'R-020':dict(status='consumed',image_sha256=[repeat.IMAGE],pixel_scope=copy.deepcopy(LOG_SCOPE)),'R-021':self.authorization}
 def tearDown(self):
  assert self.root.is_relative_to((ROOT/'out').resolve());self.temp.cleanup()
 def test_exact_authorization_and_one_claim_preserve_old_marker(self):
  old=self.marker.read_bytes();repeat.validate(self.meta,self.approvals,'R-021',self.root)
  identity=str(uuid.uuid4());repeat.claim(self.meta,self.approvals,'R-021',self.root,identity)
  self.assertEqual(self.marker.read_bytes(),old)
  with self.assertRaises(ValueError):repeat.claim(self.meta,self.approvals,'R-021',self.root,str(uuid.uuid4()))
  repeat.finish(self.root,'R-021',identity,{'phase':'recovered-android-boot-complete'},'out/observation')
  self.assertEqual(self.marker.read_bytes(),old)
 def test_default_still_rejects_consumed_image(self):
  with self.assertRaisesRegex(ValueError,'not approved'):entry_probe.require_hardware_review(self.meta,self.approvals)
 def test_wrong_or_missing_authority_and_scope(self):
  for key,value in [('status','consumed'),('mode','generic'),('base_trial','S-017'),('allow_consumed_image',False),('allow_consumed_image',1),('user_authorization','重跑enuma'),('image_sha256',['a'*64]),('human_capture_required',False),('pixel_scope',{})]:
   candidate=copy.deepcopy(self.approvals);candidate['R-021'][key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):repeat.validate(self.meta,candidate,'R-021',self.root)
  with self.assertRaises(ValueError):repeat.validate(self.meta,self.approvals,'R-022',self.root)
  for key,value in [('image_sha256','b'*64),('hardware_review','R-019'),('pixel_scope',{})]:
   with self.subTest(key=key),self.assertRaises(ValueError):repeat.validate({**self.meta,key:value},self.approvals,'R-021',self.root)
 def test_original_evidence_and_consumed_state_cannot_be_erased(self):
  self.marker.write_text('changed')
  with self.assertRaises(ValueError):repeat.validate(self.meta,self.approvals,'R-021',self.root)
 def test_runtime_failures_cannot_borrow_observation_exception(self):
  for key,value in [('automatic_android_return',False),('observation_valid',False),('restoration_supported',False),('device_recovery_failed',True),('boot_clock_failed',True),('result',{'warning_code':4}),('exact_status_legibility',True)]:
   self.result.write_text(json.dumps({**self.prior,key:value}));self.authorization['base_result_sha256']=repeat.digest(self.result)
   with self.subTest(key=key),self.assertRaises(ValueError):repeat.validate(self.meta,self.approvals,'R-021',self.root)
 def test_new_attempt_not_confused_with_old_S048_same_image(self):
  current=dict(candidate_sha256=repeat.IMAGE,issued_at='now',observation_repeat='R-021',execution_id='new')
  self.assertTrue(repeat.issued_for_attempt(current,repeat.IMAGE,'R-021','new'))
  self.assertFalse(repeat.issued_for_attempt(current,repeat.IMAGE,'R-021','old'))
  self.assertFalse(repeat.issued_for_attempt(dict(candidate_sha256=repeat.IMAGE,issued_at='old'),repeat.IMAGE,'R-021','new'))
 def test_execution_before_human_ready_is_rejected_without_device(self):
  with patch.object(sys,'argv',['runner','--execute','--observation-repeat','R-021']),patch.object(runner.subprocess,'Popen') as popen,self.assertRaises(SystemExit):runner.main()
  popen.assert_not_called()
 def test_human_only_mode_does_not_become_generic_camera_bypass(self):
  for args in [['--execute','--human-camera-only'],['--execute','--human-camera-only','--observation-repeat','R-021']]:
   with patch.object(sys,'argv',['runner',*args]),patch.object(runner.subprocess,'run') as run,self.assertRaises(SystemExit):runner.main()
   run.assert_not_called()
  with patch.object(runner.subprocess,'run') as run,self.assertRaises(ValueError):
   runner.run_with_human_capture({'trial_kind':'native-video-route'},Path('unused'),'R-021','id',False)
  run.assert_not_called()
 def test_human_primary_success_preserves_original_and_waits_for_media(self):
  from types import SimpleNamespace
  self.authorization['capture_mode']='human-primary-only'
  (self.root/'config/hardware-review-approvals.json').write_text(json.dumps(self.approvals))
  image=self.root/'out/original.img';image.with_suffix('.json').write_text(json.dumps(self.meta))
  identity=str(uuid.uuid4());old=self.marker.read_bytes()
  q=dict(boot_log_replay=True,trial_kind='native-video-route',hardware_review='R-020',image_sha256=repeat.IMAGE)
  def fake_run(*args,**kwargs):
   repeat.claim(self.meta,self.approvals,'R-021',self.root,identity)
   state=dict(candidate_sha256=repeat.IMAGE,issued_at='now',observation_repeat='R-021',execution_id=identity,phase='recovered-android-boot-complete')
   (self.root/'out/device-tests/current.local.json').write_text(json.dumps(state))
   return SimpleNamespace(returncode=0)
  with patch.object(runner,'ROOT',self.root),patch.object(entry_probe,'ROOT',self.root),patch.object(runner.subprocess,'run',side_effect=fake_run):runner.run_with_human_capture(q,image,'R-021',identity,True)
  report=json.loads((self.root/'reports/enuma-system-trial-observation.json').read_text())
  self.assertTrue(report['boot_issued']);self.assertTrue(report['human_media_pending']);self.assertFalse(report['human_media_received']);self.assertFalse(report['host_camera_used'])
  self.assertEqual(self.marker.read_bytes(),old)
 def test_human_primary_preissue_failure_does_not_claim_old_boot(self):
  from types import SimpleNamespace
  self.authorization['capture_mode']='human-primary-only'
  (self.root/'config/hardware-review-approvals.json').write_text(json.dumps(self.approvals))
  image=self.root/'out/original.img';image.with_suffix('.json').write_text(json.dumps(self.meta))
  old=dict(candidate_sha256=repeat.IMAGE,issued_at='S048',phase='recovered-android-boot-complete')
  (self.root/'out/device-tests/current.local.json').write_text(json.dumps(old))
  q=dict(boot_log_replay=True,trial_kind='native-video-route',hardware_review='R-020',image_sha256=repeat.IMAGE)
  with patch.object(runner,'ROOT',self.root),patch.object(entry_probe,'ROOT',self.root),patch.object(runner.subprocess,'run',return_value=SimpleNamespace(returncode=1)),self.assertRaises(RuntimeError):runner.run_with_human_capture(q,image,'R-021',str(uuid.uuid4()),True)
  report=json.loads((self.root/'reports/enuma-system-trial-observation.json').read_text());self.assertFalse(report['boot_issued']);self.assertFalse(repeat.used_path(self.root,'R-021').exists())
 def test_new_eight_second_candidate_does_not_reuse_repeat_claim(self):
  from types import SimpleNamespace
  from native_pixel_scope import LONG_LOG_SCOPE
  newhash='b'*64;meta=dict(hardware_review='R-022',image_sha256=newhash,pixel_scope=LONG_LOG_SCOPE)
  self.approvals['R-022']=dict(status='approved',image_sha256=[newhash],pixel_scope=LONG_LOG_SCOPE,capture_mode='human-primary-only')
  (self.root/'config/hardware-review-approvals.json').write_text(json.dumps(self.approvals))
  image=self.root/'out/new-eight.img';image.with_suffix('.json').write_text(json.dumps(meta))
  q=dict(boot_log_replay=True,boot_log_hold_seconds=8,trial_kind='native-video-route',hardware_review='R-022',image_sha256=newhash)
  def fake_run(*args,**kwargs):
   command=args[0];self.assertIn('--human-camera-ready',command)
   execution_id=command[command.index('--execution-id')+1]
   (self.root/'out/device-tests/current.local.json').write_text(json.dumps(dict(candidate_sha256=newhash,issued_at='now',phase='recovered-android-boot-complete',execution_id=execution_id,hardware_review='R-022')))
   return SimpleNamespace(returncode=0)
  old=self.marker.read_bytes()
  with patch.object(runner,'ROOT',self.root),patch.object(entry_probe,'ROOT',self.root),patch.object(runner.subprocess,'run',side_effect=fake_run):runner.run_with_human_capture(q,image,None,str(uuid.uuid4()),True)
  self.assertTrue((self.root/'out/device-tests'/('consumed-'+newhash+'.local.json')).exists())
  self.assertFalse(repeat.used_path(self.root,'R-021').exists());self.assertEqual(self.marker.read_bytes(),old)

 def test_claim_invalid_execution_identity_does_not_consume(self):
  with self.assertRaises(ValueError):repeat.claim(self.meta,self.approvals,'R-021',self.root,'invalid')
  self.assertFalse(repeat.used_path(self.root,'R-021').exists())
if __name__=='__main__':unittest.main()
