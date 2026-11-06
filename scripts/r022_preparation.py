"""Offline, locally bound R-022 preparation; never an authorization or launcher.

The user requires preservation of dirty migration/development work and no
automatic publication. This exact frozen-image path binds the local runner and
documents instead. Hardware approval, fresh capture and recovery gates remain.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
from uuid import UUID
from enuma_paths import evidence_path

ROOT=Path(__file__).resolve().parents[1]
IMAGE='f684ef22ea79178953ff8efcc81fb2243f189a096ef276a676c6a27e7b4b6e5b'
FIRMWARE='8680ea79d6fd14d4526d314f430e9812955cb78a'
ARCHIVE='out/inherited-gop/qualified-dxe-log-8s-8680ea7'
QUALIFICATION='1d730f656f05d80b595168736807c1f1afe6fbcab19d5a3041c101a73cf55e9d'
SCRIPTS=('r022_preparation.py','enuma_paths.py','run_system_transport_trial.py',
         'run_enuma_entry_probe.py','reconcile_enuma_recovery.py','native_pixel_scope.py',
         'native_mask_decode.py','native_route_decode.py','boot_origin.py','observation_repeat.py')
DOCUMENTS=('AGENTS.md','firmware/AGENTS.md','README.md','docs/HANDOFF.md','docs/STATUS.md',
           'docs/NEED-REVIEW.md','docs/PENDING-HUMAN.md','docs/NEED-HUMAN.md',
           'docs/WORKLOG.md','docs/DECISIONS.md',
           'docs/operations/2026-10-26-r022-eight-second-log-observation.md')
BINDINGS=tuple('scripts/'+n for n in SCRIPTS)+DOCUMENTS+(
    'config/uefi-source.lock.json','reports/enuma-native-route-code.json',
    'reports/enuma-boot-clock-calibration.json',ARCHIVE+'/qualification.json')


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def exact(q):
    from native_pixel_scope import LONG_LOG_SCOPE
    if (q.get('image_sha256')!=IMAGE or q.get('firmware_commit')!=FIRMWARE or
        q.get('archive')!=ARCHIVE or q.get('hardware_review')!='R-022' or
        q.get('pixel_scope')!=LONG_LOG_SCOPE or q.get('boot_log_hold_seconds')!=8):
        raise ValueError('local preparation is limited to frozen R-022 / S-050')


def require_local_preparation(path,q,root=ROOT):
    root=Path(root).resolve();path=Path(path).resolve();path.relative_to(root/'out')
    exact(q);data=json.loads(path.read_text())
    if (data.get('schema')!=1 or data.get('image_sha256')!=IMAGE or data.get('trial')!='S-050' or
        data.get('authorizes_execution') is not False or data.get('publication')!='local-bound-no-commit'):
        raise ValueError('invalid local R-022 preparation')
    if set(data.get('bindings',{}))!=set(BINDINGS):raise ValueError('local bindings incomplete')
    for name,wanted in data['bindings'].items():
        if sha(root/name)!=wanted:raise ValueError('local preparation stale: '+name)
    if sha(root/ARCHIVE/'qualification.json')!=QUALIFICATION:
        raise ValueError('frozen R-022 qualification changed')
    return data


def require_unused(root):
    root=Path(root);out=root/'out/device-tests'
    marker=out/'claimed-R-022.local.json'
    if marker.exists() or (out/('consumed-'+IMAGE+'.local.json')).exists():
        raise ValueError('R-022 already claimed/consumed; do not repeat')
    paths=[out/'current.local.json',*out.glob('*/result.json')]
    for path in paths:
        if path.exists():
            state=json.loads(path.read_text())
            if state.get('candidate_sha256')==IMAGE and state.get('issued_at'):
                raise ValueError('R-022 was already issued; do not repeat')
    return marker


def require_attempt(root,meta,execution_id,human_ready,claim=False):
    """Fail closed before any device call, then atomically claim before boot.

    A crash after claim never permits an automatic reissue, even if the boot
    command's completion or the ordinary consumed marker was not recorded.
    """
    from native_pixel_scope import LONG_LOG_SCOPE
    if (meta.get('hardware_review')!='R-022' or meta.get('image_sha256')!=IMAGE or
        meta.get('pixel_scope')!=LONG_LOG_SCOPE or human_ready is not True):
        raise ValueError('R-022 exact image/scope and fresh human capture required')
    if not execution_id or str(UUID(execution_id))!=execution_id:raise ValueError('R-022 execution identity required')
    marker=require_unused(root)
    if claim:
        with marker.open('x',encoding='utf-8') as stream:
            json.dump(dict(review='R-022',trial='S-050',image_sha256=IMAGE,execution_id=execution_id,
                           phase='claimed-before-boot',time_utc=datetime.now(timezone.utc).isoformat()),stream,indent=2)
            stream.flush()
            os.fsync(stream.fileno())


def prepare(output,root=ROOT):
    root=Path(root).resolve();output=Path(output).resolve();output.relative_to(root/'out')
    output.mkdir(parents=True,exist_ok=False)
    from run_system_transport_trial import qualification
    qpath=root/ARCHIVE/'qualification.json'
    if sha(qpath)!=QUALIFICATION:raise ValueError('frozen qualification changed')
    q,image=qualification(False,qpath);exact(q)
    require_unused(root)
    state_bytes=(root/'out/device-tests/current.local.json').read_bytes();state=json.loads(state_bytes)
    if state.get('phase')!='recovered-android-boot-complete':raise ValueError('historical recovery is not reconciled')
    backup=evidence_path(state.get('recovery_backup_directory',state['directory']),root)
    if state.get('slot')!='_a' or {b['partition'] for b in state['backups']}!={'boot_a','vendor_boot_a'}:
        raise ValueError('unexpected backup contract')
    for item in state['backups']:
        if sha(backup/(item['partition']+'.bin'))!=item['sha256']:raise ValueError('local backup changed')
    # Record the real separate authorization gate, never grant it by preparing.
    approvals=json.loads((root/'config/hardware-review-approvals.json').read_text(encoding='utf-8'))
    from run_enuma_entry_probe import require_hardware_review
    approved=False
    try:
        require_hardware_review(json.loads(image.with_suffix('.json').read_text()),approvals)
        approved=True
    except ValueError:
        pass
    # No capture-ready or fresh-device bit is inferred from offline preparation.
    result=dict(schema=1,trial='S-050',image_sha256=IMAGE,publication='local-bound-no-commit',
                authorizes_execution=False,hardware_executed=False,capture_ready=False,
                fresh_device_preflight=False,bindings={n:sha(root/n) for n in BINDINGS},
                backup_resolved=str(backup.relative_to(root)),local_backup_hashes_match=True,
                prior_state_sha256=hashlib.sha256(state_bytes).hexdigest(),
                hardware_review_approved=approved,
                pending=([] if approved else ['explicit R-022 single-shot release'])+['current capture-ready confirmation',
                         'fresh enuma identity/slot/root/unlock/device-backup comparison before issue'])
    target=output/'preparation.json';target.write_text(json.dumps(result,indent=2)+'\n')
    require_local_preparation(target,q,root)
    if (root/'out/device-tests/current.local.json').read_bytes()!=state_bytes:raise ValueError('current state changed during preparation')
    return target


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    target=prepare(parser.parse_args().output)
    print('PASS: frozen R-022 archive, local backup and runner/docs bound; no device action or execution approval: '+str(target))
