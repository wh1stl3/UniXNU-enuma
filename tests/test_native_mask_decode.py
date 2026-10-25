import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from native_mask_decode import decode,make_plan

class MaskDecodeTests(unittest.TestCase):
    def test_fixed_windows_and_gap(self):
        p=make_plan(Path(__file__).resolve().parents[1])
        for i,(lo,hi) in enumerate(p['code_windows_after_issue']):
            middle=(lo+hi)/2
            r=decode(dict(origin_after_issue_lower=middle-.04,origin_after_issue_upper=middle+.04),p)
            self.assertEqual(r['warning_code'],i+1)
            self.assertEqual(r['mask'],i if i<4 else None)
            self.assertFalse(r['stop_additional_trials'])
            r=decode(dict(origin_after_issue_lower=lo-.01,origin_after_issue_upper=lo+.02),p)
            self.assertEqual(r['conclusion'],'ambiguous')
        self.assertEqual(decode(dict(origin_after_issue_lower=0,origin_after_issue_upper=.1),p)['conclusion'],'ambiguous')
        for a,b in [(1,2),(2,1),(float('nan'),2)]:
            with self.assertRaises(ValueError):decode(dict(origin_after_issue_lower=a,origin_after_issue_upper=b),p)

if __name__=='__main__':unittest.main()
