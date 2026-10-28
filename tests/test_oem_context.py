import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from decode_oem_exception import decode
from oem_runtime_candidate import limits_for
class Context(unittest.TestCase):
 def pages(self):
  values=[(0,0x9a6fd140,0x96000047,0xaeb0004),(0,0,0,0),(0,0,0,0),(0,0,0xaeb00b0,0xae00000),(0x1000,0,0x1234,1),(0x104,0xf,0xf,0xb00b0)]
  pages=[]
  for i,row in enumerate(values,1):
   prefixes=['G0','G1','S'] if i==3 else ['O','S','C']
   pages.append([f'E1{i}C{row[0]:016X}']+[p+f'{v:016X}' for p,v in zip(prefixes,row[1:])]+['G0000000000001234'])
  return pages
 def test_complete_and_partial(self):
  p=self.pages();r=decode(p,0x1234,context=True)
  self.assertTrue(r['complete']);self.assertTrue(r['translation']['probe_valid']);self.assertEqual(r['parameters']['x9'],'0xaeb00b0')
  for n in range(1,6):self.assertFalse(decode(p[:n],0x1234,context=True)['complete'])
  with self.assertRaises(ValueError):decode(p,0x1234)
 def test_malformed_extra(self):
  for idx,value in [(0,'E17C0000000000000104'),(4,'G0000000000004321'),(1,'O0000')]:
   p=self.pages();p[5][idx]=value
   with self.assertRaises(ValueError):decode(p,0x1234,context=True)
 def test_refusal_not_success(self):
  p=self.pages();p[5][0]='E16C0000000000000004'
  self.assertFalse(decode(p,0x1234,context=True)['translation']['probe_valid'])
 def test_total_hold_preserved(self):
  l=limits_for('oem-exception-context-v14')
  self.assertEqual(l['max_windows']*l['hold_us'],24000000);self.assertEqual(l['max_boots'],1)
if __name__=='__main__':unittest.main()
