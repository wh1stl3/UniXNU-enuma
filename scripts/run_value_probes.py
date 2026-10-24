"""Immutable artifacts, calibrated timing, at most one trial per invocation.

Offline validation is the default. --execute requires clean published docs and
source. No packaging, implicit queue, fixed baseline or historical raw reuse.
"""
import argparse
import hashlib
import json
import math
import statistics
import subprocess
import sys
from pathlib import Path
from reconcile_enuma_recovery import atomic_json

ROOT = Path(__file__).resolve().parents[1]
SECONDS_PER_CODE = 3.0
TOLERANCE = 0.75


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(seconds, zero_seconds, seconds_per_code=SECONDS_PER_CODE, tolerance=TOLERANCE):
    if not all(math.isfinite(x) for x in (seconds, zero_seconds, seconds_per_code, tolerance)):
        raise ValueError('non-finite timing')
    if seconds_per_code <= 0 or not 0 < tolerance < seconds_per_code / 2:
        raise ValueError('invalid timing separation')
    code = round((seconds - zero_seconds) / seconds_per_code)
    if not 0 <= code <= 15 or abs(seconds-zero_seconds-code*seconds_per_code) > tolerance:
        raise ValueError('ambiguous or out-of-range timing; no decoded value')
    return code


def calibration(rows):
    controls = [r for r in rows if r.get('role')=='constant' and r.get('outcome')=='returned']
    if len(controls)!=3 or [r['code'] for r in controls]!=[0,3,0]:
        raise ValueError('require exactly ordered 0/3/0 controls')
    if len({r['metric'] for r in controls})!=1:
        raise ValueError('controls used different return metrics')
    zero = statistics.mean([controls[0]['seconds'],controls[2]['seconds']])
    if abs(controls[0]['seconds']-controls[2]['seconds'])>TOLERANCE:
        raise ValueError('baseline drift exceeds calibration tolerance')
    if decode(controls[1]['seconds'],zero)!=3:
        raise ValueError('known-code control failed')
    return zero, controls[0]['metric']


def validate_plan(plan, root):
    if plan.get('schema')!=1 or plan.get('seconds_per_code')!=SECONDS_PER_CODE:
        raise ValueError('unsupported value transport plan')
    if len({x['id'] for x in plan['trials']})!=len(plan['trials']):
        raise ValueError('duplicate trial IDs')
    source_lock=json.loads((root/'config/uefi-source.lock.json').read_text())
    pin=source_lock['commit']
    actual=subprocess.check_output(['git','-C',str(root/'firmware'),'rev-parse','HEAD'],text=True).strip()
    if actual!=pin:raise ValueError('firmware checkout differs from qualification pin')
    for name,wanted in source_lock['file_sha256'].items():
        if digest(root/'firmware'/name)!=wanted:raise ValueError('locked firmware file changed: '+name)
    for trial in plan['trials']:
        paths={}
        for key in ('image','raw','build','audit','package'):
            path=(root/trial[key]).resolve()
            if not path.is_relative_to((root/'out').resolve()) or digest(path)!=trial['sha256'][key]:
                raise ValueError('artifact changed or outside out/: '+key)
            paths[key]=path
        build,audit,package=[json.loads(paths[k].read_text()) for k in ('build','audit','package')]
        value=build['value_probe']
        if (not build['complete'] or build['uefi_source_commit']!=pin or
            build['fd_sha256']!=audit['fd_sha256'] or package['image_sha256']!=trial['sha256']['image'] or
            package['kernel_sha256']!=trial['sha256']['raw'] or package.get('fixture_only') is not False or
            package.get('hardware_review') is not None):
            raise ValueError('source/build/audit/package binding failed')
        raw=paths['raw'].read_bytes()
        if hashlib.sha256(raw[-0x300000:]).hexdigest()!=build['fd_sha256']:
            raise ValueError('raw does not contain the audited FD')
        from package_enuma_boot import verify
        verify(paths['image'].read_bytes(),raw,b'')
        expected={'source':trial['role'],'constant_code':trial.get('code',0),
                  'register_index':trial.get('index',0),'shift':trial.get('shift',0),
                  'extra_base_seconds':0,'seconds_per_code':3}
        if value!=expected or trial['role'] not in ('constant','register'):
            raise ValueError('value profile does not match trial')
        defines=build['firmware_configuration']['defines']
        wanted={'ENUMA_VALUE_SOURCE':str(1 if trial['role']=='constant' else 2),
                'ENUMA_VALUE_CODE':str(expected['constant_code']),'ENUMA_VALUE_INDEX':str(expected['register_index']),
                'ENUMA_VALUE_SHIFT':str(expected['shift']),'ENUMA_DIAG_GOP_STEP':'0','ENUMA_DIAG_GOP_QUERY':'1',
                'ENUMA_DIAG_STAGE':'13','ENUMA_DIAG_DETAIL_POINT':'16','ENUMA_DIAG_DELAY_US':'2000000',
                'ENUMA_DIAG_DELAY_FROM_DISPLAY':'0','ENUMA_DIAG_SIMPLEFB':'1','ENUMA_DIAG_GUID_ONLY':'1',
                'ENUMA_DIAG_DISPATCH_FALLBACK':'1','ENUMA_DIAG_PIXEL_PREVIEW':'0'}
        for name,want in wanted.items():
            if defines.get(name)!=want:
                raise ValueError('unexpected compiled define: '+name)
        if (build.get('diagnostic_dispatch_guid')!='dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92' or
            build.get('diagnostic_pixel_preview') is not False or not build.get('core_patch_reversion_checked') or
            audit.get('value_transport_code',{}).get('profile')!=value):
            raise ValueError('missing code/dispatch/patch-reversion qualification')
        compiled=build.get('value_probe_compiled_contract',{})
        if (compiled.get('header_sha256')!=source_lock['file_sha256']['diagnostics/EnumaValueProbe.h'] or
            audit['value_transport_code'].get('compiled_contract')!=compiled):
            raise ValueError('compiled helper or code audit differs from locked source')


def require_published(root):
    for repo in (root,root/'firmware'):
        def git(*args):
            return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
        if git('status','--porcelain','--ignore-submodules=all'):
            raise ValueError('source/docs must be clean before device execution')
        if git('rev-parse','HEAD')!=git('ls-remote','origin','refs/heads/main').split()[0]:
            raise ValueError('source/docs HEAD has not been published')


def run_one(root,plan,trial_id,ledger_path,execute=False,invoke=subprocess.run):
    validate_plan(plan,root)
    matches=[r for r in plan['trials'] if r['id']==trial_id]
    if len(matches)!=1: raise ValueError('unknown trial ID')
    if not execute: return {'validated':trial_id,'device_action':False}
    require_published(root)
    plan_sha=hashlib.sha256(json.dumps(plan,sort_keys=True).encode()).hexdigest()
    ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else {'plan_sha256':plan_sha,'trials':[]}
    if ledger['plan_sha256']!=plan_sha: raise ValueError('ledger belongs to another artifact plan')
    rows=ledger['trials']
    if any(r.get('outcome')!='returned' for r in rows):
        raise ValueError('prior trial failed or was interrupted; freeze this plan')
    if len(rows)>=len(plan['trials']) or trial_id!=plan['trials'][len(rows)]['id']:
        raise ValueError('one trial only, in plan order; never repeat a consumed ID')
    trial=matches[0]
    if trial['role']=='register': zero,metric=calibration(rows)
    elif [r.get('code') for r in rows]+[trial.get('code')]!=[0,3,0][:len(rows)+1]:
        raise ValueError('constant trials must be 0/3/0')
    row={k:trial[k] for k in ('id','role','code','index','shift') if k in trial}
    row.update(outcome='issued',image_sha256=trial['sha256']['image'])
    rows.append(row);atomic_json(ledger_path,ledger)
    result=invoke([sys.executable,'-B',str(root/'scripts/run_enuma_entry_probe.py'),
                   '--image',str(root/trial['image']),'--label','dxe-driver-return'],
                  cwd=root,capture_output=True,text=True,timeout=240)
    state=json.loads((root/'out/device-tests/current.local.json').read_text())
    if (result.returncode or state.get('candidate_sha256')!=row['image_sha256'] or
        state.get('phase')!='recovered-android-boot-complete' or state.get('partition_digests_unchanged') is not True):
        row.update(outcome='failed',runner_returncode=result.returncode,phase=state.get('phase'))
        atomic_json(ledger_path,ledger)
        raise ValueError('trial failed: freeze plan, stop boots, reconcile recovery/docs')
    available='fastboot_return_seconds' if 'fastboot_return_seconds' in state else 'adb_return_seconds'
    row.update(outcome='returned',metric=available,seconds=state[available],
               evidence=str(Path(state['directory']).relative_to(root)))
    try:
        if trial['role']=='register':
            if available!=metric: raise ValueError('return metric differs from controls')
            row['nibble']=decode(row['seconds'],zero)
        elif len(rows)==3:
            zero,metric=calibration(rows)
            ledger['calibration']={'zero_seconds':zero,'metric':metric,'tolerance_seconds':TOLERANCE}
    except ValueError as error:
        row.update(outcome='ambiguous',reason=str(error));atomic_json(ledger_path,ledger);raise
    atomic_json(ledger_path,ledger)
    return row


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan',type=Path,required=True);p.add_argument('--trial',required=True)
    p.add_argument('--execute',action='store_true');a=p.parse_args()
    print(json.dumps(run_one(ROOT,json.loads(a.plan.read_text()),a.trial,
          ROOT/'reports/enuma-value-transport-device.json',a.execute),indent=2))


if __name__=='__main__':main()
