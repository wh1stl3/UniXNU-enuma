"""Archive qualified build artifacts or assemble a fixed, single-trial execution plan."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from reconcile_enuma_recovery import atomic_json

ROOT=Path(__file__).resolve().parents[1]


def capture(name):
    if name not in ('zero','known3','mdp-low'):
        raise ValueError('unsupported bounded candidate name')
    target=ROOT/'out/value-transport'/name
    target.mkdir(parents=True,exist_ok=True)
    files={'build':'reports/enuma-firmware-build.json','audit':'reports/enuma-fd-audit.json',
           'raw':'out/boot-candidate/enuma-uefi.raw','payload':'reports/enuma-boot-payload.json'}
    build=json.loads((ROOT/files['build']).read_text())
    audit=json.loads((ROOT/files['audit']).read_text())
    if not build['complete'] or build['fd_sha256']!=audit['fd_sha256']:
        raise ValueError('build/audit mismatch')
    for key,relative in files.items():
        dest=target/({'raw':'candidate.raw'}.get(key,key+'.json'))
        if dest.exists():raise ValueError('refuse to overwrite archived qualification: '+str(dest))
        shutil.copyfile(ROOT/relative,dest)
    shutil.copyfile(ROOT/build['fd'],target/'candidate.fd')
    return target


def assemble():
    trials=[]
    for ident,name,role,code in (('zero1','zero','constant',0),('known3','known3','constant',3),
                                ('zero2','zero','constant',0),('mdp-low','mdp-low','register',0)):
        base=ROOT/'out/value-transport'/name
        if name=='mdp-low' and not (base/'package.json').exists():continue
        fields={'id':ident,'role':role,'code':code}
        if role=='register':fields.update(index=0,shift=0)
        paths={key:str((base/file).relative_to(ROOT)) for key,file in {
            'image':'candidate.img','raw':'candidate.raw','build':'build.json',
            'audit':'audit.json','package':'package.json'}.items()}
        fields.update(paths)
        fields['sha256']={key:hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() for key,relative in paths.items()}
        trials.append(fields)
    plan={'schema':1,'seconds_per_code':3,'trials':trials}
    from run_value_probes import validate_plan
    validate_plan(plan,ROOT)
    output=ROOT/'out/value-transport/plan.json'
    if output.exists() and json.loads(output.read_text())!=plan:
        raise ValueError('refuse to change an existing execution plan')
    atomic_json(output,plan)
    atomic_json(ROOT/'reports/enuma-value-transport-qualification.json',plan)
    print('PASS: immutable source/FD/raw/image/compiler qualifications; '+str(len(trials))+' planned trials')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--capture',choices=('zero','known3','mdp-low'))
    args=p.parse_args()
    if args.capture:print(capture(args.capture))
    else:assemble()


if __name__=='__main__':main()
