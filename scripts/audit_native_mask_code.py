"""Freeze disassembly for manual review of native mask/route provider and Core."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--archive',type=Path,required=True);p.add_argument('--tool-path',type=Path,required=True);p.add_argument('--reviewed-sha256');a=p.parse_args()
    d=a.archive.resolve()
    if not d.is_relative_to(ROOT/'out'):raise ValueError('outside out')
    q=json.loads((d/'qualification.json').read_text())
    if q['trial_kind'] not in ('native-display-mask','native-video-route'):raise ValueError('wrong profile')
    stem='enuma-native-route' if q['trial_kind']=='native-video-route' else 'enuma-native-mask'
    for n,v in q['files'].items():
        if sha((d/n).read_bytes())!=v['sha256']:raise ValueError('changed archive: '+n)
    sys.path.insert(0,str(a.tool_path.resolve()));import pefile,capstone
    md=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_LITTLE_ENDIAN);md.skipdata=True
    texts=[]
    for name in ['SimpleFbDxe','DxeCore']:
        pe=pefile.PE(str(d/(name+'.efi')))
        text='\n'.join(f'{i.address:x}: {i.mnemonic} {i.op_str}' for s in pe.sections if s.Characteristics&0x20 for i in md.disasm(s.get_data(),s.VirtualAddress))+'\n'
        n=name+'.disassembly.txt';(d/n).write_text(text,newline='\n');texts.append(text)
        q['files'][n]={'sha256':sha(text.encode()),'bytes':len(text.encode())}
    digest=sha(('\n'.join(texts)).encode())
    if a.reviewed_sha256 and a.reviewed_sha256!=digest:raise ValueError('reviewed code changed')
    pending=a.reviewed_sha256 is None
    r=dict(scope='actual packaged '+q['trial_kind']+' provider and bounded exact-GUID Core terminal; manual disassembly review bound by digest',
      firmware_commit=q['firmware_commit'],native_mask_field=q.get('native_mask_field'),trial_kind=q['trial_kind'],native_route_detail=q.get('native_route_detail',False),image_sha256=q['image_sha256'],
      provider_sha256=q['files']['SimpleFbDxe.efi']['sha256'],core_sha256=q['files']['DxeCore.efi']['sha256'],
      combined_disassembly_sha256=digest,review_required=pending,hardware_success=False)
    q['review_required']=pending
    for path in [d/'qualification.json',ROOT/'reports'/(stem+'-qualification.json')]:path.write_text(json.dumps(q,indent=2)+'\n')
    (ROOT/'reports'/(stem+'-code.json')).write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
