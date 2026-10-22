"""The migrated preflight must reject unsafe staging and absent OEM inputs."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from build_enuma_firmware import source_helper


class FirmwarePreflightTests(unittest.TestCase):
    def test_changed_extension_stops_before_staging_writes(self):
        helper=source_helper()
        with tempfile.TemporaryDirectory(dir=ROOT/'out',prefix='extension-preflight-') as temp:
            target=Path(temp).resolve()
            self.assertTrue(target.is_relative_to((ROOT/'out').resolve()))
            device=target/'device';source=target/'source';meta=source/'Resources/Enuma'
            meta.mkdir(parents=True)
            (meta/'migration.json').write_text(json.dumps({'files':{}}))
            (meta/'extensions.json').write_text(json.dumps({'files':{'diagnostic.h':'0'*64}}))
            (source/'diagnostic.h').write_text('changed input')
            uefi=device/'out/uefi';core=device/'out/core'
            with self.assertRaisesRegex(ValueError,'Firmware extension changed'):
                helper.prepare(device,source,uefi,core,target/'base',target/'reference',target/'vendor')
            self.assertFalse(uefi.exists());self.assertFalse(core.exists())

    def test_source_tree_cannot_be_patch_staging(self):
        helper = source_helper()
        with tempfile.TemporaryDirectory(dir=ROOT/'out', prefix='preflight-') as temp:
            target = Path(temp).resolve()
            self.assertTrue(target.is_relative_to((ROOT/'out').resolve()))
            device = target/'device'
            with self.assertRaisesRegex(ValueError, 'inside device out'):
                helper.prepare(device, ROOT/'firmware', ROOT/'firmware', target/'core',
                               target/'base', target/'reference', target/'vendor')

    def test_missing_vendor_stops_before_staging_writes(self):
        helper = source_helper()
        with tempfile.TemporaryDirectory(dir=ROOT/'out', prefix='preflight-') as temp:
            target = Path(temp).resolve()
            self.assertTrue(target.is_relative_to((ROOT/'out').resolve()))
            device = target/'device'; source = target/'source'
            meta = source/'Resources/Enuma'; meta.mkdir(parents=True)
            (meta/'migration.json').write_text(json.dumps({'files':{}}))
            (meta/'extensions.json').write_text(json.dumps({'files':{}}))
            (meta/'vendor.json').write_text(json.dumps({'files':{'Binaries/enuma/EnvDxe/EnvDxe.efi':'0'*64}}))
            uefi = device/'out/uefi'; core = device/'out/core'
            with self.assertRaises(FileNotFoundError):
                helper.prepare(device,source,uefi,core,target/'base',target/'reference',target/'vendor')
            self.assertFalse(uefi.exists())
            self.assertFalse(core.exists())


if __name__=='__main__': unittest.main()
