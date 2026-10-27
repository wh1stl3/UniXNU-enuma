"""Check the linked Core call sequence; static evidence, not a reset guarantee."""
import argparse
import json
from pathlib import Path
import re
from audit_oem_development_fd import ROOT, sha
from map_oem_trace_rva import sections, map_return
from prepare_enuma_mmu_experiment import file_offset


def check(pe,mapping):
    names=('DxeMain','MicroSecondDelay','ResetCold','CpuDeadLoop','CoreDispatcher')
    symbols={}
    for n in names:
        matches=re.findall(r'^([0-9a-f]+)\s+00000000\s+0\s+'+n+r'$',mapping,re.M)
        if len(matches)!=1:raise ValueError('ambiguous map symbol '+n)
        symbols[n]=int(matches[0],16)
    sequence=[]
    for site in range(symbols['DxeMain'],symbols['CoreDispatcher'],4):
        try:target=map_return(pe,site+4).get('static_target_rva')
        except ValueError:continue
        if target==hex(symbols['CoreDispatcher']):sequence.append(site)
    if len(sequence)!=1:raise ValueError('ambiguous dispatcher call')
    site=sequence[0]
    for i,n in enumerate(names[1:]):
        if map_return(pe,site-12+4*i+4).get('static_target_rva')!=hex(symbols[n]):
            raise ValueError('missing stage10 call sequence')
    return {'call_rvas':{n:hex(site-12+4*i) for i,n in enumerate(names[1:])},
            'symbol_rvas':{n:hex(v) for n,v in symbols.items()}}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();build=a.build.resolve();build.relative_to(ROOT/'out')
    out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    product=build/'work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64/MdeModulePkg/Core/Dxe/DxeMain/OUTPUT'
    pe=(product/'DxeCore.efi').read_bytes();mapping=(product/'DxeCore.map').read_text()
    result=check(pe,mapping);negative=[]
    for name,rva in result['call_rvas'].items():
        off=file_offset(pe,int(rva,16));mutated=pe[:off]+bytes.fromhex('1f2003d5')+pe[off+4:]
        try:check(mutated,mapping)
        except ValueError:negative.append(name)
        else:raise AssertionError('accepted removed call '+name)
    result.update(passed=True,core_pe_sha256=sha(pe),map_sha256=sha(mapping.encode()),
                  text_sha256=next(sha(pe[s[3]:s[3]+s[2]]) for s in sections(pe) if s[0]=='.text'),
                  removed_call_checks=negative,script_sha256=sha(Path(__file__).read_bytes()),
                  scope='linked call sequence only; not full control-flow proof or physical reset guarantee')
    (out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
