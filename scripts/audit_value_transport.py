"""Bounded disassembly checks for the actual packaged value-transport PE."""
import hashlib
import re
import subprocess


def audit_value_code(payload, build, out):
    out.mkdir(parents=True,exist_ok=True)
    pe=out/'SimpleFbDxe.efi';pe.write_bytes(payload)
    assembly=subprocess.check_output(['llvm-objdump','-d',str(pe)],text=True)
    (out/'SimpleFbDxe.disassembly.txt').write_text(assembly)
    constants={};reads=[];writes=[]
    for line in assembly.splitlines():
        fields=line.split('\t')
        if len(fields)<3:continue
        op,operands=fields[-2].strip(),fields[-1].strip()
        move=re.fullmatch(r'([wx]\d+), #(-?(?:0x[0-9a-f]+|\d+))(?:, lsl #(\d+))?',operands)
        if op in ('mov','movk') and move:
            reg=move[1][1:];v=int(move[2],0);shift=int(move[3] or 0)
            if op=='mov':constants[reg]=v & (0xffffffff if move[1][0]=='w' else 0xffffffffffffffff)
            elif reg in constants:constants[reg]=(constants[reg]&~(0xffff<<shift))|((v&0xffff)<<shift)
            continue
        access=re.search(r'\[([wx]\d+)(?:, #(-?(?:0x[0-9a-f]+|\d+)))?\]',operands)
        if access and access[1][1:] in constants:
            address=constants[access[1][1:]]+int(access[2] or '0',0)
            if 0xae00000<=address<0xae85000:
                if op in ('ldr','ldur'):reads.append(hex(address))
                elif op.startswith('st'):writes.append(hex(address))
        if op in ('bl','blr'):constants.clear()
        elif op not in ('cmp','tst','ret') and not op.startswith(('b','st')):
            dest=re.match(r'[wx](\d+)',operands)
            if dest:constants.pop(dest[1],None)
    profile=build['value_probe']
    if writes or re.search(r'\bdc\s+(?:civac|cvac|ivac)\b',assembly):
        raise ValueError('value transport contains display stores/cache maintenance')
    if profile['source']=='constant' and reads:
        raise ValueError('constant calibration contains direct display reads')
    if profile['source']=='register':
        addresses=[0xae00000,0xae05014,0xae07014,0xae09014,0xae0b014,0xae25014,0xae27014]
        if sorted(reads)!=sorted([hex(0xae6b800),hex(addresses[profile['register_index']])]):
            raise ValueError('register calibration target loads differ: '+repr(reads))
    compiled=build.get('value_probe_compiled_contract',{})
    if not compiled.get('actual_defines_checked'):
        raise ValueError('actual value compiler defines were not checked')
    return dict(profile=profile,provider_pe_sha256=hashlib.sha256(payload).hexdigest(),
                static_display_reads=reads,static_display_stores=writes,
                compiled_contract=compiled,hardware_execution=False,
                scope='packaged PE direct constant-address accesses and locked source/host checks; not full indirect dataflow proof')
