"""One explicit human-authorized observation repeat; preserve original consumption.

No device tools. Default execution remains forbidden for consumed images.
Only R-021/S-049 can repeat the recovered R-020/S-048 exact bytes/scope.
"""
import hashlib,json,uuid
from datetime import datetime,timezone
from pathlib import Path
from native_pixel_scope import LOG_SCOPE

IMAGE='c75b6c863d294d7b3e2772ddb7f46a239c7915685b9c7309f11310049945d8bf'
FIRMWARE='962f8208a9d2eca3bc626db67090e28519e088e6'
USER_WORDS='明确授权原镜像仅补拍一次'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def used_path(root,token):
    if token!='R-021':raise ValueError('unknown observation repeat authorization')
    return root/'out/device-tests/consumed-observation-repeat-R-021.local.json'

def validate(meta,approvals,token,root):
    root=Path(root);used=used_path(root,token);entry=approvals.get(token,{})
    old=approvals.get('R-020',{})
    required=dict(status='approved',mode='explicit-observation-repeat',base_review='R-020',base_trial='S-048',
                  trial='S-049',allow_consumed_image=True,user_authorization=USER_WORDS,
                  image_sha256=[IMAGE],firmware_commit=FIRMWARE,pixel_scope=LOG_SCOPE,
                  human_capture_required=True)
    if any(type(entry.get(k)) is not type(v) or entry.get(k)!=v for k,v in required.items()):
        raise ValueError('explicit exact-image observation repeat authorization missing/mismatched')
    if meta.get('hardware_review')!='R-020' or meta.get('image_sha256')!=IMAGE or meta.get('pixel_scope')!=LOG_SCOPE:
        raise ValueError('repeat must preserve original R-020 bytes and exact scope')
    if old.get('status')!='consumed' or old.get('image_sha256')!=[IMAGE] or old.get('pixel_scope')!=LOG_SCOPE:
        raise ValueError('original consumption must remain intact')
    if json.loads((root/'config/uefi-source.lock.json').read_text())['commit']!=FIRMWARE:
        raise ValueError('repeat source pin changed')
    marker=root/'out/device-tests'/('consumed-'+IMAGE+'.local.json')
    result=root/'reports/enuma-native-route-S-048-result.json'
    if not marker.is_file() or digest(marker)!=entry.get('base_consumed_marker_sha256') or digest(result)!=entry.get('base_result_sha256'):
        raise ValueError('original consumption/result evidence changed')
    prior=json.loads(result.read_text())
    if (prior.get('trial')!='S-048' or prior.get('image_sha256')!=IMAGE or
        prior.get('automatic_android_return') is not True or prior.get('observation_valid') is not True or
        prior.get('pixel_transaction_completion_supported') is not True or prior.get('restoration_supported') is not True or
        prior.get('device_recovery_failed') is not False or prior.get('boot_clock_failed') is not False or
        prior.get('result',{}).get('warning_code')!=5 or prior.get('exact_status_legibility') is not False):
        raise ValueError('repeat is limited to recovered content-legibility failure, not a runtime failure')
    if used.exists():raise ValueError('observation repeat already claimed/issued; no further use')
    return entry

def claim(meta,approvals,token,root,execution_id):
    entry=validate(meta,approvals,token,root)
    if str(uuid.UUID(execution_id))!=execution_id:raise ValueError('invalid repeat execution identity')
    value=dict(authorization=token,trial=entry['trial'],base_trial=entry['base_trial'],image_sha256=IMAGE,
               execution_id=execution_id,phase='issuing',claimed_at_utc=datetime.now(timezone.utc).isoformat(),
               original_consumed_marker_sha256=entry['base_consumed_marker_sha256'])
    # Atomic one-shot claim immediately before issued_at/fastboot boot. Any
    # uncertain outcome stays claimed; never erase it for an automatic retry.
    with used_path(Path(root),token).open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2)

def issued_for_attempt(state,image,token,execution_id):
    return (state.get('candidate_sha256')==image and bool(state.get('issued_at')) and
            state.get('observation_repeat')==token and state.get('execution_id')==execution_id)

def finish(root,token,execution_id,state,evidence):
    path=used_path(Path(root),token);value=json.loads(path.read_text())
    if value['execution_id']!=execution_id:raise ValueError('repeat result belongs to another attempt')
    value.update(phase=state['phase'],evidence=evidence)
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
