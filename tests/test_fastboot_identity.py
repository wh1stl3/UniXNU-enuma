"""Identity parsing must not accept partial or contradictory GetVar responses."""
import subprocess
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from run_enuma_entry_probe import fastboot_value_matches


class FastbootIdentityTests(unittest.TestCase):
    def result(self, text, code=0):
        return subprocess.CompletedProcess([], code, stdout=b'', stderr=text.encode())

    def test_exact_supported_output_forms(self):
        for text in ('product: enuma\nFinished. Total time: 0.001s\n',
                     '(bootloader) product: enuma\r\nFinished. Total time: 0.001s\r\n'):
            self.assertTrue(fastboot_value_matches(self.result(text), 'product', 'enuma'))

    def test_partial_missing_and_conflicting_values_rejected(self):
        for text in ('product: enuma-other\n', 'product: enumax\n', 'other-product: enuma\n',
                     'product: enuma\nproduct: nuwa\n', 'product: enuma\nproduct: enuma\n',
                     'getvar:product FAILED (remote: Variable Not found)\n',
                     'product: enuma\nFAILED (remote: error)\n'):
            self.assertFalse(fastboot_value_matches(self.result(text), 'product', 'enuma'))

    def test_slot_lock_and_exit_status(self):
        self.assertTrue(fastboot_value_matches(self.result('current-slot: a\n'), 'current-slot', 'a'))
        self.assertFalse(fastboot_value_matches(self.result('current-slot: ab\n'), 'current-slot', 'a'))
        self.assertFalse(fastboot_value_matches(self.result('unlocked: no\n'), 'unlocked', 'yes'))
        self.assertFalse(fastboot_value_matches(self.result('product: enuma\n', 1), 'product', 'enuma'))


if __name__ == '__main__':
    unittest.main()
