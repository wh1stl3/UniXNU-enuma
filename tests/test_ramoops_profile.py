"""Invalid R-017 combinations stop in argparse before source staging/build."""
from pathlib import Path
import subprocess
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
class ProfileTests(unittest.TestCase):
    def test_invalid_combinations_rejected_before_build(self):
        base=[sys.executable,'-B',str(ROOT/'firmware/Resources/Scripts/build_enuma_firmware.py'),
              '--device-root',str(ROOT),'--unixnu',str(ROOT/'out/sources/UniXNU'),
              '--diagnostic-simplefb','--stop-stage','10','--ram-payload',str(ROOT/'out/full-boot/payload/payload.img')]
        for extra in [
            ['--ramoops-map-control','--ramoops-canary-nonce','a'*32],
            ['--ramoops-map-control','--stop-stage','13'],
            ['--ramoops-map-control','--diagnostic-gop-query','1'],
            ['--ramoops-canary-nonce','A'*32],
            ['--ramoops-read-header','--ramoops-map-control'],
            ['--ramoops-read-header','--ramoops-canary-nonce','a'*32],
            ['--ramoops-read-header','--stop-stage','9'],
            ['--ramoops-map-control','--stop-delay','7']]:
            with self.subTest(extra=extra):
                r=subprocess.run(base+extra,capture_output=True,text=True,timeout=10)
                self.assertEqual(r.returncode,2)
                self.assertIn('R-017 requires',r.stderr)
if __name__=='__main__':unittest.main()
