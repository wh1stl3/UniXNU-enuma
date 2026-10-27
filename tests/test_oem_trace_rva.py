import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from map_oem_trace_rva import identify, map_return


def fixture(word, flags=0x20000000):
    data = bytearray(1024)
    data[:2] = b'MZ'
    struct.pack_into('<I', data, 60, 64)
    data[64:68] = b'PE\0\0'
    struct.pack_into('<HH', data, 68, 0xaa64, 1)
    struct.pack_into('<H', data, 84, 112)
    struct.pack_into('<H', data, 88, 0x20b)
    struct.pack_into('<8sIIII', data, 200, b'.text', 512, 4096, 512, 512)
    struct.pack_into('<I', data, 236, flags)
    struct.pack_into('<I', data, 512, word)
    return data


class MappingTests(unittest.TestCase):
    def test_direct_signed_target(self):
        self.assertEqual(map_return(fixture(0x94000002), 4100)['static_target_rva'], '0x1008')
        self.assertEqual(map_return(fixture(0x97ffffff), 4100)['static_target_rva'], '0xffc')

    def test_indirect_no_invented_target(self):
        result = map_return(fixture(0xd63f0120), 4100)
        self.assertEqual(result['target_register'], 'x9')
        self.assertIsNone(result['static_target_rva'])
        self.assertFalse(result['execution_proven'])

    def test_non_calls_rejected(self):
        for word in (0xd503201f, 0xd61f0120, 0xd65f03c0, 0x14000002):
            with self.assertRaises(ValueError):
                map_return(fixture(word), 4100)

    def test_wrong_image(self):
        with self.assertRaises(ValueError):
            identify(fixture(0x94000002))

    def test_invalid_ranges_and_permissions(self):
        for rva in (0, 3, 4099, 8192):
            with self.assertRaises(ValueError):
                map_return(fixture(0x94000002), rva)
        with self.assertRaises(ValueError):
            map_return(fixture(0x94000002, 0), 4100)
        with self.assertRaises(ValueError):
            map_return(fixture(0x94000002)[:600], 4100)

    def test_ambiguous_sections(self):
        data = fixture(0x94000002)
        struct.pack_into('<H', data, 70, 2)
        data[240:280] = data[200:240]
        with self.assertRaises(ValueError):
            map_return(data, 4100)


if __name__ == '__main__':
    unittest.main()
