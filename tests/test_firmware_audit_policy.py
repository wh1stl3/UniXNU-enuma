"""A diagnostic exclusion must never hide a normal build's missing driver."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from firmware_audit_policy import omitted_oem_modules


class FirmwareAuditPolicyTests(unittest.TestCase):
    def fixture(self):
        return {'complete':True,'fd_sha256':'a'*64,'diagnostic_omitted_oem_modules':['UFSDxe'],
                'firmware_configuration':{'defines':{'ENUMA_DIAG_DISABLE_UFS':'1'}}}

    def test_explicit_matching_diagnostic_only(self):
        self.assertEqual(omitted_oem_modules(self.fixture(),'a'*64),frozenset(['UFSDxe']))
        self.assertEqual(omitted_oem_modules({},'b'*64),frozenset())

    def test_mismatches_missing_declarations_and_other_drivers_rejected(self):
        changes=[{'complete':False},{'fd_sha256':'b'*64},{'diagnostic_omitted_oem_modules':[]},
                 {'diagnostic_omitted_oem_modules':['ClockDxe']},
                 {'diagnostic_omitted_oem_modules':['UFSDxe','ClockDxe']},
                 {'firmware_configuration':{'defines':{'ENUMA_DIAG_DISABLE_UFS':'0'}}},
                 {'firmware_configuration':{'defines':{'ENUMA_DIAG_DISABLE_UFS':'2'}}}]
        for change in changes:
            value=copy.deepcopy(self.fixture());value.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):omitted_oem_modules(value,'a'*64)


if __name__=='__main__':unittest.main()
