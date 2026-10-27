"""Exact R-023 local preparation and atomic one-shot guard. No device operations."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
from uuid import UUID
from enuma_paths import evidence_path
from native_pixel_scope import ATTRIBUTED_LOG_SCOPE

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE='out/attributed-log-20261026/qualification3'
IMAGE='360b5ec7eeb26f76858069fba78d3f69bbe90d40f125730dfcd324dbe69fbd8a'
QUALIFICATION='56e41c6cf2abd4c46890ae6d01c9440b437d32328666c67016f8ab486084ed50'
BINDINGS=tuple('scripts/'+n for n in ('r023_preparation.py','run_system_transport_trial.py','run_enuma_entry_probe.py',
    'native_pixel_scope.py','native_mask_decode.py','native_route_decode.py','boot_origin.py','enuma_paths.py',
    'reconcile_enuma_recovery.py','observation_repeat.py','firmware_audit_policy.py','decode_attributed_pixel_log.py'))+(
    'AGENTS.md','README.md','docs/STATUS.md','docs/HANDOFF.md','docs/WORKLOG.md','docs/DECISIONS.md',
    'docs/NEED-REVIEW.md','docs/NEED-HUMAN.md','docs/PENDING-HUMAN.md',
    'docs/operations/2026-10-26-r023-attributed-inset-log.md',ARCHIVE+'/qualification.json',
    'out/attributed-log-20261026/code-review.json','reports/enuma-boot-clock-calibration.json')

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def unused(root):
    out=Path(root)/'out/device-tests';marker=out/'claimed-R-023.local.json'
    if marker.exists() or (out/('consumed-'+IMAGE+'.local.json')).exists(): raise ValueError('R-023 claimed/consumed')
    for p in [out/'current.local.json',*out.glob('*/result.json')]:
        if p.exists():
            d=json.loads(p.read_text())
            if d.get('candidate_sha256')==IMAGE and d.get('issued_at'): raise ValueError('R-023 already issued')
    return marker


def require_attempt(root,meta,execution_id,human_ready,claim=False):
    if (len(IMAGE)!=64 or meta.get('hardware_review')!='R-023' or meta.get('image_sha256')!=IMAGE or
        meta.get('pixel_scope')!=ATTRIBUTED_LOG_SCOPE or human_ready is not True):
        raise ValueError('R-023 exact qualified image/scope and current capture required')
    if not execution_id or str(UUID(execution_id))!=execution_id: raise ValueError('unique execution UUID required')
    marker=unused(root)
    if claim:
        with marker.open('x',encoding='utf-8') as f:
            json.dump(dict(review='R-023',trial='S-051',image_sha256=IMAGE,execution_id=execution_id,
                           phase='claimed-before-boot',time_utc=datetime.now(timezone.utc).isoformat()),f,indent=2)
            f.flush();os.fsync(f.fileno())


def require_local_preparation(path,q,root=ROOT):
    root=Path(root).resolve();path=Path(path).resolve();path.relative_to(root/'out')
    data=json.loads(path.read_text())
    if (q.get('image_sha256')!=IMAGE or data.get('image_sha256')!=IMAGE or data.get('trial')!='S-051' or
        data.get('authorizes_execution') is not False or data.get('publication')!='local-bound-no-commit' or
        set(data.get('bindings',{}))!=set(BINDINGS)): raise ValueError('invalid R-023 local preparation')
    for n,h in data['bindings'].items():
        if sha(root/n)!=h: raise ValueError('stale preparation: '+n)
    return data


def qualification(path,published=False,preparation=None,root=ROOT):
    root=Path(root).resolve();path=Path(path).resolve()
    if path!=(root/ARCHIVE/'qualification.json').resolve() or sha(path)!=QUALIFICATION:
        raise ValueError('R-023 exact frozen qualification required')
    q=json.loads(path.read_text());archive=path.parent
    if not q.get('passed') or q.get('image_sha256')!=IMAGE or q.get('hardware_execution') is not False:
        raise ValueError('invalid offline qualification')
    for n,h in q['files'].items():
        p=(archive/n).resolve();p.relative_to(archive)
        if sha(p)!=h: raise ValueError('candidate file changed: '+n)
    image=archive/'image.img';meta=json.loads(image.with_suffix('.json').read_text())
    if sha(image)!=IMAGE or meta.get('pixel_scope')!=ATTRIBUTED_LOG_SCOPE: raise ValueError('image/scope mismatch')
    review=json.loads((root/'out/attributed-log-20261026/code-review.json').read_text())
    if (review.get('passed') is not True or review.get('image_sha256')!=IMAGE or
        review.get('qualification_sha256')!=QUALIFICATION): raise ValueError('actual PE review missing')
    for n,h in review['bindings'].items():
        if sha(root/n)!=h: raise ValueError('code review binding changed: '+n)
    from native_mask_decode import make_pixel_plan
    from firmware_audit_policy import omitted_oem_modules
    if (json.loads((root/'reports/enuma-boot-clock-calibration.json').read_text()).get('calibration_passed') is not True or
        review.get('decode_plan')!=make_pixel_plan(root,'R-023')): raise ValueError('fixed preissue timing plan changed')
    audit=json.loads((archive/'actual-profile-build.json').read_text())
    omitted_oem_modules(audit,q['fd_sha256'])
    runtime=dict(q,trial_kind='native-video-route',boot_log_replay=True,boot_log_hold_seconds=8,
                 native_route_cpu_pattern=True,boot_clock_capture=True,pixel_access=True,gop_published=False,
                 pixel_scope=ATTRIBUTED_LOG_SCOPE,decode_plan=make_pixel_plan(root,'R-023'))
    if preparation is not None: require_local_preparation(preparation,runtime,root)
    if published:
        if preparation is None: raise ValueError('R-023 local source/document binding required')
        from run_enuma_entry_probe import require_hardware_review
        require_hardware_review(meta,json.loads((root/'config/hardware-review-approvals.json').read_text()))
        unused(root)
    return runtime,image


def prepare(output,root=ROOT):
    root=Path(root).resolve();out=Path(output).resolve();out.relative_to(root/'out');out.mkdir(parents=True,exist_ok=False)
    q,image=qualification(root/ARCHIVE/'qualification.json',root=root);unused(root)
    p=root/'out/device-tests/current.local.json';before=p.read_bytes();state=json.loads(before)
    if state.get('phase')!='recovered-android-boot-complete' or state.get('slot')!='_a': raise ValueError('unreconciled prior recovery')
    backup=evidence_path(state.get('recovery_backup_directory',state['directory']),root)
    if {b['partition'] for b in state['backups']}!={'boot_a','vendor_boot_a'}: raise ValueError('backup contract changed')
    for b in state['backups']:
        if sha(backup/(b['partition']+'.bin'))!=b['sha256']: raise ValueError('local backup mismatch')
    from run_enuma_entry_probe import require_hardware_review
    approved=False
    try: require_hardware_review(json.loads(image.with_suffix('.json').read_text()),json.loads((root/'config/hardware-review-approvals.json').read_text()));approved=True
    except ValueError: pass
    data=dict(trial='S-051',image_sha256=IMAGE,authorizes_execution=False,publication='local-bound-no-commit',
              hardware_review_approved=approved,capture_ready=False,fresh_device_preflight=False,
              local_backup_hashes_match=True,bindings={n:sha(root/n) for n in BINDINGS},
              pending=([] if approved else ['explicit R-023 single-shot approval'])+['current capture ready','fresh identity/backups/recovery/clock gates'])
    target=out/'preparation.json';target.write_text(json.dumps(data,indent=2)+'\n');require_local_preparation(target,q,root)
    if p.read_bytes()!=before: raise ValueError('device state changed during offline preparation')
    return target


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    print(prepare(p.parse_args().output))
