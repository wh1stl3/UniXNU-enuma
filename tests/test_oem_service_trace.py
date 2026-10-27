import sys,unittest,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from decode_oem_service_trace import decode
def event(seq,call,phase,status,svc='allocate-pool'):
 return f'OEM seq={seq:016x} call={call:016x} svc={svc} phase={phase} rva=0000000000001234 s={status} guid=- value=0000000000000063\n'
class TraceDecoder(unittest.TestCase):
 def test_no_return_does_not_establish_deadlock(self):
  text='OEM cached dropped=0000000000000000 next=0000000000000001 calls=0000000000000001\n'+event(0,0,'enter','not-returned')
  d=decode(text);self.assertFalse(d['assessment']['deadlock_established']);self.assertIsNone(d['events'][0]['status_hex'])
  self.assertEqual(d['assessment']['missing_return'],'not observed in this snapshot')
 def test_reference_model_at_many_nested_snapshot_boundaries(self):
  # Independent model of retained entries and returns, not a decoder replay.
  for seed in range(32):
   rng=random.Random(seed);history=[];stack=[];calls=0
   for tick in range(350):
    if not stack or rng.randrange(3):
     call=calls;calls+=1;stack.append(call);phase='enter';status='not-returned'
    else:call=stack.pop();phase='return';status=rng.choice(['0000000000000000','0000000000000001','8000000000000009'])
    history.append((tick,call,phase,status))
    if tick not in (0,1,63,126,127,128,129,255,256,349):continue
    retained=history[-128:];lost=len(history)-len(retained)
    text=f'OEM cached dropped={lost:016x} next={len(history):016x} calls={calls:016x}\n'+''.join(event(*row) for row in retained)
    d=decode(text);entries={x[1] for x in retained if x[2]=='enter'};returns={x[1] for x in retained if x[2]=='return'}
    with self.subTest(seed=seed,tick=tick):
     self.assertEqual({x['call'] for x in d['pending_calls']},entries-returns)
     self.assertEqual(set(d['unpaired_returns']),returns-entries)
     self.assertEqual(d['dropped'],lost);self.assertFalse(d['assessment']['deadlock_established'])
 def test_truncation_duplication_and_reordering_rejected(self):
  header='OEM cached dropped=0000000000000000 next=0000000000000004 calls=0000000000000002\n'
  rows=[event(0,0,'enter','not-returned'),event(1,1,'enter','not-returned'),event(2,1,'return','0000000000000000'),event(3,0,'return','0000000000000000')]
  for damaged in [rows[:-1],rows[1:],rows+[rows[-1]],[rows[0],rows[2],rows[1],rows[3]],[rows[0],rows[1],rows[2],rows[3].replace('call=0000000000000000','call=0000000000000001')]]:
   with self.assertRaises(ValueError):decode(header+''.join(damaged))
 def test_nested_return_does_not_close_outer(self):
  text='OEM cached dropped=0000000000000000 next=0000000000000003 calls=0000000000000002\n'
  text+=event(0,0,'enter','not-returned')+event(1,1,'enter','not-returned')+event(2,1,'return','8000000000000009')
  d=decode(text);self.assertEqual(d['pending_calls'],[dict(call=0,entry_sequence=0,service='allocate-pool')]);self.assertIsNone(d['events'][0]['status_hex'])
 def test_failure_and_warning_preserved(self):
  for status in ['800000000000000e','0000000000000001']:
   text='OEM cached dropped=0000000000000000 next=0000000000000002 calls=0000000000000001\n'+event(0,0,'enter','not-returned')+event(1,0,'return',status)
   self.assertEqual(decode(text)['events'][1]['status_hex'],status)
 def test_bad_snapshot_and_attribution_rejected(self):
  header='OEM cached dropped=0000000000000000 next=0000000000000002 calls=0000000000000001\n'
  first=event(0,0,'enter','not-returned');last=event(1,0,'return','0000000000000000')
  for text in [header+first,header+first+last.replace('1234','1235'),header+first+last.replace('allocate-pool','locate-protocol'),header+first+last.replace('0000000000000063','0000000000000064'),header+first.replace('not-returned','0000000000000000')+last,header+first+last.replace('phase=return','phase=enter')]:
   with self.subTest(text=text),self.assertRaises(ValueError):decode(text)
 def test_configuration_registration(self):
  header='OEM cached dropped=0000000000000000 next=0000000000000002 calls=0000000000000001\n'
  first=event(0,0,'enter','not-returned','install-configuration-table')
  last=event(1,0,'return','8000000000000009','install-configuration-table')
  self.assertEqual(decode(header+first+last)['events'][1]['status_hex'],'8000000000000009')
  self.assertRaises(ValueError,decode,header+first+last.replace('install-configuration-table','allocate-pool'))
 def test_overwrite_unpaired_return_explicit(self):
  text='OEM cached dropped=0000000000000001 next=0000000000000081 calls=0000000000000081\n'
  text+=event(1,0,'return','0000000000000000')
  text+=''.join(event(i,i,'enter','not-returned') for i in range(2,129))
  d=decode(text);self.assertEqual(d['unpaired_returns'],[0]);self.assertEqual(len(d['pending_calls']),127)
if __name__=='__main__':unittest.main()
