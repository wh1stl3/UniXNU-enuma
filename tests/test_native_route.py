"""Route categories must remain distinct from mask codes and reject mixed scopes."""
import json,sys,tempfile,unittest,subprocess
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from native_mask_decode import make_plan
from native_route_decode import decode,CATEGORIES,DETAIL_CATEGORIES,STAGING_CATEGORIES
import run_system_transport_trial as runner
class RouteTests(unittest.TestCase):
    def test_all_codes_and_ambiguity(self):
        plan=make_plan(ROOT)
        for n,(lo,hi) in enumerate(plan['code_windows_after_issue'],1):
            x=(lo+hi)/2
            r=decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan)
            self.assertEqual(r['category'],CATEGORIES[str(n)])
            self.assertFalse(r['stop_additional_trials'])
            self.assertEqual(decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan,True,True)['category'],STAGING_CATEGORIES[str(n)])
            self.assertEqual(decode(dict(origin_after_issue_lower=x,origin_after_issue_upper=x+.01),plan,True)['category'],DETAIL_CATEGORIES[str(n)])
        self.assertTrue(decode(dict(origin_after_issue_lower=0,origin_after_issue_upper=.01),plan)['stop_additional_trials'])
    def test_scope_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();arc=root/'out/a';arc.mkdir(parents=True);report=root/'reports/q.json';report.parent.mkdir()
            q=dict(trial_kind='native-video-route',archive='out/a',native_query=0,native_control=False,native_route_audit=True,
              boot_clock_capture=True,maximum_reads=330,maximum_wait_calls=2,maximum_mmio_offset='0x6c26c',pixel_access=False,gop_published=False,
              terminal_return={'code_delays_seconds':[2,7,12,17,22],'completion_fallback':False},result_categories=CATEGORIES)
            for key,value in [('native_query',1),('native_route_audit',1),('maximum_reads',331),('pixel_access',True),('result_categories',{}),('native_route_detail',1),('native_route_detail',True),('native_route_staging',1),('native_route_staging',True)]:
                changed={**q,key:value};report.write_text(json.dumps(changed));(arc/'qualification.json').write_text(json.dumps(changed))
                with patch.object(runner,'ROOT',root),self.assertRaisesRegex(ValueError,'scope invalid'):runner.qualification(False,report)
    def test_cli_excludes_observer(self):
        p=subprocess.run([sys.executable,'-B',str(ROOT/'firmware/Resources/Scripts/build_enuma_firmware.py'),
          '--device-root',str(ROOT),'--unixnu',str(ROOT/'out/sources/UniXNU'),'--native-route-audit','--native-observe-query','1','--inherited-video-audit',
          '--inherited-video-terminal','--diagnostic-simplefb','--diagnostic-gop-query','1'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2);self.assertIn('native route requires',p.stderr)
if __name__=='__main__':unittest.main()
