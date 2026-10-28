"""Selected final CPU exception edges and real context loads; deletion negatives."""
def check_cpu(p):
 def calls(name,dest,count):
  hits=p.calls(name,dest)
  if len(hits)!=count:raise ValueError(name+' calls '+dest+' count differs')
  for i,a in enumerate(hits):p.mark(a,name+'->'+dest+str(i))
  return hits
 calls('CommonCExceptionHandler','EnumaUnhandledExceptionCheckpoint',1)
 # No-registered-handler branch preserves x0 type/x1 context; unknown-type
 # diagnostics save and restore both before entering the same default edge.
 p.seq('CommonCExceptionHandler',{0xc:0xf1000c1f,0x10:0x54000108,
     0x1c:0xf8607902,0x20:0xb40002a2,0x2c:0xd61f0040,0x30:0xa90003e1,0x70:0xa94003e1})
 p.call('CommonCExceptionHandler',0x74,'EnumaUnhandledExceptionCheckpoint')
 calls('EnumaUnhandledExceptionCheckpoint','ExSnapshot',1)
 present=calls('EnumaUnhandledExceptionCheckpoint','ExPresent',3)
 owner=calls('EnumaUnhandledExceptionCheckpoint','ExFindOwner',1)[0]
 if not present[0]<owner<present[1]<present[2]:raise ValueError('raw first / optional owner / pages ordering changed')
 calls('EnumaUnhandledExceptionCheckpoint','EnumaOemClockExit',1)
 calls('EnumaUnhandledExceptionCheckpoint','ResetCold',1)
 calls('EnumaUnhandledExceptionCheckpoint','CpuPause',1)
 p.seq('EnumaUnhandledExceptionCheckpoint',{0x10:0x34000089,0x1c:0x17ffffff,
     0x20:0x52800029,0x28:0xd5034fdf,0x30:0x72001c1f,0x34:0x540001c0,
     0x38:0x52800020,0x40:0x72001c1f,0x44:0x54000140,0x54:0x52800040,
     0x5c:0x72001c1f,0x60:0x54000060,0x64:0x52800060})
 # Actual ARM64 EFI_SYSTEM_CONTEXT_AARCH64 offsets, not live ESR/FAR reads.
 p.seq('ExSnapshot',{0x14:0xf9418028,0x1c:0xf9418c2a,0x20:0xf941902b,
                     0x24:0xf941842c,0x28:0xa9002120,0x2c:0xf9407828,0x30:0xa9012d2a,
                     0x44:0xa9023128,0x58:0xf900192a})
 session=0
 for off,opcode,shift in ((0x34,0xd280000a,0),(0x38,0xf2a0000a,16),(0x40,0xf2c0000a,32),(0x48,0xf2e0000a,48)):
  a=p.sym('ExSnapshot')+off;w=p.word(a)
  if w&0xffe0001f!=opcode:raise ValueError('exception session materialization changed')
  session|=((w>>5)&0xffff)<<shift;p.mark(a,'exception_session_'+str(shift))
 p.exception_session=session
 # Require exact cached-state access opcodes with relocated offsets ignored.
 base=p.sym('EnumaUnhandledExceptionCheckpoint')
 for off,w in ((0xc,0x39400109),(0x24,0x39000109)):
  if p.word(base+off)&0xffc003ff!=w:raise ValueError('recursion latch absent')
  p.mark(base+off,'exception_latch_'+str(off))
 p.seq('ExMapped',{0x24:0xd5384248,0x60:0xd5382049,0xf0:0xd5087815,
     0xf4:0xd5033fdf,0xf8:0xd5387408,0xfc:0x37000308,0x100:0x92749d09,
     0x104:0xeb0902bf,0x108:0x540002a1,0x150:0xd5187414,0x15c:0xd5187414})
 p.seq('EnumaOemClockExit',{8:0x52909000,0xc:0x72a003c0,0x1c:0x17ffffff})
 for off,n in ((0x10,'MicroSecondDelay'),(0x14,'ResetCold'),(0x18,'CpuPause')):p.call('EnumaOemClockExit',off,n)
 calls('ExReadMeta','ExMapped',1)
 calls('ExPresent','ExPage',1)
 # No dangerous formatter/protocol/allocator calls on these numeric paths.
 bad={'AsciiSPrint','UnicodeSPrintAsciiFormat','SerialPortWrite','CoreAllocatePool','CoreGetMemoryMap','CoreLocateProtocol','CoreHandleProtocol'}
 bad_addresses={a for a,n in p.entries if n in bad}
 for name in ('EnumaUnhandledExceptionCheckpoint','ExSnapshot','ExFindOwner','ExReadMeta','ExPage','ExMapped'):
  for a in p.region(name):
   if p.target(a) in bad_addresses:raise ValueError('unsafe exception dependency in '+name)
