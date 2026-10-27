"""Decode a transcribed five-row progress page; not an OCR or hardware claim."""
import argparse,json,re
from pathlib import Path
NAMES={1:'first-service-before',2:'first-service-return',3:'sid-locate-before',4:'sid-locate-return',5:'core-start-image-return'}
def decode(text,session,experiment='oem-progress-v2'):
    if experiment not in ('oem-progress-v2','oem-early-v3'):raise ValueError('unknown experiment')
    names=NAMES if experiment=='oem-progress-v2' else {1:'call1-before',2:'call1-return',3:'kernel-locate-before',4:'kernel-locate-return',5:'core-start-image-return'}
    rows=text.splitlines()
    if len(rows)!=5 or any(len(r)!=20 for r in rows):raise ValueError('five exact 20-character rows required')
    m=re.fullmatch(r'([ES])0([1-5])(C[0-9a-f]{16}| {17})',rows[0])
    if not m:raise ValueError('bad phase row')
    phase=int(m[2]);returned=phase in (2,4,5)
    if experiment=='oem-early-v3' and phase in (1,2) and m[3]!='C'+f'{1:016x}':raise ValueError('early experiment requires call1')
    if (m[1]=='S')!=returned or (phase==5)!=(m[3]==' '*17):raise ValueError('phase/call mismatch')
    def value(row,label):
        match=re.fullmatch(label+r'([0-9a-f]{16}) {3}',row)
        if not match:raise ValueError('bad '+label+' row')
        return int(match[1],16)
    seq=value(rows[1],'Q');token=value(rows[4],'G')
    if not session or token!=session:raise ValueError('session differs')
    rva=None if phase==5 else value(rows[2],'O')
    if phase==5 and rows[2]!=' '*20:raise ValueError('driver return has no service caller RVA')
    status=value(rows[3],'S') if returned else None
    if not returned and rows[3]!='E'+' '*19:raise ValueError('entry cannot have status')
    return dict(phase=phase,event=names[phase],experiment=experiment,session=hex(token),sequence=seq,
                call=None if phase==5 else int(m[3][1:],16),caller_rva=None if rva is None else hex(rva),
                returned=returned,status=None if status is None else hex(status),
                scope='transcribed screen observation only; entry is not execution completion; no GOP or BDS claim')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('page',type=Path);p.add_argument('--session',required=True,type=lambda x:int(x,0));p.add_argument('--experiment',choices=('oem-progress-v2','oem-early-v3'),required=True);a=p.parse_args()
    print(json.dumps(decode(a.page.read_text(),a.session,a.experiment),indent=2))
if __name__=='__main__':main()
