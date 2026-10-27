import contextlib,io,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import run_deferred_menu_trial as trial
class TrialBoundary(unittest.TestCase):
 def test_default_is_offline(self):
  with patch.object(sys,'argv',['trial','--preparation','x']),patch.object(trial,'qualification',return_value=({'image_sha256':'x','scope':{}},Path('x'))),patch.object(trial.subprocess,'call',side_effect=AssertionError('device call')) as boot,contextlib.redirect_stdout(io.StringIO()):
   self.assertEqual(trial.main(),0);boot.assert_not_called()
 def test_capture_required_before_child(self):
  with patch.object(sys,'argv',['trial','--preparation','x','--execute']),patch.object(trial,'qualification',return_value=({},Path('x'))),patch.object(trial.subprocess,'call',side_effect=AssertionError('device call')) as boot:
   with self.assertRaises(ValueError):trial.main()
   boot.assert_not_called()
 def test_refused_qualification_does_not_start_child(self):
  with patch.object(sys,'argv',['trial','--preparation','x','--execute','--human-camera-ready','--execution-id','20d0ee21-23f7-4b00-90b9-10bb0be75b38']),patch.object(trial,'qualification',side_effect=ValueError('pending approval')),patch.object(trial.subprocess,'call') as boot:
   with self.assertRaises(ValueError):trial.main()
   boot.assert_not_called()
if __name__=='__main__':unittest.main()
