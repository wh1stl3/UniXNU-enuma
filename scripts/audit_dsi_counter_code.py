"""Restricted constant/table dataflow on the actual packaged AArch64 PE.

This checks recognizable MMIO sites and the wait argument, not all control flow
or every possible indirect access. Runtime read bounds come from source+tests.
"""
import re,struct
from collections import deque

def audit_counter_code(payload,assembly,step):
    bases=(0xae6b800,0xae6c000)
    if step!=17:assert struct.pack('<QQ',*bases) in payload,'DSI base table absent in PE'
    pe=struct.unpack_from('<I',payload,0x3c)[0]
    count=struct.unpack_from('<H',payload,pe+6)[0]
    section=pe+24+struct.unpack_from('<H',payload,pe+20)[0]
    sections=[struct.unpack_from('<IIII',payload,section+i*40+8) for i in range(count)]
    def bytes_at(rva,n):
        for vs,va,size,offset in sections:
            if va<=rva and rva+n<=va+size:return payload[offset+rva-va:offset+rva-va+n]
        return b''
    instructions={};reads=set();stores=set();sites=set();wait_sites=set()
    for line in assembly.splitlines():
        fields=line.split('\t')
        if len(fields)<3:continue
        address=re.match(r'\s*([0-9a-f]+):',fields[0])
        if address:instructions[int(address[1],16)]=(fields[-2].strip(),fields[-1].strip(),line.strip())
    entry=struct.unpack_from('<I',payload,pe+24+16)[0]
    assert entry in instructions,'PE entry is not disassembled'
    states={entry:{}};queue=deque([entry]);iterations=0
    while queue:
        pc=queue.popleft();values={k:set(v) for k,v in states[pc].items()};op,args,line=instructions[pc]
        iterations+=1;assert iterations<100000,'dataflow did not converge'
        handled=False
        move=re.fullmatch(r'([wx]\d+), #(-?(?:0x[0-9a-f]+|\d+))(?:, lsl #(\d+))?',args)
        if op in ('mov','movk') and move:
            reg=move[1][1:];v=int(move[2],0);shift=int(move[3] or 0)
            if op=='mov':values[reg]={v & (0xffffffff if move[1][0]=='w' else 0xffffffffffffffff)}
            elif reg in values:values[reg]={(x&~(0xffff<<shift))|((v&0xffff)<<shift) for x in values[reg]}
            handled=True
        page=re.match(r'x(\d+), (0x[0-9a-f]+)',args)
        if op=='adrp' and page:values[page[1]]={int(page[2],0)};handled=True
        add=re.fullmatch(r'x(\d+), x(\d+), #(\d+)',args)
        if op=='add' and add and add[2] in values:values[add[1]]={v+int(add[3]) for v in values[add[2]]};handled=True
        table=re.fullmatch(r'x(\d+), \[x(\d+), x\d+, lsl #3\]',args)
        if op=='ldr' and table and table[2] in values and any(bytes_at(x,16)==struct.pack('<QQ',*bases) for x in values[table[2]]):
            values[table[1]]=set(bases);handled=True
        access=re.search(r'\[x(\d+)(?:, #(-?(?:0x[0-9a-f]+|\d+)))?\]',args)
        if access and access[1] in values:
            targets={v+int(access[2] or '0',0) for v in values[access[1]]}
            target=targets & ({b+off for b in bases for off in (0,0xa8,0xac,0x26c)}|{0xae00000})
            if target:
                if op in ('ldr','ldur'):reads.update(target);sites.add(line)
                elif op.startswith('st'):stores.update(target)
        if op in ('bl','blr'):
            if values.get('0')=={100000}:wait_sites.add(pc)
            values={k:v for k,v in values.items() if int(k)>=19}
        elif not handled and op not in ('cmp','tst','ret') and not op.startswith(('b','st','cb','tb')):
            dest=re.match(r'[wx](\d+)',args)
            if dest:values.pop(dest[1],None)
            if op=='ldp':
                for dest in re.findall(r'\b[wx](\d+)\b',args.split('[')[0]):values.pop(dest,None)
        targets=[]
        if op not in ('ret','br'):
            branch=re.search(r'0x([0-9a-f]+)',args)
            if op=='b' or op.startswith(('b.','cb','tb')):
                assert branch,'branch without direct target'
                targets.append(int(branch[1],16))
            if op!='b':targets.append(pc+4)
        for target in targets:
            if target not in instructions:continue
            if target not in states:
                states[target]={k:set(v) for k,v in values.items()};queue.append(target);continue
            previous=states[target]
            # Unknown on either incoming edge remains unknown. Widen finite
            # sets above eight values to unknown to bound loop analysis.
            merged={k:previous[k]|values[k] for k in previous.keys() & values.keys() if len(previous[k]|values[k])<=8}
            if merged!=previous:states[target]=merged;queue.append(target)
    offsets={15:(0,0xa8),16:(0,0xa8,0xac),17:(0x26c,),18:(0,0xa8,0xac,0x26c)}[step]
    wanted={b+off for b in bases for off in offsets}
    if step>=17:wanted.add(0xae00000)
    assert reads==wanted and not stores,(reads,stores,wanted)
    waits=len(wait_sites);assert waits==(1 if step in (16,18) else 0),waits
    if step in (16,18):assert re.search(r'cmp\s+w\d+, #64',assembly),'delta bound absent'
    return dict(scope=__doc__,static_possible_target_loads=sorted(hex(v) for v in reads),static_target_stores=sorted(hex(v) for v in stores),recognized_mmio_sites=sorted(sites),wait_100000_call_sites=waits,delta_64_comparison=step in (16,18),entry_rva=hex(entry),reachable_instruction_count=len(states),complete_indirect_access_or_control_flow_proof=False,hardware_execution=False)
