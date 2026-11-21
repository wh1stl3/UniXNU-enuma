import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('handoff', Path(__file__).parents[1] / 'ufs-handoff-log.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture():
    entries = [
        dict(kind='window', pa=4096, length=4096),
        dict(kind='alloc', id='a', category='data', owner='caller', efi_type=4, source='pages', pa=16384, length=4096),
        dict(kind='map', id='a'),
        dict(kind='submit', request='r', ids=['a']),
        dict(kind='complete', request='r', status='success'),
        dict(kind='ebs', attempt=1, status='success'),
        dict(kind='end')]
    for i, event in enumerate(entries):
        event['seq'] = i
    return dict(schema=1, lost=0, overflow=False, events=entries)


class TestLog(unittest.TestCase):
    def test_unknown_without_coverage(self):
        self.assertEqual(module.interpret(fixture())[0], 'UNKNOWN')

    def test_overlap(self):
        log = fixture(); log['events'][1]['pa'] = 4096
        self.assertEqual(module.interpret(log)[0], 'RISK')

    def test_rejections(self):
        cases = []
        x = fixture(); x['events'][1]['pa'] = (1 << 64) - 1; cases.append(x)
        x = fixture(); x['events'][4] = dict(seq=4, kind='release', id='a'); cases.append(x)
        x = fixture(); x['events'][4] = dict(seq=4, kind='reuse', id='a'); cases.append(x)
        x = fixture(); x['events'][1]['source'] = 'unknown'; cases.append(x)
        x = fixture(); x['events'][5]['attempt'] = 2; cases.append(x)
        x = fixture(); x['lost'] = 1; cases.append(x)
        x = fixture(); x['overflow'] = True; cases.append(x)
        x = fixture(); x['events'][3]['seq'] = 9; cases.append(x)
        x = fixture(); x['events'][4]['status'] = 'timeout'; cases.append(x)
        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(module.interpret(case)[0], 'UNKNOWN')


if __name__ == '__main__':
    unittest.main()
