"""Check complete UUID conversion against EFI_GUID memory layout."""
import struct
import sys
import unittest
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from build_enuma_firmware import diagnostic_guid_defines


class DiagnosticGuidTests(unittest.TestCase):
    def test_complete_efi_guid_byte_order(self):
        value='12345678-9abc-def0-1122-334455667788'
        definitions=diagnostic_guid_defines(value)
        words=[int(definitions[key].removesuffix('ULL'),16) for key in
               ('ENUMA_DIAG_GUID_LOW64','ENUMA_DIAG_GUID_HIGH64')]
        self.assertEqual(struct.pack('<QQ',*words),uuid.UUID(value).bytes_le)
        self.assertEqual(definitions['ENUMA_DIAG_GUID_ENABLED'],'1')

    def test_disabled_and_malformed_guid(self):
        self.assertEqual(diagnostic_guid_defines(None),{
            'ENUMA_DIAG_GUID_ENABLED':'0','ENUMA_DIAG_GUID_LOW64':'0','ENUMA_DIAG_GUID_HIGH64':'0'})
        with self.assertRaises(ValueError):diagnostic_guid_defines('not-a-guid')


if __name__=='__main__':unittest.main()
