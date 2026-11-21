"""Mutate actual private-table input bytes in memory, not a mirrored decoder."""
import importlib.util
from pathlib import Path
import struct
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'check-enuma-ufs-property-closure.py'
spec = importlib.util.spec_from_file_location('private_property', SCRIPT)
closure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(closure)


class PropertyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = closure.ROOT.parent / 'uefi-enuma/Binaries/enuma/DALSys/DALSys.efi'
        cls.data = closure.pinned_bytes(path.read_bytes(), closure.DAL_PIN)
        cls.pe = closure.base.PE(cls.data)

    def mutate(self, rva, fmt, value):
        data = bytearray(self.data)
        struct.pack_into(fmt, data, self.pe.offset(rva, struct.calcsize(fmt)), value)
        return closure.base.PE(bytes(data))

    def test_real_private_records(self):
        result = closure.private_resources(self.pe)
        self.assertEqual(result['node_count'], 25)
        self.assertEqual([r['raw_uint32'] for r in result['records']],
                         [[0, 1, 0x4e0, 0x30, 0], [16, 1, 0xe0, 0x30, 0]])
        self.assertEqual([r['referenced_node_raw_uint64_at_0x10'] for r in result['records']], [0x15000000] * 2)
        self.assertIn('UNKNOWN', result['unknown'])

    def test_changed_input_hash_rejected(self):
        data = bytearray(self.data); data[-1] ^= 1
        with self.assertRaisesRegex(ValueError, 'fixed input hash mismatch'):
            closure.pinned_bytes(bytes(data), closure.DAL_PIN)

    def test_wrong_name(self):
        for at, message in [(0x8e38, 'SMMU name missing'), (0x1c2ef, 'IORT property name mismatch')]:
            with self.subTest(at=at):
                with self.assertRaisesRegex(ValueError, message):
                    closure.private_resources(self.mutate(at, '<B', ord('X')))

    def test_typed_index_outside_span(self):
        with self.assertRaisesRegex(ValueError, 'typed index outside physical span'):
            closure.private_resources(self.mutate(0x1c438, '<I', 0xffffffff))

    def test_node_outside_table(self):
        with self.assertRaisesRegex(ValueError, 'node length outside private table'):
            closure.private_resources(self.mutate(0x2c6e1, '<H', 0xffff))

    def test_record_outside_node(self):
        with self.assertRaisesRegex(ValueError, 'record range outside node'):
            closure.private_resources(self.mutate(0x2c6ec, '<I', 0x60))


if __name__ == '__main__':
    unittest.main()
