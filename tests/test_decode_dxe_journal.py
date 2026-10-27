import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from decode_dxe_journal import decode, inf_catalog

GUID='11223344-5566-7788-99aa-bbccddeeff00'
def line(seq,point,phase,status,guid=GUID):
    return f'DXE seq={seq:016x} p={point:08x} phase={phase} o=00000000 s={status} guid={guid}\n'

class Attribution(unittest.TestCase):
    def test_current_provider_is_not_previous_return(self):
        text='DXE cached dropped=0000000000000000 next=0000000000000003\n'
        text+=line(0,15,'before-start','not-returned')
        text+=line(1,13,'start-return','8000000000000001')
        text+=line(2,15,'before-start','not-returned')
        result=decode(text)
        self.assertEqual(result['events'][1]['preceding_start_sequence'],0)
        self.assertEqual(result['unclosed_before_start'],{GUID:[2]})
        self.assertFalse(result['screen_log_verified'])

    def test_reject_incomplete_or_invented_return(self):
        header='DXE cached dropped=0000000000000000 next=0000000000000001\n'
        good=line(0,15,'before-start','not-returned')
        for text in [header,header+good+good,header+good.replace('not-returned','0000000000000000'),
                     header+good.replace('before-start','start-return'),header+good.replace('seq=0000000000000000','seq=0000000000000001'),
                     header+good.replace(GUID,'1'*36),header+good.replace('not-returned','not-returne?')]:
            with self.subTest(text=text),self.assertRaises(ValueError): decode(text)

    def test_empty_and_loss(self):
        self.assertEqual(decode('DXE cached dropped=0000000000000000 next=0000000000000000\n')['events'],[])
        with self.assertRaises(ValueError):decode('DXE cached dropped=0000000000000001 next=0000000000000000\n')

    def test_inf_catalog_binds_bytes_and_keeps_duplicate_guids(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=Path(tmp)/'a.inf';b=Path(tmp)/'b.inf'
            a.write_text('[Defines]\nBASE_NAME = DriverA\nFILE_GUID = '+GUID+'\n[Sources]\nFake.c\n')
            b.write_text(a.read_text().replace('DriverA','DriverB'))
            catalog=inf_catalog([a,b]);self.assertEqual(len(catalog[GUID]),2)
            self.assertNotEqual(catalog[GUID][0]['sha256'],catalog[GUID][1]['sha256'])
            a.write_text('[Sources]\nBASE_NAME = forged\nFILE_GUID = '+GUID+'\n')
            with self.assertRaises(ValueError):inf_catalog([a])

if __name__=='__main__':unittest.main()
