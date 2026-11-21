import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("readcheck", Path(__file__).parents[1] / "enuma-native-readcheck.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ReadCheck(unittest.TestCase):
    def setUp(self):
        self.p = dict(enabled=True, hc_resource="synthetic", sid=7, context_bank=8,
                      mapping_contract="synthetic", lun=2, block_size=512, capacity_blocks=20, lba=1)
        self.o = dict(old_backing_excluded=True, producer_excluded=True, mapping_compatible=True,
                      tr_empty=True, tm_empty=True, tr_stop_readback=True, command_ok=True,
                      lun=2, block_size=512, capacity_blocks=20)
        self.block = b"EFI PART" + bytes(504)

    def run_check(self):
        return mod.evaluate(self.p, self.o, self.block, self.block)

    def test_default_and_unknown(self):
        self.assertEqual(mod.evaluate({}, {}, b'', b'')["result"], "blocked: disabled")
        for field in ("hc_resource", "sid", "context_bank", "mapping_contract", "lun"):
            p = dict(self.p, **{field: None})
            self.assertEqual(mod.evaluate(p, self.o, self.block, self.block)["result"], "blocked: unknown " + field)

    def test_distinct_gates_first_failure(self):
        for field in ("old_backing_excluded", "producer_excluded", "mapping_compatible", "tr_empty", "tm_empty", "tr_stop_readback"):
            o = dict(self.o, **{field: False})
            self.assertEqual(mod.evaluate(self.p, o, self.block, self.block)["result"], "blocked: " + field)
        self.o.update(tr_empty=False, tm_empty=False, command_ok=False)
        self.assertEqual(self.run_check()["result"], "blocked: tr_empty")

    def test_geometry_and_compare(self):
        self.assertEqual(self.run_check()["result"], "fixture-match")
        for field, value, reason in (("lun", 3, "lun"), ("block_size", 4096, "block_size"),
                                     ("capacity_blocks", 21, "capacity"), ("lba", 20, "range")):
            p = dict(self.p, **{field: value})
            self.assertEqual(mod.evaluate(p, self.o, self.block, self.block)["result"], "failed: " + reason)
        self.assertEqual(mod.evaluate(self.p, self.o, self.block, bytes(512))["result"], "failed: mismatch")
        self.assertEqual(mod.evaluate(self.p, self.o, self.block, b'')["result"], "failed: block length")
        self.o["command_ok"] = False
        self.assertEqual(self.run_check()["result"], "failed: first command")

    def test_historical_primary_fixture_only(self):
        path = Path(__file__).parents[2] / '.cache/live-capture/20261107T141941555586Z/sda_first_32768.bin'
        if not path.is_file():
            self.skipTest('historical local input unavailable')
        block = path.read_bytes()[4096:8192]
        self.assertEqual(block[:8], b'EFI PART')
        self.p.update(block_size=4096, capacity_blocks=61880320)
        self.o.update(block_size=4096, capacity_blocks=61880320)
        self.assertEqual(mod.evaluate(self.p, self.o, block, block)['result'], 'fixture-match')
        self.p['lun'] = None
        self.assertEqual(mod.evaluate(self.p, self.o, block, block)['result'], 'blocked: unknown lun')


if __name__ == "__main__":
    unittest.main()
