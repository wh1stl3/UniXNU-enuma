"""A diagnostic exclusion must never hide a normal build's missing driver."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from firmware_audit_policy import omitted_oem_modules


class FirmwareAuditPolicyTests(unittest.TestCase):
    def test_native_pixel_is_protected_and_never_declared_read_only(self):
        value=self.fixture()
        value.update(native_route_cpu_pattern=True,inherited_video_audit_read_only=False,
            inherited_video_terminal=True,diagnostic_dispatch_completion_fallback=False,
            diagnostic_simplefb_metadata_only=False,diagnostic_gop_step=0,diagnostic_gop_query=1,
            diagnostic_omitted_oem_modules=['CPRDxe','DisplayDxe','UFSDxe'],
            hardware_review_required='R-018',value_probe={'source':'off'},
            inherited_video_compiled_contract=dict(maximum_read_callbacks=660,maximum_wait_calls=5,
                maximum_framebuffer_reads=3072,framebuffer_writes=2048,pixel_access=True,
                cache_maintenance=False,protocol_published=False))
        defs=value['firmware_configuration']['defines']
        defs['ENUMA_DIAG_SIMPLEFB']='1'
        for name in ['CPU_PATTERN','CPU_ROI','CPU_BARRIER','CPU_READ','CPU_POLICY','CPU_STAGE1',
                     'ALPHA_VIEW','GLOBAL_OUTPUT','STRUCTURE','AUDIT']:defs['ENUMA_NATIVE_ROUTE_'+name]='1'
        self.assertEqual(omitted_oem_modules(value,'a'*64),frozenset(value['diagnostic_omitted_oem_modules']))
        text=copy.deepcopy(value);text.update(native_route_cpu_text=True,hardware_review_required='R-019')
        text['firmware_configuration']['defines']['ENUMA_NATIVE_ROUTE_CPU_TEXT']='1'
        text['inherited_video_compiled_contract'].update(maximum_framebuffer_reads=12288,framebuffer_writes=8192)
        self.assertEqual(omitted_oem_modules(text,'a'*64),frozenset(text['diagnostic_omitted_oem_modules']))
        text['hardware_review_required']='R-018'
        with self.assertRaises(ValueError):omitted_oem_modules(text,'a'*64)
        for key,bad in [('inherited_video_audit_read_only',True),('hardware_review_required',None),
                        ('inherited_video_terminal',False),('diagnostic_simplefb_metadata_only',True)]:
            candidate=copy.deepcopy(value);candidate[key]=bad
            with self.subTest(key=key),self.assertRaises(ValueError):omitted_oem_modules(candidate,'a'*64)
        for key in value['inherited_video_compiled_contract']:
            candidate=copy.deepcopy(value);candidate['inherited_video_compiled_contract'][key]=None
            with self.subTest(key=key),self.assertRaises(ValueError):omitted_oem_modules(candidate,'a'*64)

    def test_control_requires_video_profile_and_boolean(self):
        for value in [dict(inherited_video_entry_control=True),dict(inherited_video_entry_control='1')]:
            with self.assertRaises(ValueError): omitted_oem_modules(value,'a'*64)

    def test_terminal_profile_cannot_hide_dispatcher_fallback(self):
        for value in [dict(inherited_video_terminal=True),dict(inherited_video_terminal='1'),
                      dict(inherited_video_terminal=True,inherited_video_audit_read_only=True,
                           diagnostic_dispatch_completion_fallback=True,diagnostic_gop_query=1)]:
            with self.assertRaises(ValueError): omitted_oem_modules(value,'a'*64)
    def test_video_audit_requires_read_only_profile_not_metadata_or_pixels(self):
        value=self.fixture()
        value.update(inherited_video_audit_read_only=True,diagnostic_simplefb_metadata_only=False,
                     diagnostic_gop_step=0,diagnostic_gop_query=1,value_probe={'source':'off'},
                     gop_backend_selftest_ram_only=False,diagnostic_omitted_oem_modules=['CPRDxe','DisplayDxe','UFSDxe'])
        value['firmware_configuration']['defines'].update(ENUMA_DIAG_SIMPLEFB='1',ENUMA_DIAG_PIXEL_PREVIEW='0')
        self.assertEqual(omitted_oem_modules(value,'a'*64),frozenset(value['diagnostic_omitted_oem_modules']))
        for key,bad in [('diagnostic_simplefb_metadata_only',True),('diagnostic_pixel_preview',True),
                        ('diagnostic_gop_step',13),('diagnostic_gop_query',0),('value_probe',{'source':'raw'}),
                        ('inherited_video_audit_read_only','1'),('gop_backend_selftest_ram_only',True)]:
            candidate=copy.deepcopy(value);candidate[key]=bad
            with self.subTest(key=key),self.assertRaises(ValueError): omitted_oem_modules(candidate,'a'*64)

    def fixture(self):
        return {'complete':True,'fd_sha256':'a'*64,'diagnostic_omitted_oem_modules':['UFSDxe'],
                'firmware_configuration':{'defines':{'ENUMA_DIAG_DISABLE_UFS':'1'}}}

    def test_topology_query_needs_exact_terminal_profile_and_flags(self):
        value=self.fixture()
        value.update(inherited_video_audit_read_only=True,inherited_video_terminal=True,
                     inherited_video_topology_query=1,diagnostic_simplefb_metadata_only=False,
                     diagnostic_dispatch_completion_fallback=False,diagnostic_gop_step=0,
                     diagnostic_gop_query=1,value_probe={'source':'off'},
                     diagnostic_omitted_oem_modules=['CPRDxe','DisplayDxe','UFSDxe'])
        value['firmware_configuration']['defines'].update(ENUMA_DIAG_SIMPLEFB='1',ENUMA_VIDEO_TOPOLOGY_QUERY='1')
        self.assertEqual(omitted_oem_modules(value,'a'*64),frozenset(value['diagnostic_omitted_oem_modules']))
        for key,bad in [('inherited_video_topology_query',True),('inherited_video_topology_query',3),
                        ('inherited_video_terminal',False),('inherited_video_entry_control',True)]:
            v=copy.deepcopy(value);v[key]=bad
            with self.subTest(key=key),self.assertRaises(ValueError):omitted_oem_modules(v,'a'*64)
        v=copy.deepcopy(value);v['firmware_configuration']['defines']['ENUMA_VIDEO_TOPOLOGY_QUERY']='2'
        with self.assertRaises(ValueError):omitted_oem_modules(v,'a'*64)

    def test_reason_query_requires_consistent_selectors(self):
        v=self.fixture()
        v.update(inherited_video_audit_read_only=True,inherited_video_terminal=True,
                 inherited_video_reason_target=1,inherited_video_reason_query=1,
                 diagnostic_simplefb_metadata_only=False,diagnostic_dispatch_completion_fallback=False,
                 diagnostic_gop_step=0,diagnostic_gop_query=1,value_probe={'source':'off'},
                 diagnostic_omitted_oem_modules=['CPRDxe','DisplayDxe','UFSDxe'])
        v['firmware_configuration']['defines'].update(ENUMA_DIAG_SIMPLEFB='1',ENUMA_VIDEO_REASON_TARGET='1',ENUMA_VIDEO_REASON_QUERY='1')
        self.assertEqual(omitted_oem_modules(v,'a'*64),frozenset(v['diagnostic_omitted_oem_modules']))
        for key,bad in [('inherited_video_reason_target',True),('inherited_video_reason_target',5),('inherited_video_reason_query',0),('inherited_video_terminal',False),('inherited_video_topology_query',1)]:
            changed=copy.deepcopy(v);changed[key]=bad
            with self.subTest(key=key),self.assertRaises(ValueError):omitted_oem_modules(changed,'a'*64)

    def test_explicit_matching_diagnostic_only(self):
        self.assertEqual(omitted_oem_modules(self.fixture(),'a'*64),frozenset(['UFSDxe']))
        self.assertEqual(omitted_oem_modules({},'b'*64),frozenset())

    def test_mismatches_missing_declarations_and_other_drivers_rejected(self):
        changes=[{'complete':False},{'fd_sha256':'b'*64},{'diagnostic_omitted_oem_modules':[]},
                 {'diagnostic_omitted_oem_modules':['ClockDxe']},
                 {'diagnostic_omitted_oem_modules':['UFSDxe','ClockDxe']},
                 {'firmware_configuration':{'defines':{'ENUMA_DIAG_DISABLE_UFS':'0'}}},
                 {'firmware_configuration':{'defines':{'ENUMA_DIAG_DISABLE_UFS':'2'}}}]
        for change in changes:
            value=copy.deepcopy(self.fixture());value.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):omitted_oem_modules(value,'a'*64)

    def test_pixel_profile_requires_all_protection_declarations(self):
        value=self.fixture()
        value.update(diagnostic_pixel_preview=True, diagnostic_simplefb_metadata_only=False,
                     diagnostic_gop_step=13, diagnostic_gop_query=1, hardware_review_required='R-005',
                     diagnostic_omitted_oem_modules=['CPRDxe','DisplayDxe','UFSDxe'])
        value['firmware_configuration']['defines'].update(ENUMA_DIAG_SIMPLEFB='1', ENUMA_DIAG_PIXEL_PREVIEW='1')
        self.assertEqual(omitted_oem_modules(value,'a'*64),frozenset(value['diagnostic_omitted_oem_modules']))
        for key,bad in [('diagnostic_gop_step',12),('diagnostic_gop_query',2),
                        ('hardware_review_required',None),('diagnostic_simplefb_metadata_only',True),
                        ('diagnostic_pixel_preview',False),('complete',False),('fd_sha256','b'*64)]:
            candidate=copy.deepcopy(value);candidate[key]=bad
            with self.subTest(key=key),self.assertRaises(ValueError):omitted_oem_modules(candidate,'a'*64)
        candidate=copy.deepcopy(value);candidate['firmware_configuration']['defines']['ENUMA_DIAG_PIXEL_PREVIEW']='0'
        with self.assertRaises(ValueError):omitted_oem_modules(candidate,'a'*64)

    def test_simplefb_needs_exact_completed_metadata_mode(self):
        value=self.fixture();value['firmware_configuration']['defines']['ENUMA_DIAG_SIMPLEFB']='1'
        value['diagnostic_simplefb_metadata_only']=True;value['diagnostic_omitted_oem_modules']=['CPRDxe','DisplayDxe','UFSDxe']
        self.assertEqual(omitted_oem_modules(value,'a'*64),frozenset(value['diagnostic_omitted_oem_modules']))
        for change in ({'complete':False},{'diagnostic_simplefb_metadata_only':False},
                       {'diagnostic_omitted_oem_modules':['UFSDxe']},
                       {'diagnostic_omitted_oem_modules':['CPRDxe','DisplayDxe','UFSDxe','ClockDxe']},
                       {'firmware_configuration':{'defines':{'ENUMA_DIAG_SIMPLEFB':'1','ENUMA_DIAG_DISABLE_UFS':'0'}}}):
            candidate=copy.deepcopy(value);candidate.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):omitted_oem_modules(candidate,'a'*64)


if __name__=='__main__':unittest.main()
