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
    def test_early_call_binding(self):
        self.assertRaises(ValueError,decode,self.page(1),123,'oem-early-v3')
        page=self.page(1).replace('C'+f'{7:016x}','C'+f'{1:016x}')
        self.assertEqual(decode(page,123,'oem-early-v3')['call'],1)
    def test_early_semantics(self):
        self.assertEqual(decode(self.page(3),123,'oem-early-v3')['event'],'kernel-locate-before')
        self.assertRaises(ValueError,decode,self.page(3),123,'unknown')
    def test_post_scope(self):
        for phase in (1,2):
            page=self.page(phase).replace('C'+f'{7:016x}','C'+f'{4:016x}')
            self.assertEqual(decode(page,123,'oem-post-kernel-v4')['call'],4)
            self.assertRaises(ValueError,decode,page,123,'oem-early-v3')
        self.assertEqual(decode(self.page(3),123,'oem-post-kernel-v4')['event'],'sid-locate-before')
        self.assertEqual(decode(self.page(4),123,'oem-post-kernel-v4')['status'],'0x800000000000000e')

    def test_registration_scope(self):
        for phase in (1,2):
            page=self.page(phase).replace('C'+f'{7:016x}','C'+f'{5:016x}').replace('O'+f'{0x1bce0:016x}','O'+f'{0x5cc8:016x}')
            self.assertEqual(decode(page,123,'oem-registration-v5')['call'],5)
            self.assertRaises(ValueError,decode,page.replace('5cc8','5cc4'),123,'oem-registration-v5')
            self.assertRaises(ValueError,decode,page,123,'oem-post-kernel-v4')

    def test_main_entry_scope(self):
        page=self.page(1).replace('C'+f'{7:016x}','C'+f'{6:016x}').replace('O'+f'{0x1bce0:016x}','O'+f'{0x3608:016x}')
        self.assertEqual(decode(page,123,'oem-main-entry-v6')['event'],'main-query-before')
        self.assertEqual(decode(page.replace('C0000000000000006','C0000000000000007'),123,'oem-main-entry-v6')['call'],7)
        for bad in [page.replace('3608','3604'),page.replace('C0000000000000006','C0000000000000005'),self.page(2),self.page(4)]:
            self.assertRaises(ValueError,decode,bad,123,'oem-main-entry-v6')
        self.assertEqual(decode(self.page(5),123,'oem-main-entry-v6')['event'],'core-start-image-return')

    def test_far_summary(self):
        rows=self.page(5).splitlines();rows[0]='S05C'+f'{0xc1:016x}';rows[2]='O'+f'{0x3608:016x}'+' '*3
        page='\n'.join(rows);d=decode(page,123,'oem-far-chain-v7')
        self.assertTrue(d['milestones']['dxe-dispatch-complete']);self.assertFalse(d['milestones']['sid-entered'])
        self.assertEqual(d['status'],'0x800000000000000e')
        for flags in (0,0x41,0x4000|0xc1,0x2c1,0x8c1):
            bad=list(rows);bad[0]='S05C'+f'{flags:016x}'
            self.assertRaises(ValueError,decode,'\n'.join(bad),123,'oem-far-chain-v7')
        self.assertRaises(ValueError,decode,page,124,'oem-far-chain-v7')

if __name__=='__main__':unittest.main()
