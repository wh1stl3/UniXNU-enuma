"""Offline mainline plan validation; does not authorize or execute a device."""
import argparse
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def validate(p):
    assert p['r027']['required'] is False
    assert p['r027']['role'] == 'optional-frozen-regression'
    c = p['candidate']
    assert c['hardware_authorized'] is False and c['bootable_image'] is None
    assert all(c[x] is True for x in ('retain_oem_modules','retain_constructors','retain_error_checks'))
    ids = ['capture','oem-return-gop','darwinboot','ebs','xnu-entry']
    assert [x['id'] for x in p['checkpoints']] == ids
    for i, stage in enumerate(p['checkpoints']):
        assert stage['requires'] == ([] if not i else [ids[i-1]])
        assert stage['hardware_passed'] is False and stage['evidence']
    assert all(v is False for v in p['interpretation'].values())
    assert set(p['uncovered']) >= {'protocol methods','MMIO','SMC','locks','SMP'}
    assert len(p['sid']['uncovered_method_rvas']) == 4
    assert p['blockers'] and len(p['deployment_requirements']) == 6

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args(); out=args.output.resolve(); out.relative_to(ROOT/'out')
    out.mkdir(parents=True,exist_ok=False)
    src=ROOT/'config/oem-mainline-plan.json'; p=json.loads(src.read_text())
    validate(p)
    mutations=[lambda q:q['r027'].update(required=True),lambda q:q['candidate'].update(hardware_authorized=True),lambda q:q['candidate'].update(retain_oem_modules=False),lambda q:q['interpretation'].update(ci_is_hardware_evidence=True),lambda q:q['interpretation'].update(missing_return_is_deadlock=True),lambda q:q['checkpoints'][3].update(requires=['capture']),lambda q:q['checkpoints'][0].update(hardware_passed=True),lambda q:q.update(uncovered=[])]
    for mutate in mutations:
        q=json.loads(json.dumps(p)); mutate(q)
        try: validate(q)
        except AssertionError: pass
        else: raise AssertionError('unsafe plan accepted')
    bindings={'config/oem-mainline-plan.json':hashlib.sha256(src.read_bytes()).hexdigest()}
    for name,expected in [('out/deferred-menu-20261027/qualification1/image.img',p['r027']['image_sha256']),('out/firmware-vendor/Binaries/enuma/DisplayDxe/DisplayDxe.efi',p['candidate']['oem_pe_sha256'])]:
        actual=hashlib.sha256((ROOT/name).read_bytes()).hexdigest(); assert actual==expected,name
        bindings[name]=actual
    approvals=json.loads((ROOT/'config/hardware-review-approvals.json').read_text())
    assert approvals['R-027']['status']=='paused-by-user'
    capture=json.loads((ROOT/'out/mainline-plan-20261027/precall/result.json').read_text())
    assert capture['passed'] and not capture['hardware_executed'] and not capture['board_sink_connected']
    report=dict(plan_checks_passed=True,negative_cases_rejected=len(mutations),component_capture_regression_passed=True,firmware_candidate_qualified=False,hardware_executed=False,execution_ready=False,blockers=p['blockers'],bindings=bindings)
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
