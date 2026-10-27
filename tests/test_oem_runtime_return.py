"""Run the real one-boot controller against simulated transports, never devices."""
import json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import run_oem_runtime_trial as runner

class ReturnEndpoints(unittest.TestCase):
 def run_trial(self,mode):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);original=root/'original';old=original/'out/device-tests/previous';old.mkdir(parents=True)
   local=original/'out/device-tests';out=root/'out/device-tests';out.mkdir(parents=True)
   image=root/'out/image.img';image.write_bytes(b'image');backup=original/'out/backups';backup.mkdir()
   bindings=[]
   for n in ('boot_a','vendor_boot_a'):
    f=backup/(n+'.bin');f.write_bytes(n.encode());bindings.append(dict(partition=n,sha256=runner.sha(f)))
   previous=dict(directory=str(old),recovery_backup_directory=str(backup),slot='_a',backups=bindings,phase='android-recovered')
   (local/'current.local.json').write_text(json.dumps(previous));(old/'target.local.json').write_text(json.dumps(dict(serial='fixture-enuma')))
   q=dict(run_config=dict(trial_id='fixture'),image_sha256=runner.sha(image))
   issued=False;calls=[];ticks=iter(range(10000));enums=0
   def transport(argv,**kwargs):
    nonlocal issued,enums
    calls.append(argv);tool=Path(argv[0]).name;args=argv[3:]
    code=0;value=b''
    if tool=='fastboot.exe' and argv[1:]==['devices']:
     enums+=1;value=b'fixture-enuma fastboot\n' if mode=='no-disconnect' else b''
    elif tool=='fastboot.exe' and args[:1]==['getvar']:
     value={'product':b'product: enuma','current-slot':b'current-slot: a','unlocked':b'unlocked: yes'}[args[1]]
    elif tool=='fastboot.exe' and args[:1]==['boot']:issued=True
    elif tool=='adb.exe' and args[:1]==['shell']:
     cmd=' '.join(args[1:])
     if 'getprop ro.product.device' in cmd:value=b'other' if issued and mode=='wrong-device' else b'enuma'
     elif 'getprop sys.boot_completed' in cmd:value=b'1'
     elif 'getprop ro.boot.slot_suffix' in cmd:value=b'_a'
     elif 'getprop ro.boot.flash.locked' in cmd:value=b'0'
     elif 'sha256sum' in cmd:
      value=next(x['sha256'].encode() for x in bindings if '/'+x['partition'] in cmd)+b' partition'
     elif 'id' in cmd:value=b'uid=0(root)'
    return subprocess.CompletedProcess(argv,code,value,b'')
   with patch.object(runner,'ROOT',root),patch.object(runner,'ORIGINAL',original),patch.object(runner,'validate',return_value=(q,image)),patch.object(runner,'claim',return_value=(q,image)),patch.object(runner.subprocess,'run',side_effect=transport),patch.object(runner.subprocess,'check_output',return_value='fixture.img'),patch.object(runner.time,'sleep'),patch.object(runner.time,'monotonic',side_effect=lambda:next(ticks)),patch.object(sys,'argv',['runner','--qualification',str(root/'out/q'),'--execute','--human-ready']):
    if mode=='android':runner.main()
    else:self.assertRaises(ValueError,runner.main)
   state=json.loads((out/'current.local.json').read_text())
   boots=[c for c in calls if Path(c[0]).name=='fastboot.exe' and c[3:4]==['boot']]
   self.assertEqual(len(boots),1)
   self.assertFalse(any(c[3:4] in (['flash'],['erase'],['set_active']) for c in calls))
   if mode=='android':
    self.assertEqual(state['phase'],'android-recovered-visual-review-pending');self.assertEqual(state['observed_return_endpoint'],'android')
    self.assertIsNone(state['manual_recovery'])
    self.assertFalse(any(Path(c[0]).name=='fastboot.exe' and c[3:4]==['reboot'] for c in calls))
    self.assertEqual(sum('sha256sum' in ' '.join(c) for c in calls),4)
   else:self.assertEqual(state['phase'],'manual-recovery-needed')
 def test_direct_android_return(self):self.run_trial('android')
 def test_wrong_android_identity(self):self.run_trial('wrong-device')
 def test_stale_fastboot_presence(self):self.run_trial('no-disconnect')

if __name__=='__main__':unittest.main()
