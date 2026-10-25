"""R-018 remains an exact-image gate and cannot enter the camera-free runner."""
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from native_pixel_scope import SCOPE
from native_mask_decode import make_pixel_plan
from native_route_decode import decode,CPU_PATTERN_CATEGORIES
from run_enuma_entry_probe import require_hardware_review
import run_system_transport_trial as runner

class PixelScopeTests(unittest.TestCase):
    def test_exact_approval(self):
        meta=dict(hardware_review='R-018',image_sha256='abc',pixel_scope=SCOPE)
        approved=dict(status='approved',image_sha256=['abc'],pixel_scope=SCOPE)
        require_hardware_review(meta,{'R-018':approved})
        for key,value in [('status','pending'),('image_sha256',['different']),('pixel_scope',{})]:
            with self.assertRaises(ValueError):require_hardware_review(meta,{'R-018':{**approved,key:value}})
        changed=copy.deepcopy(SCOPE);changed['hold_us']=500001
        with self.assertRaises(ValueError):require_hardware_review({**meta,'pixel_scope':changed},{'R-018':approved})

    def test_camera_free_rejected_before_device(self):
        with patch.object(runner.subprocess,'run') as called,self.assertRaises(ValueError):
            runner.run_without_camera(dict(native_route_cpu_pattern=True,trial_kind='native-video-route',
                pixel_access=True,gop_published=False,boot_clock_capture=True,framebuffer_writes=2048),Path('unused'))
        called.assert_not_called()
        with patch.object(runner,'qualification',return_value=({'native_route_cpu_pattern':True},Path('unused'))), \
             patch.object(sys,'argv',['runner','--no-camera']),patch.object(runner,'run_without_camera') as called, \
             self.assertRaises(SystemExit):runner.main()
        called.assert_not_called()

    def test_five_results_and_restore_hard_stop(self):
        plan=make_pixel_plan(Path(__file__).resolve().parents[1])
        self.assertEqual(plan['sampler_seconds'],[0,.9])
        windows=plan['code_windows_after_issue']
        for a,b in zip(windows,windows[1:]):self.assertLess(a[1],b[0])
        flags=dict(structure=True,global_output=True,alpha_view=True,cpu_stage1=True,cpu_policy=True,
                   cpu_read=True,cpu_barrier=True,cpu_roi=True,cpu_pattern=True)
        for n,(lo,hi) in enumerate(windows,1):
            middle=(lo+hi)/2
            result=decode(dict(origin_after_issue_lower=middle,origin_after_issue_upper=middle+.01),plan,**flags)
            self.assertEqual(result['category'],CPU_PATTERN_CATEGORIES[str(n)])
            self.assertEqual(result['stop_additional_trials'],n==4)

if __name__=='__main__':unittest.main()
