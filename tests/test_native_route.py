"""Route categories must remain distinct from mask codes and reject mixed scopes."""
import json,sys,tempfile,unittest,subprocess
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from native_mask_decode import make_plan
from native_route_decode import decode,CATEGORIES,DETAIL_CATEGORIES,STAGING_CATEGORIES,LAYOUT_CATEGORIES,BLEND_CATEGORIES,STRUCTURE_CATEGORIES,GEOMETRY_CATEGORIES,GLOBAL_OUTPUT_CATEGORIES,GLOBAL_DETAIL_CATEGORIES,ALPHA_VIEW_CATEGORIES,CPU_STAGE1_CATEGORIES,CPU_ATTRIBUTE_CATEGORIES,CPU_POLICY_CATEGORIES,CPU_READ_CATEGORIES,CPU_BARRIER_CATEGORIES,CPU_ROI_CATEGORIES
import run_system_transport_trial as runner
class RouteTests(unittest.TestCase):
    def test_all_codes_and_ambiguity(self):
        plan=make_plan(ROOT)
        for n,(lo,hi) in enumerate(plan['code_windows_after_issue'],1):
            x=(lo+hi)/2
            r=decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan)
            self.assertEqual(decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan,True,False,True)['category'],LAYOUT_CATEGORIES[str(n)])
            self.assertEqual(decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan,True,False,True,True)['category'],BLEND_CATEGORIES[str(n)])
            self.assertEqual(decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan,structure=True)['category'],STRUCTURE_CATEGORIES[str(n)])
            self.assertEqual(decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan,structure=True,structure_detail=True)['category'],GEOMETRY_CATEGORIES[str(n)])
            self.assertEqual(decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan,structure=True,global_output=True)['category'],GLOBAL_OUTPUT_CATEGORIES[str(n)])
            self.assertEqual(decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan,structure=True,global_output=True,global_detail=True)['category'],GLOBAL_DETAIL_CATEGORIES[str(n)])
            self.assertEqual(decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan,structure=True,global_output=True,alpha_view=True)['category'],ALPHA_VIEW_CATEGORIES[str(n)])
            self.assertEqual(decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan,structure=True,global_output=True,alpha_view=True,cpu_stage1=True)['category'],CPU_STAGE1_CATEGORIES[str(n)])
            self.assertEqual(decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan,structure=True,global_output=True,alpha_view=True,cpu_stage1=True,cpu_attribute=True)['category'],CPU_ATTRIBUTE_CATEGORIES[str(n)])
            self.assertEqual(decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan,structure=True,global_output=True,alpha_view=True,cpu_stage1=True,cpu_policy=True)['category'],CPU_POLICY_CATEGORIES[str(n)])
            self.assertEqual(decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan,structure=True,global_output=True,alpha_view=True,cpu_stage1=True,cpu_policy=True,cpu_read=True)['category'],CPU_READ_CATEGORIES[str(n)])
            self.assertEqual(decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan,structure=True,global_output=True,alpha_view=True,cpu_stage1=True,cpu_policy=True,cpu_read=True,cpu_barrier=True)['category'],CPU_BARRIER_CATEGORIES[str(n)])
            self.assertEqual(decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan,structure=True,global_output=True,alpha_view=True,cpu_stage1=True,cpu_policy=True,cpu_read=True,cpu_barrier=True,cpu_roi=True)['category'],CPU_ROI_CATEGORIES[str(n)])
            self.assertEqual(r['category'],CATEGORIES[str(n)])
            self.assertFalse(r['stop_additional_trials'])
            self.assertEqual(decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan,True,True)['category'],STAGING_CATEGORIES[str(n)])
            self.assertEqual(decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan,True)['category'],DETAIL_CATEGORIES[str(n)])
        self.assertTrue(decode(dict(origin_after_issue_lower=0,origin_after_issue_upper=.01),plan)['stop_additional_trials'])
    def test_scope_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();arc=root/'out/a';arc.mkdir(parents=True);report=root/'reports/q.json';report.parent.mkdir()
            q=dict(trial_kind='native-video-route',archive='out/a',native_query=0,native_control=False,native_route_audit=True,native_border_view=True,
              boot_clock_capture=True,maximum_reads=330,maximum_wait_calls=2,maximum_mmio_offset='0x6c26c',pixel_access=False,gop_published=False,
              terminal_return={'code_delays_seconds':[2,7,12,17,22],'completion_fallback':False},result_categories=CATEGORIES)
            for key,value in [('native_route_cpu_roi',1),('native_route_cpu_roi',True),('native_route_cpu_barrier',1),('native_route_cpu_barrier',True),('native_route_cpu_read',1),('native_route_cpu_read',True),('native_route_cpu_policy',1),('native_route_cpu_policy',True),('native_route_cpu_attribute',1),('native_route_cpu_attribute',True),('native_route_cpu_stage1',1),('native_route_cpu_stage1',True),('native_route_alpha_view',1),('native_route_alpha_view',True),('native_route_global_detail',1),('native_route_global_detail',True),('native_route_global_output',1),('native_route_global_output',True),('native_route_structure_detail',1),('native_route_structure_detail',True),('native_route_structure',1),('native_route_structure',True),('native_route_blend',1),('native_route_blend',True),('native_route_layout',1),('native_route_layout',True),('native_border_view',1),('native_border_view',False),('native_query',1),('native_route_audit',1),('maximum_reads',331),('pixel_access',True),('result_categories',{}),('native_route_detail',1),('native_route_detail',True),('native_route_staging',1),('native_route_staging',True)]:
                changed={**q,key:value};report.write_text(json.dumps(changed));(arc/'qualification.json').write_text(json.dumps(changed))
                with patch.object(runner,'ROOT',root),self.assertRaisesRegex(ValueError,'scope invalid'):runner.qualification(False,report)
    def test_cli_excludes_observer(self):
        p=subprocess.run([sys.executable,'-B',str(ROOT/'firmware/Resources/Scripts/build_enuma_firmware.py'),
          '--device-root',str(ROOT),'--unixnu',str(ROOT/'out/sources/UniXNU'),'--native-route-audit','--native-observe-query','1','--inherited-video-audit',
          '--inherited-video-terminal','--diagnostic-simplefb','--diagnostic-gop-query','1'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2);self.assertIn('native route requires',p.stderr)
    def test_alpha_obligation_cannot_be_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();arc=root/'out/a';arc.mkdir(parents=True);report=root/'reports/q.json';report.parent.mkdir()
            q=dict(trial_kind='native-video-route',archive='out/a',native_query=0,native_control=False,
              native_route_audit=True,native_border_view=True,native_route_structure=True,
              native_route_global_output=True,native_route_alpha_view=True,
              boot_clock_capture=True,maximum_reads=330,maximum_wait_calls=2,maximum_mmio_offset='0x6c26c',
              pixel_access=False,gop_published=False,
              terminal_return={'code_delays_seconds':[2,7,12,17,22],'completion_fallback':False},
              result_categories=ALPHA_VIEW_CATEGORIES)
            for value in (None,False,1):
                changed={**q,'alpha_semantics_unproven':value};report.write_text(json.dumps(changed));(arc/'qualification.json').write_text(json.dumps(changed))
                with patch.object(runner,'ROOT',root),self.assertRaisesRegex(ValueError,'scope invalid'):
                    runner.qualification(False,report)
    def test_cpu_query_cannot_expand_into_data_or_mapping_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();arc=root/'out/a';arc.mkdir(parents=True);report=root/'reports/q.json';report.parent.mkdir()
            q=dict(trial_kind='native-video-route',archive='out/a',native_query=0,native_control=False,
              native_route_audit=True,native_border_view=True,native_route_structure=True,
              native_route_global_output=True,native_route_alpha_view=True,alpha_semantics_unproven=True,
              native_route_cpu_stage1=True,maximum_translation_operations=18432,cpu_stage1_only=True,
              cpu_memory_data_access=False,cpu_mapping_changes=False,
              boot_clock_capture=True,maximum_reads=330,maximum_wait_calls=2,maximum_mmio_offset='0x6c26c',
              pixel_access=False,gop_published=False,
              terminal_return={'code_delays_seconds':[2,7,12,17,22],'completion_fallback':False},
              result_categories=CPU_STAGE1_CATEGORIES)
            for key,value in [('maximum_translation_operations',18433),('maximum_translation_operations',True),
                              ('cpu_stage1_only',False),('cpu_memory_data_access',True),('cpu_mapping_changes',True),
                              ('cpu_memory_data_access',0),('alpha_semantics_unproven',False)]:
                changed={**q,key:value};report.write_text(json.dumps(changed));(arc/'qualification.json').write_text(json.dumps(changed))
                with patch.object(runner,'ROOT',root),self.assertRaisesRegex(ValueError,'scope invalid'):
                    runner.qualification(False,report)
if __name__=='__main__':unittest.main()
