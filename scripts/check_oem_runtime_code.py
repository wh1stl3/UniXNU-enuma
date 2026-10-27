"""Audit bounded linked instruction sequences; not a whole-program proof."""
import re,struct
from prepare_enuma_mmu_experiment import file_offset
from map_oem_trace_rva import map_return

def check_exception(pe,mapping):
    def symbol(n):
        hits={int(a,16) for a in re.findall(r'^([0-9a-f]+)\s+00000000\s+0\s+'+n+r'$',mapping,re.M)}
        if len(hits)!=1:raise ValueError('missing exception symbol '+n)
        return hits.pop()
    start=symbol('DumpCpuContext')
    for off,n in [(8,'ResetCold'),(12,'CpuPause')]:
        if map_return(pe,start+off+4).get('static_target_rva')!=hex(symbol(n)):raise ValueError('CPU exception terminal differs')
    if struct.unpack_from('<I',pe,file_offset(pe,start+16))[0]!=0x17ffffff:raise ValueError('CPU exception loop missing')
    return start

def check(pe,mapping):
    entries=[(int(a,16),n) for a,n in re.findall(r'^([0-9a-f]+)\s+00000000\s+0\s+(\S+)$',mapping,re.M)]
    def sym(n):
        hits={a for a,name in entries if name==n}
        if len(hits)!=1:raise ValueError('ambiguous symbol '+n)
        return hits.pop()
    def word(a):return struct.unpack_from('<I',pe,file_offset(pe,a))[0]
    def target(a):
        w=word(a)
        if w&0x7c000000!=0x14000000:return None
        x=w&0x3ffffff
        if x&0x2000000:x-=0x4000000
        return a+4*x
    def region(n):
        start=sym(n);end=min(a for a,_ in entries if a>start)
        return range(start,end,4)
    def calls(n,dest):return [a for a in region(n) if target(a)==sym(dest)]
    sites={}
    def unique(name,hits):
        if len(hits)!=1:raise ValueError('missing/ambiguous runtime sequence '+name)
        sites[name]=hits[0];return hits[0]
    dispatch=unique('dispatcher',calls('DxeMain','CoreDispatcher'))
    # The dispatcher runs BEFORE the completion fallback, unlike stage10.
    for off,name in [(12,'MicroSecondDelay'),(16,'ResetCold'),(20,'CpuDeadLoop')]:
        if target(dispatch+off)!=sym(name):raise ValueError('completion fallback missing')
        sites['completion_'+name]=dispatch+off
    if word(dispatch+4)!=0x5299f800 or word(dispatch+8)!=0x72a00d40:raise ValueError('fallback delay differs from 7s')
    detail=unique('target_delay',calls('EnumaDispatchDetailCheckpoint','MicroSecondDelay'))
    if word(detail-8)!=0x52909000 or word(detail-4)!=0x72a003c0:raise ValueError('target delay differs from 2s')
    if target(detail+4)!=sym('ResetCold') or target(detail+16)!=sym('CpuDeadLoop'):raise ValueError('target stop missing')
    sites['target_reset']=detail+4;sites['target_loop']=detail+16
    # Identical code folding may alias the capture terminal and exception entry.
    for name in ('OemCaptureTerminal','DumpCpuContext'):
        start=sym(name)
        if target(start+8)!=sym('ResetCold') or target(start+12)!=sym('CpuPause') or word(start+16)!=0x17ffffff:
            raise ValueError('exception/capture terminal missing')
        sites[name+'_reset']=start+8;sites[name+'_pause']=start+12;sites[name+'_loop']=start+16
    unique('capture_stop',calls('OemRuntimeBeforeForward','EnumaCaptureStop'))
    unique('capture_terminal',calls('OemRuntimeBeforeForward','OemCaptureTerminal'))
    for name,mask,w in [('bsp',0xffffffe0,0xd53800a0),('save_daif',0xffffffe0,0xd53b4220),
                         ('mask_daif',0xffffffff,0xd5034fdf),('restore_daif',0xffffffe0,0xd51b4220)]:
        unique(name,[a for a in region('OemBoardSink') if word(a)&mask==w])
    if not sites['bsp']<sites['save_daif']<sites['mask_daif']<sites['restore_daif']:raise ValueError('interrupt sequence ordering')
    unique('hold_direct_timer',calls('OemHold','MicroSecondDelay'))
    return sites

def verify_with_deletions(pe,mapping):
    sites=check(pe,mapping)
    for name,a in sites.items():
        offset=file_offset(pe,a);mutated=pe[:offset]+bytes.fromhex('1f2003d5')+pe[offset+4:]
        try:check(mutated,mapping)
        except ValueError:pass
        else:raise ValueError('removed instruction admitted: '+name)
    return dict(sites={n:hex(a) for n,a in sites.items()},deletion_checks=len(sites),
                scope='selected instruction sequences only; GUID predicates additionally source/flags bound; no physical recovery guarantee')
