import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from decode_cached_log_text import decode_lines
class Format(unittest.TestCase):
    def test_complete(self):
        a=decode_lines(['C0d Odeadbeef+  ','S80000000       ',' 00000001       '])
        self.assertEqual(a['status_hex'],'8000000000000001');self.assertEqual(a['ordinal_hex'],'deadbeef')
        self.assertTrue(a['efi_error_bit']);self.assertTrue(a['older_records_lost']);self.assertFalse(a['screen_log_verified'])
    def test_warning_and_no_loss(self):
        a=decode_lines(['C0d O00000000','S00000000',' 00000005'])
        self.assertFalse(a['efi_error_bit']);self.assertFalse(a['older_records_lost'])
    def test_unclear_and_wrong_layout(self):
        good=['C0d O00000001','S80000000',' 00000001']
        bad=[[],good[:2],good+['extra'],[None,*good[1:]]]
        for row,replacement in [(0,'C0d O0000000?'),(0,'C0d 000000001'),(0,'C0d ODEADBEEF'),(0,'C0d O00000001++++'),(1,'S8000000O'),(1,'S8000000'),(2,'00000001'),(2,' 00000001\n'),(2,' 00000001        ')]:
            a=good.copy();a[row]=replacement;bad.append(a)
        for a in bad:
            with self.subTest(a=a),self.assertRaises(ValueError):decode_lines(a)
if __name__=='__main__':unittest.main()
