import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from reconcile_enuma_recovery import reconcile


class RecoveryReconciliationTests(unittest.TestCase):
    def fixture(self,root):
        (root/'out/device-tests').mkdir(parents=True);(root/'reports').mkdir()
        backup=root/'out/backup';backup.mkdir()
        partitions=[]
        for name in ('boot_a','vendor_boot_a'):
            (backup/(name+'.bin')).write_bytes(name.encode())
            partitions.append(dict(partition=name,sha256=hashlib.sha256(name.encode()).hexdigest()))
        state=dict(phase='manual-recovery-needed',slot='_a',directory=str(backup),backups=partitions)
        path=root/'out/device-tests/current.local.json';path.write_text(json.dumps(state))
        return path,state

    def invoke(self,slot='_a',bad_digest=False):
        def run(args,**kwargs):
            command=args[-1]
            if args[-1]=='devices':text='List of devices attached\nfixture device\n'
            elif command=='getprop ro.product.device':text='enuma'
            elif command=='getprop sys.boot_completed':text='1'
            elif command=='getprop ro.boot.slot_suffix':text=slot
            elif command=='getprop ro.boot.flash.locked':text='0'
            elif command=='su -c id':text='uid=0(root)'
            elif 'sha256sum' in command:
                name=command.rstrip("'").split('/')[-1]
                text=('0'*64 if bad_digest else hashlib.sha256(name.encode()).hexdigest())+' block'
            else:raise AssertionError('unexpected or mutating device command: '+repr(args))
            return SimpleNamespace(returncode=0,stdout=text)
        return run

    def test_success_retains_failed_trial_and_redacts_target(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'out') as td:
            root=Path(td);path,state=self.fixture(root)
            failed=root/'out/device-tests/result.json';failed.write_text('original failed trial')
            reconcile(root,self.invoke())
            self.assertEqual(json.loads(path.read_text())['phase'],'recovered-android-boot-complete')
            self.assertEqual(failed.read_text(),'original failed trial')
            self.assertNotIn('fixture',(root/'reports/enuma-recovery-reconciliation.json').read_text())

    def test_slot_or_digest_failure_does_not_clear_guard(self):
        for invoke in (self.invoke(slot='_b'),self.invoke(bad_digest=True)):
            with tempfile.TemporaryDirectory(dir=ROOT/'out') as td:
                root=Path(td);path,state=self.fixture(root);before=path.read_bytes()
                with self.assertRaises(ValueError):reconcile(root,invoke)
                self.assertEqual(path.read_bytes(),before)


if __name__=='__main__':unittest.main()
