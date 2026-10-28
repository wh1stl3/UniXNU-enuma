"""Bind v13's three display resource mappings to source, linked SEC and final FD."""
import hashlib
import re
import struct
from check_oem_dispcc_map import converted_te, MAP
from map_oem_trace_rva import sections

REGIONS=(('Display VBIF',0xaeb0000,0x3000),('Display DSI0',0xae94000,0x1000),('Display DSI1',0xae96000,0x1000))
BASELINE='6afce88b9ff48bfa5987ab19ac17d6dabc09ffbeca3f11ef1ee92e95a6bb7560'
NEGATIVES=['name','base','size','hob','resource','cache','type','arm','deleted']
def line(region):
    n,b,z=region
    return f'  {{"{n}", {hex(b)}ULL, {hex(z)}ULL, AddDev, MMAP_IO, UNCACHEABLE, MmIO, NS_DEVICE}},\n'
def record(region):
    n,b,z=region
    return struct.pack('<32sQQIIIII4x',n.encode(),b,z,2,1,0x400,11,6)
def source_check(text):
    original=text
    for region in REGIONS:
        if text.count(line(region))!=1:raise ValueError('exact display descriptor missing/duplicate')
        original=original.replace(line(region),'')
    if hashlib.sha256(original.encode()).hexdigest()!=BASELINE:raise ValueError('changes outside three display additions')
    rows=re.findall(r'\{"([^"]+)",\s*(0x[0-9a-f]+)ULL,\s*(0x[0-9a-f]+)ULL,',text,re.I)
    for name,base,size in REGIONS:
        if base%4096 or size%4096:raise ValueError('alignment')
        for n,b,z in rows:
            if n!=name and int(b,16)<base+size and base<int(b,16)+int(z,16):raise ValueError('display mapping overlap')
    return rows
def linked_check(pe,mapping,index,region):
    hits=re.findall(r'^([0-9a-f]+)\s+00000000\s+0\s+mRegions$',mapping,re.M)
    if len(hits)!=1:raise ValueError('SEC symbol missing/ambiguous')
    rec=record(region);rva=int(hits[0],16)+index*len(rec)
    offsets=[s[3]+rva-s[1] for s in sections(pe) if s[1]<=rva and rva+len(rec)<=s[1]+s[2]]
    if len(offsets)!=1 or pe[offsets[0]:offsets[0]+len(rec)]!=rec or pe.count(rec)!=1:raise ValueError('linked display descriptor differs')
    return offsets[0],rva
def audit(build,files):
    source=(build/'work/uefi'/MAP).read_text();source_check(source)
    active=re.sub(r'#if ENUMA_RAMOOPS_MAP.*?#endif\n','',source,flags=re.S)
    names=re.findall(r'\{"([^"]+)"',active)
    products=list((build/'work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64').rglob('OUTPUT/Sec.efi'))
    if len(products)!=1:raise ValueError('SEC product absent/ambiguous')
    pe=products[0].read_bytes();mapping=products[0].with_suffix('.map').read_text()
    guid='9affb503-e643-4141-8b90-17e8588b1d35';packed=files.get(guid,{}).get('te',[])
    raw=list((build/'work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/Ffs').rglob(guid.upper()+'Te.raw'))
    if len(raw)!=1 or len(packed)!=1:raise ValueError('SEC TE missing/ambiguous')
    te=packed[0];expected,count=converted_te(pe,raw[0].read_bytes(),0x9fc00000)
    if te!=expected:raise ValueError('final SEC conversion differs')
    stripped=struct.unpack_from('<H',te,6)[0];results=[]
    for region in REGIONS+(('DISP_CC',0xaf00000,0x20000),):
        index=names.index(region[0]);off,rva=linked_check(pe,mapping,index,region);rec=record(region)
        offsets=[]
        for i in range(te[4]):
            _,_,va,n,ptr=struct.unpack_from('<8sIIII',te,40+i*40)
            if va<=rva and rva+len(rec)<=va+n:offsets.append(ptr-stripped+40+rva-va)
        if len(offsets)!=1 or te[offsets[0]:offsets[0]+len(rec)]!=rec:raise ValueError('final TE descriptor differs')
        neg=[]
        for label,pos in zip(NEGATIVES,[0,32,40,48,52,56,60,64,None]):
            bad=bytearray(pe)
            if pos is None:bad[off:off+len(rec)]=bytes(len(rec))
            else:bad[off+pos]^=1
            try:linked_check(bytes(bad),mapping,index,region)
            except ValueError:neg.append(label)
            else:raise ValueError('mutation accepted: '+label)
        results.append(dict(name=region[0],base=hex(region[1]),size=hex(region[2]),descriptor_rva=hex(rva),negative_checks=neg))
    return dict(passed=True,regions=results,fd_sec_exact_match=True,sec_te_relocations=count,sec_te_sha256=hashlib.sha256(te).hexdigest(),source_sha256=hashlib.sha256(source.encode()).hexdigest(),active_descriptor_count=len(names),live_page_tables_verified=False)
def require_evidence(m,bindings):
    if not m or m.get('passed') is not True or m.get('fd_sec_exact_match') is not True:raise ValueError('v13 linked display mapping absent')
    regions=m.get('regions',[])
    expected=REGIONS+(('DISP_CC',0xaf00000,0x20000),)
    if len(regions)!=len(expected):raise ValueError('v13 mapping evidence count')
    for row,(name,base,size) in zip(regions,expected):
        if (row.get('name'),row.get('base'),row.get('size'),row.get('negative_checks'))!=(name,hex(base),hex(size),NEGATIVES):raise ValueError('v13 mapping evidence differs')
    for name in ('scripts/check_oem_display_map.py','scripts/check_oem_dispcc_map.py','tests/test_oem_display_map.py'):
        if name not in bindings:raise ValueError('unbound v13 checker')
