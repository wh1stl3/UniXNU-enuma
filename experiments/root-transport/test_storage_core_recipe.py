"""Check against actual captured records, including C/C++ flag separation."""
import json
import unittest
from pathlib import Path
from compile_storage_core import ROOT, SOURCES, invocation


class RecipeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / 'out/ci-single-crypto-41016592491/driver-inputs/manifest.json').read_text())

    def test_only_rebase_and_source_output_change(self):
        for name in SOURCES:
            with self.subTest(source=name):
                source = ROOT / name
                language = '-xc++' if source.suffix == '.cpp' else '-xc'
                record = next(r for r in self.manifest['compile_records'] if language in r['arguments'])
                tree = Path('/isolated/input tree')
                output = Path('/isolated/output') / (source.stem + '.o')
                args = invocation(record, self.manifest['source_root'], tree, source, output, [Path('/extra include')])
                self.assertEqual(args[0], '-I/extra include')
                expected = [s.replace(self.manifest['source_root'], str(tree)) for s in record['arguments'][1:]]
                expected[expected.index(language) + 1] = str(source)
                expected[expected.index('-o') + 1] = str(output)
                self.assertEqual(args[1:], expected)
                self.assertIn('-mkernel', args)
                self.assertIn('--target=arm64-apple-ios17.0.0', args)
                self.assertEqual('-std=gnu++2b' in args, source.suffix == '.cpp')

    def test_reject_wrong_language(self):
        for record in self.manifest['compile_records']:
            suffix = '.c' if '-xc++' in record['arguments'] else '.cpp'
            with self.assertRaisesRegex(ValueError, 'language mismatch'):
                invocation(record, self.manifest['source_root'], Path('/tree'),
                           Path('/source' + suffix), Path('/out.o'), [])


if __name__ == '__main__':
    unittest.main()
