"""WSL: run actual reservation C under sanitizers; no images/device commands."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
if sys.version_info < (3,11):
    import tomli
    sys.modules['tomllib']=tomli
from audit_inputs import parse_fdt

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'out/log-readback/fdt-host';out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'diagnostics/fdt_reserve.c'
    subprocess.run(['clang','-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
        '-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie',str(source),
        str(ROOT/'diagnostics/fdt_reserve_host.c'),'-o',str(out/'check')],check=True)
    original=(ROOT/'out/device/live-fdt.bin').read_bytes()
    if hashlib.sha256(original).hexdigest()!='643aa3ec450139d38f8cde9a94bca6d9e8e75e752cb7aa992685d34267434c62':
        raise ValueError('unreviewed FDT input')
    cases=[('actual',original,True)]
    # Linux removes rng-seed after entry. Live FDT padding is not necessarily
    # present at firmware handoff. Reconstruct only its structure with a zero
    # synthetic seed; preserve all 524 bytes as a valid property, no free NOPs.
    seeded=bytearray(original);h=struct.unpack_from('>10I',original)
    strings=original[h[3]:h[3]+h[8]];seedoff=strings.index(b'rng-seed\0')
    pos=h[2]
    while pos<h[2]+h[9]:
        token=struct.unpack_from('>I',original,pos)[0]
        if token==4:
            end=pos
            while struct.unpack_from('>I',original,end)[0]==4:end+=4
            if end-pos!=524:raise ValueError('unexpected NOP layout')
            seeded[pos:end]=struct.pack('>III',3,512,seedoff)+bytes(512)
            break
        pos+=4
        if token==1:pos=(original.index(0,pos)+4)&~3
        elif token==3:pos=(pos+8+struct.unpack_from('>I',original,pos)[0]+3)&~3
    else:raise ValueError('expected live NOP padding missing')
    cases.append(('synthetic-pre-entry-seed-no-nops',bytes(seeded),True))
    for name,offset,value in [('bad-magic',0,0),('oversize',4,0x200001),
        ('bad-structure',8,60),('bad-strings',12,0xfffffffc),('reserve-offset',16,48),
        ('bad-version',20,16),('future-version',24,18),('bad-strings-size',32,0xffffffff),
        ('bad-structure-size',36,0xfffffffc),('existing-owner',44,0x1000),
        ('bad-root',56,2),('invalid-token',56,0x42)]:
        data=bytearray(original);struct.pack_into('>I',data,offset,value);cases.append((name,bytes(data),False))
    for length in (0,39,55,100,len(original)-1):
        cases.append(('truncated-'+str(length),original[:length],False))
    # Minimal valid FDT with too little removable padding must be byte-identical.
    minimal=struct.pack('>10I',0xd00dfeed,72,56,72,40,17,16,0,0,16)+bytes(16)+struct.pack('>4I',1,0,2,9)
    cases.append(('no-nops',minimal,False))
    cases.append(('sufficient-nops',struct.pack('>10I',0xd00dfeed,88,56,88,40,17,16,0,0,32)+bytes(16)+struct.pack('>8I',1,0,4,4,4,4,2,9),True))
    results=[]
    for name,data,success in cases:
        inp=out/(name+'.input');result=out/(name+'.output');inp.write_bytes(data)
        run=subprocess.run([str(out/'check'),str(inp),str(result)],capture_output=True,text=True,check=True)
        actual=result.read_bytes()
        if run.stdout.strip()!=str(int(success)):raise ValueError(name+': unexpected result')
        if success:
            if len(actual)!=len(data) or parse_fdt(actual)!=parse_fdt(data):raise ValueError(name+': semantic change')
            if struct.unpack_from('>4Q',actual,40)!=(0x9fff7000,0x8000,0,0):raise ValueError(name+': wrong reservation')
            # Second invocation must refuse existing ownership without any write.
            inp.write_bytes(actual)
            run=subprocess.run([str(out/'check'),str(inp),str(result)],capture_output=True,text=True,check=True)
            if run.stdout.strip()!='0' or result.read_bytes()!=actual:raise ValueError(name+': repeated mutation')
        elif actual!=data:raise ValueError(name+': modified on rejection')
        results.append({'case':name,'accepted':success,'passed':True})
    (ROOT/'reports/enuma-log-fdt-host.json').write_text(json.dumps({
        'scope':'host ASan/UBSan only; no boot or physical log access',
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'input_sha256':hashlib.sha256(original).hexdigest(),'cases':results,
        'all_node_property_bytes_preserved':True,'range':['0x9fff7000','0x8000']},indent=2)+'\n')
    print('PASS: '+str(len(cases))+' sanitizer cases, semantic equality, rejection atomicity and repeat guard')

if __name__=='__main__':main()
