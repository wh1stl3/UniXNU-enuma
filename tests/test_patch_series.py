"""Replay the actual overlapping DXE patches twice against the pinned Mu files."""
import hashlib
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_enuma_firmware import apply_patch_series


class PatchSeriesTests(unittest.TestCase):
    def test_overlapping_dxe_series_is_idempotent(self):
        archive = ROOT / 'out/firmware-build/mu-basecore.tar.gz'
        lock = json.loads((ROOT / 'config/firmware-build.lock.json').read_text())
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),
                         lock['archive_sha256']['mu-basecore.tar.gz'])
        with tempfile.TemporaryDirectory(dir=ROOT / 'out', prefix='patch-replay-') as temp:
            stage = Path(temp).resolve()
            self.assertTrue(stage.is_relative_to((ROOT / 'out').resolve()))
            names = ['MdeModulePkg/Core/Dxe/DxeMain/DxeMain.c',
                     'MdeModulePkg/Core/Dxe/DxeMain.inf',
                     'MdeModulePkg/Core/Dxe/Dispatcher/Dispatcher.c']
            with tarfile.open(archive) as source:
                for name in names:
                    member = next(m for m in source.getmembers() if m.name.endswith('/' + name))
                    target = stage / name; target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(source.extractfile(member).read().replace(b'\r\n', b'\n'))
            patches = [(stage, ROOT / 'firmware/patches' / name) for name in
                       ('dxe-stage-checkpoints.patch', 'dxe-dispatch-return.patch',
                        'dxe-driver-checkpoints.patch')]
            apply_patch_series(patches)
            once = {name: (stage / name).read_bytes() for name in names}
            self.assertEqual(once[names[0]].count(b'EnumaStageCheckpoint (11);'), 1)
            for point in (12, 13):
                self.assertEqual(once[names[2]].count(f'EnumaDispatchCheckpoint ({point});'.encode()), 1)
            apply_patch_series(patches)
            self.assertEqual(once, {name: (stage / name).read_bytes() for name in names})


if __name__ == '__main__': unittest.main()
