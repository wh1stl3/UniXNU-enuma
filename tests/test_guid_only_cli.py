import subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class GuidOnlyCliTests(unittest.TestCase):
    def rejected(self,options,message):
        p=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/build_enuma_firmware.py'),
            '--unixnu',str(ROOT/'out/sources/UniXNU'),*options],capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertIn(message,p.stderr)
    def test_guid_only_invalid_combinations_rejected_before_build(self):
        base=['--stop-stage','13','--dispatch-guid-only']
        guid=['--dispatch-guid','dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92']
        for extra in ([],guid+['--dispatch-ordinal','2'],guid+['--detail-point','23'],guid+['--detail-point','26'],guid+['--stop-stage','12']):
            with self.subTest(extra=extra):self.rejected(base+extra,'GUID-only requires')
    def test_completion_fallback_requires_guid_only(self):
        self.rejected(['--dispatch-completion-fallback'],'fallback requires --dispatch-guid-only')
