import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from boot_origin import bound

class BootOriginTests(unittest.TestCase):
    def samples(self):
        return [dict(start=100+n,end=100.04+n,stdout=f'{20+n}.00 10.00\n12345678-1234-1234-1234-123456789abc\n') for n in range(3)]
    def test_quantization_and_transport_bound(self):
        r=bound(self.samples(),70)
        self.assertAlmostEqual(r['origin_after_issue_lower'],9.99)
        self.assertAlmostEqual(r['origin_after_issue_upper'],10.04)
        self.assertFalse(r['calibrated_firmware_delay'])
    def test_refuse_stale_boot_and_invalid_observation(self):
        old=bound(self.samples())['boot_id_sha256']
        with self.assertRaisesRegex(ValueError,'old boot'):bound(self.samples(),70,old)
        bad=[]
        for key,value in [('stdout','nan 0.00\ninvalid'),('start',float('nan')),('end',99),('end',105)]:
            s=copy.deepcopy(self.samples());s[0][key]=value;bad.append(s)
        s=self.samples();s[1]['stdout']=s[1]['stdout'].replace('9abc','9abd');bad.append(s)
        s=self.samples();s[1]['stdout']=s[1]['stdout'].replace('21.00','18.00');bad.append(s)
        s=self.samples();s[1]['start']=99;bad.append(s)
        s=self.samples();s[1]['stdout']=s[1]['stdout'].replace('21.00','21.50');bad.append(s)
        # A single broad sample is narrowed by the remaining two; make all broad.
        bad.pop(3)
        s=self.samples()
        for item in s:item['end']=item['start']+.4
        bad.append(s)
        for s in bad:
            with self.subTest(samples=s),self.assertRaises(ValueError):bound(s,70)
        with self.assertRaises(ValueError):bound(self.samples(),90)

if __name__=='__main__':unittest.main()
