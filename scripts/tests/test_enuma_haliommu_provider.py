"""Focused provider increment; no vendor execution and no old suite replay."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'audit-enuma-ufsdxe-exit.py'
spec = importlib.util.spec_from_file_location('hal_audit', SCRIPT)
ufs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ufs)


class ProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binary = ufs.ROOT.parent / 'uefi-enuma/Binaries/enuma/HALIOMMU/HALIOMMU.efi'
        ufspath = ufs.ROOT.parent / 'uefi-enuma/Binaries/enuma/UFSDxe/UFSDxe.efi'
        cls.pe = ufs.PE(ufspath.read_bytes())
        _, cls.ins = ufs.disassemble('/usr/bin/llvm-objdump', ufspath, cls.pe)
        cls.layout, _, _ = ufs.header_layout(Path('/home/wh1stl3/enuma-fw/mu_basecore'), '/usr/bin/clang')

    def audit(self, instructions=None):
        with tempfile.TemporaryDirectory() as directory:
            return ufs.audit_provider(self.binary, self.pe, self.ins if instructions is None else instructions,
                                      self.layout, '/usr/bin/llvm-objdump', Path(directory))

    def test_real_provider_chain(self):
        report = self.audit()
        self.assertEqual(report['guid'], '54b6d3b4-5d33-4f91-8600-6c41d5deb19a')
        self.assertEqual(report['table_targets'], {0: 0x16b4, 0x10: 0x1920, 0x40: 0x2f10})
        self.assertEqual(report['client_context']['bytes'], 0x38)
        self.assertEqual([g['w2'] for g in report['ufsdxe_calls']['groups']], [0, 16])
        self.assertIn('UNKNOWN', report['resource_selection']['actual_UFS_records'])

    def test_provider_guid_mutation(self):
        read = ufs.PE.read
        def mutate(pe, rva, size):
            data = read(pe, rva, size)
            return bytes([data[0] ^ 1]) + data[1:] if rva == 0x9048 else data
        with patch.object(ufs.PE, 'read', mutate):
            with self.assertRaisesRegex(ValueError, 'provider GUID mismatch'):
                self.audit()

    def test_factory_table_member_mutation(self):
        read = ufs.PE.read
        def mutate(pe, rva, size):
            data = read(pe, rva, size)
            return struct.pack('<Q', 0x14d0) if rva == 0x90a0 else data
        with patch.object(ufs.PE, 'read', mutate):
            with self.assertRaisesRegex(ValueError, 'provider factory member mismatch'):
                self.audit()

    def test_selector_parameter_mutations(self):
        for at, instruction in [(0x141c4, ('mov', 'w2, #0x1')),
                                (0x14238, ('orr', 'w2, wzr, #0x11'))]:
            with self.subTest(at=at):
                instructions = dict(self.ins)
                instructions[at] = instruction
                with self.assertRaisesRegex(ValueError, 'UFSDxe provider parameters member/source mismatch'):
                    self.audit(instructions)


if __name__ == '__main__':
    unittest.main()
