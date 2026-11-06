"""R026 one-shot bounded menu guard. Offline preparation never authorizes boot."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
from uuid import UUID
from full_menu_scope import SCOPE
from enuma_paths import evidence_path
ROOT=Path(__file__).resolve().parents[1]
ARCHIVE='out/full-menu-20261027/qualification1'
IMAGE='d6d3d61a65d36d0194c5af6656c2e58220c64175548e155d8742f104cadcebce'
QUALIFICATION='10d3564a3cd5d4fce35b7b597098a0de31a546d9186d5cbe74da7d9a60d77221'
BINDINGS=('scripts/r026_preparation.py','scripts/run_full_menu_trial.py','scripts/run_enuma_entry_probe.py',
          'scripts/full_menu_scope.py','scripts/firmware_audit_policy.py','scripts/qualify_full_menu.py',
          'AGENTS.md','docs/STATUS.md','docs/HANDOFF.md','docs/NEED-REVIEW.md','docs/NEED-HUMAN.md',
          'docs/PENDING-HUMAN.md','docs/WORKLOG.md','docs/DECISIONS.md',
          'docs/operations/2026-10-27-full-menu-firmware.md')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def unused(root):
    folder=Path(root)/'out/device-tests';marker=folder/'claimed-R-026.local.json'
    if marker.exists() or (folder/('consumed-'+IMAGE+'.local.json')).exists():raise ValueError('R026 already claimed/consumed')
    for p in [folder/'current.local.json',*folder.glob('*/result.json')]:
        if p.exists():
            data=json.loads(p.read_text())
            if data.get('candidate_sha256')==IMAGE and data.get('issued_at'):raise ValueError('R026 image was already issued')
    return marker
def require_attempt(root,meta,execution_id,human_ready,claim=False):
    if len(IMAGE)!=64 or meta.get('image_sha256')!=IMAGE or meta.get('hardware_review')!='R-026' or meta.get('pixel_scope')!=SCOPE:
        raise ValueError('R026 exact qualified image and scope required')
    if human_ready is not True or not execution_id or str(UUID(execution_id))!=execution_id:raise ValueError('R026 current capture and execution UUID required')
    marker=unused(root)
    if claim:
        with marker.open('x',encoding='utf-8') as f:
            json.dump(dict(review='R-026',trial='S-054',image_sha256=IMAGE,execution_id=execution_id,
                           phase='claimed-before-boot',time_utc=datetime.now(timezone.utc).isoformat()),f,indent=2)
            f.flush();os.fsync(f.fileno())
def qualification(preparation=None,published=False,root=ROOT):
    root=Path(root).resolve();archive=root/ARCHIVE;qpath=archive/'qualification.json'
    if len(IMAGE)!=64 or len(QUALIFICATION)!=64 or sha(qpath)!=QUALIFICATION:raise ValueError('R026 qualification is not frozen')
    q=json.loads(qpath.read_text())
    if not q.get('passed') or q.get('hardware_execution') is not False or q.get('image_sha256')!=IMAGE or q.get('scope')!=SCOPE:raise ValueError('invalid R026 qualification')
    for name,h in q['files'].items():
        p=(archive/name).resolve();p.relative_to(archive)
        if sha(p)!=h:raise ValueError('R026 artifact changed: '+name)
    review_path=root/'out/full-menu-20261027/execution-review.json';review=json.loads(review_path.read_text())
    if review.get('passed') is not True or review.get('image_sha256')!=IMAGE or review.get('qualification_sha256')!=QUALIFICATION:raise ValueError('R026 PE review missing')
    for name,h in review['bindings'].items():
        if sha(root/name)!=h:raise ValueError('R026 execution binding changed: '+name)
    image=archive/'image.img';meta=json.loads(image.with_suffix('.json').read_text())
    if sha(image)!=IMAGE or meta.get('pixel_scope')!=SCOPE:raise ValueError('R026 image/scope changed')
    unused(root)
    if preparation is not None:
        p=Path(preparation).resolve();p.relative_to(root/'out');data=json.loads(p.read_text())
        if data.get('trial')!='S-054' or data.get('image_sha256')!=IMAGE or data.get('authorizes_execution') is not False or set(data.get('bindings',{}))!=set(BINDINGS):raise ValueError('invalid R026 preparation')
        for name,h in data['bindings'].items():
            if sha(root/name)!=h:raise ValueError('stale R026 preparation: '+name)
    if published:
        if preparation is None:raise ValueError('R026 requires current local source/document preparation')
        from run_enuma_entry_probe import require_hardware_review
        require_hardware_review(meta,json.loads((root/'config/hardware-review-approvals.json').read_text()))
    return q,image
def prepare(output,root=ROOT):
    root=Path(root).resolve();out=Path(output).resolve();out.relative_to(root/'out');out.mkdir(parents=True,exist_ok=False)
    q,image=qualification(root=root)
    state_path=root/'out/device-tests/current.local.json';before=state_path.read_bytes();state=json.loads(before)
    if state.get('phase')!='recovered-android-boot-complete' or state.get('slot')!='_a':raise ValueError('prior recovery not reconciled')
    backup=evidence_path(state.get('recovery_backup_directory',state['directory']),root)
    if {b['partition'] for b in state['backups']}!={'boot_a','vendor_boot_a'}:raise ValueError('backup contract changed')
    for b in state['backups']:
        if sha(backup/(b['partition']+'.bin'))!=b['sha256']:raise ValueError('backup mismatch')
    data=dict(trial='S-054',image_sha256=IMAGE,authorizes_execution=False,capture_ready=False,
              fresh_device_preflight=False,local_backup_hashes_match=True,bindings={name:sha(root/name) for name in BINDINGS})
    target=out/'preparation.json';target.write_text(json.dumps(data,indent=2)+'\n');qualification(target,root=root)
    if state_path.read_bytes()!=before:raise ValueError('device state changed during preparation')
    return target
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    print(prepare(parser.parse_args().output))
