"""New diagnostic replay cannot borrow an old hardware review or budget."""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from firmware_audit_policy import omitted_oem_modules

class DiagnosticPolicyTests(unittest.TestCase):
    def fixture(self):
        b=json.loads((ROOT/'out/inherited-gop/qualified-dxe-log-8s-8680ea7/firmware-build.json').read_text())
        b['firmware_configuration']['defines'].update(ENUMA_BOOT_LOG_REPLAY='3',ENUMA_PROBE_JOURNAL_REPLAY='1')
        b.update(diagnostic_pixel_log=True,hardware_review_required='R-024',attributed_pixel_scope=dict(origin_x=64,origin_y=96,width=320,height=160,hold_us=8000000,barriers_max=3))
        b['inherited_video_compiled_contract'].update(maximum_framebuffer_reads=153600,framebuffer_writes=102400)
        return b
    def test_valid_new_profile(self):
        b=self.fixture()
        self.assertEqual(omitted_oem_modules(b,b['fd_sha256']),frozenset(['CPRDxe','DisplayDxe','UFSDxe']))
    def test_reject_wrong_profile_or_old_authorization(self):
        for key,value in [('hardware_review_required','R-023'),('hardware_review_required','R-022'),('diagnostic_pixel_log',False),('diagnostic_pixel_log',1),('attributed_pixel_log',True),('attributed_pixel_scope',{}),('boot_log_hold_seconds',2)]:
            b=self.fixture();b[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError): omitted_oem_modules(b,b['fd_sha256'])
    def test_reject_macro_and_budget_drift(self):
        for key,value in [('ENUMA_BOOT_LOG_REPLAY','2'),('ENUMA_BOOT_LOG_REPLAY','1'),('ENUMA_PROBE_JOURNAL_REPLAY','0'),('ENUMA_BOOT_JOURNAL','0')]:
            b=self.fixture();b['firmware_configuration']['defines'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError): omitted_oem_modules(b,b['fd_sha256'])
        for key,value in [('maximum_framebuffer_reads',153601),('framebuffer_writes',102401),('maximum_wait_calls',6),('protocol_published',True),('cache_maintenance',True)]:
            b=self.fixture();b['inherited_video_compiled_contract'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError): omitted_oem_modules(b,b['fd_sha256'])

if __name__=='__main__': unittest.main()
