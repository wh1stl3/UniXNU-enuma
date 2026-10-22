"""Exercise malformed FDTs and donor identity/digest rejection without device I/O."""
import copy
import hashlib
import plistlib
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_inputs import donor_audit, parse_fdt


def u32(*values):
    return struct.pack('>' + 'I' * len(values), *values)


def fixture():
    names = b'model\0'
    body = u32(1) + bytes(4) + u32(3, 6, 0) + b'enuma\0\0\0' + u32(2, 9)
    return u32(0xD00DFEED, 56 + len(body) + len(names), 56, 56 + len(body), 40, 17, 16, 0, len(names), len(body)) + bytes(16) + body + names


class FdtTests(unittest.TestCase):
    def test_valid_root(self):
        self.assertEqual(parse_fdt(fixture()), {'/': {'model': b'enuma\0'}})

    def test_every_truncation_rejected(self):
        data = fixture()
        for length in range(len(data)):
            with self.subTest(length=length), self.assertRaises(ValueError):
                parse_fdt(data[:length])

    def test_corrupt_offsets_sizes_and_tokens(self):
        for offset, value in ((0, 0), (8, 0xFFFFFFFC), (12, 56), (16, 41), (20, 16),
                              (32, 0xFFFFFFFF), (36, 0xFFFFFFFF), (56, 3), (64, 99),
                              (68, 0xFFFFFFFF), (72, 0xFFFFFFFF), (84, 9), (88, 2)):
            data = bytearray(fixture())
            struct.pack_into('>I', data, offset, value)
            with self.subTest(offset=offset, value=value), self.assertRaises(ValueError):
                parse_fdt(data)


class DonorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.cache = Path(self.temp.name)
        (self.cache / 'components').mkdir()
        self.board = {'ipsw': {'product': 'iPad7,1', 'version': '17.7.11', 'build': '21H461',
                               'device_class': 'j120ap', 'chip_id': 0x8011, 'board_id': 12}}
        items = {}
        for index, name in enumerate(('KernelCache', 'DeviceTree', 'StaticTrustCache', 'Cryptex1,SystemTrustCache', 'OS', 'Cryptex1,SystemOS')):
            data = ('synthetic component ' + name).encode()
            member = f'component-{index}'
            (self.cache / 'components' / member).write_bytes(data)
            items[name] = {'Info': {'Path': member}, 'Digest': hashlib.sha384(data).digest()}
        self.manifest = {'ProductVersion': '17.7.11', 'ProductBuildVersion': '21H461',
                         'SupportedProductTypes': ['iPad7,1'], 'BuildIdentities': [{
                             'Info': {'DeviceClass': 'j120ap', 'RestoreBehavior': 'Erase', 'Variant': 'synthetic'},
                             'ApChipID': '0x8011', 'ApBoardID': '0x0c', 'Manifest': items}]}

    def tearDown(self):
        self.temp.cleanup()

    def audit(self):
        (self.cache / 'BuildManifest.plist').write_bytes(plistlib.dumps(self.manifest))
        return donor_audit(self.cache, self.board)

    def test_matching_identity(self):
        self.assertEqual(len(self.audit()['components']), 6)

    def test_wrong_os_and_product(self):
        for key, value in (('ProductVersion', '16.7.16'), ('ProductBuildVersion', 'wrong'), ('SupportedProductTypes', ['iPhone10,3'])):
            saved = self.manifest[key]
            self.manifest[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.audit()
            self.manifest[key] = saved

    def test_ambiguous_identity(self):
        self.manifest['BuildIdentities'].append(copy.deepcopy(self.manifest['BuildIdentities'][0]))
        with self.assertRaises(ValueError):
            self.audit()

    def test_wrong_board(self):
        self.manifest['BuildIdentities'][0]['ApBoardID'] = '0x0d'
        with self.assertRaises(ValueError):
            self.audit()

    def test_component_corruption(self):
        (self.cache / 'components/component-0').write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'SHA384 mismatch'):
            self.audit()

    def test_reference_pin_mismatch(self):
        self.board['ipsw']['sha256'] = {'component-4': '0' * 64}
        with self.assertRaisesRegex(ValueError, 'SHA256 mismatch'):
            self.audit()


if __name__ == '__main__':
    unittest.main()
