"""Reviewed late DXE scope: no OEM-side display, real status and one summary."""
import re,struct
from prepare_enuma_mmu_experiment import file_offset
from map_oem_trace_rva import sections

def check_far(pe,mapping,event=False):
 entries=[(int(a,16),n) for a,n in re.findall(r'^([0-9a-f]+)\s+00000000\s+0\s+(\S+)$',mapping,re.M)]
 def sym(name):
  hits={a for a,n in entries if n==name}
  if len(hits)!=1:raise ValueError('missing far symbol '+name)
  return hits.pop()
 def word(a):return struct.unpack_from('<I',pe,file_offset(pe,a))[0]
 def target(a):
  w=word(a)
  if w&0x7c000000!=0x14000000:return None
  v=w&0x3ffffff;return a+4*(v-0x4000000 if v&0x2000000 else v)
 def region(name):
  start=sym(name);return range(start,min(a for a,n in entries if a>start),4)
 sites={}
 def sequence(name,reviewed,expected):
  start=sym(name)
  for address,value in expected.items():
   off=address-reviewed
   if word(start+off)!=value:raise ValueError(name+' far instruction differs '+hex(off))
   sites[name+'_'+hex(off)]=start+off
  return start
 sequence('DxeMain',0x2c84,{}) # DxeMain-relative sites below bind from actual dispatcher call
 calls=[a for a in region('DxeMain') if target(a)==sym('CoreDispatcher')]
 if len(calls)!=1:raise ValueError('dispatch call differs')
 base=calls[0]
 for address,value in {0x3bbc:0xf943d908,0x3bc0:0xb40003e8,0x3bc8:0x395f2108,0x3bcc:0x36300388,
  0x3bdc:0x910b4000,0x3be0:0xd10183a2,0x3be4:0xaa1f03e1,0x3bec:0xf940a108,0x3bf0:0xd63f0100,
  0x3bf8:0xf9402109,0x3bfc:0xf85a03a8,0x3c08:0xf100001f,0x3c18:0x0a0a0120,
  0x3c1c:0x7100041f,0x3c20:0x540000a1,0x3c24:0xf9400d08,0x3c2c:0x1a9f07e1}.items():
  a=base+address-0x3bb0
  if word(a)!=value:raise ValueError('inlined far availability probe differs '+hex(address-0x3bb0))
  sites['far_probe_'+hex(address-0x3bb0)]=a
 finish=sequence('OemProgressFarFinish',0x11cc0,{0x11cdc:0xb4000568,0x11ce4:0x35000528,
  0x11cf0:0x363004c8,0x11cf8:0x52803009,0x11cfc:0x5280100a,0x11d04:0x9a890149,
  0x11d14:0xb2770109,0x11d18:0x9a890108,0x11d20:0xb2760109,0x11d24:0x9a890108,
  0x11d28:0xf9000e88,0x11d30:0xa942228b,0x11d40:0xf9400e8c,0x11d44:0x3900b3e9,
  0x11d4c:0xa901afec,0x11d50:0x9280000b,0x11d58:0xa900a3eb,0x11d60:0xf90003ea})
 if target(finish+0xc4)!=sym('OemProgressEmit'):raise ValueError('late summary emission missing')
 sites['far_emit']=finish+0xc4
 sequence('OemProgressReturned',0x11ed4,{0x11ee0:0xb4000109,0x11ee8:0x350000c8,
  0x11ef8:0xb27a0129,0x11efc:0xa9000109,0x11f00:0xd65f03c0})
 if not event:
  sequence('OemProgressObserve',0x12404,{0x12508:0xf9001708,0x12510:0x7100113f,
   0x12518:0x340005d4,0x1251c:0x528b9909,0x12520:0xeb09011f,0x12524:0x54000561,
   0x12530:0xb27f010a,0x12538:0xf9000f0a,0x1253c:0xb50004a9,0x12540:0x52840049,
   0x12558:0x5286c109,0x1255c:0xeb09011f,0x12570:0x913d0021,0x1257c:0xb4000360,
   0x1258c:0x913cc021,0x12598:0xb50001c0,0x125a4:0x52800409,0x125a8:0x5280020a,
   0x125b8:0x340000d4,0x125c4:0xb5000069,0x125c8:0xb2750108,
   0x125f0:0x52800109,0x125f4:0x5280008a,0x12604:0x34fffbf4,0x12610:0xb5fffb89,0x12614:0xb2740108})
 for name in (['OemProgressRecord','OemProgressReturned'] if event else ['OemProgressObserve','OemProgressReturned']):
  if any(target(a) in [sym('OemProgressEmit'),sym('OemProgressPresent')] for a in region(name)):raise ValueError('early display reintroduced')
 sequence('OemProgressPresent',0x12214,{0x12224:0x7100141f,0x12228:0x54000841,
  0x12238:0x39559109,0x1223c:0x350007a9,0x12258:0x5280002a,0x12260:0x3915910a,
  0x1234c:0x528000a1,0x1236c:0xf9400e61,0x1239c:0xf9400a61,0x123ac:0xf9401261})
 sequence('EnumaDispatchDetailCheckpoint',0xfe58,{0xff38:0xf9001162,0xff3c:0xb9002960,
  0xffa8:0xa940fbfd,0xffac:0xf84207f3,0xffb0:0xd65f03c0})
 for a in region('EnumaDispatchDetailCheckpoint'):
  if target(a) in [sym('ResetCold'),sym('MicroSecondDelay'),sym('CpuDeadLoop')]:raise ValueError('target early terminal reintroduced')
 emit=sequence('OemProgressEmit',0x11d98,{0x11db8:0xf100103f,0x11dbc:0x540002c1,
  0x11dc8:0x37280269,0x11de0:0x528000a0,0x11df8:0xd63f0180,0x11e00:0x540000a0})
 for name,expected in [(('OemProgressRecord.Main' if event else 'OemProgressObserve.Main'),'690476b00c977a48a4b528db7b45cef1'),
                       ('EnumaOemFarDispatchComplete.Guid','dea94290dc23384a96fb7aded080516a')]:
  address=sym(name);section=next(s for s in sections(pe) if s[1]<=address<section_end(s))
  off=section[3]+address-section[1]
  if pe[off:off+16]!=bytes.fromhex(expected):raise ValueError('far GUID differs '+name)
 return sites

def section_end(s):return s[1]+s[2]
