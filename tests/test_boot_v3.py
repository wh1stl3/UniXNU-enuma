import sys
import struct
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from package_enuma_boot import ROOT, package, verify


class BootV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        out = ROOT / 'out/boot-v3-tests'; out.mkdir(parents=True, exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(dir=out)
        cls.directory = Path(cls.temp.name)
        cls.kernel = bytearray(8193); cls.kernel[56:60] = b'ARM\x64'
        struct.pack_into('<Q', cls.kernel, 16, len(cls.kernel))
        cls.ramdisk = b'fixture-ramdisk' * 301
        k = cls.directory / 'fixture.raw'; k.write_bytes(cls.kernel)
        r = cls.directory / 'ramdisk'; r.write_bytes(cls.ramdisk)
        cls.image = cls.directory / 'not-for-device.fixture.img'
        cls.report = package(k, r, cls.image, fixture=True)
        cls.data = cls.image.read_bytes()
        import json
        (ROOT / 'reports/boot-v3-roundtrip.json').write_text(json.dumps(cls.report, indent=2) + '\n')

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def test_aosp_roundtrip(self):
        self.assertTrue(self.report['fixture_only'])
        verify(self.data, self.kernel, self.ramdisk)

    def test_truncated(self):
        for cut in (0, 43, 1579, 4095, 4096, len(self.data)-1):
            with self.assertRaises(ValueError): verify(self.data[:cut], self.kernel, self.ramdisk)

    def test_wrong_version(self):
        data = bytearray(self.data); struct.pack_into('<I', data, 40, 1)
        with self.assertRaises(ValueError): verify(data, self.kernel, self.ramdisk)

    def test_payload_mutation(self):
        data = bytearray(self.data); data[4097] ^= 1
        with self.assertRaises(ValueError): verify(data, self.kernel, self.ramdisk)

    def test_appended_dtb_rejected(self):
        with self.assertRaises(ValueError): verify(self.data + bytes(4096), self.kernel, self.ramdisk)

    def test_size_overflow_rejected(self):
        data = bytearray(self.data); struct.pack_into('<I', data, 8, 0xffffffff)
        with self.assertRaises(ValueError): verify(data, self.kernel, self.ramdisk)


if __name__ == '__main__': unittest.main()
