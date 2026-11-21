"""Necessary checks for already-written framing/manual-page/layout model only."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result
pages = load('identity_pages', ROOT / 'scripts/enuma-ufs-identity-pages.py')
identity = load('identity_data', ROOT / 'scripts/parse-enuma-ufs-identity.py')


class PageTests(unittest.TestCase):
    def test_ascii_roundtrip(self):
        data = bytes(range(256)) * 8
        frames = pages.encode(data)
        self.assertTrue(all(f.isascii() and len(f) <= 1200 for f in frames))
        self.assertEqual(pages.decode(list(reversed(frames))), data)

    def test_missing_duplicate_and_mixed_rejected(self):
        frames = pages.encode(b'synthetic' * 200)
        for bad in (frames[:-1], frames + [frames[0]], frames[:-1] + [pages.encode(b'other' * 400)[-1]]):
            with self.subTest(kind=len(bad)):
                with self.assertRaises(ValueError):
                    pages.decode(bad)

    def test_checksum_rejected(self):
        frames = pages.encode(b'synthetic' * 100)
        frames[0] = frames[0][:-4] + 'AAAA'
        with self.assertRaisesRegex(ValueError, 'checksum'):
            pages.decode(frames)

    def test_manual_boundaries_and_exit_events(self):
        for exit_key in ('SCAN_SUSPEND', 'ENTER', 'ESC'):
            state = pages.ManualPages(2)
            state.event('UP'); self.assertEqual(state.index, 0)
            state.event('DOWN'); state.event('DOWN'); self.assertEqual(state.index, 1)
            state.event(exit_key); state.event('UP')
            self.assertTrue(state.exited); self.assertEqual(state.index, 1)

    def test_zero_overflow_and_large_text_clipping(self):
        parsed = identity.parse(identity.synthetic_demo())
        for width, height in ((0, 800), (800, 0), (1 << 63, 800), (200, 20)):
            with self.assertRaises(ValueError):
                pages.summary_layout(parsed, width, height)
        layout = pages.summary_layout(parsed, 512, 800)
        self.assertTrue(all(len(x) <= (512-16)//16 for x in layout['lines']))
        self.assertGreater(layout['qr_region'], 0)


if __name__ == '__main__':
    unittest.main()
