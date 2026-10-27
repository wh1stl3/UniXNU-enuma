import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from decode_oem_progress_page import decode
class Pages(unittest.TestCase):
    def page(self,phase):
        ret=phase in (2,4,5)
        return '\n'.join([('S' if ret else 'E')+f'{phase:02x}'+(' '*17 if phase==5 else 'C'+f'{7:016x}'),
          'Q'+f'{9:016x}'+' '*3,' '*20 if phase==5 else 'O'+f'{0x1bce0:016x}'+' '*3,
          'S'+f'{0x800000000000000e:016x}'+' '*3 if ret else 'E'+' '*19,'G'+f'{123:016x}'+' '*3])
    def test_all_phases(self):
        for phase in range(1,6):
            r=decode(self.page(phase),123);self.assertEqual(r['phase'],phase)
            self.assertEqual(r['returned'],phase in (2,4,5))
    def test_session(self):self.assertRaises(ValueError,decode,self.page(1),124)
    def test_truncation(self):self.assertRaises(ValueError,decode,self.page(2)[:-1],123)
    def test_entry_status(self):self.assertRaises(ValueError,decode,self.page(1).replace('E'+' '*19,'S'+('0'*16)+' '*3),123)
    def test_phase_prefix(self):self.assertRaises(ValueError,decode,'E'+self.page(2)[1:],123)
    def test_driver_caller(self):self.assertRaises(ValueError,decode,self.page(5).replace('\n'+' '*20+'\n','\nO'+'0'*16+' '*3+'\n'),123)
if __name__=='__main__':unittest.main()
