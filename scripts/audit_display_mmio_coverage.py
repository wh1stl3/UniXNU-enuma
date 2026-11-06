"""Audit static enuma display MMIO coverage without touching the target."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 source=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/MemoryMapLib/MemoryMapLib.c'
 regions=[dict(name=n,base=int(b,16),length=int(s,16)) for n,b,s in re.findall(r'\{"([^"]+)", (0x[0-9a-f]+)ULL, (0x[0-9a-f]+)ULL',source.read_text())]
 base,length=0xae00000,0x84208
 overlaps=[r for r in regions if r['base']<base+length and base<r['base']+r['length']]
 coverage=[r for r in overlaps if r['base']<=base and base+length<=r['base']+r['length']]
 report=dict(scope='static fixed firmware map vs live DT evidence; no device operations',requested_base=hex(base),live_dt_length=hex(length),covering_regions=coverage,overlapping_regions=overlaps,existing_mapping_covers_mdp=bool(coverage),proposed_page_length=hex((length+4095)&~4095),mapping_applied=False,runtime_mmio_reads=False,decision='R-004 required before extending the fixed memory map')
 (ROOT/'reports/enuma-display-mmio-coverage.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 assert not overlaps,'Review changed memory table before using the proposal'
 print('PASS: MDP window is absent, proposed page-aligned window does not overlap existing entries; no map changed')
if __name__=='__main__':main()
