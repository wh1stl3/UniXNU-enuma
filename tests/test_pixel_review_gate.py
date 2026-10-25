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
    def test_r017_exact_scope_and_image_required(self):
        scope={'base':'0xB0000000','size':'0x200000','marker_bytes':44,'stage':10}
        meta={'hardware_review':'R-017','image_sha256':'a'*64,'ramoops_scope':scope}
        approval={'R-017':{'status':'approved','image_sha256':['a'*64],'ramoops_scope':scope}}
        probe.require_hardware_review(meta,approval)
        for changes in [{'ramoops_scope':{}},{'image_sha256':'b'*64}]:
            with self.assertRaises(ValueError):probe.require_hardware_review({**meta,**changes},approval)
    def test_map_control_does_not_reauthorize_writer(self):
        scope={'base':'0xB0000000','size':'0x200000','marker_bytes':0,'stage':10,'reset':'cold'}
        meta={'hardware_review':'R-017-MAP','image_sha256':'a'*64,'ramoops_scope':scope}
        approval={'R-017-MAP':{'status':'approved','image_sha256':['a'*64],'ramoops_scope':scope},
                  'R-017':{'status':'consumed','image_sha256':['b'*64]}}
        probe.require_hardware_review(meta,approval)
        with self.assertRaises(ValueError):probe.require_hardware_review({**meta,'ramoops_scope':{**scope,'marker_bytes':44}},approval)
        with self.assertRaisesRegex(ValueError,'not approved'):probe.require_hardware_review({'hardware_review':'R-017','image_sha256':'b'*64},approval)
    def test_header_read_scope_cannot_expand(self):
        scope={'base':'0xB0000000','size':'0x200000','marker_bytes':0,
               'header_read_offsets':[0,4,8],'reset':'cold'}
        meta={'hardware_review':'R-017-READ','image_sha256':'c'*64,'ramoops_scope':scope}
        approval={'R-017-READ':{'status':'approved','image_sha256':['c'*64],'ramoops_scope':scope}}
        probe.require_hardware_review(meta,approval)
        for changes in [{'marker_bytes':44},{'header_read_offsets':[0,4,8,12]},{'reset':'warm'}]:
            with self.assertRaises(ValueError):probe.require_hardware_review({**meta,'ramoops_scope':{**scope,**changes}},approval)
    def test_pending_main_never_calls_device_tools(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'out',prefix='pixel-review-') as td:
            root=Path(td).resolve();image=root/'out/protected.img';image.parent.mkdir();image.write_bytes(b'protected fixture')
            image.with_suffix('.json').write_text(json.dumps({'image_sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'hardware_review':'R-005'}))
            config=root/'config';config.mkdir();(config/'hardware-review-approvals.json').write_text(json.dumps({'R-005':{'status':'pending','image_sha256':[]}}))
            with patch.object(probe,'ROOT',root),patch.object(sys,'argv',['probe','--image',str(image),'--label','dxe-driver-return']),patch.object(probe.subprocess,'run',side_effect=AssertionError('no device tools')) as call:
                with self.assertRaisesRegex(ValueError,'not approved'):probe.main()
                call.assert_not_called()
if __name__=='__main__':unittest.main()
