"""Check exact constant-only native calibration PE pair and original cold Core."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--positive',type=Path,required=True);p.add_argument('--negative',type=Path,required=True)
    p.add_argument('--tool-path',type=Path,required=True);p.add_argument('--reviewed-diff-sha256');a=p.parse_args()
    sys.path.insert(0,str(a.tool_path.resolve()));import pefile,capstone
    def executable(path):return [(s.VirtualAddress,s.get_data()) for s in pefile.PE(str(path)).sections if s.Characteristics&0x20]
    ref=executable(ROOT/'out/inherited-gop/qualified-terminal-1a4b204-q1/DxeCore.efi')
    md=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_LITTLE_ENDIAN);md.skipdata=True
    codes=[];rows=[];qs=[];dirs=[a.positive.resolve(),a.negative.resolve()]
    for query,d in enumerate(dirs,1):
        if not d.is_relative_to(ROOT/'out'):raise ValueError('outside out')
        q=json.loads((d/'qualification.json').read_text());qs.append(q)
        if q.get('native_control') is not True or q.get('native_query')!=query or q.get('boot_clock_capture') is not True:raise ValueError('wrong constant profile')
        for name,meta in q['files'].items():
            if sha((d/name).read_bytes())!=meta['sha256']:raise ValueError('archive changed')
        if executable(d/'DxeCore.efi')!=ref:raise ValueError('cold Core differs from reviewed S010')
        code={i.address:dict(mnemonic=i.mnemonic,operands=i.op_str,bytes=bytes(i.bytes).hex()) for base,data in executable(d/'SimpleFbDxe.efi') for i in md.disasm(data,base)}
        codes.append(code)
        text='\n'.join(f'{addr:x}: {v["mnemonic"]} {v["operands"]}' for addr,v in code.items())+'\n'
        (d/'provider.disassembly.txt').write_text(text,newline='\n')
        q['files']['provider.disassembly.txt']={'sha256':sha(text.encode()),'bytes':len(text.encode())}
        if any(s in (d/'provider.map').read_text() for s in ['EnumaObserveNativeVideo','LocateMemoryRegionByName',' Read\n',' Wait\n']):raise ValueError('unexpected display sampler/helper linked')
        rows.append(dict(native_query=query,native_control=True,image_sha256=q['image_sha256'],provider_sha256=q['files']['SimpleFbDxe.efi']['sha256'],core_sha256=q['files']['DxeCore.efi']['sha256'],disassembly_sha256=sha(text.encode()),core_executable_equal_reviewed_S010=True))
    if qs[0]['firmware_commit']!=qs[1]['firmware_commit'] or codes[0].keys()!=codes[1].keys():raise ValueError('pair layout/source differs')
    changes=[dict(rva=hex(addr),positive=v,negative=codes[1][addr]) for addr,v in codes[0].items() if v!=codes[1][addr]]
    digest=sha(json.dumps(changes,sort_keys=True,separators=(',',':')).encode())
    if len(changes)!=1 or changes[0]['positive']['mnemonic']!='mov' or changes[0]['negative']['mnemonic']!='mov' or changes[0]['positive']['operands']!='w0, #1' or changes[0]['negative']['operands']!='w0, #5':raise ValueError('constant pair contains more than one return constant change')
    if a.reviewed_diff_sha256 and digest!=a.reviewed_diff_sha256:raise ValueError('reviewed difference changed')
    pending=a.reviewed_diff_sha256 is None
    report=dict(scope='constant-only native calibration actual provider/Core pair; not display observation',firmware_commit=qs[0]['firmware_commit'],queries=rows,changes=changes,differences_sha256=digest,review_required=pending,hardware_success=False)
    (ROOT/'reports/enuma-native-display-code.json').write_text(json.dumps(report,indent=2)+'\n')
    for q,d in zip(qs,dirs):
        q['review_required']=pending
        for path in [d/'qualification.json',ROOT/f'reports/enuma-native-display-q{q["native_query"]}-qualification.json']:path.write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(review_required=pending,differences_sha256=digest,changes=changes),indent=2))
if __name__=='__main__':main()
