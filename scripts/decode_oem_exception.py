"""Decode photographed v11 pages only; no invented fields or device I/O."""
import argparse,json,re,uuid
from pathlib import Path
def decode(pages,session,inventory=None):
 if type(session) is not int or not 0<session<2**64 or not 1<=len(pages)<=3:raise ValueError('session/pages required')
 parsed=[]
 for index,page in enumerate(pages,1):
  if len(page)!=5 or not re.fullmatch('E1'+str(index)+'C[0-9a-fA-F]{16}',page[0]):raise ValueError('wrong or out-of-order exception page')
  if page[4].lower()!=f'G{session:016x}'.lower():raise ValueError('foreign session')
  prefixes=('O','S','C') if index<3 else ('G0','G1','S')
  values=[]
  for line,prefix in zip(page[1:4],prefixes):
   if not re.fullmatch(prefix+'[0-9a-fA-F]{16}',line):raise ValueError('truncated/malformed exception field')
   values.append(int(line[len(prefix):],16))
  parsed.append((int(page[0][4:],16),values))
 typ,(pc,esr,far)=parsed[0]
 if typ>3:raise ValueError('invalid exception type')
 ec=(esr>>26)&63
 result=dict(exception_type=typ,pc=hex(pc),esr=hex(esr),far_raw=hex(far),esr_ec=hex(ec),
   abort_fsc=hex(esr&63) if ec in (0x20,0x21,0x24,0x25) else None,
   far_usable_for_abort=ec in (0x20,0x21,0x24,0x25) and not esr&(1<<10),
   session=hex(session),owner=None,owner_fd_verified=False,complete=len(pages)==3,
   limitation='Photographed exception snapshot; ELR and FAR meanings depend on exception class. No GOP/driver success or unique fault cause.')
 if len(pages)>1:
  flags,(base,rva,size)=parsed[1];state=flags&255;valid=bool(flags&256)
  if state>6 or flags&~0x1ff or (valid and state!=1):raise ValueError('invalid owner flags')
  if state==1:
   if not base or not 0<size<=0x4000000 or base+size>2**64-1 or not 0<=rva<size or base+rva!=pc:raise ValueError('owner bounds/PC mismatch')
  elif base or rva or size:raise ValueError('non-unique owner has image values')
  result['owner']=dict(state=state,base=hex(base),rva=hex(rva),size=size,guid=None,guid_available=valid)
  if len(pages)==3:
   lr,(g0,g1,spsr)=parsed[2];result.update(lr=hex(lr),spsr=hex(spsr))
   guid=str(uuid.UUID(int=(g0<<64)|g1))
   if not valid and (g0 or g1):raise ValueError('invalid GUID must be zero')
   if valid:
    result['owner']['guid']=guid
    matches=[m for m in inventory or [] if m['guid']==guid and m['image_size']==size]
    if len(matches)==1:
     m=matches[0];result.update(owner_fd_verified=True,module=m['name'],module_pe_sha256=m['pe_sha256'])
     result['pc_sections']=[s for s in m['sections'] if s['rva']<=rva<s['rva']+s['bytes']]
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--qualification',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 q=json.loads(a.qualification.read_text());data=json.loads(a.input.read_text())
 if q['scope'] not in ('oem-exception-v11','oem-exception-dispcc-v12'):raise ValueError('exception qualification required')
 result=decode(data['pages'],q['run_config']['session'],q['exception_inventory'])
 with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
