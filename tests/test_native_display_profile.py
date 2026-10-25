"""Reject mixed native profiles and malformed hardware qualification before use."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import run_system_transport_trial as runner

class NativeProfileTests(unittest.TestCase):
    def test_mixed_profiles_rejected_before_staging(self):
        base=[sys.executable,'-B',str(ROOT/'firmware/Resources/Scripts/build_enuma_firmware.py'),
              '--device-root',str(ROOT),'--unixnu',str(ROOT/'out/sources/UniXNU'),
              '--native-observe-query','1','--diagnostic-simplefb','--diagnostic-gop-query','1']
        for extra in [[],['--inherited-video-audit','--inherited-video-terminal','--inherited-video-entry-control'],
                      ['--inherited-video-audit','--inherited-video-terminal','--inherited-video-topology-query','1'],
                      ['--inherited-video-audit','--inherited-video-terminal','--inherited-video-reason-target','counter-enable']]:
            with self.subTest(extra=extra):
                p=subprocess.run(base+extra,capture_output=True,text=True,timeout=15)
                self.assertEqual(p.returncode,2)
                self.assertIn('native observation requires',p.stderr)

    def test_malformed_scope_rejected_before_image_or_device_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();archive=root/'out/archive';archive.mkdir(parents=True)
            report=root/'reports/native.json';report.parent.mkdir()
            q=dict(trial_kind='native-display-observe',archive='out/archive',native_query=1,
                   maximum_reads=26,maximum_wait_calls=2,maximum_mmio_offset='0x6c26c',
                   pixel_access=False,gop_published=False,
                   terminal_return={'pass':2,'fail':7,'completion_fallback':False})
            for key,bad in [('native_query',True),('native_query',0),('maximum_reads',330),
                            ('maximum_wait_calls',3),('maximum_mmio_offset','0x85000'),
                            ('pixel_access',True),('gop_published',True),('native_control','yes'),('native_control',True),
                            ('terminal_return',{'pass':2,'fail':7,'completion_fallback':True})]:
                with self.subTest(key=key,bad=bad),patch.object(runner,'ROOT',root):
                    changed={**q,key:bad}
                    report.write_text(json.dumps(changed));(archive/'qualification.json').write_text(json.dumps(changed))
                    with self.assertRaisesRegex(ValueError,'native observer scope invalid'):
                        runner.qualification(False,report)

if __name__=='__main__':unittest.main()
