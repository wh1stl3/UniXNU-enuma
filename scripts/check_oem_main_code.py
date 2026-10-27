"""Reviewed v6 linked main query, entry-only rendering and real status paths."""
import re,struct
from prepare_enuma_mmu_experiment import file_offset
from map_oem_trace_rva import sections

def check_main(pe,mapping):
 entries=[(int(a,16),n) for a,n in re.findall(r'^([0-9a-f]+)\s+00000000\s+0\s+(\S+)$',mapping,re.M)]
 def sym(n):
  hits={a for a,name in entries if name==n}
  if len(hits)!=1:raise ValueError('missing main code symbol '+n)
  return hits.pop()
 def word(a):return struct.unpack_from('<I',pe,file_offset(pe,a))[0]
 def target(a):
  w=word(a)
  if w&0x7c000000!=0x14000000:return None
  x=w&0x3ffffff
  return a+4*(x-0x4000000 if x&0x2000000 else x)
 sites={}
 def sequence(name,expected,reviewed_start):
  start=sym(name)
  for address,value in expected.items():
   off=address-reviewed_start
   if word(start+off)!=value:raise ValueError(name+' reviewed instruction differs at '+hex(off))
   sites[name+'_'+hex(off)]=start+off
  return start
 obs=sequence('OemProgressObserve',{
  0x12530:0x7100051f,0x12534:0x540003e1,0x1253c:0x5286c109,0x12540:0xf9403108,
  0x12544:0xeb09011f,0x12548:0x54000341,0x1254c:0xf1001a9f,0x12550:0x54000643,
  0x12558:0x3941f509,0x1255c:0x340005e9,0x12560:0xb0000081,0x12564:0x91020100,
  0x12568:0x913cc021,0x1256c:0x52800202,0x12574:0xb5000520,0x12578:0x34000156,
  0x12584:0x39400109,0x12588:0x36080489,0x1258c:0x39401908,0x12590:0x35000448,
  0x12594:0x52800028,0x12598:0x39287b68,0x1259c:0x14000005,0x125a0:0x52800020,
  0x125c8:0x39687b68,0x125cc:0x34000268,0x125d0:0x34000116,0x125f0:0x52800060},0x123d0)
 for off in (0x125ac-0x123d0,0x12614-0x123d0):
  a=obs+off
  if target(a)!=sym('OemProgressEmit'):raise ValueError('entry emission target differs')
  sites['entry_emit_'+hex(off)]=a
 # All observer emissions have reviewed phase1/phase3 arguments; returned
 # service events take the latch/return branch instead of drawing phase2/4.
 end=min(a for a,n in entries if a>obs)
 if [a for a in range(obs,end,4) if target(a)==sym('OemProgressEmit')]!=[obs+0x1dc,obs+0x244]:raise ValueError('unexpected observer emission')
 sequence('OemProgressPresent',{0x12170:0x7100093f,0x12174:0x54000a48,0x12194:0x5280054b,
  0x12198:0x1ad5214a,0x1219c:0x6a0b015f,0x121a0:0x540008e0},0x12140)
 loc=sequence('EnumaTraceLocateProtocol',{0x11e98:0xaa1503e0,0x11e9c:0xaa1603e1,
  0x11ea0:0xaa1403e2,0x11ea8:0xf940a108,0x11eac:0xd63f0100,0x11eb0:0xaa0003f4,
  0x11ec8:0xaa1403e5,0x11ed0:0xaa1403e0},0x11e30)
 for off,name in ((0x5c,'EnumaServiceBegin'),(0x9c,'EnumaServiceEnd')):
  a=loc+off
  if target(a)!=sym(name):raise ValueError('real locate trace order differs')
  sites['locate_'+name]=a
 returned=sequence('OemProgressReturned',{0x11d0c:0xaa0003f3,0x11d24:0xf90013f3,
  0x11d34:0x3900b3e9,0x11d68:0x528000a0},0x11ce4)
 if target(returned+0x8c)!=sym('OemProgressEmit'):raise ValueError('real Core result emission missing')
 sites['actual_core_emit']=returned+0x8c
 # Registration remains a transparent observer; source/table synchronization
 # is checked by the shared sync audit and real Core host tests.
 reg=sym('EnumaTraceInstallConfigurationTable')
 for off,value in {0x24:0x528b990a,0x58:0xf9406102,0xc0:0xf9406108,
                   0xc4:0xd63f0100,0xc8:0xaa0003f3,0xe8:0xaa1303e0}.items():
  if word(reg+off)!=value:raise ValueError('registration forwarding differs')
  sites['registration_'+hex(off)]=reg+off
 main=sym('OemProgressObserve.Main')
 s=next(s for s in sections(pe) if s[1]<=main< s[1]+s[2]);off=s[3]+main-s[1]
 if pe[off:off+16]!=bytes.fromhex('690476b00c977a48a4b528db7b45cef1'):raise ValueError('ChipInfo GUID differs')
 return sites
