"""Firmware ownership adapter rejects mismatches before importing build code."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('build_adapter',ROOT/'scripts/build_enuma_firmware.py')
adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)

class OwnershipTests(unittest.TestCase):
    def test_implementation_is_firmware_owned(self):
        module=adapter._backend()
        self.assertEqual(Path(module.__file__).resolve(),ROOT/'firmware/Resources/Scripts/build_enuma_firmware.py')
        self.assertEqual(module.SOURCE,ROOT/'firmware')
        self.assertIsNone(module.ROOT)

    def test_source_change_rejected_before_import(self):
        original=Path.read_bytes
        def changed(path):
            data=original(path)
            return data+b'altered' if path.name=='build_enuma_firmware.py' else data
        with patch.object(Path,'read_bytes',changed),patch.object(adapter.importlib.util,'spec_from_file_location') as load:
            with self.assertRaisesRegex(ValueError,'hash mismatch'):adapter._backend()
            load.assert_not_called()

    def test_revision_mismatch_rejected_before_import(self):
        with patch.object(adapter.subprocess,'check_output',return_value='0'*40),patch.object(adapter.importlib.util,'spec_from_file_location') as load:
            with self.assertRaisesRegex(ValueError,'device lock'):adapter._backend()
            load.assert_not_called()

if __name__=='__main__':unittest.main()
