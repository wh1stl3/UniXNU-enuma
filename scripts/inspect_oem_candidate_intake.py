"""Read-only OEM candidate intake. No imports from producer, claims or device calls.
This report is not execution authorization or a replacement for the guarded runner.
"""
import argparse, hashlib, json
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def inside(root,name):
 p=(root/name).resolve();p.relative_to(root.resolve());return p

def inspect(root,directory):
 root=root.resolve();directory=directory.resolve();directory.relative_to(root/'out')
 qp=directory/'qualification.json'
 try:
  qbytes=qp.read_bytes();q=json.loads(qbytes)
  if not isinstance(q,dict): raise ValueError('qualification must be an object')
 except (OSError,ValueError):
  return dict(scope='read-only transport intake, not firmware or execution qualification',software_intake_consistent=False,execution_ready=False,hardware_executed=False,blockers=['qualification absent, unreadable or incomplete; producer may still be writing'],changed_bindings=[],matched_attempts=[],remaining=['wait for producer final qualification; never infer readiness from a directory or image alone'])
 reasons=[];observed={};changed=[]
 if q.get('passed') is not True or q.get('software_ready') is not True: reasons.append('software qualification not passed')
 cfg=q.get('run_config',{});trial=cfg.get('trial_id');image=q.get('image_sha256')
 if not isinstance(trial,str) or not trial or cfg.get('experiment')!=q.get('scope'): reasons.append('invalid experiment identity')
 ip=directory/'image.img'
 if not ip.is_file() or sha(ip)!=image or ip.stat().st_size!=q.get('image_bytes'): reasons.append('image identity mismatch')
 bindings=q.get('source_bindings',{})
 if not isinstance(bindings,dict): bindings={};reasons.append('invalid bindings')
 required={'scripts/run_oem_runtime_trial.py','scripts/oem_runtime_candidate.py','scripts/qualify_oem_runtime.py','scripts/audit_oem_development_fd.py'}
 if not required.issubset(bindings) or not any(n.startswith('firmware/') for n in bindings): reasons.append('incomplete source binding')
 for name,wanted in bindings.items():
  try:
   p=inside(root,name);actual=sha(p);observed[name]=actual
   if actual!=wanted: changed.append(name)
  except (ValueError,OSError): changed.append(name)
 if changed: reasons.append('bound source mismatch')
 ledger=root/'out/oem-runtime-attempts';attempts=[]
 for p in sorted(ledger.glob('*.json')):
  try:
   e=json.loads(p.read_text());assert isinstance(e,dict) and e.get('trial_id') and e.get('image_sha256')
  except (ValueError,OSError,AssertionError): reasons.append('unreadable or malformed attempt ledger');continue
  if e.get('trial_id')==trial or e.get('image_sha256')==image:
   attempts.append({'path':str(p.relative_to(root)),'sha256':sha(p)})
 if attempts: reasons.append('trial or exact image already claimed; no replay')
 limits=q.get('runtime_limits',{})
 if limits.get('max_boots')!=1 or limits.get('partition_writes') is not False or limits.get('needs_current_camera_and_manual_recovery') is not True: reasons.append('single-attempt recovery contract absent')
 # Detect changes during intake; the producer may be working in another tree.
 for name,digest in observed.items():
  try: stable=sha(inside(root,name))==digest
  except (ValueError,OSError): stable=False
  if not stable: reasons.append('source changed during intake');break
 if qp.read_bytes()!=qbytes: reasons.append('qualification changed during intake')
 return dict(scope='read-only transport intake, not firmware or execution qualification',qualification_sha256=hashlib.sha256(qbytes).hexdigest(),trial_id=trial,image_sha256=image,software_intake_consistent=not reasons,execution_ready=False,hardware_executed=False,blockers=list(dict.fromkeys(reasons)),changed_bindings=changed,matched_attempts=attempts,remaining=['scope-specific qualifier and machine code review','latest code hypothesis and discriminating observation plan','current single authorization, filming, identity, backup and recovery gates'])

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--producer-root',type=Path,required=True);ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 output=a.output.resolve();output.relative_to(Path(__file__).resolve().parents[1]/'out');output.mkdir(parents=True,exist_ok=False)
 result=inspect(a.producer_root,a.candidate);(output/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
