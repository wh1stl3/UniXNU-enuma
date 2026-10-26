"""R-018 remains an exact-image gate and cannot enter the camera-free runner."""
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from native_pixel_scope import SCOPE,TEXT_SCOPE
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

    def test_text_scope_cannot_reuse_contrast_approval(self):
        meta=dict(hardware_review='R-019',image_sha256='text',pixel_scope=TEXT_SCOPE)
        approved=dict(status='approved',image_sha256=['text'],pixel_scope=TEXT_SCOPE)
        require_hardware_review(meta,{'R-019':approved})
        for entry in [{**approved,'status':'pending'},{**approved,'pixel_scope':SCOPE},
                      {**approved,'image_sha256':['contrast']}]:
            with self.assertRaises(ValueError):require_hardware_review(meta,{'R-019':entry})
        with self.assertRaises(ValueError):require_hardware_review(meta,{'R-018':approved})

    def test_log_scope_has_independent_authorization_and_timing(self):
        from native_pixel_scope import LOG_SCOPE
        meta=dict(hardware_review='R-020',image_sha256='log',pixel_scope=LOG_SCOPE)
        approved=dict(status='approved',image_sha256=['log'],pixel_scope=LOG_SCOPE)
        require_hardware_review(meta,{'R-020':approved})
        for changes in [{'pixel_scope':TEXT_SCOPE},{'pixel_scope':SCOPE},{'status':'consumed'},{'image_sha256':['old']}]:
            with self.assertRaises(ValueError):require_hardware_review(meta,{'R-020':{**approved,**changes}})
        plan=make_pixel_plan(Path(__file__).resolve().parents[1],'R-020')
        self.assertEqual(plan['sampler_seconds'],[0,2.4])
        for a,b in zip(plan['code_windows_after_issue'],plan['code_windows_after_issue'][1:]):self.assertLess(a[1],b[0])

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
        text_plan=make_pixel_plan(Path(__file__).resolve().parents[1],'R-019')
        self.assertEqual(text_plan['code_windows_after_issue'],plan['code_windows_after_issue'])
        self.assertTrue(text_plan['declared_profile'].startswith('R-019'))
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
