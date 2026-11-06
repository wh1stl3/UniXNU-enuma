"""Recheck manually inspected R023 PE instructions and unchanged Core code bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
from native_mask_decode import make_pixel_plan
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def sections(path):
    data=path.read_bytes();pe=struct.unpack_from('<I',data,60)[0]
    count=struct.unpack_from('<H',data,pe+6)[0];optional=struct.unpack_from('<H',data,pe+20)[0]
    result={}
    for i in range(count):
        start=pe+24+optional+40*i;name=data[start:start+8].rstrip(b'\0').decode()
        virtual,address,size,offset=struct.unpack_from('<IIII',data,start+8)
        result[name]=data[offset:offset+min(size,virtual)]
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--qualification',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();qp=a.qualification.resolve();out=a.output.resolve();qp.relative_to(ROOT/'out');out.relative_to(ROOT/'out')
    if out.exists(): raise ValueError('new review output required')
    q=json.loads(qp.read_text());d=qp.parent;assert q['passed'] and q['hardware_review']=='R-023'
    for n,h in q['files'].items(): assert sha(d/n)==h,n
    asm=(d/'SimpleFbDxe.disassembly.txt').read_text();instructions={}
    for line in asm.splitlines():
        fields=line.split('\t');match=re.match(r'\s*([0-9a-f]+):',fields[0])
        if match and len(fields)>1: instructions[match[1]]=re.sub(r'\s+',' ',' '.join(fields[1:]).split('//')[0].strip())
    expected={
        '106c':'sub sp, sp, #0x32, lsl #12','1070':'sub sp, sp, #0x1b0',
        '12bc':'cmp w9, #0x1','12c8':'cmp w9, #0x10',
        '1344':'cmp x10, x11','1368':'cmp x10, x15','1384':'cmp w14, #0x1',
        '15f8':'cmp w11, #0xd','1608':'ldrb w8, [x8, #0x40]',
        '16d0':'ldr x1, [x24, #0x20]','16e0':'ldr x1, [x24, #0x18]!',
        '1770':'mov w12, #0x3047','1778':'mov w14, #0x3147',
        '1824':'dsb sy','1828':'mov w23, #0xc800','1830':'mov w25, #0x140',
        '1858':'add w8, w8, #0x60','1860':'add w9, w9, #0x100',
        '18c4':'bl 0x24bc <.text+0x14bc>','19bc':'mov w8, #0xc800',
        '1a30':'dsb sy','1a3c':'mov w20, #0xc800',
        '1ac8':'mov w0, #0x1200','1ad0':'movk w0, #0x7a, lsl #16',
        '1afc':'mov w23, #0xc800','1b24':'ldr w2, [x24, x22, lsl #2]',
        '1b44':'cmp w0, #0x1','1b48':'add x22, x22, #0x1',
        '1b70':'dsb sy','1b78':'mov w24, #0xc800','1bf8':'mov w9, #0x4',
        '3b04':'lsr w9, w8, #12','3b08':'cmp w9, #0x18','3b24':'str w19, [x20]',
        '3b64':'lsr w9, w8, #11','3b68':'cmp w9, #0x4a','3b84':'ldr w8, [x21]',
        '3e28':'sub x11, x10, #0x60','3e2c':'cmp x11, #0x9f',
        '3e38':'cmp x8, #0x100','3e40':'cmp x8, #0x600'}
    for addr,instruction in expected.items(): assert instructions.get(addr)==instruction,(addr,instructions.get(addr),instruction)
    assert sum(v=='dsb sy' for v in instructions.values())==3
    assert not any(re.match(r'(?:dc |msr (?:ttbr|tcr|mair|sctlr|vttbr))',v) for v in instructions.values())
    frozen=ROOT/'out/inherited-gop/qualified-dxe-log-8s-8680ea7/DxeCore.efi'
    assert sha(frozen)=='753ff2dd2444aeec2404c149c32771933f71d84dcb5e3b371261f7f1c15fb6da'
    old=sections(frozen);new=sections(d/'DxeCore.efi')
    assert old['.text']==new['.text'] and old['.data']==new['.data']
    assert bytes([3,2,1,0,5,4,7,6,8,9,10,11,12,13,14,15]) in (d/'SimpleFbDxe.efi').read_bytes()
    paths=[qp,*[d/n for n in ('SimpleFbDxe.efi','DxeCore.efi','SimpleFbDxe.disassembly.txt','DxeCore.disassembly.txt')],
           ROOT/'out/attributed-log-20261026/build2/source-manifest.json',ROOT/'out/attributed-log-20261026/tests2/result.json',
           ROOT/'scripts/qualify_attributed_log.py',ROOT/'scripts/check_attributed_pixel_log.py',Path(__file__)]
    report=dict(passed=True,scope='manual source/control-flow and exact packaged instruction review; not hardware proof',
        image_sha256=q['image_sha256'],qualification_sha256=sha(qp),hardware_execution=False,
        actual_entry_stack_bytes=0x60+0x32000+0x1b0,actual_nested_native_sampler_frame_bytes=0x60+0x2000+0x250,
        configured_stack_bytes=262144,stack_high_water_measured=False,
        core_text_and_initialized_data_identical_to_r022=True,core_whole_pe_identical=False,
        observations=['private snapshot v1/16-byte ABI checked before callback; complete sequence/loss/HasGuid validation',
          'latest point13 with GUID required; 64-bit status/sequence plus canonical UUID, no current-provider return',
          '51200 words, x64..383/y96..255; 153600 read and102400 store callback caps',
          'save then second Native6 validation before stores; three DSB; 0x7a1200 microsecond hold',
          'all post-store paths attempt whole restore and readback; restore failure has code4 precedence',
          'unchanged Core .text retains prior GUID-only warning1..5 cold-reset transport; PE differs outside code',
          'no cache-line or mapping setter instructions; no GOP/ConOut publication or requirements clearing'],
        decode_plan=make_pixel_plan(ROOT,'R-023'),
        limitations=['larger ROI CPU time and physical corner clearance untested; fixed timing window is not enlarged after observation',
                     'entry plus nested frames are below existing stack allocation; total hardware stack high-water remains unmeasured',
                     'known requirements22/stage2/SMMU/alpha obligations remain'],
        instruction_checks=expected,bindings={str(p.relative_to(ROOT)):sha(p) for p in paths})
    out.write_text(json.dumps(report,indent=2)+'\n');print('PASS: exact new PE scope, attribution, restore paths and unchanged Core code')


if __name__=='__main__': main()
