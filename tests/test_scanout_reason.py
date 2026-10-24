import math,unittest
from scripts.decode_scanout_reason import decode_pair
class ReasonDecoderTests(unittest.TestCase):
 def test_six_classes_and_modest_noise(self):
  for c in range(6):
   for fnoise,rnoise in ((0,0),(0.4,-0.3),(-0.6,0.4)):
    with self.subTest(c=c,fnoise=fnoise,rnoise=rnoise):
     d=decode_pair(17,17+c*4+fnoise,17+(5-c)*4+rnoise)
     self.assertTrue(d['accepted']);self.assertEqual(d['class_number'],c)
 def test_changed_class_between_trials(self):
  for a in range(6):
   for b in range(6):
    if a!=b:self.assertFalse(decode_pair(17,17+a*4,17+(5-b)*4)['accepted'])
 def test_core_fallback_or_failed_encoding_not_a_class(self):
  for a,b in ((5,0),(0,5),(0,0),(5,5)):
   self.assertFalse(decode_pair(17,17+a,17+b)['accepted'])
 def test_excessive_jitter_and_stale_baseline(self):
  self.assertFalse(decode_pair(17,27.1,29)['accepted'])
  self.assertFalse(decode_pair(17,26.8,30.8)['accepted'])
 def test_invalid(self):
  for x in (math.nan,math.inf,0,-1,'17',True):self.assertFalse(decode_pair(17,x,20)['accepted'])
if __name__=='__main__':unittest.main()
