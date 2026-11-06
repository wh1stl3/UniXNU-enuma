"""Compare actual native observer pair and cold Core code; no device operation."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--positive',type=Path,required=True)
    p.add_argument('--negative',type=Path,required=True)
    p.add_argument('--reviewed-diff-sha256')
    p.add_argument('--tool-path',type=Path)
    a=p.parse_args()
    if a.tool_path:sys.path.insert(0,str(a.tool_path.resolve()))
    import pefile,capstone
    def executable(path):
        return [(s.VirtualAddress,s.get_data()) for s in pefile.PE(str(path)).sections if s.Characteristics&0x20]
    reference=executable(ROOT/'out/inherited-gop/qualified-terminal-1a4b204-q1/DxeCore.efi')
    md=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_LITTLE_ENDIAN);md.skipdata=True
    rows=[];codes=[];qs=[];tails=[]
    for query,d in enumerate([a.positive.resolve(),a.negative.resolve()],1):
        if not d.is_relative_to(ROOT/'out'):raise ValueError('archive outside out')
        q=json.loads((d/'qualification.json').read_text());qs.append(q)
        if q.get('trial_kind')!='native-display-observe' or q.get('native_query')!=query:raise ValueError('wrong native pair')
        for name,meta in q['files'].items():
            if sha((d/name).read_bytes())!=meta['sha256']:raise ValueError('archive changed')
        if executable(d/'DxeCore.efi')!=reference:raise ValueError('Core executable differs from reviewed S-010 cold terminal')
        code={i.address:dict(mnemonic=i.mnemonic,operands=i.op_str,bytes=bytes(i.bytes).hex())
              for base,data in executable(d/'SimpleFbDxe.efi') for i in md.disasm(data,base)}
        codes.append(code)
        mapping=(d/'provider.map').read_text()
        sizes=[int(v,16) for v in re.findall(r'^00001050 ([0-9a-fA-F]+)\s+4\s+.*dll\.lto\.obj:',mapping,re.M)]
        if not sizes or max(sizes)==0:raise ValueError('actual entry extent missing')
        end=0x1050+max(sizes)
        pe=pefile.PE(str(d/'SimpleFbDxe.efi'))
        section=next(s for s in pe.sections if s.VirtualAddress==0x1000)
        tails.append(section.get_data()[end-0x1000:section.Misc_VirtualSize])
        assembly='\n'.join(f'{addr:x}: {v["mnemonic"]} {v["operands"]}' for addr,v in code.items())+'\n'
        path=d/'provider.disassembly.txt';path.write_text(assembly)
        q['files'][path.name]={'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}
        rows.append(dict(native_query=query,image_sha256=q['image_sha256'],provider_sha256=q['files']['SimpleFbDxe.efi']['sha256'],
                         core_sha256=q['files']['DxeCore.efi']['sha256'],disassembly_sha256=sha(path.read_bytes()),core_executable_equal_reviewed_S010=True))
    if qs[0]['firmware_commit']!=qs[1]['firmware_commit'] or codes[0].keys()!=codes[1].keys():raise ValueError('pair source/layout mismatch')
    changes=[dict(rva=hex(addr),positive=v,negative=codes[1][addr]) for addr,v in codes[0].items() if v!=codes[1][addr]]
    if not changes:raise ValueError('no complementary code change')
    helper_changes=[]
    for x,y in zip(md.disasm(tails[0],0x1540),md.disasm(tails[1],0x1528)):
        if bytes(x.bytes)!=bytes(y.bytes):
            if x.mnemonic!='bl' or y.mnemonic!='bl' or x.op_str!='#0x1038' or y.op_str!='#0x1038':
                raise ValueError('unreviewed helper code change')
            helper_changes.append(dict(positive_rva=hex(x.address),negative_rva=hex(y.address),target='CpuPause0x1038'))
    if len(tails[0])!=len(tails[1]) or len(helper_changes)!=1:raise ValueError('unexpected helper extent/relocation')
    digest=sha(json.dumps(changes,sort_keys=True,separators=(',',':')).encode())
    if a.reviewed_diff_sha256 and digest!=a.reviewed_diff_sha256:raise ValueError('reviewed diff changed')
    pending=a.reviewed_diff_sha256 is None
    diff=ROOT/'out/native-display-code-diff.json';diff.write_text(json.dumps(changes,indent=2)+'\n')
    report=dict(scope='actual independent observer pair; independently review both optimized entry flows; helper tail equal except one reviewed CpuPause call relocation',
                firmware_commit=qs[0]['firmware_commit'],queries=rows,difference_count=len(changes),differences_sha256=digest,
                complete_diff=diff.relative_to(ROOT).as_posix(),helper_tail_bytes_equal=False,helper_tail_relocations=helper_changes,
                review_required=pending,hardware_success=False)
    if not pending:
        report['manual_review']=[
          'q1 entry1050..153c and q2 entry1050..1524 independently reviewed: compiler changes stack allocation and control-flow layout, so this is not a three-instruction-only pair',
          'map/PCD contract precedes MMIO; revision first/final loads ae00000, major6000 and equality checks',
          'two interfaces b800/c000 within MDP, loops3 samples, Stall100000 twice, STATUSbit0 before Frame, <=26 read bounds',
          'zero Timing, changed Timing/Enable, inactive or non-increasing/wrapped/over64 Frame clear independent masks; ExactEnable3 only updates separate mask',
          'q1 14d0..1514 requires collection success and four masks3 =>warning1 else5; q2 14c8..1504 failure=>1, all four masks3=>5',
          'Read q1 15b0..1634 and q2 1598..161c whitelist four offsets per interface and revision; target access only LDR W, stores go to callback output/local state',
          'linked helper tail equal except DebugAssert call1594/157c to same CpuPause1038; packaged Core executable byte-equal reviewed S010 cold terminal; no provider reset constructor/library or GOP publication']
    (ROOT/'reports/enuma-native-display-code.json').write_text(json.dumps(report,indent=2)+'\n')
    for q,d in zip(qs,[a.positive,a.negative]):
        q['review_required']=pending
        for path in [d/'qualification.json',ROOT/f'reports/enuma-native-display-q{q["native_query"]}-qualification.json']:
            path.write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(review_required=pending,differences_sha256=digest,difference_count=len(changes),helper_tail_relocations=helper_changes),indent=2))

if __name__=='__main__':main()
