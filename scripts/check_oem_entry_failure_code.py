"""Check the actual binding-rejection CoreExit/terminal-loop sequence."""
import argparse,json,re,struct
from pathlib import Path
from audit_oem_development_fd import ROOT,sha
from prepare_enuma_mmu_experiment import file_offset
from map_oem_trace_rva import map_return


def check(pe,mapping):
    def symbol(name):
        found=set(int(x,16) for x in re.findall(r'^([0-9a-f]+)\s+00000000\s+0\s+'+name+r'$',mapping,re.M))
        if len(found)!=1:raise ValueError('ambiguous symbol '+name)
        return found.pop()
    start,end,pause=symbol('CoreStartImage'),symbol('CoreExit'),symbol('CpuPause');hits=[]
    for rva in range(start,end-8,4):
        try:
            if map_return(pe,rva+4).get('static_target_rva')!=hex(end):continue
            if map_return(pe,rva+8).get('static_target_rva')!=hex(pause):continue
        except ValueError:continue
        # B -4: return from CpuPause loops back to the same pause call.
        if struct.unpack_from('<I',pe,file_offset(pe,rva+8))[0]==0x17ffffff:hits.append(rva)
    if len(hits)!=1:raise ValueError('binding rejection terminal sequence missing')
    return hits[0]


def main():
    p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    product=a.build/'work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64/MdeModulePkg/Core/Dxe/DxeMain/OUTPUT'
    pe=(product/'DxeCore.efi').read_bytes();mapping=(product/'DxeCore.map').read_text();site=check(pe,mapping)
    for i in range(3):
        off=file_offset(pe,site+i*4);mutated=pe[:off]+bytes.fromhex('1f2003d5')+pe[off+4:]
        try:check(mutated,mapping)
        except ValueError:pass
        else:raise AssertionError('accepted removed terminal instruction')
    result=dict(passed=True,core_sha256=sha(pe),core_exit_rva=hex(site),pause_call_rva=hex(site+4),loop_rva=hex(site+8),
                deletion_checks=3,script_sha256=sha(Path(__file__).read_bytes()),
                scope='static rejection terminal sequence; no complete control-flow or runtime claim')
    (out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
