"""Reviewed v14 final ARM64 context/guard sequences, with deletion negatives."""
def check(p):
 def calls(name,dest,count):
  hits=p.calls(name,dest)
  if len(hits)!=count:raise ValueError(name+' calls '+dest+' count differs')
  for i,a in enumerate(hits):p.mark(a,name+'->'+dest+str(i))
  return hits
 def address(name,adr_off,add_off,reg,expected):
  a=p.sym(name)+adr_off;w=p.word(a);v=p.word(p.sym(name)+add_off)
  if w&0x9f00001f!=0x90000000|reg or v&0xffc003ff!=0x91000000|(reg<<5)|reg:
   raise ValueError('context ADRP/ADD changed')
  imm=((w>>5)&0x7ffff)*4+((w>>29)&3)
  if imm&(1<<20):imm-=1<<21
  if (a&~4095)+(imm<<12)+((v>>10)&4095)!=expected:raise ValueError('context record address differs')
  p.mark(a,name+':address'+str(adr_off));p.mark(p.sym(name)+add_off,name+':address'+str(add_off))
 calls('CommonCExceptionHandler','EnumaUnhandledExceptionCheckpoint',1)
 p.seq('CommonCExceptionHandler',{0xc:0xf1000c1f,0x10:0x54000108,0x1c:0xf8607902,
  0x20:0xb40002a2,0x2c:0xd61f0040,0x30:0xa90003e1,0x70:0xa94003e1})
 p.call('CommonCExceptionHandler',0x74,'EnumaUnhandledExceptionCheckpoint')
 n='EnumaUnhandledExceptionCheckpoint'
 snapshot=calls(n,'ExSnapshot',1)[0];capture=calls(n,'ExContextCapture',1)[0]
 present=calls(n,'ExPresent',6);owner=calls(n,'ExFindOwner',1)[0]
 if not snapshot<capture<present[0]<owner<present[1] or present!=sorted(present):raise ValueError('context capture/page ordering changed')
 for dest in ('EnumaOemClockExit','ResetCold','CpuPause'):calls(n,dest,1)
 p.seq(n,{0x14:0x34000089,0x20:0x17ffffff,0x24:0x52800029,0x2c:0xd5034fdf,
  0x30:0xf90007e1,0x38:0x72001c1f,0x3c:0x54000380,0x40:0xf94007e0,
  0x48:0x52800020,0x50:0x72001c1f,0x54:0x540002c0,0x64:0x52800040,
  0x6c:0x72001c1f,0x70:0x540001e0,0x74:0x52800060,0x7c:0x72001c1f,
  0x80:0x54000160,0x84:0x52800080,0x8c:0x72001c1f,0x90:0x540000e0,
  0x94:0x528000a0,0x9c:0x72001c1f,0xa0:0x54000060,0xa4:0x528000c0})
 for off,w in ((0x10,0x39400109),(0x28,0x39000109)):
  a=p.sym(n)+off
  if p.word(a)&0xffc003ff!=w:raise ValueError('context recursion latch absent')
  p.mark(a,'context_latch_'+str(off))
 # Original saved exception context; zero the extended record before capture.
 p.seq('ExSnapshot',{0x10:0xaa0003f4,0x18:0xf1000e9f,0x1c:0x540002c8,
  0x20:0xaa0103f3,0x24:0xb4000281,0x2c:0x2a1f03e1,0x34:0x52801402,
  0x38:0x9100e2a0,0x40:0xf9418e69,0x48:0xf941926a,0x4c:0xf9418268,
  0x50:0xf9407a6b,0x54:0xa9012aa9,0x60:0xa90022b4,0x64:0xf9418668,
  0x6c:0xa90222ab,0x70:0xf9001aa9})
 address('ExSnapshot',0x28,0x30,21,p.sym('mExRecord'))
 calls('ExSnapshot','.weak.memset.default._ModuleEntryPoint',1)
 # This session compiles as MOVN + two MOVKs (top 16 bits are all ones).
 session=0
 for off,opcode,shift in ((0x58,0x92800009,0),(0x5c,0xf2a00009,16),(0x68,0xf2c00009,32)):
  a=p.sym('ExSnapshot')+off;w=p.word(a)
  if w&0xffe0001f!=opcode:raise ValueError('context session materialization changed')
  value=((w>>5)&65535)<<shift
  session=(~value)&((1<<64)-1) if off==0x58 else (session&~(65535<<shift))|value
  p.mark(a,'context_session_'+str(shift))
 p.exception_session=session
 n='ExContextCapture'
 # Registers are loaded from EFI_SYSTEM_CONTEXT, not clobbered live registers.
 p.seq(n,{4:0xf9400009,0xc:0xa94a2c0a,0x10:0xf9000109,0x14:0xf9402009,
  0x18:0xf9000509,0x1c:0xf9402409,0x20:0xf9000909,0x24:0xf9402809,
  0x28:0xa901a909,0x2c:0xd5384249,0x30:0xf100113f,0x34:0xa902a50b,
  0x38:0x540003a1,0x40:0xd5382009,0x44:0xd538202a,0x48:0xd5382048,
  0x4c:0xd538100b,0x54:0xa9002989,0x58:0xa9012d88,0x5c:0x3600028b,
  0x60:0x92590508,0x64:0xb5000248,0x6c:0xd5387409,0x74:0xf940010a,
  0x78:0xd508780a,0x7c:0xd5033fdf,0x80:0xd538740a,0x84:0xf900550a,
  0x88:0xf940010b,0x8c:0xd508782b,0x90:0xd5033fdf,0x94:0xd538740a,
  0x98:0xf900590a,0x9c:0xd5187409,0xa0:0xd5033fdf,0xa4:0x52800029,
  0xa8:0xf9005d09,0xac:0xd65f03c0})
 for adr,add,reg,offset in ((0,8,8,104),(0x3c,0x50,12,160),(0x68,0x70,8,24)):
  address(n,adr,add,reg,p.sym('mExRecord')+offset)
 for a in p.region(n):
  if p.word(a)&0xfc000000==0x94000000 or p.word(a)&0xfffffc1f in (0xd63f0000,0xd61f0000):raise ValueError('context capture calls out')
 p.seq('ExMapped',{0x24:0xd5384248,0x60:0xd5382049,0xf0:0xd5087815,
  0xf4:0xd5033fdf,0xf8:0xd5387408,0xfc:0x37000308,0x100:0x92749d09,
  0x104:0xeb0902bf,0x108:0x540002a1,0x150:0xd5187414,0x15c:0xd5187414})
 p.seq('EnumaOemClockExit',{8:0x52909000,0xc:0x72a003c0,0x1c:0x17ffffff})
 for off,dest in ((0x10,'MicroSecondDelay'),(0x14,'ResetCold'),(0x18,'CpuPause')):p.call('EnumaOemClockExit',off,dest)
 p.seq('ExHold',{0x10:0x52812008,0x14:0x72a007a8,0x18:0x6b08003f,0x1c:0x54000121,0x28:0x370000c9,0x2c:0x52812000,0x34:0x72a007a0})
 p.call('ExHold',0x3c,'MicroSecondDelay')
 calls('ExReadMeta','ExMapped',1);calls('ExPresent','ExPage',1)
 bad={'AsciiSPrint','UnicodeSPrintAsciiFormat','SerialPortWrite','CoreAllocatePool','CoreGetMemoryMap','CoreLocateProtocol','CoreHandleProtocol'}
 bad_addresses={a for a,n in p.entries if n in bad}
 for n in ('EnumaUnhandledExceptionCheckpoint','ExSnapshot','ExContextCapture','ExFindOwner','ExReadMeta','ExPage','ExMapped'):
  if any(p.target(a) in bad_addresses for a in p.region(n)):raise ValueError('unsafe context dependency '+n)
