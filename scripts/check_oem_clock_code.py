"""Selected linked v9 timer, true-return and exception paths; not whole-program proof."""
import re
import struct
from prepare_enuma_mmu_experiment import file_offset


class Image:
    def __init__(self, pe, mapping):
        self.pe = pe
        self.entries = [(int(a, 16), n) for a, n in re.findall(
            r'^([0-9a-f]+)\s+00000000\s+0\s+(\S+)$', mapping, re.M)]
        self.sites = {}

    def sym(self, name):
        hits = {a for a, n in self.entries if n == name}
        if len(hits) != 1:
            raise ValueError('missing/ambiguous clock symbol ' + name)
        return hits.pop()

    def word(self, a):
        return struct.unpack_from('<I', self.pe, file_offset(self.pe, a))[0]

    def target(self, a):
        w = self.word(a)
        if w & 0x7c000000 != 0x14000000:
            return None
        v = w & 0x3ffffff
        return a + 4 * (v - 0x4000000 if v & 0x2000000 else v)

    def region(self, name):
        a = self.sym(name)
        return range(a, min(b for b, _ in self.entries if b > a), 4)

    def calls(self, name, dest):
        return [a for a in self.region(name) if self.target(a) == self.sym(dest)]

    def mark(self, a, label):
        self.sites[label] = a

    def seq(self, name, expected):
        for off, w in expected.items():
            a = self.sym(name) + off
            if self.word(a) != w:
                raise ValueError(name + ' instruction differs at ' + hex(off))
            self.mark(a, name + ':' + hex(off))

    def call(self, name, off, dest):
        a = self.sym(name) + off
        if self.word(a) & 0xfc000000 != 0x94000000 or self.target(a) != self.sym(dest):
            raise ValueError(name + ' missing BL ' + dest)
        self.mark(a, name + ':' + hex(off))


def check(core, mapping, cpu, cpu_map, force, gop=False, exception=False):
    if force not in (0, 1, 5, 6) or (force==6 and not gop):
        raise ValueError('invalid clock force')
    c, p = Image(core, mapping), Image(cpu, cpu_map)
    for _, n in c.entries:
        if n in ('OemBoardSink', 'OemPixelRead', 'OemPixelWrite', 'OemProgressEmit',
                 'OemProgressFarFinish', 'OemProgressObserve', 'OemProgressBefore', 'OemProgressAfter'):
            raise ValueError('legacy display/tail observer retained: ' + n)
    dispatch = c.calls('DxeMain', 'CoreDispatcher')
    if len(dispatch) != 1:
        raise ValueError('actual dispatcher call missing')
    d = dispatch[0]
    c.mark(d, 'actual_dispatch')
    if c.target(d + 4) != c.sym('EnumaOemFarDispatchComplete') or c.word(d + 4) & 0xfc000000 != 0x94000000:
        raise ValueError('clock completion not immediately after dispatcher')
    c.mark(d + 4, 'dispatch_completion')
    if c.word(d + 8) != 0xd4200020:
        raise ValueError('completion no-return changed')
    c.mark(d + 8, 'dispatch_noreturn')
    if gop:
        from check_oem_gop_code import check_core
        check_core(c,force)
    elif force == 0:
        c.seq('EnumaOemFarDispatchComplete', {0xc:0x5280008b, 0x14:0xf9400109,
            0x18:0xa941a908, 0x1c:0xf100013f, 0x20:0x1a9f07e9,
            0x24:0xd3461908, 0x28:0xf100015f, 0x2c:0x1a8b156a,
            0x30:0x6a08013f, 0x34:0x52800068, 0x38:0x1a881140})
        c.call('EnumaOemFarDispatchComplete', 0x3c, 'EnumaOemClockExit')
        c.seq('EnumaOemClockExit', {8:0x52896808, 0xc:0x52872809,
            0x10:0x72a00988, 0x14:0x72bffa49, 0x18:0x1b082400, 0x28:0x17ffffff})
        for off, n in ((0x1c,'MicroSecondDelay'),(0x20,'ResetCold'),(0x24,'CpuPause')):
            c.call('EnumaOemClockExit', off, n)
        c.seq('OemCaptureTerminal', {8:0x52800040})
        c.call('OemCaptureTerminal', 0xc, 'EnumaOemClockExit')
        c.seq('EnumaOemCoreSyncSystemTable', {0x70:0x52800040})
        c.call('EnumaOemCoreSyncSystemTable', 0x74, 'EnumaOemClockExit')
    else:
        c.call('EnumaOemFarDispatchComplete', 8, 'EnumaOemClockExit')
        if c.sym('OemCaptureTerminal') != c.sym('EnumaOemFarDispatchComplete'):
            raise ValueError('forced terminal folding differs')
        c.seq('EnumaOemClockExit', {8:0x52909000 if force==1 else 0x52963000,
            0xc:0x72a003c0 if force==1 else 0x72a029e0, 0x1c:0x17ffffff})
        for off,n in ((0x10,'MicroSecondDelay'),(0x14,'ResetCold'),(0x18,'CpuPause')):
            c.call('EnumaOemClockExit', off, n)
        c.call('EnumaOemCoreSyncSystemTable', 0x70, 'EnumaOemClockExit')
    c.seq('EnumaOemCoreSyncSystemTable', {0x10:0xb40002c8,0x1c:0x34000269,
        0x24:0xf9469529,0x28:0xeb00013f,0x2c:0x54000221,0x34:0xf9403809,
        0x3c:0x91004102,0x40:0x52800f01,0x48:0xf9003149,0x4c:0xf9403409,
        0x50:0xaa0803e0,0x54:0xb900015f,0x58:0xf940ad6b,0x5c:0xf9002d49,
        0x60:0xd63f0160,0x64:0xb7f80060})
    sync = c.calls('CoreInstallConfigurationTable','EnumaOemCoreSyncSystemTable')
    if len(sync) != 2:
        raise ValueError('system table synchronization missing')
    for a,n in zip(sync,('CoreFreePool','CoreNotifySignalList')):
        if c.target(a+8) != c.sym(n):
            raise ValueError('system table synchronization ordering differs')
        c.mark(a, 'sync_before_'+n)
    if c.word(sync[0]-4) != 0xf9003816:
        raise ValueError('table publication missing')
    c.mark(sync[0]-4,'table_publication')
    started, observed = c.calls('CoreDispatcher','CoreStartImage'), c.calls('CoreDispatcher','OemProgressReturned')
    if len(started)!=1 or len(observed)!=1 or observed[0]!=started[0]+64:
        raise ValueError('true Core return gate differs')
    s,o=started[0],observed[0]
    c.mark(s,'actual_CoreStartImage');c.mark(o,'actual_Core_return')
    for off,w in {4:0xf9404348,8:0xaa0003fb,12:0xf9400a89,16:0xeb08013f,
                  32:0xf84be129,36:0xeb08013f,52:0x39400108,60:0xaa1b03e0}.items():
        if exception and off==32:continue
        if c.word(s+off)!=w:raise ValueError('true identity/status gate changed')
        c.mark(s+off,'return_gate_'+str(off))
    if exception:
        # LTO may address EnumaStartingImage relative to another data symbol.
        # Resolve the actual ADRP/ADD/LDUR target, not an old layout displacement.
        a=s+24;adr,add,ld=c.word(a),c.word(a+4),c.word(a+8)
        if adr&0x9f00001f!=0x90000009 or add&0xffc003ff!=0x91000129 or ld&0xffe00fff!=0xf8400129:
            raise ValueError('starting image identity load changed')
        imm=((adr>>5)&0x7ffff)<<2|((adr>>29)&3)
        if imm&(1<<20):imm-=1<<21
        disp=(ld>>12)&511
        if disp&256:disp-=512
        target=(a&~4095)+(imm<<12)+((add>>10)&4095)+disp
        if target!=c.sym('EnumaStartingImage'):raise ValueError('wrong starting image identity global')
        for i in range(3):c.mark(a+4*i,'starting_image_address_'+str(i))
    for off,op in ((20,0x54000001),(40,0x54000001),(56,0x34000008)):
        a=s+off;w=c.word(a);v=(w>>5)&0x7ffff
        if v&0x40000:v-=0x80000
        if w&0xff00001f!=op or a+4*v!=o+4:raise ValueError('return gate refusal changed')
        c.mark(a,'return_refusal_'+str(off))
    c.seq('OemProgressReturned',{0xc:0xb4000109,0x14:0x350000c8,
        0x24:0xb27a0129,0x28:0xa9000109,0x2c:0xd65f03c0})
    # The completed event pointer is delivered before RestoreTPL can notify.
    for name,record,raise_at,restore in (('EnumaServiceBegin',0x84,0x44,0x94),
                                       ('EnumaServiceEnd',0x78,0x48,0x90)):
        c.call(name,record,'EnumaServiceRecord')
        c.seq(name,{raise_at:0xd63f0100,restore:0xd63f0100})
    c.seq('EnumaServiceRecord',{0xb0:0xb9004abb,0xb8:0x390132b9,
        0xc0:0xa9026aa9,0xc4:0xa903aeb7,0xc8:0xf9010e6a,
        0xf4:0xf9012528,0xf8:0x3909952a,0x110:0xf9512662,
        0x114:0xb4000162,0x118:0xf94007e1,0x11c:0xaa1303e0,0x13c:0xd61f0040})
    for a in c.region('OemProgressRecord'):
        w=c.word(a)
        if w&0xfc000000==0x94000000 and c.target(a)!=c.sym('CompareMem'):
            raise ValueError('non-RAM observer call')
        if w&0xfffffc1f in (0xd63f0000,0xd61f0000):
            raise ValueError('indirect observer call')
    stores=[a for a in c.region('CoreStartImage') if c.word(a)==0xf9112769]
    if len(stores)!=1:raise ValueError('Recorded hook missing')
    store=stores[0];adr=store-24;add=store-12;w=c.word(adr);v=c.word(add)
    if w&0x9f00001f!=0x90000009 or v&0xffc003ff!=0x91000129:
        raise ValueError('Recorded hook address sequence differs')
    imm=((w>>5)&0x7ffff)*4+((w>>29)&3)
    if imm&(1<<20):imm-=1<<21
    if (adr&~0xfff)+(imm<<12)+((v>>10)&0xfff)!=c.sym('OemProgressRecord'):
        raise ValueError('wrong Recorded hook')
    for a in (adr,add,store):c.mark(a,'event_hook_'+str(a-store))
    if exception:
        from check_oem_exception_code import check_cpu
        check_cpu(p)
    else:
        # Real CPU handler default edge, including compiler-specialized delay body.
        p.seq('CommonCExceptionHandler',{0x20:0xb4000282,0x2c:0xd61f0040})
        p.call('CommonCExceptionHandler',0x70,'EnumaOemClockExit')
        for off,n in ((8,'MicroSecondDelay'),(0xc,'ResetCold'),(0x10,'CpuPause')):
            p.call('EnumaOemClockExit',off,n)
        p.seq('EnumaOemClockExit',{0x14:0x17ffffff})
        if force not in (5,6):
            p.seq('MicroSecondDelay',{8:0x52994000,0xc:0x72a77340,
                0x14:0x52994000,0x18:0x72a77340})
            p.call('MicroSecondDelay',0x10,'NanoSecondDelay')
            a=p.sym('MicroSecondDelay')+0x20
            if p.word(a)&0xfc000000!=0x14000000 or p.target(a)!=p.sym('NanoSecondDelay'):
                raise ValueError('second one-second tail delay missing')
            p.mark(a,'second_second')
        else:
            p.seq('MicroSecondDelay',{0x10:(0x529f9813 if force==6 else 0x52963013),0x14:0x52884814,0x18:0x928847f5,
                0x1c:(0x72a03373 if force==6 else 0x72a029f3),0x20:0x72a001f4,0x24:0xf2bffe15,0x28:0xeb14027f,
                0x2c:0x540000c3,0x30:0x52994000,0x34:0x8b150273,
                0x38:0x72a77340,0x40:0x17fffffa,0x50:0xd65f03c0})
            p.call('MicroSecondDelay',0x3c,'NanoSecondDelay')
    return c,p


def verify(core, mapping, cpu, cpu_map, force, gop=False, exception=False):
    c,p=check(core,mapping,cpu,cpu_map,force,gop,exception)
    for which,obj in enumerate((c,p)):
        for name,a in obj.sites.items():
            blob=bytearray(obj.pe);struct.pack_into('<I',blob,file_offset(blob,a),0xd503201f)
            try:check(bytes(blob) if which==0 else core,mapping,
                      bytes(blob) if which==1 else cpu,cpu_map,force,gop,exception)
            except ValueError:pass
            else:raise ValueError('removed clock instruction admitted: '+name)
    return dict(core_sites={n:hex(a) for n,a in c.sites.items()},
                cpu_sites={n:hex(a) for n,a in p.sites.items()},
                deletion_checks=len(c.sites)+len(p.sites),force=force,gop_mode=gop,
                exception_session=getattr(p,'exception_session',None),
                cpu_exception_rva=hex(p.sym('CommonCExceptionHandler')),
                scope='selected linked timer/return/sync/CPU-default-exception sequences only; no hardware path proof')
