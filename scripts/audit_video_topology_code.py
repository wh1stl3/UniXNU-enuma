"""Bind reviewed symmetric Core and actual complementary provider instructions."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]


def sha(blob):return hashlib.sha256(blob).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--positive',type=Path,required=True);p.add_argument('--negative',type=Path,required=True);p.add_argument('--tool-path',type=Path);a=p.parse_args()
    if a.tool_path:sys.path.insert(0,str(a.tool_path.resolve()))
    import pefile,capstone
    old=pefile.PE(str(ROOT/'out/inherited-gop/qualified-terminal-1a4b204-q1/DxeCore.efi'))
    executable=lambda pe:[(s.VirtualAddress,s.get_data()) for s in pe.sections if s.Characteristics&0x20]
    dirs=[a.positive,a.negative];rows=[];codes=[]
    md=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_LITTLE_ENDIAN)
    md.skipdata=True
    for query,d in enumerate(dirs,1):
        q=json.loads((d/'qualification.json').read_text())
        if q['topology_status_query']!=query:raise ValueError('wrong query archive order')
        for name,meta in q['files'].items():
            if sha((d/name).read_bytes())!=meta['sha256']:raise ValueError('archive changed')
        core=pefile.PE(str(d/'DxeCore.efi'))
        if executable(core)!=executable(old):raise ValueError('Core executable changed from reviewed S-010')
        pe=pefile.PE(str(d/'SimpleFbDxe.efi'));instructions={i.address:(i.mnemonic,i.op_str) for s in pe.sections if s.Characteristics&0x20 for i in md.disasm(s.get_data(),s.VirtualAddress)}
        codes.append(instructions)
        expected='ne' if query==1 else 'eq'
        sites=[addr for addr,v in instructions.items() if v==('cmp','w8, #0xd') and instructions.get(addr+4)==('mov','w8, #5') and instructions.get(addr+8)==('csinc','x0, x8, xzr, '+expected)]
        if len(sites)!=1:raise ValueError('actual status selector fingerprint absent or ambiguous')
        addr=sites[0]
        rows.append(dict(query=query,core_sha256=sha((d/'DxeCore.efi').read_bytes()),provider_sha256=sha((d/'SimpleFbDxe.efi').read_bytes()),selector_rva=hex(addr),selector=[dict(rva=hex(x),mnemonic=instructions[x][0],operands=instructions[x][1]) for x in [addr,addr+4,addr+8]],core_executable_equal_reviewed_S010=True))
    # Full disassembly is retained locally; compare every decoded instruction.
    # Only the metadata-rejection constants and the status selector condition
    # may change between the two actual providers.
    if codes[0].keys()!=codes[1].keys():raise ValueError('provider executable instruction layout changed')
    changes=[]
    for addr,left in codes[0].items():
        right=codes[1][addr]
        if left==right:continue
        if (left,right) not in [(('mov','w0, #5'),('mov','w0, #1')),(('csinc','x0, x8, xzr, ne'),('csinc','x0, x8, xzr, eq'))]:
            raise ValueError('unexpected provider runtime change at '+hex(addr)+': '+repr((left,right)))
        changes.append(dict(rva=hex(addr),positive=left,negative=right))
    if len(changes)!=3:raise ValueError('expected exactly two metadata-return constants and one selector condition')
    report=dict(scope='actual archived providers and reviewed symmetric Core executable comparison; no hardware success inference',queries=rows,provider_instruction_changes=changes,core_reference='out/inherited-gop/qualified-terminal-1a4b204-q1/DxeCore.efi',source_predicates_unchanged=True,physical_gop_tested=False)
    (ROOT/'reports/enuma-video-topology-code.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: both Core executables equal reviewed S-010; providers differ only in three complementary-result instructions')


if __name__=='__main__':main()
