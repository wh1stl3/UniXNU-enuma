"""Strict saved OEM service snapshot decoder; no device access or guessed returns."""
import argparse,json,re,uuid
from pathlib import Path
HEADER=re.compile(r'OEM cached dropped=([0-9a-f]{16}) next=([0-9a-f]{16}) calls=([0-9a-f]{16})')
EVENT=re.compile(r'OEM seq=([0-9a-f]{16}) call=([0-9a-f]{16}) svc=(locate-protocol|handle-protocol|allocate-pool) phase=(enter|return) rva=([0-9a-f]{16}|unknown) s=([0-9a-f]{16}|not-returned) guid=([0-9a-f-]{36}|-) value=([0-9a-f]{16})')
def decode(text):
 rows=text.splitlines()
 if not rows or len(rows)>129:raise ValueError('complete bounded snapshot required')
 h=HEADER.fullmatch(rows[0])
 if not h:raise ValueError('invalid snapshot header')
 dropped,next_seq,calls=(int(x,16) for x in h.groups());count=len(rows)-1
 if count!=min(next_seq,128) or dropped!=next_seq-count:raise ValueError('incomplete snapshot/loss mismatch')
 pending={};seen_returns=set();events=[];unpaired=[]
 for offset,row in enumerate(rows[1:]):
  m=EVENT.fullmatch(row)
  if not m:raise ValueError('noncanonical row; no OCR guessing')
  seq,call,svc,phase,rva,status,guid,value=m.groups();seq=int(seq,16);call=int(call,16)
  if seq!=next_seq-count+offset or call>=calls:raise ValueError('sequence/call outside snapshot')
  if (phase=='enter')!=(status=='not-returned'):raise ValueError('invented or absent return status')
  if guid!='-' and str(uuid.UUID(guid))!=guid:raise ValueError('noncanonical GUID')
  if svc=='allocate-pool' and guid!='-':raise ValueError('pool event cannot name a protocol')
  signature=(svc,rva,guid,value)
  if phase=='enter':
   if call in pending or call in seen_returns:raise ValueError('duplicate call identity')
   pending[call]=(seq,signature)
  else:
   if call in seen_returns:raise ValueError('duplicate return')
   seen_returns.add(call)
   if call in pending:
    entered,expected=pending.pop(call)
    if signature!=expected:raise ValueError('return attribution differs from entry')
   elif dropped:unpaired.append(call)
   else:raise ValueError('return without an entry in lossless snapshot')
  events.append(dict(sequence=seq,call=call,service=svc,phase=phase,caller_rva=None if rva=='unknown' else rva,status_hex=None if phase=='enter' else status,protocol=None if guid=='-' else guid,value_hex=value))
 return dict(events=events,dropped=dropped,next_sequence=next_seq,calls=calls,
  pending_calls=[dict(call=k,entry_sequence=v[0],service=v[1][0]) for k,v in pending.items()],unpaired_returns=unpaired,
  assessment=dict(deadlock_established=False,missing_return='not observed in this snapshot',
   overwritten_events=dropped,recording_counter_exhausted=next_seq==2**64-1 or calls==2**64-1,
   unpaired_return_meaning='entry absent from retained window; do not invent its sequence or arguments'),
  hardware_verified=False,limitations=['Pending means no return in this snapshot; not proof of a hang.','RVA needs the exact loaded PE and execution binding before symbol attribution.','Only three wrapped Boot Services are covered; MMIO, SMC and protocol method calls are not traced.'])
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('transcript',type=Path);a=p.parse_args();print(json.dumps(decode(a.transcript.read_text(encoding='ascii')),indent=2))
