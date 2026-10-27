"""Offline, exact-image admission and irreversible local single-attempt claim."""
import hashlib
import json
from pathlib import Path
from uuid import UUID

SCOPE = 'oem-first-call-preforward-v1'
LIMITS = dict(max_boots=1, selected_call=0, hold_us=8000000,
              roi=[64,96,320,160], observation_seconds=75,
              partition_writes=False, needs_current_camera_and_manual_recovery=True)
PROGRESS_SCOPE='oem-progress-v2'
EARLY_SCOPE='oem-early-v3'
POST_SCOPE='oem-post-kernel-v4'
REG_SCOPE='oem-registration-v5'
MAIN_SCOPE='oem-main-entry-v6'
FAR_SCOPE='oem-far-chain-v7'
def limits_for(scope):
    if scope==FAR_SCOPE:return dict(LIMITS,selected_call=0,max_windows=1,max_total_hold_us=8000000,call_selection='ram-only-until-dxe-complete')
    if scope==MAIN_SCOPE:return dict(LIMITS,selected_call=6,max_windows=3,max_total_hold_us=24000000,call_selection='minimum6-and-exact-rva3608')
    if scope==REG_SCOPE:return dict(LIMITS,selected_call=5,max_windows=5,max_total_hold_us=40000000)
    if scope==SCOPE:return dict(LIMITS)
    if scope==POST_SCOPE:return dict(LIMITS,selected_call=4,max_windows=5,max_total_hold_us=40000000)
    if scope==EARLY_SCOPE:return dict(LIMITS,selected_call=1,max_windows=5,max_total_hold_us=40000000)
    if scope==PROGRESS_SCOPE:return dict(LIMITS,max_windows=5,max_total_hold_us=40000000)
    raise ValueError('unknown OEM experiment')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(root, directory):
    root=root.resolve(); directory=directory.resolve()
    directory.relative_to(root/'out')
    q=json.loads((directory/'qualification.json').read_text())
    if q.get('passed') is not True or q.get('software_ready') is not True or q.get('scope') not in (SCOPE,PROGRESS_SCOPE,EARLY_SCOPE,POST_SCOPE,REG_SCOPE,MAIN_SCOPE,FAR_SCOPE):
        raise ValueError('not an admitted OEM runtime candidate')
    c=q['run_config']
    if (set(c)!=set(('trial_id','session','selected_call','profile','experiment')) or
        str(UUID(c['trial_id']))!=c['trial_id'] or type(c['session']) is not int or
        not 0<c['session']<2**64 or type(c['selected_call']) is not int or
        c['selected_call']!=(6 if q['scope']==MAIN_SCOPE else 5 if q['scope']==REG_SCOPE else 4 if q['scope']==POST_SCOPE else 1 if q['scope']==EARLY_SCOPE else 0) or c['profile']!='oem-control' or c['experiment']!=q['scope']):
        raise ValueError('runtime configuration differs')
    if q['runtime_limits']!=limits_for(q['scope']) or q['identity'].get('runtime')!=c:
        raise ValueError('runtime identity or limits differ')
    image=directory/'image.img'
    if sha(image)!=q['image_sha256'] or image.stat().st_size!=q['image_bytes']:
        raise ValueError('candidate image changed')
    bindings=q['source_bindings']
    for required in ('scripts/run_oem_runtime_trial.py','scripts/oem_runtime_candidate.py',
                     'scripts/qualify_oem_runtime.py','scripts/audit_oem_development_fd.py'):
        if required not in bindings: raise ValueError('incomplete source binding')
    if not any(n.startswith('firmware/') for n in bindings):raise ValueError('firmware unbound')
    for name,digest in bindings.items():
        path=(root/name).resolve();path.relative_to(root)
        if sha(path)!=digest:raise ValueError('bound source changed: '+name)
    return q,image

def claim(root,directory,human_ready):
    if not human_ready:raise ValueError('current camera and manual recovery readiness required')
    q,image=validate(root,directory)
    ledger=root/'out/oem-runtime-attempts';ledger.mkdir(parents=True,exist_ok=True)
    entry=dict(trial_id=q['run_config']['trial_id'],image_sha256=q['image_sha256'],
               qualification_sha256=sha(directory/'qualification.json'),human_ready=True)
    # Exclusive creation consumes this trial even if a subsequent transport fails.
    with (ledger/(entry['trial_id']+'.json')).open('x') as f:
        json.dump(entry,f,indent=2);f.flush()
    return q,image
