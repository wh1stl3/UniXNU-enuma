"""Targeted instruction regression for the reviewed R025 build3 PE; no device."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
from audit_attributed_log_code import sections
ROOT=Path(__file__).resolve().parents[1]
# Actual reviewed MenuRead/MenuWrite/MenuBarrier and address gate instructions.
CHECKS={
 '4a88':('bl','0x4b60'), '4a94':('mov','w9, #35327'),'4a98':('movk','w9, #102, lsl #16'),
 '4ab8':('ldr','w8, [x20]'),'4abc':('str','w8, [x19]'),
 '4aec':('bl','0x4b60'),'4af8':('mov','w9, #14079'),'4afc':('movk','w9, #95, lsl #16'),
 '4b1c':('str','w19, [x20]'),'4b38':('mov','w9, #8193'),'4b58':('dsb','sy'),
 '4b74':('cmp','w8, #22'),'4c80':('sub','x11, x10, #96'),'4c84':('cmp','x11, #599'),
 '4c90':('cmp','x8, #256'),'4c98':('cmp','x8, #3456'),
 '5678':('cbz','w8, 0x5c94'),'5680':('cbnz','w8, 0x5c94')}
# Cleanup reordering adds four bytes before the unchanged callback functions.
CHECKS={format(int(a,16)+4,'x'):(m,re.sub(r'0x[0-9a-f]+',lambda n:hex(int(n[0],16)+4),o)) for a,(m,o) in CHECKS.items()}
CORE_CHECKS={'fa24':('cbz','x20, 0xfab4'),'fa28':('sub','x8, x19, #6'),
 'fa2c':('cmp','x0, #13'),'fa30':('ccmn','x8, #5, #0, eq'),
 'fa40':('mov','x8, #7789'),'fa44':('movk','x8, #56573, lsl #16'),
 'fa48':('movk','x8, #30861, lsl #32'),'fa4c':('movk','x8, #20476, lsl #48'),
 'fa60':('mov','x8, #7054'),'fa64':('movk','x8, #12234, lsl #16'),
 'fa68':('movk','x8, #25973, lsl #32'),'fa6c':('movk','x8, #37402, lsl #48'),
 'fa78':('mov','w8, #19264'),'fa80':('movk','w8, #76, lsl #16'),
 'fa88':('madd','x0, x19, x8, x9'),'fa8c':('bl','0x1b8fc'),
 'fa90':('bl','0x16f4'),'fa94':('bl','0x13b8')}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def image_range(path,rva,size):
    blob=path.read_bytes();pe=struct.unpack_from('<I',blob,0x3c)[0]
    count=struct.unpack_from('<H',blob,pe+6)[0];optional=struct.unpack_from('<H',blob,pe+20)[0]
    for index in range(count):
        offset=pe+24+optional+index*40
        length,address,raw_size,raw=struct.unpack_from('<IIII',blob,offset+8)
        if address<=rva and rva+size<=address+raw_size:return blob[raw+rva-address:raw+rva-address+size]
    raise ValueError('reviewed code range absent')
def check(instructions,checks=CHECKS):
    for address,(mnemonic,operand) in checks.items():
        actual=instructions.get(address)
        if not actual or actual[0]!=mnemonic or not actual[1].startswith(operand):raise ValueError('reviewed instruction changed: '+address)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    out=args.output.resolve();out.relative_to(ROOT/'out')
    if out.exists():raise ValueError('refusing to overwrite review')
    qdir=ROOT/'out/menu-window-20261026/qualification2';q=json.loads((qdir/'qualification.json').read_text())
    if not q.get('passed') or q.get('image_sha256')!='17a18ace93a002ac394ef4727148e893d7defe420496b4d3e8df7dde115be0cd':raise ValueError('not the reviewed candidate')
    pe=qdir/'SimpleFbDxe.efi';assembly=qdir/'SimpleFbDxe.disassembly.txt'
    if sha(pe)!='6ceb4762579df4a0c5469031cf33cce1b706f4c26b5e88c37354151da4158a50':raise ValueError('not the reviewed provider PE')
    instructions={m[1]:(m[2],m[3]) for m in re.finditer(r'^\s*([0-9a-f]+):(?:\s+[0-9a-f]{2}){4}\s+([a-z0-9.]+)\s+([^\n]+)',assembly.read_text(),re.M)}
    check(instructions);removed=dict(instructions);removed.pop('4b20')
    try:check(removed)
    except ValueError:pass
    else:raise ValueError('removed physical store was accepted')
    previous=ROOT/'out/menu-window-20261026/qualification1/SimpleFbDxe.efi'
    if image_range(previous,0x4a68,0x248)!=image_range(pe,0x4a6c,0x248):raise ValueError('physical callback code changed beyond relocation')
    core=qdir/'DxeCore.efi'
    old_core=sections(previous.parent/'DxeCore.efi');new_core=sections(core)
    if any(old_core[name]!=new_core[name] for name in ('.text','.data')):raise ValueError('Core code/data changed between reviewed menu builds')
    core_instructions={m[1]:(m[2],m[3]) for m in re.finditer(r'^\s*([0-9a-f]+):(?:\s+[0-9a-f]{2}){4}\s+([a-z0-9.]+)\s+([^\n]+)',(qdir/'DxeCore.disassembly.txt').read_text(),re.M)}
    check(core_instructions,CORE_CHECKS)
    result=dict(passed=True,scope='targeted manually reviewed instruction regression and source/runtime binding; no physical acceptance',
                image_sha256=q['image_sha256'],qualification_sha256=sha(qdir/'qualification.json'),
                instruction_checks={a:' '.join(v) for a,v in CHECKS.items()},core_instruction_checks={a:' '.join(v) for a,v in CORE_CHECKS.items()},removed_store_rejected=True,physical_callback_bytes_unchanged_from_review1=True,
                conclusions=['read/write address gate retains requirements22 and window bounds',
                             'physical callbacks enforce 6720000 reads/6240000 writes/8194 barriers',
                             'private GOP Blt checks ready and latched fault before drawing',
                             'QEMU ran actual same Ui/Menu adapter; physical callbacks substituted only',
                             'full BDS/UniXNURun/config discovery and physical input not exercised'],
                timing_decoder='none; old log code5 windows are not reused')
    out.write_text(json.dumps(result,indent=2)+'\n');print('PASS: reviewed R025 physical callbacks, window/requirements gate and first-fault stop')
if __name__=='__main__':main()
