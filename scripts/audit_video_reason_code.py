"""Review-bind exact complementary provider code differences and fixed Core."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--positive',type=Path,required=True);p.add_argument('--negative',type=Path,required=True);p.add_argument('--tool-path',type=Path);p.add_argument('--reviewed-diff-sha256');a=p.parse_args()
    if a.tool_path:sys.path.insert(0,str(a.tool_path.resolve()))
    import pefile,capstone
    reference=pefile.PE(str(ROOT/'out/inherited-gop/qualified-terminal-1a4b204-q1/DxeCore.efi'))
    executable=lambda pe:[(s.VirtualAddress,s.get_data()) for s in pe.sections if s.Characteristics&0x20]
    md=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_LITTLE_ENDIAN);md.skipdata=True
    rows=[];code=[];qs=[]
    for query,d in enumerate([a.positive,a.negative],1):
        q=json.loads((d/'qualification.json').read_text());qs.append(q)
        if q.get('reason_query')!=query or not q.get('reason_target'):raise ValueError('wrong reason pair order')
        for name,meta in q['files'].items():
            if sha((d/name).read_bytes())!=meta['sha256']:raise ValueError('archive changed')
        if executable(pefile.PE(str(d/'DxeCore.efi')))!=executable(reference):raise ValueError('Core executable differs from reviewed S-010')
        pe=pefile.PE(str(d/'SimpleFbDxe.efi'))
        instructions={i.address:dict(mnemonic=i.mnemonic,operands=i.op_str,bytes=bytes(i.bytes).hex()) for s in pe.sections if s.Characteristics&0x20 for i in md.disasm(s.get_data(),s.VirtualAddress)}
        code.append(instructions)
        rows.append(dict(query=query,reason_target=q['reason_target'],image_sha256=q['image_sha256'],provider_sha256=q['files']['SimpleFbDxe.efi']['sha256'],core_sha256=q['files']['DxeCore.efi']['sha256'],core_executable_equal_reviewed_S010=True))
    if qs[0]['firmware_commit']!=qs[1]['firmware_commit'] or qs[0]['reason_target']!=qs[1]['reason_target'] or code[0].keys()!=code[1].keys():raise ValueError('source/target/provider layout mismatch')
    changes=[dict(rva=hex(addr),positive=v,negative=code[1][addr]) for addr,v in code[0].items() if v!=code[1][addr]]
    if not changes:raise ValueError('no complementary runtime change')
    digest=sha(json.dumps(changes,sort_keys=True,separators=(',',':')).encode())
    if a.reviewed_diff_sha256 and a.reviewed_diff_sha256!=digest:raise ValueError('actual code differs from reviewed diff')
    report=dict(scope='actual archived reason classifier executable comparison; manual review of every changed instruction is required',firmware_commit=qs[0]['firmware_commit'],queries=rows,changes=changes,differences_sha256=digest,review_required=a.reviewed_diff_sha256 is None,hardware_success=False)
    (ROOT/'reports/enuma-video-reason-code.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(review_required=report['review_required'],differences_sha256=digest,changes=changes),indent=2))
if __name__=='__main__':main()
