"""Check actual encoded inputs against the unchanged ArmCpu DT byte contract."""
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from prepare_enuma_adt_fragment import ROOT, hardware_fragment, locked_encoder


def decode(blob):
    nodes = {}
    def visit(offset, parent):
        count, children = struct.unpack_from('<II', blob, offset); offset += 8
        props = {}
        for _ in range(count):
            key, size = struct.unpack_from('<32sI', blob, offset); offset += 36
            props[key.rstrip(b'\0').decode()] = blob[offset:offset+size]
            offset += (size+3)&~3
        name = props['name'].rstrip(b'\0').decode()
        path = (parent+'/'+name) if parent is not None else ''
        nodes[path] = props
        for _ in range(children): offset = visit(offset, path)
        return offset
    assert visit(0, None) == len(blob)
    return nodes


class FragmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Windows offline fixtures use only hash-locked source paths.
        cls.blob, _ = hardware_fragment(ROOT/'out/device/live-fdt.bin',
            locked_encoder(Path('D:/Code/PortingiOSLegacy/common/sources/UniXNU-sheng')))
        cls.nodes = decode(cls.blob)

    def test_cpu_affinity_and_identity(self):
        for i in range(8):
            p = self.nodes['/cpus/cpu'+str(i)]
            self.assertEqual(p['reg'], struct.pack('<I', i*0x100))
            self.assertEqual(p['device_type'], b'cpu\0')
            self.assertEqual(p['compatible'], b'qcom,kryo\0')
            self.assertEqual(p['timebase-frequency'], struct.pack('<I',19200000))

    def test_actual_armcpu_gic_layout(self):
        bus = struct.unpack('<3Q', self.nodes['/arm-io']['ranges'])
        gic = self.nodes['/arm-io/intc']
        self.assertEqual(gic['compatible'], b'arm,gic-v3\0')
        self.assertEqual(len(gic['compatible']),11)
        regions = struct.unpack('<4Q',gic['reg'])
        self.assertEqual(regions[0],0x17a00000)
        self.assertEqual(regions[2],0x17a60000)
        self.assertEqual(gic['redistributor-stride'],struct.pack('<Q',0x20000))
        for i in (0,2):
            self.assertGreaterEqual(regions[i],bus[0])
            self.assertLessEqual(regions[i]-bus[0]+regions[i+1],bus[2])
            self.assertEqual(bus[1]+regions[i]-bus[0],regions[i])

    def test_no_foreign_or_unobserved_boot_inputs(self):
        self.assertNotIn('/chosen',self.nodes)
        self.assertEqual(self.nodes['/psci']['method'],b'smc\0')
        for forbidden in (b'sheng',b'cortex-a715',b'sm8550',b'dram-size',b'framebuffer'):
            self.assertNotIn(forbidden,self.blob)


if __name__ == '__main__': unittest.main()
