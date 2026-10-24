"""Invalid pixel build combinations must reject before source staging."""
import os,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FIRMWARE=Path(os.environ.get('ENUMA_TEST_FIRMWARE',ROOT/'firmware'))
class PixelProfileTests(unittest.TestCase):
    def test_invalid_pixel_combinations(self):
        base=[sys.executable,'-B',str(FIRMWARE/'Resources/Scripts/build_enuma_firmware.py'),'--device-root',str(ROOT),'--unixnu',str(ROOT/'out/not-used')]
        for args in [
            ['--diagnostic-gop-step','13','--diagnostic-gop-query','1'],
            ['--diagnostic-pixel-preview','--diagnostic-gop-step','12','--diagnostic-gop-query','1'],
            ['--diagnostic-pixel-preview','--diagnostic-gop-step','14','--diagnostic-gop-query','1'],
            ['--diagnostic-pixel-preview','--diagnostic-gop-step','15','--diagnostic-gop-query','1'],
            ['--diagnostic-pixel-preview','--diagnostic-gop-step','16','--diagnostic-gop-query','1'],
            ['--diagnostic-pixel-preview','--diagnostic-gop-step','17','--diagnostic-gop-query','1'],
            ['--diagnostic-pixel-preview','--diagnostic-gop-step','18','--diagnostic-gop-query','1'],
            ['--diagnostic-pixel-preview','--diagnostic-gop-step','19','--diagnostic-gop-query','1'],
            ['--diagnostic-pixel-preview','--diagnostic-gop-step','20','--diagnostic-gop-query','1'],
            ['--diagnostic-pixel-preview','--diagnostic-gop-step','21','--diagnostic-gop-query','1'],
            ['--diagnostic-pixel-preview','--diagnostic-gop-step','22','--diagnostic-gop-query','1'],
            ['--diagnostic-pixel-preview','--diagnostic-gop-step','23','--diagnostic-gop-query','1'],
            ['--diagnostic-pixel-preview','--diagnostic-gop-step','13','--diagnostic-gop-query','2'],
            ['--diagnostic-pixel-preview','--diagnostic-gop-query','1'],
            ['--diagnostic-pixel-preview','--diagnostic-gop-step','13','--diagnostic-gop-query','1']]:
            with self.subTest(args=args):
                result=subprocess.run(base+args,capture_output=True,text=True)
                self.assertEqual(result.returncode,2)
                self.assertTrue('Pixel preview requires' in result.stderr or 'GOP query requires' in result.stderr,result.stderr)
if __name__=='__main__':unittest.main()
