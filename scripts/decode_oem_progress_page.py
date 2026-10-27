"""Decode a transcribed five-row progress page; not an OCR or hardware claim."""
import argparse,json,re
from pathlib import Path
NAMES={1:'first-service-before',2:'first-service-return',3:'sid-locate-before',4:'sid-locate-return',5:'core-start-image-return'}
def decode_far(text,session):
    rows=text.splitlines()
    if len(rows)!=5 or any(len(r)!=20 for r in rows):raise ValueError('five exact rows required')
    first=re.fullmatch(r'S05C([0-9a-f]{16})',rows[0])
    if not first:raise ValueError('far summary header differs')
    flags=int(first[1],16)
    if flags&~0x3fff or flags&0xc1!=0xc1:raise ValueError('missing real return or DXE completion')
    for child,parent in [(8,4),(32,16),(512,256),(2048,32),(4096,8),(8192,2)]:
        if flags&child and not flags&parent:raise ValueError('inconsistent milestone flags')
    def value(row,label):
        m=re.fullmatch(label+r'([0-9a-f]{16}) {3}',row)
        if not m:raise ValueError('bad '+label+' row')
        return int(m[1],16)
    seq=value(rows[1],'Q');rva=value(rows[2],'O');status=value(rows[3],'S');token=value(rows[4],'G')
    if not session or token!=session:raise ValueError('session differs')
    names={1:'armed',2:'registration-returned',4:'main-entered',8:'main-query-returned',16:'sid-entered',32:'sid-returned',64:'core-start-image-returned',128:'dxe-dispatch-complete',256:'gop-protocol-present',512:'gop-mode-pointer-present',1024:'conout-pointer-present',2048:'sid-status-success',4096:'main-query-status-success',8192:'registration-status-success'}
    return dict(phase=5,event='dxe-complete-summary',experiment='oem-far-chain-v7',session=hex(token),sequence=seq,flags=hex(flags),milestones={n:bool(flags&b) for b,n in names.items()},call=None,last_service_rva=hex(rva),returned=True,status=hex(status),scope='actual Core status and observed coarse milestones; GOP/ConOut presence is not hardware acceptance')

def decode(text,session,experiment='oem-progress-v2'):
    if experiment=='oem-far-chain-v7':return decode_far(text,session)
    if experiment not in ('oem-progress-v2','oem-early-v3','oem-post-kernel-v4','oem-registration-v5','oem-main-entry-v6'):raise ValueError('unknown experiment')
    names=NAMES if experiment=='oem-progress-v2' else {1:'call1-before',2:'call1-return',3:'kernel-locate-before',4:'kernel-locate-return',5:'core-start-image-return'}
    if experiment=='oem-post-kernel-v4':names={1:'call4-before',2:'call4-return',3:'sid-locate-before',4:'sid-locate-return',5:'core-start-image-return'}
    if experiment=='oem-registration-v5':names={1:'registration-before',2:'registration-return',3:'sid-locate-before',4:'sid-locate-return',5:'core-start-image-return'}
    if experiment=='oem-main-entry-v6':names={1:'main-query-before',3:'sid-locate-before',5:'core-start-image-return'}
    rows=text.splitlines()
    if len(rows)!=5 or any(len(r)!=20 for r in rows):raise ValueError('five exact 20-character rows required')
    m=re.fullmatch(r'([ES])0([1-5])(C[0-9a-f]{16}| {17})',rows[0])
    if not m:raise ValueError('bad phase row')
    phase=int(m[2]);returned=phase in (2,4,5)
    if experiment=='oem-main-entry-v6' and (phase not in (1,3,5) or (phase==1 and (m[3]==' '*17 or int(m[3][1:],16)<6))):raise ValueError('main-entry phase or call differs')
    if experiment=='oem-early-v3' and phase in (1,2) and m[3]!='C'+f'{1:016x}':raise ValueError('early experiment requires call1')
    if experiment=='oem-post-kernel-v4' and phase in (1,2) and m[3]!='C'+f'{4:016x}':raise ValueError('post-kernel experiment requires call4')
    if experiment=='oem-registration-v5' and phase in (1,2) and m[3]!='C'+f'{5:016x}':raise ValueError('registration requires call5')
    if (m[1]=='S')!=returned or (phase==5)!=(m[3]==' '*17):raise ValueError('phase/call mismatch')
    def value(row,label):
        match=re.fullmatch(label+r'([0-9a-f]{16}) {3}',row)
        if not match:raise ValueError('bad '+label+' row')
        return int(match[1],16)
    seq=value(rows[1],'Q');token=value(rows[4],'G')
    if not session or token!=session:raise ValueError('session differs')
    rva=None if phase==5 else value(rows[2],'O')
    if phase==5 and rows[2]!=' '*20:raise ValueError('driver return has no service caller RVA')
    if experiment=='oem-registration-v5' and phase in (1,2) and rva!=0x5cc8:raise ValueError('registration caller differs')
    if experiment=='oem-main-entry-v6' and phase==1 and rva!=0x3608:raise ValueError('main query caller differs')
    status=value(rows[3],'S') if returned else None
    if not returned and rows[3]!='E'+' '*19:raise ValueError('entry cannot have status')
    return dict(phase=phase,event=names[phase],experiment=experiment,session=hex(token),sequence=seq,
                call=None if phase==5 else int(m[3][1:],16),caller_rva=None if rva is None else hex(rva),
                returned=returned,status=None if status is None else hex(status),
                scope='transcribed screen observation only; entry is not execution completion; no GOP or BDS claim')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('page',type=Path);p.add_argument('--session',required=True,type=lambda x:int(x,0));p.add_argument('--experiment',choices=('oem-progress-v2','oem-early-v3','oem-post-kernel-v4','oem-registration-v5','oem-main-entry-v6','oem-far-chain-v7'),required=True);a=p.parse_args()
    print(json.dumps(decode(a.page.read_text(),a.session,a.experiment),indent=2))
if __name__=='__main__':main()
