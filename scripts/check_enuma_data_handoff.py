"""Run pinned DarwinBoot parsing against FAT-readback Data and no-Data ADTs."""
import argparse, hashlib, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--with-data',type=Path,required=True)
    p.add_argument('--without-data',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    base=ROOT/'out/sources/UniXNU';relative='drivers/DarwinBoot/DarwinBootPkg/Driver/'
    lock=json.loads((ROOT/'config/porting-sources.lock.json').read_text())['unixnu_interface_sha256']
    sources={}
    for name in ['DarwinBoot.c','WindowSize.h']:
        path=base/relative/name;sources[name]=sha(path)
        if sources[name]!=lock[relative+name]:raise ValueError('DarwinBoot source pin mismatch')
    original=(base/relative/'DarwinBoot.c').read_text()
    start=original.index('STATIC\nBOOLEAN\nAdtNode (');end=original.index('STATIC\nEFI_STATUS\nGetMap (',start)
    fragment=out/'AdtNode.inc';fragment.write_text(original[start:end])
    commands=[]
    def run(args):
        r=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=120)
        commands.append(dict(command=list(map(str,args)),returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
        (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
        if r.returncode:raise ValueError(r.stderr+r.stdout)
    run(['/usr/bin/clang','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-pie','-no-pie',
         '-I'+str(base/relative),'-DDARWIN_ADT_SOURCE="'+str(fragment)+'"',ROOT/'tests/darwin_adt_contract.c','-o',out/'adt-test'])
    inputs={}
    for name,directory,packed in [('without_data',a.without_data,False),('with_data',a.with_data,True)]:
        report=json.loads((directory/'result.json').read_text())
        if report['passed'] is not True or report['data_seed_included']!=packed:raise ValueError('payload report mismatch')
        image=directory/'payload/payload.img'
        if sha(image)!=report['payload_sha256']:raise ValueError('payload changed')
        extracted=[]
        for suffix in ['adt','trustcache']:
            data=subprocess.check_output(['mtype','-i',str(image),'::/EFI/UniXNU/Payloads/kernel.macho.'+suffix])
            path=out/(name+'.'+suffix);path.write_bytes(data)
            if sha(path)!=report['readback']['Payloads/kernel.macho.'+suffix]:raise ValueError('FAT content changed')
            extracted.append(path)
        run([out/'adt-test','0x20000000',*extracted,*(['packed'] if packed else [])])
        inputs[name]=dict(payload_sha256=sha(image),adt_sha256=sha(extracted[0]),trust_sha256=sha(extracted[1]))
    result=dict(passed=True,sources=sources,fragment_sha256=sha(fragment),inputs=inputs,
                hardware_executed=False,boot_services_exited=False,data_mounted=False,
                scope='real DarwinBoot ADT/trust parser, actual FAT readback, all truncations; host ASan/UBSan only')
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS: both FAT ADTs and trust inputs accepted; malformed/truncated inputs rejected')
if __name__=='__main__':main()
