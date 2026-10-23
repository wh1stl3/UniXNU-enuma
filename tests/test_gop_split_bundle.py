"""Reject stale transport, mismatched configuration and altered payloads offline."""
import copy,importlib.util,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gop_bundle',ROOT/'scripts/check_gop_split_bundle.py')
bundle=importlib.util.module_from_spec(spec);spec.loader.exec_module(bundle)

class GuardTests(unittest.TestCase):
    def altered_metadata(self,change):
        original=bundle.read
        def edited(path):
            value=copy.deepcopy(original(path));change(path,value);return value
        with patch.object(bundle,'read',edited),self.assertRaises(AssertionError):bundle.main('gop-mode-split-probes.json','enuma-gop-mode-split.json')

    def test_wrong_firmware(self):
        def change(path,value):
            if path.name=='gop-mode-split-probes.json':value['firmware_commit']='0'*40
        self.altered_metadata(change)

    def test_old_transport(self):
        def change(path,value):
            if path.name=='enuma-firmware-build.json':value['diagnostic_gop_transport']='provider-local-v1'
        self.altered_metadata(change)

    def test_additional_define_difference(self):
        def change(path,value):
            if path.name=='enuma-firmware-build.json' and 'pointer' in path.parent.name:
                value['firmware_configuration']['defines']['ENUMA_DIAG_DELAY_US']='7000000'
        self.altered_metadata(change)

    def test_image_modified(self):
        original=Path.read_bytes
        def edited(path):
            raw=original(path)
            if path.suffix=='.img':
                raw=bytearray(raw);raw[4096+192]^=1;return bytes(raw)
            return raw
        with patch.object(Path,'read_bytes',edited),self.assertRaises(AssertionError):bundle.main('gop-mode-split-probes.json','enuma-gop-mode-split.json')

if __name__=='__main__':unittest.main()
