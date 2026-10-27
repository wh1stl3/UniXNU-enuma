"""Reviewed v8 linked event delivery before RestoreTPL; mutation checks in caller."""
import re,struct
from prepare_enuma_mmu_experiment import file_offset
from check_oem_far_code import check_far
from check_oem_early_code import data_offset

def check_event(pe,mapping):
 entries=[(int(a,16),n) for a,n in re.findall(r'^([0-9a-f]+)\s+00000000\s+0\s+(\S+)$',mapping,re.M)]
 def sym(n):
  hits={a for a,name in entries if name==n}
  if len(hits)!=1:raise ValueError('missing event symbol '+n)
  return hits.pop()
 def word(a):return struct.unpack_from('<I',pe,file_offset(pe,a))[0]
 def target(a):
  w=word(a)
  if w&0x7c000000!=0x14000000:return None
  v=w&0x3ffffff;return a+4*(v-0x4000000 if v&0x2000000 else v)
 def region(n):
  start=sym(n);return range(start,min(a for a,_ in entries if a>start),4)
 sites=check_far(pe,mapping,True)
 def seq(n,base,expected):
  start=sym(n)
  for a,w in expected.items():
   off=a-base
   if word(start+off)!=w:raise ValueError(n+' event instruction differs '+hex(off))
   sites[n+'_'+hex(off)]=start+off
 sync=sym('EnumaOemCoreSyncSystemTable')
 seq('EnumaOemCoreSyncSystemTable',0,{0x10:0xb40002c8,0x1c:0x34000269,0x24:0xf9450d29,
  0x28:0xeb00013f,0x2c:0x54000221,0x34:0xf9403809,0x3c:0x91004102,0x40:0x52800f01,
  0x48:0xf9003149,0x4c:0xf9403409,0x50:0xaa0803e0,0x54:0xb900015f,0x58:0xf940ad6b,
  0x5c:0xf9002d49,0x60:0xd63f0160,0x64:0xb7f80060})
 if target(sync+0x74)!=sym('OemCaptureTerminal'):raise ValueError('sync not terminal')
 sites['sync_terminal']=sync+0x74
 calls=[a for a in region('CoreInstallConfigurationTable') if target(a)==sync]
 if len(calls)!=2:raise ValueError('sync publication calls missing')
 for a,n in zip(calls,['CoreFreePool','CoreNotifySignalList']):
  if target(a+8)!=sym(n):raise ValueError('sync order differs')
  sites['sync_before_'+n]=a
 if word(calls[0]-4)!=0xf9003816:raise ValueError('table not published')
 sites['sync_published']=calls[0]-4
 seq('OemProgressRecord',0x123cc,{0x123ec:0xeb00013f,0x123f0:0x7a400900,0x123f4:0x540006e1,
  0x123f8:0xf9400828,0x12400:0x3940b035,0x1240c:0xf903ed28,0x12410:0xb9402828,
  0x12414:0x7100051f,0x12418:0x54000200,0x1241c:0x7100111f,0x12420:0x54000581,
  0x12428:0x528b9909,0x1242c:0xeb09011f,0x12430:0x54000501,0x12434:0x340004f5,
  0x12440:0xb27f0109,0x12444:0xf903e689,0x12448:0xb500044a,0x1244c:0x52840049,
  0x12458:0x3940b668,0x1245c:0x340003a8,0x12464:0x5286c109,0x12468:0xeb09011f,
  0x12478:0x913d0021,0x1247c:0x52800202,0x12484:0xb40002e0,
  0x12490:0x913cc021,0x12494:0x52800202,0x1249c:0xb50001a0,
  0x124a8:0x52800409,0x124ac:0x5280020a,0x124b8:0xf903e688,0x124bc:0x340000b5,
  0x124c4:0xb5000069,0x124c8:0xb2750108,0x124cc:0xf903e688,
  0x124e8:0x52800109,0x124ec:0x5280008a,0x124f8:0xf903e688,
  0x124fc:0x34fffc75,0x12504:0xb5fffc29,0x12508:0xb2740108,0x1250c:0xf903e688})
 for a in region('OemProgressRecord'):
  if word(a)&0xfc000000==0x94000000 and target(a)!=sym('CompareMem'):raise ValueError('non-RAM observer call')
  if word(a)&0xfffffc1f in (0xd63f0000,0xd61f0000):raise ValueError('indirect observer call')
 # Record finishes this exact event, then passes its saved pointer to Recorded.
 seq('EnumaServiceRecord',0x1387c,{0x1392c:0xb9004abb,0x13934:0x390132b9,
  0x1393c:0xa9026aa9,0x13940:0xa903aeb7,0x13944:0xf9010e6a,0x13970:0xf9012528,
  0x13974:0x3909952a,0x1398c:0xf9512662,0x13990:0xb4000162,
  0x13994:0xf94007e1,0x13998:0xaa1303e0,0x139b8:0xd61f0040})
 # Actual record calls occur after RaiseTPL(HIGH_LEVEL), before RestoreTPL.
 for n,base,raise_a,record_a,restore_a in [('EnumaServiceBegin',0x136d8,0x1371c,0x1375c,0x1376c),('EnumaServiceEnd',0x137a4,0x137ec,0x1381c,0x13834)]:
  start=sym(n);a=start+record_a-base
  if target(a)!=sym('EnumaServiceRecord'):raise ValueError('event record delivery missing')
  sites[n+'_record']=a
  for address,value in [(raise_a,0xd63f0100),(restore_a,0xd63f0100)]:
   at=start+address-base
   if word(at)!=value:raise ValueError('TPL call differs')
   sites[n+'_'+hex(address-base)]=at
 seq('EnumaServiceBegin',0x136d8,{0x13700:0x528003e0,0x13718:0xf9400d28,0x13768:0xf9401108})
 seq('EnumaServiceEnd',0x137a4,{0x137c8:0x528003e0,0x137e8:0xf9400d08,0x13830:0xf9401108})
 # Compiler inlined Arm into CoreStartImage; bind exact callback address/store.
 # Derive from the unique reviewed store, avoiding assumptions about function entry.
 stores=[a for a in region('CoreStartImage') if word(a)==0xf9112769]
 if len(stores)!=1:raise ValueError('Recorded hook not installed')
 store=stores[0];adr=store-24;add=store-12;w=word(adr);v=word(add)
 if w&0x9f00001f!=0x90000009 or v&0xffc003ff!=0x91000129:raise ValueError('event hook address sequence differs')
 imm=((w>>5)&0x7ffff)*4+((w>>29)&3)
 if imm&(1<<20):imm-=1<<21
 address=(adr&~0xfff)+(imm<<12)+((v>>10)&0xfff)
 if address!=sym('OemProgressRecord'):raise ValueError('wrong Recorded function')
 for a in [adr,add,store]:sites['event_hook_'+hex(a-store)]=a
 if any(n in ('OemProgressObserve','OemProgressBefore','OemProgressAfter') for _,n in entries):raise ValueError('old tail observer retained')
 guid=sym('OemProgressRecord.Sid');off=data_offset(pe,guid)
 if pe[off:off+16]!=bytes.fromhex('b4d3b654335d914f86006c41d5deb19a'):raise ValueError('SID GUID differs')
 return sites,guid
