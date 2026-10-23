import subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PoolCliTests(unittest.TestCase):
    def test_global_pool_gates_reject_driver_selection_before_build(self):
        for point in (26,27):
            for selector in (['--dispatch-ordinal','2'],['--dispatch-guid','4138022f-06c7-4f79-9c94-7e33b511a4e7']):
                with self.subTest(point=point,selector=selector):
                    p=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/build_enuma_firmware.py'),'--unixnu',str(ROOT/'out/sources/UniXNU'),'--stop-stage','13','--detail-point',str(point),*selector],capture_output=True,text=True)
                    self.assertEqual(p.returncode,2);self.assertIn('no driver GUID/ordinal attribution',p.stderr)
