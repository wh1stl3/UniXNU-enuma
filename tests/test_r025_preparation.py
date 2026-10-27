import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import r025_preparation as guard
from menu_window_scope import SCOPE
from run_enuma_entry_probe import require_hardware_review
from firmware_audit_policy import omitted_oem_modules

class R025Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);(self.root/'out/device-tests').mkdir(parents=True)
        self.digest='a'*64;self.execution=str(uuid4())
        self.meta=dict(hardware_review='R-025',image_sha256=self.digest,pixel_scope=copy.deepcopy(SCOPE))
        self.patcher=patch.object(guard,'IMAGE',self.digest);self.patcher.start();self.addCleanup(self.patcher.stop)
    def test_capture_required(self):
        with self.assertRaises(ValueError):guard.require_attempt(self.root,self.meta,self.execution,False)
        self.assertEqual(list((self.root/'out/device-tests').iterdir()),[])
    def test_atomic_single_shot(self):
        guard.require_attempt(self.root,self.meta,self.execution,True,True)
        with self.assertRaises(ValueError):guard.require_attempt(self.root,self.meta,str(uuid4()),True,True)
    def test_existing_issue_blocks_new_uuid(self):
        (self.root/'out/device-tests/current.local.json').write_text(json.dumps(dict(candidate_sha256=self.digest,issued_at='earlier')))
        with self.assertRaises(ValueError):guard.require_attempt(self.root,self.meta,self.execution,True)
    def test_changed_scope_rejected(self):
        self.meta['pixel_scope']['width']=801
        with self.assertRaises(ValueError):guard.require_attempt(self.root,self.meta,self.execution,True)
    def test_wrong_image_rejected(self):
        self.meta['image_sha256']='b'*64
        with self.assertRaises(ValueError):guard.require_attempt(self.root,self.meta,self.execution,True)
    def test_uuid_required(self):
        with self.assertRaises(ValueError):guard.require_attempt(self.root,self.meta,'not-a-uuid',True)
    def test_approval_binds_new_scope(self):
        approvals={'R-025':dict(status='approved',image_sha256=[self.digest],pixel_scope=copy.deepcopy(SCOPE))}
        require_hardware_review(self.meta,approvals)
        approvals['R-025']['pixel_scope']['framebuffer_writes_max']-=1
        with self.assertRaises(ValueError):require_hardware_review(self.meta,approvals)
    def test_pending_is_not_approval(self):
        with self.assertRaises(ValueError):require_hardware_review(self.meta,{'R-025':dict(status='pending',image_sha256=[self.digest],pixel_scope=SCOPE)})
    def test_new_flag_without_full_declaration_rejected(self):
        with self.assertRaises(ValueError):omitted_oem_modules(dict(firmware_configuration={'defines':{'ENUMA_BOUNDED_MENU':'1'}}),self.digest)
    def test_exact_policy_and_mutations(self):
        definitions=dict(ENUMA_BOUNDED_MENU='1',ENUMA_DIAG_SIMPLEFB='1',ENUMA_DIAG_DISABLE_UFS='1',
            ENUMA_DIAG_STAGE='13',ENUMA_DIAG_DETAIL_POINT='16',ENUMA_DIAG_GUID_ONLY='1',ENUMA_DIAG_DISPATCH_FALLBACK='0',
            ENUMA_DIAG_GOP_QUERY='1',ENUMA_DIAG_GOP_STEP='0',ENUMA_BOOT_LOG_REPLAY='0',ENUMA_PROBE_JOURNAL_REPLAY='0',
            ENUMA_NATIVE_ROUTE_CPU_TEXT='0',ENUMA_NATIVE_ROUTE_CPU_PATTERN='1',ENUMA_NATIVE_ROUTE_CPU_POLICY='1',ENUMA_NATIVE_ROUTE_ALPHA_VIEW='1')
        build=dict(complete=True,profile='menu-window',fd_sha256=self.digest,bounded_menu=True,menu_window_scope=copy.deepcopy(SCOPE),
                   hardware_review_required='R-025',firmware_configuration={'defines':definitions},diagnostic_omitted_oem_modules=['CPRDxe','DisplayDxe','UFSDxe'])
        self.assertEqual(omitted_oem_modules(build,self.digest),frozenset(['CPRDxe','DisplayDxe','UFSDxe']))
        for key in definitions:
            mutated=copy.deepcopy(build);mutated['firmware_configuration']['defines'][key]='9'
            with self.subTest(key=key),self.assertRaises(ValueError):omitted_oem_modules(mutated,self.digest)
        mutated=copy.deepcopy(build);mutated['menu_window_scope']['width']=1600
        with self.assertRaises(ValueError):omitted_oem_modules(mutated,self.digest)
        with self.assertRaises(ValueError):omitted_oem_modules(build,'b'*64)
if __name__=='__main__':unittest.main()
