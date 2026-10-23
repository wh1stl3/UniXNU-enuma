"""Protected-image review checks do not invoke ADB or fastboot."""
import hashlib,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('probe',ROOT/'scripts/run_enuma_entry_probe.py');probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
class ReviewGateTests(unittest.TestCase):
    def test_pending_rejected(self):
        with self.assertRaisesRegex(ValueError,'not approved'):probe.require_hardware_review({'hardware_review':'R-005','image_sha256':'a'*64},{'R-005':{'status':'pending','image_sha256':['a'*64]}})
    def test_wrong_image_rejected(self):
        with self.assertRaisesRegex(ValueError,'not approved'):probe.require_hardware_review({'hardware_review':'R-005','image_sha256':'b'*64},{'R-005':{'status':'approved','image_sha256':['a'*64]}})
    def test_consumed_single_trial_rejected(self):
        with self.assertRaisesRegex(ValueError,'not approved'):probe.require_hardware_review({'hardware_review':'R-005','image_sha256':'a'*64},{'R-005':{'status':'consumed','image_sha256':['a'*64]}})
    def test_exact_approved_image(self):
        probe.require_hardware_review({'hardware_review':'R-005','image_sha256':'a'*64},{'R-005':{'status':'approved','image_sha256':['a'*64]}})
    def test_unknown_review_rejected(self):
        with self.assertRaisesRegex(ValueError,'Unknown'):probe.require_hardware_review({'hardware_review':'unknown','image_sha256':'a'*64},{})
    def test_untagged_unchanged(self):
        probe.require_hardware_review({'image_sha256':'a'*64},{})
    def test_pending_main_never_calls_device_tools(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'out',prefix='pixel-review-') as td:
            root=Path(td).resolve();image=root/'out/protected.img';image.parent.mkdir();image.write_bytes(b'protected fixture')
            image.with_suffix('.json').write_text(json.dumps({'image_sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'hardware_review':'R-005'}))
            config=root/'config';config.mkdir();(config/'hardware-review-approvals.json').write_text(json.dumps({'R-005':{'status':'pending','image_sha256':[]}}))
            with patch.object(probe,'ROOT',root),patch.object(sys,'argv',['probe','--image',str(image),'--label','dxe-driver-return']),patch.object(probe.subprocess,'run',side_effect=AssertionError('no device tools')) as call:
                with self.assertRaisesRegex(ValueError,'not approved'):probe.main()
                call.assert_not_called()
if __name__=='__main__':unittest.main()
