"""Guard that free-space normalization cannot erase allocated FAT clusters."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('discovery', Path(__file__).resolve().parents[1] /
                                             'scripts/prepare_enuma_discovery_volume.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FreeSpaceTests(unittest.TestCase):
    def fixture(self):
        raw = bytearray(8 * 512)
        struct.pack_into('<H', raw, 11, 512)
        raw[13] = 1
        struct.pack_into('<H', raw, 14, 1)
        raw[16] = 2
        struct.pack_into('<I', raw, 32, 8)
        struct.pack_into('<I', raw, 36, 1)
        raw[82:90] = b'FAT32   '
        raw[510:512] = b'\x55\xaa'
        for fat in (512, 1024):
            struct.pack_into('<I', raw, fat + 2 * 4, 0x0fffffff)
        raw[1536:2048] = b'A' * 512  # allocated cluster 2
        raw[2048:2560] = b'R' * 512  # free cluster 3 with residue
        return raw

    def test_allocated_cluster_and_metadata_preserved(self):
        raw = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / 'fixture.img'
            image.write_bytes(raw)
            self.assertEqual(module.clear_free_clusters(image), 1)
            result = image.read_bytes()
            self.assertEqual(result[:2048], raw[:2048])
            self.assertEqual(result[2048:], bytes(len(raw) - 2048))

    def test_disagreeing_fat_refuses_without_modifying_image(self):
        raw = self.fixture()
        struct.pack_into('<I', raw, 1024 + 3 * 4, 0x0fffffff)
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / 'fixture.img'
            image.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, 'copies disagree'):
                module.clear_free_clusters(image)
            self.assertEqual(image.read_bytes(), raw)

    def test_truncated_size_and_invalid_cluster_size_refused(self):
        for case in ('truncated', 'cluster'):
            raw = self.fixture()
            if case == 'truncated':
                raw = raw[:-1]
            else:
                raw[13] = 3
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                image = Path(directory) / 'fixture.img'
                image.write_bytes(raw)
                with self.assertRaises(ValueError):
                    module.clear_free_clusters(image)
                self.assertEqual(image.read_bytes(), raw)


if __name__ == '__main__':
    unittest.main()
