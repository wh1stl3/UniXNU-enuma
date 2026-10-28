"""Simulate transport without invoking any device executable."""
import json,sys,tempfile,unittest,subprocess
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import run_oem_runtime_trial as runner
from oem_runtime_candidate import sha

class Transport(unittest.TestCase):
    def test_clock_target_rejects_missing_calibration_before_device_or_claim(self):
        q=dict(scope='oem-far-clock-v9')
        with patch.object(runner,'validate',return_value=(q,Path('unused'))),patch.object(runner,'claim') as claim,patch.object(runner.subprocess,'run') as run,patch.object(sys,'argv',['trial','--qualification','unused','--execute','--human-ready']):
            with self.assertRaisesRegex(ValueError,'calibration required'):runner.main()
            claim.assert_not_called();run.assert_not_called()
    def test_gop_target_missing_calibration_before_claim_or_device(self):
        q=dict(scope='oem-gop-mode-v10')
        with patch.object(runner,'validate',return_value=(q,Path('image.img'))),patch.object(runner,'claim') as claim,patch.object(runner.subprocess,'run') as run,patch.object(sys,'argv',['trial','--qualification','out','--execute','--human-ready']):
            with self.assertRaisesRegex(ValueError,'calibration required'):runner.main()
            claim.assert_not_called();run.assert_not_called()
    def run_case(self,boot_failure=False,bad_android=False,clock_failure=False):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);root=base/'isolated';original=base/'original';backup=original/'out/backup'
            backup.mkdir(parents=True);(original/'out/device-tests').mkdir()
            (root/'out').mkdir(parents=True);image=root/'out/image.img';image.write_bytes(b'image')
            backups=[]
            for name in ['boot_a','vendor_boot_a']:
                p=backup/(name+'.bin');p.write_bytes(b'original partition');backups.append(dict(partition=name,sha256=sha(p)))
            (backup/'target.local.json').write_text(json.dumps(dict(serial='test-enuma')))
            (original/'out/device-tests/current.local.json').write_text(json.dumps(dict(directory=str(backup),slot='_a',backups=backups)))
            q=dict(scope='oem-far-clock-low-v9' if clock_failure else 'oem-progress-v2',run_config=dict(trial_id='test-id'),image_sha256=sha(image));commands=[];enumerations=iter([b'',b'test-enuma fastboot\n'])
            def run(argv,**kwargs):
                commands.append(argv);text=' '.join(map(str,argv));out=b'';rc=0
                props={'ro.product.device':'other' if bad_android else 'enuma','sys.boot_completed':'1',
                       'ro.boot.slot_suffix':'_a','ro.boot.flash.locked':'0'}
                if 'getprop ' in text:out=props[text.split('getprop ')[1]].encode()
                elif 'sha256sum' in text:out=(backups[0]['sha256']+' partition').encode()
                elif 'su -c id' in text:out=b'uid=0(root)'
                elif argv[-1]=='devices':out=next(enumerations)
                elif 'getvar' in argv:
                    key=argv[-1];out=(key+': '+{'product':'enuma','current-slot':'a','unlocked':'yes'}[key]).encode()
                elif 'boot' in argv and boot_failure:rc=1;out=b'FAILED simulated'
                return subprocess.CompletedProcess(argv,rc,out,b'')
            with patch.object(runner,'ROOT',root),patch.object(runner,'ORIGINAL',original), \
                 patch.object(runner,'validate',return_value=(q,image)),patch.object(runner,'claim',return_value=(q,image)), \
                 patch.object(runner.subprocess,'run',side_effect=run),patch.object(runner.subprocess,'check_output',return_value='D:/fixture.img'), \
                 patch.object(runner.time,'sleep'),patch('boot_origin.capture',side_effect=[(dict(boot_id_sha256='old'),[]),ValueError('clock samples rejected')]),patch.object(sys,'argv',['trial','--qualification',str(root/'out'), '--execute','--human-ready']):
                if boot_failure or bad_android:
                    with self.assertRaises(ValueError):runner.main()
                else:runner.main()
            state=json.loads((root/'out/device-tests/current.local.json').read_text())
            return commands,state
    def test_clock_failure_keeps_verified_android_recovery(self):
        commands,state=self.run_case(clock_failure=True)
        self.assertEqual(state['phase'],'android-recovered-visual-review-pending')
        self.assertFalse(state['clock_observation_valid'])
        self.assertEqual(sum('boot' in c for c in commands),1)
    def test_one_boot_and_verified_recovery(self):
        commands,state=self.run_case()
        self.assertEqual(sum('boot' in c for c in commands),1)
        self.assertEqual(state['phase'],'android-recovered-visual-review-pending')
        self.assertFalse(any(any(x in c for x in ['flash','erase','set_active']) for c in commands))
    def test_boot_failure_no_retry(self):
        commands,state=self.run_case(boot_failure=True)
        self.assertEqual(sum('boot' in c for c in commands),1)
        self.assertEqual(state['phase'],'manual-recovery-needed')
        self.assertFalse(any(c[-1]=='reboot' for c in commands))
    def test_wrong_android_no_write(self):
        commands,state=self.run_case(bad_android=True)
        self.assertFalse(any('reboot' in c or 'boot' in c for c in commands))
        self.assertEqual(state['phase'],'preflight-rejected')

if __name__=='__main__':unittest.main()
