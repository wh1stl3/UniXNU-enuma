"""Camera-free native observations retain the guarded runner and consumed ledger."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import run_system_transport_trial as runner


class NoCameraTests(unittest.TestCase):
    def test_guarded_outcomes(self):
        for outcome in ('returned', 'preissue-abort', 'host-timeout'):
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp); (root/'out/device-tests').mkdir(parents=True); (root/'reports').mkdir()
                q=dict(trial_kind='native-video-route',pixel_access=False,gop_published=False,
                       boot_clock_capture=True,image_sha256='abc')
                state=dict(candidate_sha256='abc',phase='fastboot-identity-aborted')
                if outcome!='preissue-abort':state.update(issued_at='test',phase='observing-reset-return')
                (root/'out/device-tests/current.local.json').write_text(json.dumps(state))
                def invoke(command, **kwargs):
                    self.assertIn('run_enuma_entry_probe.py',command[5])
                    self.assertIn('--boot-clock',command)
                    self.assertEqual(kwargs['timeout'],240)
                    if outcome=='host-timeout':raise subprocess.TimeoutExpired(command,240)
                    return subprocess.CompletedProcess(command,0 if outcome=='returned' else 1)
                with patch.object(runner,'ROOT',root),patch.object(runner.subprocess,'run',side_effect=invoke) as called:
                    if outcome=='returned':runner.run_without_camera(q,root/'image.img')
                    else:
                        with self.assertRaises((RuntimeError,subprocess.TimeoutExpired)):
                            runner.run_without_camera(q,root/'image.img')
                    self.assertEqual(called.call_count,1)
                report=json.loads((root/'reports/enuma-system-trial-observation.json').read_text())
                self.assertFalse(report['camera_used']);self.assertFalse(report['media_recorded'])
                self.assertEqual(report['boot_issued'],outcome!='preissue-abort')
                self.assertEqual((root/'out/device-tests/consumed-abc.local.json').exists(),outcome!='preissue-abort')
                self.assertNotIn('video',report)

    def test_scope_before_device(self):
        q=dict(trial_kind='native-video-route',pixel_access=False,gop_published=False,boot_clock_capture=True)
        for key,value in [('trial_kind','other'),('pixel_access',True),('gop_published',True),('boot_clock_capture',False)]:
            with patch.object(runner.subprocess,'run') as called,self.assertRaises(ValueError):
                runner.run_without_camera({**q,key:value},Path('unused.img'))
            called.assert_not_called()


if __name__=='__main__':unittest.main()
