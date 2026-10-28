import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from oem_exit_clock import SCOPES,logic,make_plan,require_plan,decode
class ClockTests(unittest.TestCase):
 def setUp(self):
  self.q=dict(scope=SCOPES[0],image_sha256='c'*64,run_config=dict(trial_id='target'),source_bindings={'source':'hash'})
  def report(scope,image,trial,delay):
   return dict(automatic_android_return=True,independent_recovery_passed=True,clock_observation=dict(scope=scope,image_sha256=image*64,trial_id=trial,logic_sha256=logic(self.q),observed_unix=9990,boot_id_changed=True,post_boot_clock=dict(origin_after_issue_lower=40+delay,origin_after_issue_upper=40.1+delay)))
  self.low=report(SCOPES[1],'a','low',2);self.high=report(SCOPES[2],'b','high',22)
  self.plan=make_plan(self.low,self.high,self.q,10000)
 def test_calibration_and_all_codes(self):
  for code in range(1,6):
   o=dict(image_sha256=self.q['image_sha256'],trial_id='target',logic_sha256=logic(self.q),boot_id_changed=True,post_boot_clock=dict(origin_after_issue_lower=42+5*(code-1),origin_after_issue_upper=42.1+5*(code-1)))
   report=dict(automatic_android_return=True,independent_recovery_passed=True,clock_observation=o)
   d=decode(self.q,self.plan,report,10001);self.assertEqual(d['code'],code);self.assertFalse(d['unique_execution_path_proven']);self.assertFalse(d['hardware_success_proven'])
  o['post_boot_clock']=dict(origin_after_issue_lower=70,origin_after_issue_upper=70.1)
  self.assertTrue(decode(self.q,self.plan,report,10001)['stop_additional_trials'])
  report['automatic_android_return']=False
  self.assertRaises(ValueError,decode,self.q,self.plan,report,10001)
 def test_calibration_rejects_bad_provenance(self):
  for key,value in [('automatic_android_return',False),('independent_recovery_passed',False)]:
   low=copy.deepcopy(self.low);low[key]=value;self.assertRaises(ValueError,make_plan,low,self.high,self.q,10000)
  for key,value in [('scope',SCOPES[0]),('logic_sha256','wrong'),('observed_unix',0),('boot_id_changed',False)]:
   low=copy.deepcopy(self.low);low['clock_observation'][key]=value;self.assertRaises(ValueError,make_plan,low,self.high,self.q,10000)
 def test_drift_and_changed_windows(self):
  high=copy.deepcopy(self.high);high['clock_observation']['post_boot_clock']=dict(origin_after_issue_lower=65,origin_after_issue_upper=65.1)
  self.assertRaises(ValueError,make_plan,self.low,high,self.q,10000)
  plan=copy.deepcopy(self.plan);plan['code_windows_after_issue'][0][0]-=1
  self.assertRaises(ValueError,require_plan,self.q,plan,10001)
 def test_target_and_expiration(self):
  q=copy.deepcopy(self.q);q['image_sha256']='d'*64
  self.assertRaises(ValueError,require_plan,q,self.plan,10001)
  self.assertRaises(ValueError,require_plan,self.q,self.plan,14000)
 def test_bad_interval(self):
  for lo,hi in [(float('nan'),50),(49,48),(49,50)]:
   low=copy.deepcopy(self.low);low['clock_observation']['post_boot_clock']=dict(origin_after_issue_lower=lo,origin_after_issue_upper=hi)
   self.assertRaises(ValueError,make_plan,low,self.high,self.q,10000)
 def test_gop_family_six_codes_and_no_old_controls(self):
  q=copy.deepcopy(self.q);q['scope']=SCOPES[3]
  low=copy.deepcopy(self.low);high=copy.deepcopy(self.high)
  low['clock_observation']['scope']=SCOPES[4];high['clock_observation']['scope']=SCOPES[5]
  high['clock_observation']['post_boot_clock']=dict(origin_after_issue_lower=67,origin_after_issue_upper=67.1)
  p=make_plan(low,high,q,10000);self.assertEqual(len(p['code_windows_after_issue']),6)
  self.assertRaises(ValueError,make_plan,self.low,self.high,q,10000)
  self.assertRaises(ValueError,require_plan,q,self.plan,10001)
  for code in range(1,7):
   o=dict(image_sha256=q['image_sha256'],trial_id='target',logic_sha256=logic(q),boot_id_changed=True,post_boot_clock=dict(origin_after_issue_lower=42+5*(code-1),origin_after_issue_upper=42.1+5*(code-1)))
   report=dict(automatic_android_return=True,independent_recovery_passed=True,clock_observation=o)
   d=decode(q,p,report,10001);self.assertEqual(d['code'],code);self.assertFalse(d['hardware_success_proven'])
   if code==6:self.assertIn('native-gop-mode',d['category'])
   if code==5:self.assertIn('without-validated',d['category'])
 def test_plan_cannot_extend_observation_freshness(self):
  low=copy.deepcopy(self.low);high=copy.deepcopy(self.high)
  low['clock_observation']['observed_unix']=6401
  p=make_plan(low,high,self.q,10000)
  self.assertEqual(p['expires_unix'],10001)
  self.assertRaises(ValueError,require_plan,self.q,p,10002)
  p['expires_unix']=13600
  self.assertRaises(ValueError,require_plan,self.q,p,10000)
if __name__=='__main__':unittest.main()
