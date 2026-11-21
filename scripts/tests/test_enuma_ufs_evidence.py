"""Input validation tests; mutations use real local bytes, never hardware."""
import copy
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
import zlib
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'check-enuma-ufs-evidence.py'
spec = importlib.util.spec_from_file_location('ufs_evidence', SCRIPT)
ufs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ufs)


class GptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.capture = ufs.ROOT / '.cache/live-capture/20261107T141941555586Z'
        cls.original = (cls.capture / 'sda_first_32768.bin').read_bytes()
        cls.sectors = int((cls.capture / 'sda_sectors.txt').read_text())

    def check(self, data=None, block=4096, sectors=None):
        return ufs.gpt_evidence(self.original if data is None else data, block,
                                self.sectors if sectors is None else sectors)

    def mutate(self, offset, fmt, value, entries=False):
        data = bytearray(self.original)
        struct.pack_into(fmt, data, offset, value)
        # Repair independent CRCs, so tests exercise semantic geometry validation.
        if entries:
            struct.pack_into('<I', data, 4096 + 88, zlib.crc32(data[8192:16384]))
        struct.pack_into('<I', data, 4096 + 16, 0)
        struct.pack_into('<I', data, 4096 + 16, zlib.crc32(data[4096:4096 + 92]))
        return data

    def test_real_primary_and_units(self):
        result = self.check()
        self.assertEqual(result['total_bytes'], 253461790720)
        self.assertEqual(result['total_logical_blocks'], 61880320)
        self.assertEqual(result['userdata'], {'first_lba': 2686976,
            'last_lba_inclusive': 61880314, 'blocks': 59193339, 'bytes': 242455916544})
        self.assertIn('UNKNOWN', result['backup_gpt'])

    def test_earlier_original(self):
        earlier = self.capture.parent / '20261107T141806Z'
        # Earlier collector had a trailing transport suffix; only header-directed bytes count.
        result = ufs.gpt_evidence((earlier / 'sda_first_32768.bin').read_bytes(),
            int((earlier / 'sda_logical_block_size.txt').read_text()),
            int((earlier / 'sda_sectors.txt').read_text()))
        self.assertEqual(result['userdata'], self.check()['userdata'])

    def test_non4096(self):
        with self.assertRaisesRegex(ValueError, '4096'):
            self.check(block=512)

    def test_capacity_overflow(self):
        with self.assertRaisesRegex(ValueError, 'overflow'):
            self.check(sectors=1 << 64)

    def test_sector_unit_confusion(self):
        with self.assertRaisesRegex(ValueError, 'geometry'):
            self.check(sectors=self.sectors // 8)

    def test_bad_header_crc(self):
        data = bytearray(self.original)
        data[4096 + 56] ^= 1
        with self.assertRaisesRegex(ValueError, 'header CRC'):
            self.check(data)

    def test_bad_entry_crc(self):
        data = bytearray(self.original)
        data[8192 + 48] ^= 1
        with self.assertRaisesRegex(ValueError, 'entry CRC'):
            self.check(data)

    def test_entry_window_overflow(self):
        data = self.mutate(4096 + 72, '<Q', (1 << 64) - 1)
        with self.assertRaisesRegex(ValueError, 'window overflow'):
            self.check(data)

    def test_truncated_entries(self):
        with self.assertRaisesRegex(ValueError, 'truncated GPT entries'):
            self.check(self.original[:10000])

    def test_out_of_range_partition_with_valid_crcs(self):
        data = self.mutate(8192 + 40, '<Q', 61880320, entries=True)
        with self.assertRaisesRegex(ValueError, 'outside usable'):
            self.check(data)

    def test_inverted_partition_with_valid_crcs(self):
        data = self.mutate(8192 + 32, '<Q', 61880314, entries=True)
        with self.assertRaisesRegex(ValueError, 'outside usable'):
            self.check(data)


class DtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = ufs.Tree(ufs.ROOT / '.cache/device-evidence/20261109-live-dt/live.dts')
        cls.hc = cls.tree.find('ufshc@1d84000')
        cls.shared = ufs.Tree(ufs.ROOT.parent / 'UniXNU-sm8250-common/dts/sm8250.dtsi', fragment=True)

    def setUp(self):
        self.t = copy.deepcopy(self.tree)

    def test_actual_provider_cells_and_order(self):
        refs = self.t.refs(self.hc, 'clocks', '#clock-cells')
        self.assertEqual([r['args'] for r in refs],
                         [[167], [6], [166], [179], [170], [0], [178], [176], [177]])
        self.assertEqual(refs[5]['compatible'], ['qcom,kona-rpmh-clk'])

    def test_unresolved_reset(self):
        self.t.nodes[self.hc]['resets'] = [[0xdeadbeef, 33]]
        with self.assertRaisesRegex(ValueError, 'unresolved critical phandle'):
            self.t.refs(self.hc, 'resets', '#reset-cells')

    def test_truncated_provider_specifier(self):
        self.t.nodes[self.hc]['clocks'] = [[0x16]]
        with self.assertRaisesRegex(ValueError, 'truncated clocks'):
            self.t.refs(self.hc, 'clocks', '#clock-cells')

    def test_missing_provider_cell_definition(self):
        del self.t.nodes[self.t.provider(0x16)]['#reset-cells']
        with self.assertRaises(KeyError):
            self.t.refs(self.hc, 'resets', '#reset-cells')

    def test_dtc_variable_cells_not_pairs(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'test.dts'
            source.write_text('/dts-v1/; / { a: a { #clock-cells=<0>; }; '
                'b: b { #clock-cells=<2>; }; c { clocks=<&a>, <&b 7 9>, <&a>; }; };')
            tree = ufs.Tree(source)
        self.assertEqual([r['args'] for r in tree.refs('/c', 'clocks', '#clock-cells')],
                         [[], [7, 9], []])

    def test_reg_overflow(self):
        self.t.nodes['/soc']['#address-cells'] = [[2]]
        self.t.nodes[self.hc]['reg'] = [[0xffffffff, 0xfffffff0, 0x100]]
        with self.assertRaisesRegex(ValueError, 'overflow'):
            self.t.reg(self.hc)

    def test_missing_critical_supply_in_collector(self):
        del self.t.nodes[self.hc]['vcc-supply']
        with patch.object(ufs, 'Tree', return_value=self.t):
            with self.assertRaisesRegex(ValueError, 'supply reference'):
                ufs.dt_evidence(None, None)

    def test_shared_hc_mismatch_in_collector(self):
        shared = copy.deepcopy(self.shared)
        shared.nodes[shared.find('ufshc@1d84000')]['reg'] = [[0, 0x1d84000, 0, 0x2000]]
        with patch.object(ufs, 'Tree', side_effect=[self.t, shared]):
            with self.assertRaisesRegex(ValueError, '^shared HC mismatch$'):
                ufs.dt_evidence(None, None)

    def test_shared_enabled_in_collector(self):
        shared = copy.deepcopy(self.shared)
        shared.nodes[shared.find('ufshc@1d84000')]['status'] = ['okay']
        with patch.object(ufs, 'Tree', side_effect=[self.t, shared]):
            with self.assertRaisesRegex(ValueError, '^shared HC/PHY must remain disabled$'):
                ufs.dt_evidence(None, None)

    def test_nonidentity_bus_range_in_collector(self):
        # Valid cell geometry, but child0 maps to parent0x1000 rather than0.
        self.t.nodes['/soc']['ranges'] = [[0, 0, 0x1000, 0xffffffff]]
        with patch.object(ufs, 'Tree', return_value=self.t):
            with self.assertRaisesRegex(ValueError, '^non-identity bus range unsupported$'):
                ufs.dt_evidence(None, None)

    def test_wrong_irq_in_collector(self):
        # Valid three-cell GIC specifier; reject INTID substituted for SPI index.
        self.t.nodes[self.hc]['interrupts'] = [[0, 297, 4]]
        with patch.object(ufs, 'Tree', return_value=self.t):
            with self.assertRaisesRegex(ValueError, '^unexpected GIC SPI tuple$'):
                ufs.dt_evidence(None, None)

    def test_reset_pin_direction_in_collector(self):
        provider = self.t.nodes[self.t.provider(0x77)]
        del provider['config']['output-low']
        with patch.object(ufs, 'Tree', return_value=self.t):
            with self.assertRaisesRegex(ValueError, 'reset pin configuration'):
                ufs.dt_evidence(None, None)

    def test_missing_gpt_is_unknown_not_prose(self):
        with patch.object(Path, 'is_file', return_value=False), \
             patch.object(ufs, 'dt_evidence', return_value={}), \
             patch.object(ufs, 'firmware_evidence', return_value={}), \
             patch.object(Path, 'read_bytes', return_value=b''):
            report = ufs.collect()
        self.assertEqual(report['gpt']['status'], 'UNKNOWN')
        self.assertTrue(all(v == 'UNKNOWN' for v in report['unknown'].values()))
        history = report['historical_partition_identity']
        self.assertEqual(history['linux_sda_to_lun'], 'UNKNOWN')
        self.assertEqual(history['proc_partition']['unit_bytes'], 1024)


if __name__ == '__main__':
    unittest.main()
