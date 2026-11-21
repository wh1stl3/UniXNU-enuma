"""Only self-generated synthetic snapshots; success never identifies a device."""
import copy
import importlib.util
import json
from pathlib import Path
import struct
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'parse-enuma-ufs-identity.py'
spec = importlib.util.spec_from_file_location('identity_parser', SCRIPT)
identity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(identity)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.input = identity.synthetic_demo()

    def test_synthetic_association_not_current_identity(self):
        result = identity.parse(self.input)
        self.assertTrue(result['synthetic'])
        self.assertEqual(result['records'][1]['partition_association'], 'MATCHED_WITHIN_SYNTHETIC_SNAPSHOT')
        self.assertEqual(result['current_device_identity'], 'UNKNOWN')

    def test_ufs_and_scsi_little_endian(self):
        path = identity.device_path(self.input['records'][0]['device_path_hex'])
        self.assertEqual(path['transport'], [{'kind': 'UFS', 'pun': 1, 'lun': 3}])
        scsi = struct.pack('<BBHHH', 3, 2, 8, 0x1234, 0x5678) + identity.END
        self.assertEqual(identity.device_path(scsi.hex())['transport'][0]['lun'], 0x5678)

    def test_truncated_path(self):
        with self.assertRaisesRegex(ValueError, 'truncated'):
            identity.device_path('0319060001')

    def test_illegal_node_length(self):
        with self.assertRaisesRegex(ValueError, 'illegal node length'):
            identity.device_path('03190300')

    def test_bad_fixed_node_length(self):
        with self.assertRaisesRegex(ValueError, 'UFS node length'):
            identity.device_path('03190700010300' + identity.END.hex())

    def test_missing_end(self):
        with self.assertRaisesRegex(ValueError, 'missing complete'):
            identity.device_path('031906000103')

    def test_revision_fields_unavailable(self):
        self.input['records'][0]['media']['LowestAlignedLba'] = 0
        with self.assertRaisesRegex(ValueError, 'Revision insufficient'):
            identity.parse(self.input)
        self.input = identity.synthetic_demo()
        self.input['records'][0]['block_io_revision'] = 0x20001
        self.input['records'][0]['media']['OptimalTransferLengthGranularity'] = 1
        with self.assertRaisesRegex(ValueError, 'Revision insufficient'):
            identity.parse(self.input)

    def test_duplicate_parent_does_not_pick_first(self):
        extra = copy.deepcopy(self.input['records'][0]); extra['id'] = 'second-parent'
        self.input['records'].append(extra)
        child = identity.parse(self.input)['records'][1]
        self.assertEqual(child['partition_association'], 'UNKNOWN')
        self.assertIn('missing/ambiguous complete parent path', child['reasons'])

    def test_same_capacity_other_parent_not_identity(self):
        self.input['records'][0]['device_path_hex'] = '031906000104' + identity.END.hex()
        self.assertEqual(identity.parse(self.input)['records'][1]['partition_association'], 'UNKNOWN')

    def test_signature_mismatch(self):
        self.input['gpt_reference']['partition_signature_hex'] = bytes(reversed(range(16))).hex()
        self.assertIn('partition signature/number mismatch', identity.parse(self.input)['records'][1]['reasons'])

    def test_capacity_without_signature_not_identity(self):
        del self.input['gpt_reference']['partition_signature_hex']
        self.assertEqual(identity.parse(self.input)['records'][1]['partition_association'], 'UNKNOWN')

    def test_4096_512_logical_unit_mismatch(self):
        self.input['records'][0]['media']['BlockSize'] = 512
        self.assertIn('4096/512 logical-block unit mismatch', identity.parse(self.input)['records'][1]['reasons'])
        self.input['gpt_reference']['logical_block_bytes'] = 512
        with self.assertRaisesRegex(ValueError, 'not Linux512'):
            identity.parse(self.input)

    def test_linux_sector_geometry_not_lba(self):
        self.input['gpt_reference']['first_lba'] *= 8
        self.input['gpt_reference']['last_lba_inclusive'] = 29 * 8 + 7
        self.assertIn('GPT/HD geometry mismatch; units are logical blocks, not Linux sectors',
                      identity.parse(self.input)['records'][1]['reasons'])

    def test_legal_target_is_not_presence(self):
        self.input['records'] = []
        self.input['legal_target_luns'] = [{'target_hex': bytes(range(16)).hex(), 'lun': 3}]
        result = identity.parse(self.input)
        self.assertEqual(result['current_device_identity'], 'UNKNOWN')
        self.assertIn('does not prove presence', result['legal_target_existence'])

    def test_media_id_and_cached_present_are_not_persistent_or_live(self):
        result = identity.parse(self.input)
        for record in result['records']:
            self.assertEqual(record['device_exists_now'], 'UNKNOWN')
            self.assertEqual(record['media_id_identity'], 'UNKNOWN: not persistent')

    def test_selector_and_public_route_not_ownership(self):
        self.input['public_evidence'] = {'selector': 16, 'iort_route_reference': 'synthetic public routing row'}
        for record in identity.parse(self.input)['records']:
            self.assertIn('UNKNOWN', record['sid_context_exclusivity'])

    def test_mode_adapter_id_is_not_lun(self):
        self.input['records'][0]['pass_thru_mode'] = {'AdapterId': 0, 'Attributes': 3, 'IoAlign': 8}
        with self.assertRaisesRegex(ValueError, 'unsupported fields: record'):
            identity.parse(self.input)  # v2 deliberately omits Mode, no LUN association benefit

    def test_unknown_path_has_no_default_lun(self):
        path = bytes((3, 0x7e, 4, 0)) + identity.END
        self.input['records'] = [dict(self.input['records'][0], device_path_hex=path.hex())]
        self.assertEqual(identity.parse(self.input)['records'][0]['path_transport'], 'UNKNOWN')

    def test_existing_gpt_reference_does_not_invent_uefi_identity(self):
        report = json.loads((identity.ROOT / '.cache/ufs-evidence/report.json').read_text())
        self.input['gpt_reference'] = identity.gpt_reference_from_report(report)
        child = identity.parse(self.input)['records'][1]
        self.assertTrue(child['synthetic'])
        self.assertEqual(child['partition_association'], 'UNKNOWN')
        self.assertNotIn('partition_signature_hex', self.input['gpt_reference'])

    def test_missing_record_prevents_global_uniqueness(self):
        extra = {'id': 'unread', 'status': 'unread', 'reason': 'not read', 'truncated': False}
        self.input['records'].append(extra); self.input['envelope']['reported_handles'] = 3
        result = identity.parse(self.input)
        self.assertFalse(result['global_uniqueness_eligible'])
        self.assertEqual(result['summary']['userdata'], 'UNKNOWN')

    def test_limit_and_count_mismatch(self):
        for count in (1, 65):
            self.input['envelope']['reported_handles'] = count
            self.assertEqual(identity.parse(self.input)['summary']['userdata'], 'UNKNOWN')

    def test_synthetic_scsi_match_is_not_ufs_lun(self):
        parent = struct.pack('<BBHHH', 3, 2, 8, 1, 3) + identity.END
        old = bytes.fromhex(self.input['records'][1]['device_path_hex'])
        hd_start = len(bytes.fromhex(self.input['records'][0]['device_path_hex'])) - 4
        self.input['records'][0]['device_path_hex'] = parent.hex()
        self.input['records'][1]['device_path_hex'] = (parent[:-4] + old[hd_start:]).hex()
        result = identity.parse(self.input)
        self.assertEqual(result['summary']['ufs_lun_candidate'], 'UNKNOWN')

    def test_real_historical_reference_has_no_circular_parent(self):
        reference = identity.historical_gpt_reference()
        self.assertEqual(reference['partition_name'], 'userdata')
        self.assertEqual(reference['partition_number'], 34)
        self.assertEqual(len(bytes.fromhex(reference['partition_signature_hex'])), 16)
        self.assertNotIn('parent_device_path_hex', reference)
        self.input['gpt_reference'] = reference
        self.assertEqual(identity.parse(self.input)['summary']['userdata'], 'UNKNOWN')


if __name__ == '__main__':
    unittest.main()
