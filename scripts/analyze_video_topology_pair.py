"""Conservative paired timing support; never turn timing into a directly read status."""
import argparse
import json
import math
from pathlib import Path


def analyze(positive,negative):
    target=positive.get('reason_target',0)
    reason_mode=bool(target)
    if reason_mode and (type(target) is not int or target not in range(1,5) or negative.get('reason_target')!=target):
        raise ValueError('inconsistent first-reason targets')
    field='reason_query' if reason_mode else 'topology_status_query'
    for row,query in [(positive,1),(negative,2)]:
        if type(row.get(field)) is not int or row.get(field)!=query or row.get('consumed') is not True or row.get('automatic_android_return') is not True:
            raise ValueError('require issued, recovered complementary status queries')
        if row.get('boot_returncode')!=0 or row.get('timing',{}).get('fastboot_return_seconds') is not None:
            raise ValueError('boot command failure or intervening fastboot reboot invalidates timing comparison')
        checks=row.get('recovery',{}).get('checks',{})
        if checks!={'device':'enuma','boot_completed':'1','slot':'_a','flash_locked':'0','root_available':True}:
            raise ValueError('independent recovery gate missing')
        parts=row['recovery'].get('partitions',[])
        if {p['partition'] for p in parts}!={'boot_a','vendor_boot_a'} or len(parts)!=2 or not all(p.get('device_and_backup_match') is True for p in parts):
            raise ValueError('partition recovery gate missing')
    if positive['firmware_commit']!=negative['firmware_commit'] or positive['image_sha256']==negative['image_sha256']:
        raise ValueError('require same source and distinct complementary images')
    deltas={}
    for key in ['adb_return_seconds','boot_complete_seconds']:
        values=[r['timing'].get(key) for r in [positive,negative]]
        if any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 or v>75 for v in values):
            raise ValueError('missing or out-of-bound return timing')
        deltas[key]=round(values[1]-values[0],3)
    if all(3<=v<=7 for v in deltas.values()):result='topology-status-supported'
    elif all(-7<=v<=-3 for v in deltas.values()):result='non-topology-status-supported'
    else:result='ambiguous'
    if reason_mode:
        result={'topology-status-supported':'selected-reason-supported','non-topology-status-supported':'other-reason-supported','ambiguous':'ambiguous'}[result]
    return dict(scope='indirect paired timing support under same-source classifier; not direct firmware status/reason or cross-boot snapshot stability',
                conclusion=result,negative_minus_positive_seconds=deltas,
                reason_target=target,supported_reason_set={1:[5],2:[6,9,10,11,13],3:[4],4:[4,5,6,7,9,10,11,13]}.get(target) if result=='selected-reason-supported' else None,
                supported_status_set=([13] if result=='topology-status-supported' else list(range(13)) if result=='non-topology-status-supported' else None) if not reason_mode else None,
                successful_sample_not_excluded=result not in ('topology-status-supported','selected-reason-supported'),
                predeclared_absolute_delta_window_seconds=[3,7],exact_status_observed=False,gop_verified=False,
                limitation='Android boot noise and changing inherited state remain confounders; timeout, missing recovery or an ambiguous pair cannot classify')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--positive',type=Path,required=True);p.add_argument('--negative',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();result=analyze(json.loads(a.positive.read_text()),json.loads(a.negative.read_text()))
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(result['conclusion'])


if __name__=='__main__':main()
