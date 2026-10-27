"""Apply pinned same-donor PMGR byte contracts at enuma's actual prelink slide.

Static imports/dispatch evidence only; does not qualify live class metadata.
"""
import argparse,hashlib,json,re,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True)
    p.add_argument('--prelink',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    peer=a.evidence_root/'out/sources/UniXNU-umi';pin='3eb72578597d2ca16471b172d45eddc096a34a04';name='scripts/audit-umi-pmgr-contract.py'
    original=(peer/name).read_bytes()
    if original!=subprocess.check_output(['git','-C',str(peer),'show',pin+':'+name]):raise ValueError('peer changed')
    base=ROOT/'out/sources/UniXNU';kit=base/'kits/NativePrelink'
    kitpin=json.loads((ROOT/'config/sources.lock.json').read_text())['sources']['UniXNU']['gitlinks']['kits/NativePrelink']
    for path in kit.glob('*.py'):
        if path.read_bytes()!=subprocess.check_output(['git','-C',str(kit),'show',kitpin+':'+path.name]):raise ValueError('parser changed')
    candidate=a.prelink/'userland-components.experimental.macho';emitter=a.prelink/'emitter.json'
    report=json.loads((a.prelink/'result.json').read_text());plan=json.loads(emitter.read_text())
    if sha(candidate)!=report['image_sha256'] or plan['slide']!=int(report['slide'],16):raise ValueError('prelink differs')
    donor=a.evidence_root/'out/donor-audit/kernelcache.decompressed'
    if sha(donor)!='f18b4df865405f2a287b84977d7aca745e056d656d9fc9df1662970ce2969de7':raise ValueError('donor differs')
    # Anchor to the actual PMGR text extent and the pinned reference's
    # constructor at text+0x58. The full executable hash and every instruction
    # contract below validate the mapping; a guessed global slide is not used.
    text_extent,=[e for e in plan['extents'] if e['module']=='com.apple.driver.ApplePMGR' and e['segment']=='__TEXT_EXEC']
    delta=text_extent['va']-(0xfffffff0049f0058-0x58)
    text=original.decode();marker='# The target-specific driver is inspected';at=text.index(marker)
    head,tail=text[:at],text[at:];addresses={}
    def relocate(match):
        old=int(match[0],16);new=old+delta;addresses[hex(old)]=hex(new);return hex(new)
    head=re.sub(r'0xfffffff[0-9a-f]{9}',relocate,head)
    # Exact pinned prelink module, never a second unchecked import from peer.
    head=head.replace("ROOT = Path(__file__).resolve().parents[1]",'ROOT = Path('+repr(str(base))+')')
    script=out/'pmgr-contract.py';script.write_text(head+tail)
    current=out/'candidate.macho';shutil.copyfile(candidate,current);shutil.copyfile(emitter,current.with_suffix('.json'))
    commands=[]
    def run(image,result,success,error=None):
        command=[sys.executable,'-B',str(script),'--candidate',str(image),'--donor',str(donor),'--output',str(result)]
        r=subprocess.run(command,capture_output=True,text=True,timeout=120)
        commands.append(dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
        (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
        if (r.returncode==0)!=success or (not success and result.exists()):raise ValueError('unexpected contract result '+r.stdout+r.stderr)
        if not success and (error not in r.stderr or 'Traceback' in r.stderr):raise ValueError('wrong rejection reason '+r.stderr)
    run(current,out/'contract.json',True)
    sys.path.insert(0,str(kit));import native_prelink as np
    data=current.read_bytes();meta=np.macho(data)
    for label,reference_va in [('read_dispatch',0xfffffff004a24adc),('write_dispatch',0xfffffff004a230ec),('pmgr_import',0xfffffff005cfac08)]:
        mutated=bytearray(data);offset=np.backed_offset(meta['segments'],reference_va+delta,8,len(data));mutated[offset]^=1
        path=out/(label+'.macho');path.write_bytes(mutated);shutil.copyfile(emitter,path.with_suffix('.json'))
        run(path,out/(label+'-result.json'),False,
            'PMGR imports differ' if label=='pmgr_import' else 'Original executable differs: com.apple.driver.ApplePMGR')
    result=dict(passed=True,reference_commit=pin,reference_script_sha256=hashlib.sha256(original).hexdigest(),
        adapted_script_sha256=sha(script),candidate_sha256=sha(candidate),emitter_sha256=sha(emitter),
        actual_slide=hex(plan['slide']),reference_slide=hex(plan['slide']-delta),address_translation=addresses,
        contract=json.loads((out/'contract.json').read_text()),negative_cases=3,
        live_native_4k=False,private_abi_qualified=False,service_registered=False,hardware_executed=False,
        scope='static same-donor relocated PMGR contract, not compiler layout or live metadata qualification')
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS: enuma PMGR dispatch/import contract and three mutations rejected')
if __name__=='__main__':main()
