import unittest,sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from decode_oem_exception import decode
class ExceptionPages(unittest.TestCase):
 def setUp(self):
  self.pages=[['E11C0000000000000000','O0000000010000120','S0000000096000004','C0000000000000000','G0000000000001234'],['E12C0000000000000101','O0000000010000000','S0000000000000120','C0000000000010000','G0000000000001234'],['E13C0000000010000100','G04138022f06c74f79','G19c947e33b511a4e7','S00000000000003c5','G0000000000001234']]
 def test_full_and_partial(self):
  inv=[dict(guid='4138022f-06c7-4f79-9c94-7e33b511a4e7',image_size=65536,name='DisplayDxe',pe_sha256='test',sections=[dict(rva=256,bytes=512,executable=True)])]
  r=decode(self.pages,0x1234,inv);self.assertTrue(r['owner_fd_verified']);self.assertEqual(r['module'],'DisplayDxe');self.assertTrue(r['far_usable_for_abort'])
  r=decode(self.pages[:1],0x1234);self.assertIsNone(r['owner']);self.assertFalse(r['complete'])
  r=decode(self.pages[:2],0x1234);self.assertIsNone(r['owner']['guid']);self.assertFalse(r['owner_fd_verified'])
 def test_wrong_session_truncation_order(self):
  for pages in (self.pages[::-1],[],self.pages*2,[self.pages[0][:-1]],[[x[:-1] for x in self.pages[0]]]):
   with self.assertRaises(ValueError):decode(pages,0x1234)
  with self.assertRaises(ValueError):decode(self.pages,0x4321)
 def test_owner_mismatch(self):
  for row,value in ((0,'E12C0000000000000103'),(1,'O0000000010000004'),(2,'S0000000000010000')):
   p=copy.deepcopy(self.pages);p[1][row]=value
   with self.assertRaises(ValueError):decode(p,0x1234)
 def test_far_validity(self):
  p=copy.deepcopy(self.pages);p[0][2]='S0000000096000410';self.assertFalse(decode(p,0x1234)['far_usable_for_abort'])
  p[0][2]='S00000000bc000000';self.assertFalse(decode(p,0x1234)['far_usable_for_abort'])
 def test_unknown_guid_not_guessed(self):
  r=decode(self.pages,0x1234,[]);self.assertFalse(r['owner_fd_verified'])
if __name__=='__main__':unittest.main()
