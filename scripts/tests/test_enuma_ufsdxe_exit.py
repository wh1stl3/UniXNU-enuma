"""Exercise the real pinned image/tool and reject malformed mappings/tool failures."""
import importlib.util
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'audit-enuma-ufsdxe-exit.py'
spec = importlib.util.spec_from_file_location('ufs_exit', SCRIPT)
ufs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ufs)
BINARY = ufs.ROOT.parent / 'uefi-enuma/Binaries/enuma/UFSDxe/UFSDxe.efi'


class ExitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = BINARY.read_bytes()
        cls.pe = ufs.PE(cls.data)
        cls.headers = Path('/home/wh1stl3/enuma-fw/mu_basecore')
        with tempfile.TemporaryDirectory() as directory:
            cls.report = ufs.audit(BINARY, cls.headers, '/usr/bin/llvm-objdump', '/usr/bin/clang', Path(directory))
        _, cls.instructions = ufs.disassemble('/usr/bin/llvm-objdump', BINARY, cls.pe)

    def test_real_image_mapping(self):
        self.assertEqual((self.pe.entry, self.pe.subsystem), (0x1000, 12))
        self.assertEqual(self.pe.rva(0x14912), 0x14912)
        self.assertEqual(self.pe.read(0x190a8, 16).hex(), '55f0ab27b8b1264c8048748f37baa2df')

    def test_nonidentity_raw_mapping(self):
        # A valid mapping must use section raw offsets, not assume RVA==file offset.
        pe = ufs.PE(self.data)
        text = next(s for s in pe.sections if s['name'] == '.text')
        text['raw'] += 0x100
        self.assertEqual(pe.offset(0x1100), 0x1200)
        self.assertEqual(pe.rva(0x1200), 0x1100)

    def test_truncated_header(self):
        with self.assertRaisesRegex(ValueError, 'PE header boundary'):
            ufs.PE(self.data[:64])

    def test_section_outside_file(self):
        data = bytearray(self.data)
        pe = struct.unpack_from('<I', data, 60)[0]
        optsize = struct.unpack_from('<H', data, pe + 20)[0]
        struct.pack_into('<I', data, pe + 24 + optsize + 20, len(data) - 4)
        with self.assertRaisesRegex(ValueError, 'section outside'):
            ufs.PE(data)

    def test_invalid_rva_and_crossing_end(self):
        for rva, size in [(0xffffffff, 8), (0x1d000, 4), (-1, 4), (0x18ffe, 4)]:
            with self.subTest(rva=rva):
                with self.assertRaises(ValueError):
                    self.pe.offset(rva, size)

    def test_disassembler_failure_is_failure(self):
        with self.assertRaises(subprocess.CalledProcessError):
            ufs.disassemble('/usr/bin/false', BINARY, self.pe)

    def test_empty_disassembler_output_is_failure(self):
        with self.assertRaisesRegex(ValueError, 'no usable instructions'):
            ufs.disassemble('/usr/bin/true', BINARY, self.pe)

    def test_actual_xrefs_and_event_arguments(self):
        strings = self.report['strings']
        self.assertEqual([s['xrefs'][0]['instruction_rva'] for s in strings], [0x278c, 0x27e4])
        exits = [e for e in self.report['event_sites'] if e['is_exit_event']]
        self.assertEqual([(e['call_rva'], e['arguments_x0_x5'][:4]) for e in exits],
                         [(0x5eec, [0x200, 8, 0x5de8, 0]), (0x6184, [0x200, 16, 0x60c0, 0])])
        self.assertEqual(exits[1]['callback']['direct_targets'][0]['target_rva'], 0x603c)
        self.assertEqual(exits[1]['direct_callee_tables'][0]['indirect_calls'][0]['instruction_rva'], 0x6088)
        self.assertTrue(all(v == 'UNKNOWN' for v in self.report['unknown'].values()))

    def test_mutated_real_xref_not_found(self):
        instructions = dict(self.instructions)
        instructions[0x2788] = ('adrp', 'x0, 0x15000')
        _, refs = ufs.trace(instructions, 0x277c, 0x27f8, 0x1a8e0, self.report['headers'])
        self.assertFalse(any(r['target_rva'] == 0x14912 for r in refs))

    def test_non_bs_pointer_not_service_by_offset_coincidence(self):
        events, _ = ufs.trace(self.instructions, 0x5e34, 0x5f24, 0xdead, self.report['headers'])
        self.assertEqual(events, [])

    def test_interface_guid_mismatch(self):
        for rva, name in [(0x192a8, 'StatusCode'), (0x19098, 'Shim HOB')]:
            with self.subTest(rva=rva):
                data = bytearray(self.data)
                data[self.pe.offset(rva)] ^= 1
                with self.assertRaisesRegex(ValueError, name + ' GUID mismatch'):
                    ufs.interface_evidence(ufs.PE(bytes(data)), self.instructions, self.report['headers'], self.headers)

    def test_interface_wrong_source_or_member(self):
        for at, operands, message in [
                (0x6064, 'x8, [x10, #0x8e8]', 'StatusCode LocateProtocol/flag'),
                (0x606c, 'x8, [x8, #0x148]', 'StatusCode LocateProtocol/flag'),
                (0x4cdc, 'x2, [x8, #0x10]', 'Shim config library'),
                (0x4c10, 'x3, [x8, #0x18]', 'Shim config library')]:
            with self.subTest(at=at):
                instructions = dict(self.instructions)
                instructions[at] = ('ldr', operands)
                with self.assertRaisesRegex(ValueError, message + ' member/source mismatch'):
                    ufs.interface_evidence(self.pe, instructions, self.report['headers'], self.headers)


if __name__ == '__main__':
    unittest.main()
