"""Archive qualified build artifacts or assemble a fixed, single-trial execution plan."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from reconcile_enuma_recovery import atomic_json

ROOT=Path(__file__).resolve().parents[1]


def capture(name, image=None):
    if name not in ('zero','known3','mdp-low'):
        raise ValueError('unsupported bounded candidate name')
    if image is None:
        raise ValueError('the packaged image of this candidate must be given')
    target=ROOT/'out/value-transport'/name
    target.mkdir(parents=True,exist_ok=True)
    source=Path(image)
    if not source.is_absolute():
        source=ROOT/source
    source=source.resolve()
    if not source.is_relative_to((ROOT/'out').resolve()):
        raise ValueError('candidate image outside out/')
    files={'build':'reports/enuma-firmware-build.json','audit':'reports/enuma-fd-audit.json',
           'raw':'out/boot-candidate/enuma-uefi.raw',
           'payload':str(source.with_suffix('.json').relative_to(ROOT))}
    build=json.loads((ROOT/files['build']).read_text())
    audit=json.loads((ROOT/files['audit']).read_text())
    if not build['complete'] or build['fd_sha256']!=audit['fd_sha256']:
        raise ValueError('build/audit mismatch')
    # The archived qualification must describe this candidate. Without this
    # check a capture taken after a later build silently keeps the wrong
    # firmware, raw and value profile.
    expected_code={'zero':0,'known3':3,'mdp-low':0}[name]
    profile=build.get('value_probe') or {}
    if profile.get('constant_code')!=expected_code or profile.get('source') not in ('constant','register'):
        raise ValueError('archived build does not describe this candidate: '+str(profile))
    for key,relative in files.items():
        dest=target/({'raw':'candidate.raw','payload':'package.json'}.get(key,key+'.json'))
        if dest.exists():raise ValueError('refuse to overwrite archived qualification: '+str(dest))
        shutil.copyfile(ROOT/relative,dest)
    shutil.copyfile(ROOT/build['fd'],target/'candidate.fd')
    shutil.copyfile(source,target/'candidate.img')
    # The probe runner verifies the image against the report next to it.
    report=source.with_suffix('.json')
    if not report.exists():
        raise ValueError('packaging report missing next to the image')
    shutil.copyfile(report,target/'candidate.json')
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
    p.add_argument('--image',type=Path,help='the packaged boot image of this candidate')
    args=p.parse_args()
    if args.capture:print(capture(args.capture,args.image))
    else:assemble()


if __name__=='__main__':main()
