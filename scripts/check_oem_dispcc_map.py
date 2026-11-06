"""Verify v12's bounded DISP_CC mapping in source and the actual linked SEC PE."""
import hashlib
import re
import struct
from map_oem_trace_rva import sections

BASE=0x0af00000
SIZE=0x20000
FAULT=0x0af022c0
LINE='  {"DISP_CC", 0xaf00000ULL, 0x20000ULL, AddDev, MMAP_IO, UNCACHEABLE, MmIO, NS_DEVICE},\n'
# EFI_MEMORY_REGION_DESCRIPTOR: fixed Mu headers, also checked by ARM64 static assertions.
RECORD=struct.pack('<32sQQIIIII4x',b'DISP_CC',BASE,SIZE,2,1,0x400,11,6)
MAP='Platforms/Xiaomi/enumaPkg/Library/MemoryMapLib/MemoryMapLib.c'
BASELINE='5fee8940c4cee08fb3cac33f75ffe706a624fce5e7f435447141bd133ab5fba8'

def source_check(text):
    if text.count(LINE)!=1:raise ValueError('exact DISP_CC descriptor absent/duplicated')
    # Every previous descriptor and compile-time mapping branch must be unchanged.
    if hashlib.sha256(text.replace(LINE,'').encode()).hexdigest()!=BASELINE:
        raise ValueError('mapping changes beyond approved DISP_CC addition')
    rows=re.findall(r'\{"([^"]+)",\s*(0x[0-9a-f]+)ULL,\s*(0x[0-9a-f]+)ULL,',text,re.I)
    for name,address,length in rows:
        address=int(address,16);length=int(length,16)
        if name!='DISP_CC' and address<BASE+SIZE and BASE<address+length:
            raise ValueError('DISP_CC overlaps '+name)
    if BASE%4096 or SIZE%4096 or not BASE<=FAULT<BASE+SIZE:raise ValueError('mapping coverage/alignment')
    return rows

def linked_check(pe,mapping,index):
    hits=re.findall(r'^([0-9a-f]+)\s+00000000\s+0\s+mRegions$',mapping,re.M)
    if len(hits)!=1:raise ValueError('SEC table symbol missing/ambiguous')
    rva=int(hits[0],16)+index*len(RECORD)
    matches=[s for s in sections(pe) if s[1]<=rva and rva+len(RECORD)<=s[1]+s[2]]
    if len(matches)!=1:raise ValueError('SEC descriptor outside file-backed section')
    s=matches[0];offset=s[3]+rva-s[1]
    if pe[offset:offset+len(RECORD)]!=RECORD:raise ValueError('linked DISP_CC range/attributes differ')
    if pe.count(RECORD)!=1:raise ValueError('linked DISP_CC descriptor not unique')
    return offset,rva

def converted_te(pe,raw,new_base):
    """Reproduce GenFv DIR64 relocation and zero section-tail padding."""
    if raw[:4]!=b'VZ\x64\xaa':raise ValueError('TE input architecture')
    expected=bytearray(raw);stripped=struct.unpack_from('<H',raw,6)[0]
    peoff=struct.unpack_from('<I',pe,60)[0];opt=peoff+24
    old_base=struct.unpack_from('<Q',pe,opt+24)[0]
    if struct.unpack_from('<Q',raw,16)[0]!=old_base:raise ValueError('PE/TE input base differs')
    def poff(rva,size):
        found=[s[3]+rva-s[1] for s in sections(pe) if s[1]<=rva and rva+size<=s[1]+s[2]]
        if len(found)!=1:raise ValueError('relocation source outside PE section')
        return found[0]
    te_sections=[struct.unpack_from('<8sIIII',raw,40+i*40) for i in range(raw[4])]
    def toff(rva,size):
        found=[ptr-stripped+40+rva-va for _,vs,va,n,ptr in te_sections if va<=rva and rva+size<=va+n]
        if len(found)!=1 or found[0]<0 or found[0]+size>len(raw):raise ValueError('relocation outside TE')
        return found[0]
    reloc,size=struct.unpack_from('<II',pe,opt+112+5*8)
    if not reloc or not size:raise ValueError('original SEC relocations required')
    start=poff(reloc,size);end=start+size;count=0
    while start<end:
        page,n=struct.unpack_from('<II',pe,start)
        if n<8 or n%2 or start+n>end:raise ValueError('bad relocation block')
        for pos in range(start+8,start+n,2):
            entry=struct.unpack_from('<H',pe,pos)[0];kind=entry>>12
            if kind==0:continue
            if kind!=10:raise ValueError('unexpected ARM64 relocation type')
            addr=toff(page+(entry&4095),8)
            value=struct.unpack_from('<Q',expected,addr)[0]
            struct.pack_into('<Q',expected,addr,(value+new_base-old_base)&((1<<64)-1));count+=1
        start+=n
    for _,virtual,_,n,ptr in te_sections:
        if n>virtual:
            start=ptr-stripped+40+virtual;end=ptr-stripped+40+n
            if start<0 or end>len(expected):raise ValueError('TE padding bounds')
            expected[start:end]=bytes(end-start)
    struct.pack_into('<Q',expected,16,new_base)
    return bytes(expected),count

def audit(build,files):
    source=(build/'work/uefi'/MAP).read_text()
    rows=source_check(source)
    # RAMOOPS_MAP=0 in this scope; the inactive optional descriptor is not linked.
    active=re.sub(r'#if ENUMA_RAMOOPS_MAP.*?#endif\n','',source,flags=re.S)
    names=re.findall(r'\{"([^"]+)"',active)
    index=names.index('DISP_CC')
    products=list((build/'work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64').rglob('OUTPUT/Sec.efi'))
    if len(products)!=1:raise ValueError('SEC product absent/ambiguous')
    pe=products[0].read_bytes();mapping=products[0].with_suffix('.map').read_text()
    offset,rva=linked_check(pe,mapping,index)
    # SEC is packaged as TE, not PE32: bind the actual conversion output and
    # resolve its descriptor through the TE section table and StrippedSize.
    guid='9affb503-e643-4141-8b90-17e8588b1d35'
    packed=files.get(guid,{}).get('te',[])
    raw=list((build/'work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/Ffs').rglob(guid.upper()+'Te.raw'))
    if len(raw)!=1 or len(packed)!=1:raise ValueError('SEC TE absent/ambiguous')
    te=packed[0]
    expected,relocations=converted_te(pe,raw[0].read_bytes(),0x9fc00000)
    if te!=expected:raise ValueError('SEC FD TE differs from reproduced relocation/conversion')
    if te[:4]!=b'VZ\x64\xaa':raise ValueError('SEC TE architecture')
    stripped=struct.unpack_from('<H',te,6)[0];count=te[4]
    offsets=[]
    for i in range(count):
        _,_,va,n,ptr=struct.unpack_from('<8sIIII',te,40+i*40)
        if va<=rva and rva+len(RECORD)<=va+n:offsets.append(ptr-stripped+40+rva-va)
    if len(offsets)!=1 or te[offsets[0]:offsets[0]+len(RECORD)]!=RECORD:
        raise ValueError('final TE descriptor differs from linked SEC')
    negatives=[]
    for label,position in [('name',0),('base',32),('size',40),('hob',48),('resource',52),('cache',56),('type',60),('arm',64)]:
        changed=bytearray(pe);changed[offset+position]^=1
        try:linked_check(bytes(changed),mapping,index)
        except ValueError:negatives.append(label)
        else:raise ValueError('descriptor mutation accepted: '+label)
    changed=bytearray(pe);changed[offset:offset+len(RECORD)]=bytes(len(RECORD))
    try:linked_check(bytes(changed),mapping,index)
    except ValueError:negatives.append('deleted')
    else:raise ValueError('deleted descriptor accepted')
    return dict(passed=True,base=hex(BASE),size=hex(SIZE),fault_address=hex(FAULT),
                device_attribute='NS_DEVICE',sec_sha256=hashlib.sha256(pe).hexdigest(),sec_te_sha256=hashlib.sha256(te).hexdigest(),
                sec_te_relocations=relocations,sec_te_relocation_and_padding_verified=True,
                descriptor_rva=hex(rva),descriptor_index=index,descriptor_bytes=len(RECORD),
                active_descriptor_count=len(names),source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                fd_sec_exact_match=True,negative_checks=negatives,live_page_tables_verified=False)
