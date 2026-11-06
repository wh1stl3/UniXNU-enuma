"""Build a disposable, directory-only APFS seed with pinned Linux tools.

No device, activation preferences, user records, board UUID or memory edits.
The seed's 512MiB logical filesystem size is an offline test choice, not RAM
reservation or a persistent partition allocation.
"""
import argparse, hashlib, json, os, subprocess, sys, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidence-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    peer=a.evidence_root.resolve()/'out/sources/UniXNU-fajita-latest-review'
    umi=a.evidence_root.resolve()/'out/sources/UniXNU-umi'
    pin='fb8c389bd9877d4db0ef6e09170b83752dec7259';umi_pin='3eb72578597d2ca16471b172d45eddc096a34a04'
    builder=peer/'scripts/make-data-seed-linux.py';packer=umi/'package/data-store/packed_ramdisk.py'
    sources={}
    for repo,commit,name in [(peer,pin,'scripts/make-data-seed-linux.py'),(peer,pin,'data-seed.json'),(umi,umi_pin,'package/data-store/packed_ramdisk.py')]:
        path=repo/name
        if path.read_bytes()!=subprocess.check_output(['git','-C',str(repo),'show',commit+':'+name]):raise ValueError('reference changed '+name)
        sources[name]=dict(commit=commit,sha256=sha(path))
    spec=json.loads((peer/'data-seed.json').read_text())
    # Select directory declarations only. Reference SetupDone/ForceNoBuddy and
    # other preferences are deliberately outside this seed's implemented scope.
    spec={k:spec[k] for k in ['volume_name','case_sensitive','role','directories']}
    spec['size_mib']=512
    spec_path=out/'directory-spec.json';spec_path.write_text(json.dumps(spec,indent=2)+'\n')
    volume,container=str(uuid.uuid4()),str(uuid.uuid4())
    command=[sys.executable,'-B',str(builder),'--packer',str(packer),'--spec',str(spec_path),
             '--out',str(out/'seed'),'--fetch-apfsprogs',str(out/'apfsprogs'),
             '--volume-uuid',volume,'--container-uuid',container,'--timestamp','1793059200','--keep-raw']
    (out/'invocation.json').write_text(json.dumps(dict(command=command,sources=sources,spec_sha256=sha(spec_path)),indent=2)+'\n')
    with (out/'build.log').open('w') as log:
        result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),timeout=1200)
    if result.returncode:raise ValueError('seed build failed; see '+str(out/'build.log'))
    apfs_pin='1bd1c1c2140d13d1b6d2e03379316572bee70aa3'
    if subprocess.check_output(['git','-C',str(out/'apfsprogs'),'rev-parse','HEAD'],text=True).strip()!=apfs_pin:raise ValueError('apfsprogs pin differs')
    built=json.loads((out/'seed/data-linux.json').read_text())
    from enuma_data_seed import inspect_seed
    packed=out/'seed/data-linux.dbr';checked=inspect_seed(packed,built['packed_sha256'])
    if built['logical_bytes']!=512<<20 or built['directories']!=spec['directories'] or built['encrypted'] or built['role_value']!='0x0':raise ValueError('seed policy differs')
    result=dict(passed=True,sources=sources,apfsprogs_commit=apfs_pin,
        tools={name:sha(out/'apfsprogs'/name/name) for name in ['mkapfs','apfsck']},
        seed=built,packed_format=checked,hardware_executed=False,os_mount_tested=False,
        scope='disposable directory-only APFS seed; offline filesystem validation, not userland or activation success',
        remaining=['Data owner UUID/OS policy integration','RamBlock archive and initialization','target OS mount and launchd','framebuffer/HID/desktop services'])
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: offline APFS seed '+built['packed_sha256'])
if __name__=='__main__':main()
