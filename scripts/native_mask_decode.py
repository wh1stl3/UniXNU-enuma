"""Fixed boot-origin windows; no adaptation to the candidate observation."""
import json
import math

def make_plan(root):
    baselines=[]
    for name,delay in [('S-021',2),('S-022',7)]:
        r=json.loads((root/f'reports/enuma-boot-clock-{name}-result.json').read_text())
        if not all(r.get(k) is True for k in ['automatic_android_return','observation_valid','boot_id_changed']):
            raise ValueError('invalid calibration trial')
        c=r['post_boot_clock']
        baselines.append([c['origin_after_issue_lower']-delay,c['origin_after_issue_upper']-delay])
    base=[min(x[0] for x in baselines),max(x[1] for x in baselines)]
    # Fixed +/-1 second for cross-boot overhead; sampler at most 0.2 seconds.
    windows=[[base[0]+d-1,base[1]+d+.2+1] for d in [2,7,12,17,22]]
    return dict(baseline_envelope_seconds=base,tolerance_seconds=1,sampler_seconds=[0,.2],
                code_windows_after_issue=windows,source_trials=['S-021','S-022'],
                full_interval_containment=True,uncertainty_limit_seconds=.25,
                limitation='Indirect timing inference; boot overhead can change. No exact register or unique execution-path proof.')

def make_pixel_plan(root):
    plan=make_plan(root)
    # Two complete100ms-window samplers plus at most500ms hold: total0.9s.
    plan['sampler_seconds']=[0,.9]
    base=plan['baseline_envelope_seconds']
    plan['code_windows_after_issue']=[[base[0]+d-1,base[1]+d+.9+1] for d in [2,7,12,17,22]]
    plan['declared_profile']='R-018 two samplers and bounded500ms hold; preissue envelope'
    return plan

def decode(clock,plan):
    lo=clock['origin_after_issue_lower'];hi=clock['origin_after_issue_upper']
    if not all(math.isfinite(v) for v in [lo,hi]) or lo>hi or hi-lo>.25:
        raise ValueError('invalid observation interval')
    found=[i for i,(a,b) in enumerate(plan['code_windows_after_issue']) if a<=lo<=hi<=b]
    if len(found)!=1:return dict(conclusion='ambiguous',mask=None,stop_additional_trials=True)
    code=found[0]
    return dict(conclusion='collection-failed' if code==4 else 'mask-inferred',mask=None if code==4 else code,
                warning_code=code+1,stop_additional_trials=False,
                direct_register_log=False)
