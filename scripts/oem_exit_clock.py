"""Fresh paired calibration, bounded Linux boot origins, indirect exit inference."""
import argparse,hashlib,json,math,time
from pathlib import Path
SCOPES=('oem-far-clock-v9','oem-far-clock-low-v9','oem-far-clock-high-v9','oem-gop-mode-v10','oem-gop-mode-low-v10','oem-gop-mode-high-v10')
TARGET_SCOPES=(SCOPES[0],SCOPES[3])
NAMES={1:'instrumented-exception',2:'diagnostic-terminal',3:'dispatch-complete-without-matched-core-return',4:'dispatch-complete-core-nonzero-status',5:'dispatch-complete-core-success'}
def family(q):
 if q.get('scope')==SCOPES[0]:return SCOPES[:3],(2,7,12,17,22)
 if q.get('scope')==SCOPES[3]:return SCOPES[3:],(2,7,12,17,22,27)
 raise ValueError('target clock scope required')

def logic(q):return hashlib.sha256(json.dumps(q['source_bindings'],sort_keys=True).encode()).hexdigest()
def interval(c):
 lo=c['origin_after_issue_lower'];hi=c['origin_after_issue_upper']
 if type(lo) not in (int,float) or type(hi) not in (int,float) or not all(math.isfinite(x) for x in (lo,hi)) or not 0<=lo<=hi or hi-lo>.25:raise ValueError('invalid bounded boot origin')
 return lo,hi
def make_plan(low,high,q,now=None):
 now=time.time() if now is None else now
 scopes,delays=family(q)
 bases=[];ids=set();images=set()
 for report,scope,delay in [(low,scopes[1],delays[0]),(high,scopes[2],delays[-1])]:
  if report.get('automatic_android_return') is not True or report.get('independent_recovery_passed') is not True:raise ValueError('confirmed automatic return and independent recovery required')
  o=report['clock_observation']
  if o['scope']!=scope or o['logic_sha256']!=logic(q):raise ValueError('calibration scope/source mismatch')
  if not 0<=now-o['observed_unix']<=3600:raise ValueError('calibration older than one hour')
  if o['boot_id_changed'] is not True:raise ValueError('new Android boot not established')
  ids.add(o['trial_id']);images.add(o['image_sha256']);lo,hi=interval(o['post_boot_clock']);bases.append((lo-delay,hi-delay))
 if len(ids)!=2 or len(images)!=2 or q['run_config']['trial_id'] in ids or q['image_sha256'] in images:raise ValueError('distinct calibration/target trials required')
 base=(min(x[0] for x in bases),max(x[1] for x in bases))
 if base[1]-base[0]>1:raise ValueError('calibration baseline drift exceeds one second')
 return dict(passed=True,target_image_sha256=q['image_sha256'],logic_sha256=logic(q),created_unix=now,source_observed_unix=[x['clock_observation']['observed_unix'] for x in (low,high)],expires_unix=min(now+3600,low['clock_observation']['observed_unix']+3600,high['clock_observation']['observed_unix']+3600),
   source_trial_ids=sorted(ids),source_report_sha256=[hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest() for x in (low,high)],
   baseline_envelope_seconds=base,code_windows_after_issue=[[base[0]+d-1,base[1]+d+1] for d in delays],
   limitation='Indirect timing inference only. Variable pre-exit execution or uninstrumented resets can alias a code; no unique path, persistent log or hardware success proof.')
def require_plan(q,p,now=None):
 now=time.time() if now is None else now
 scopes,delays=family(q)
 if p.get('passed') is not True or p.get('target_image_sha256')!=q['image_sha256'] or p.get('logic_sha256')!=logic(q):raise ValueError('exact current clock calibration required')
 times=p.get('source_observed_unix',[])
 if len(times)!=2 or not all(type(t) in (int,float) and math.isfinite(t) and 0<=p['created_unix']-t<=3600 for t in times):raise ValueError('calibration observation times missing/invalid')
 if p['expires_unix']!=min(p['created_unix']+3600,*(t+3600 for t in times)) or not p['created_unix']<=now<=p['expires_unix']:raise ValueError('calibration expired')
 b=p['baseline_envelope_seconds']
 if len(b)!=2 or not all(math.isfinite(x) for x in b) or not 0<=b[1]-b[0]<=1:raise ValueError('invalid baseline')
 if p['code_windows_after_issue']!=[[b[0]+d-1,b[1]+d+1] for d in delays]:raise ValueError('clock windows changed')
def decode(q,p,report,now=None):
 require_plan(q,p,now)
 if report.get('automatic_android_return') is not True or report.get('independent_recovery_passed') is not True:raise ValueError('confirmed automatic return and independent recovery required')
 o=report['clock_observation']
 if o['image_sha256']!=q['image_sha256'] or o['trial_id']!=q['run_config']['trial_id'] or o['logic_sha256']!=logic(q) or o['boot_id_changed'] is not True:raise ValueError('observation identity differs')
 lo,hi=interval(o['post_boot_clock']);hits=[i+1 for i,(a,b) in enumerate(p['code_windows_after_issue']) if a<=lo<=hi<=b]
 if len(hits)!=1:return dict(conclusion='unknown-or-ambiguous',stop_additional_trials=True)
 return dict(conclusion='indirect-clock-code-inferred',code=hits[0],category=('native-gop-mode-api-and-bounds-validated' if hits[0]==6 else 'core-success-without-validated-native-gop-mode' if q['scope']==SCOPES[3] and hits[0]==5 else NAMES[hits[0]]),direct_log=False,unique_execution_path_proven=False,hardware_success_proven=False,limitation=p['limitation'])
def main():
 p=argparse.ArgumentParser();p.add_argument('--low',type=Path,required=True);p.add_argument('--high',type=Path,required=True);p.add_argument('--qualification',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 a.output.resolve().relative_to(Path(__file__).resolve().parents[1]/'out')
 q=json.loads(a.qualification.read_text());plan=make_plan(json.loads(a.low.read_text()),json.loads(a.high.read_text()),q)
 with a.output.open('x',encoding='utf-8') as f:json.dump(plan,f,indent=2)
 print('PASS: fresh exact-target paired clock windows; inference remains indirect')
if __name__=='__main__':main()
