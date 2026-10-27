"""Reject ambiguous or contradictory new-page transcripts instead of guessing."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from decode_diagnostic_pixel_log import decode_lines
class DiagnosticDecoderTests(unittest.TestCase):
    def page(self,marker='C',status='0000000000000000'):
        return [marker+'0d O0000001f+','S'+status,'Q00000000000000b9','G004de8591d2b34077','G1bbbeb12070094eb6']
    def test_three_status_classes(self):
        for marker,status in [('C','0000000000000000'),('W','0000000000000001'),('E','8000000000000001')]:
            d=decode_lines(self.page(marker,status));self.assertEqual(d['severity'],marker)
            self.assertEqual(d['guid'],'04de8591-d2b3-4077-bbbe-b12070094eb6')
            self.assertFalse(d['current_provider_return']);self.assertFalse(d['screen_log_verified'])
    def test_reject_contradictory_severity(self):
        for marker,status in [('C','0000000000000001'),('W','0000000000000000'),('E','0000000000000001'),('W','8000000000000001')]:
            with self.assertRaises(ValueError):decode_lines(self.page(marker,status))
    def test_reject_missing_extra_and_obscured(self):
        page=self.page()
        for damaged in [page[:4],page+[''],['?'+page[0][1:]]+page[1:],[page[0].replace('O','0')]+page[1:]]:
            with self.assertRaises(ValueError):decode_lines(damaged)
    def test_reject_bad_sequence_width_and_labels(self):
        for row in range(1,5):
            p=self.page();p[row]=p[row][:-1]
            with self.assertRaises(ValueError):decode_lines(p)
        p=self.page();p[1]='5'+p[1][1:]
        with self.assertRaises(ValueError):decode_lines(p)
if __name__=='__main__':unittest.main()
