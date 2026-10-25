import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('collector', ROOT / 'scripts/collect_enuma_pstore.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class CollectorTests(unittest.TestCase):
    def test_marker_rejects_shell_or_nonunique_input(self):
        for bad in ['', 'abc', 'x' * 32, 'a' * 32 + ';id']:
            with self.assertRaises(ValueError):
                collector.marker_for(bad)

    def test_reads_exact_device_and_console_without_writes(self):
        calls = []
        nonce = 'a' * 32
        def run(command, **kwargs):
            calls.append(command)
            data = (b'enuma\n' if command[-1].startswith('getprop') else
                    b'0\n' if command[-1] == 'su -c "id -u"' else
                    b'old boot\n' + collector.marker_for(nonce))
            return subprocess.CompletedProcess(command, 0, data, b'')
        with tempfile.TemporaryDirectory(dir=ROOT / 'out') as parent:
            report = collector.collect('adb', 'TEST-ONLY', nonce, Path(parent) / 'capture', run=run)
            self.assertTrue(report['marker_present'])
            self.assertEqual(len(report['snapshots']), 1)
        self.assertEqual([c[-1] for c in calls], [
            'getprop ro.product.device', 'su -c "id -u"',
            'su -c "test -f /sys/fs/pstore/console-ramoops-0 && cat /sys/fs/pstore/console-ramoops-0"'])
        self.assertEqual(calls[-1][3:5], ['shell','-T'])
        self.assertTrue(all(c[1:3] == ['-s', 'TEST-ONLY'] for c in calls))

    def test_wrong_device_stops_before_root_or_console_read(self):
        calls = []
        def run(command, **kwargs):
            calls.append(command)
            return subprocess.CompletedProcess(command, 0, b'nuwa\n', b'')
        with tempfile.TemporaryDirectory(dir=ROOT / 'out') as parent:
            target = Path(parent) / 'capture'
            with self.assertRaisesRegex(ValueError, 'not enuma'):
                collector.collect('adb', 'TEST-ONLY', 'a' * 32, target, run=run)
            self.assertTrue((target / 'collection.json').exists())
        self.assertEqual(len(calls), 1)

    def test_output_escape_and_existing_directory_rejected_before_adb(self):
        with self.assertRaises(ValueError):
            collector.collect('adb', 'TEST-ONLY', 'a' * 32, ROOT / 'reports')
        with tempfile.TemporaryDirectory(dir=ROOT / 'out') as path:
            with self.assertRaises(FileExistsError):
                collector.collect('adb', 'TEST-ONLY', 'a' * 32, path)

    def test_stale_marker_is_not_current(self):
        self.assertNotIn(collector.marker_for('a' * 32), collector.marker_for('b' * 32))
    def test_remote_missing_file_error_is_not_saved_as_console(self):
        def run(command, **kwargs):
            if command[-1].startswith('getprop'):data,rc=b'enuma\n',0
            elif command[-1]=='su -c "id -u"':data,rc=b'0\n',0
            else:data,rc=b'cat: console-ramoops-0: No such file or directory\n',1
            return subprocess.CompletedProcess(command,rc,data,b'')
        with tempfile.TemporaryDirectory(dir=ROOT/'out') as parent:
            report=collector.collect('adb','TEST-ONLY','a'*32,Path(parent)/'capture',seconds=0.02,run=run)
            self.assertFalse(report['marker_present']);self.assertEqual(report['snapshots'],[])
            self.assertGreater(report['read_errors'],0)


if __name__ == '__main__':
    unittest.main()
