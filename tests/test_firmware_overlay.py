"""Reject source overlays that silently omit loaders or borrow another board."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_firmware_overlay import ROOT, check_graph


class OverlayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.package = Path(self.temp.name) / 'enumaPkg'
        shutil.copytree(ROOT / 'firmware/Platforms/Xiaomi/enumaPkg', self.package)

    def change(self, name, before, after):
        path = self.package / name
        source = path.read_text()
        self.assertIn(before, source)
        path.write_text(source.replace(before, after))

    def test_complete_local_graph(self):
        result = check_graph(self.package)
        self.assertEqual(len(result['packaged_modules']), 3)

    def test_dsc_only_loader_rejected(self):
        self.change('Include/UniXNU.fdf.inc', 'INF DarwinBootPkg/Driver/DarwinBoot.inf', '')
        with self.assertRaisesRegex(ValueError, 'Components or FvMain'):
            check_graph(self.package)

    def test_wrong_volume_rejected(self):
        self.change('enuma.fdf', '!include enumaPkg/Include/UniXNU.fdf.inc', '')
        self.change('enuma.fdf', '[FV.FVMAIN_COMPACT]',
                    '[FV.FVMAIN_COMPACT]\n!include enumaPkg/Include/UniXNU.fdf.inc')
        with self.assertRaisesRegex(ValueError, 'Components or FvMain'):
            check_graph(self.package)

    def test_foreign_vendor_rejected(self):
        self.change('Include/DXE.inc', '$(ENUMA_VENDOR_DXE)', 'Binaries/alioth/Drivers.inc')
        with self.assertRaisesRegex(ValueError, 'foreign board'):
            check_graph(self.package)

    def test_missing_guard_rejected(self):
        self.change('enuma.dsc', '!error ENUMA_PLATFORM_CONFIG is missing: memory/GOP configuration needs review', '')
        with self.assertRaisesRegex(ValueError, 'input guard'):
            check_graph(self.package)

    def test_include_cycle_rejected(self):
        self.change('Include/UniXNU.fdf.inc', 'INF DarwinBootPkg/Driver/DarwinBoot.inf',
                    '!include enumaPkg/enuma.fdf')
        with self.assertRaisesRegex(ValueError, 'include cycle'):
            check_graph(self.package)

    def test_include_escape_rejected(self):
        self.change('enuma.fdf', 'enumaPkg/Include/DXE.inc', 'enumaPkg/../../outside.inc')
        with self.assertRaisesRegex(ValueError, 'escapes package'):
            check_graph(self.package)


if __name__ == '__main__':
    unittest.main()
