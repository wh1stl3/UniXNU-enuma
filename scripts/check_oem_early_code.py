"""Review-bound ARM64 sync and early-call sequences, with deletion negatives."""
import re,struct
from prepare_enuma_mmu_experiment import file_offset
from map_oem_trace_rva import sections

def data_offset(pe,rva):
    hits=[s for s in sections(pe) if s[1]<=rva and rva+16<=s[1]+s[2]]
    if len(hits)!=1:raise ValueError('GUID is not uniquely file-backed')
    s=hits[0]
    return s[3]+rva-s[1]

def check(pe,mapping):
    entries=[(int(a,16),n) for a,n in re.findall(r'^([0-9a-f]+)\s+00000000\s+0\s+(\S+)$',mapping,re.M)]
    def sym(n):
        hits={a for a,name in entries if name==n}
        if len(hits)!=1:raise ValueError('missing sync symbol '+n)
        return hits.pop()
    def word(a):return struct.unpack_from('<I',pe,file_offset(pe,a))[0]
    def target(a):
        w=word(a)
        if w&0xfc000000!=0x94000000:return None
        x=w&0x3ffffff
        return a+4*(x-0x4000000 if x&0x2000000 else x)
    def region(n):
        start=sym(n);return range(start,min(a for a,_ in entries if a>start),4)
    start=sym('EnumaOemCoreSyncSystemTable');sites={}
    # Reviewed build: active/publication gates, source identity, pointer/count,
    # CRC arguments/reset/call and actual error branch to terminal callback.
    expected={0x10:0xb40002c8,0x1c:0x34000269,0x24:0xf944d529,
              0x28:0xeb00013f,0x2c:0x54000221,0x34:0xf9403809,
              0x3c:0x91004102,0x40:0x52800f01,0x48:0xf9003149,
              0x4c:0xf9403409,0x50:0xaa0803e0,0x54:0xb900015f,
              0x58:0xf940ad6b,0x5c:0xf9002d49,0x60:0xd63f0160,
              0x64:0xb7f80060}
    for off,w in expected.items():
        if word(start+off)!=w:raise ValueError('sync instruction differs: '+hex(off))
        sites['sync_'+hex(off)]=start+off
    if target(start+0x74)!=sym('OemCaptureTerminal'):raise ValueError('sync failure not terminal')
    sites['sync_terminal']=start+0x74
    calls=[a for a in region('CoreInstallConfigurationTable') if target(a)==start]
    if len(calls)!=2:raise ValueError('sync publication sites missing')
    for a,name in zip(calls,('CoreFreePool','CoreNotifySignalList')):
        if target(a+8)!=sym(name):raise ValueError('sync ordering differs: '+name)
        sites['before_'+name]=a
    if word(calls[0]-4)!=0xf9003816:raise ValueError('new table not published before sync')
    sites['publish_new_table']=calls[0]-4
    selects=[a for a in region('OemProgressObserve') if word(a)==0xf100069f]
    if len(selects)!=1:raise ValueError('call1 selector missing')
    a=selects[0]
    if word(a+4)!=0x540001e1 or target(a+0x38)!=sym('OemProgressEmit'):
        raise ValueError('call1 branch/emission changed')
    sites['call1_compare']=a;sites['call1_branch']=a+4;sites['call1_emit']=a+0x38
    guid=sym('OemProgressObserve.Sid');off=data_offset(pe,guid)
    if pe[off:off+16]!=bytes.fromhex('e72b06b50b17324abe21689262ff4399'):
        raise ValueError('early Kernel GUID differs')
    return sites,guid

def verify(pe,mapping):
    sites,guid=check(pe,mapping)
    for name,a in sites.items():
        off=file_offset(pe,a);mutated=pe[:off]+bytes.fromhex('1f2003d5')+pe[off+4:]
        try:check(mutated,mapping)
        except ValueError:pass
        else:raise ValueError('deleted early instruction accepted: '+name)
    off=data_offset(pe,guid);mutated=bytearray(pe);mutated[off]^=1
    try:check(mutated,mapping)
    except ValueError:pass
    else:raise ValueError('changed Kernel GUID accepted')
    return dict(sites={n:hex(a) for n,a in sites.items()},kernel_guid_rva=hex(guid),
                deletion_checks=len(sites),guid_mutation_checks=1,
                scope='selected linked instruction sequences; not whole-program or hardware proof')
