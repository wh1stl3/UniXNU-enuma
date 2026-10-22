"""Diagnostic gate selection must fail closed; test actual source transformation."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_entry_probe import instrument, ROOT


class EntryProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=(ROOT/'out/firmware-build/uefi/BootShim/BootShim.S').read_text()

    def test_preserve_header_and_real_copy_body(self):
        for stage in ('shim-entry','shim-copy'):
            result=instrument(self.source,stage,2)
            self.assertEqual(result.split('_Start:')[0],self.source.split('_Start:')[0])
            copy=lambda s:s[s.index('_CopyLoop:'):s.index('_Entry:')]
            self.assertEqual(copy(result),copy(self.source))
            self.assertIn('  smc #0',result)
            self.assertIn('  movk x0, #0x8400, lsl #16',result)
            self.assertEqual(result.count('  b .LEnumaResetGate'),1)

    def test_moved_hook_rejected(self):
        with self.assertRaises(ValueError):instrument(self.source.replace('_Start:','_Moved:'),'shim-entry',2)
        with self.assertRaises(ValueError):instrument(self.source.replace('  br    x5','  br x5'),'shim-copy',2)

    def test_unsupported_delay_or_stage_rejected(self):
        for stage,delay in (('sec-entry',2),('shim-entry',0),('shim-copy',120)):
            with self.assertRaises(ValueError):instrument(self.source,stage,delay)


if __name__=='__main__':unittest.main()
