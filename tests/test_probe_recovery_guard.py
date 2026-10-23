"""An unresolved previous probe must reject new trials before any device command."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import run_enuma_entry_probe as probe
class RecoveryGuardTests(unittest.TestCase):
    def test_unrecovered_previous_probe_never_calls_device_tools(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'out',prefix='recovery-guard-') as td:
            r=Path(td).resolve();self.assertTrue(r.is_relative_to((ROOT/'out').resolve()))
            image=r/'out/fixture.img';image.parent.mkdir();image.write_bytes(b'unit-test fixture')
            image.with_suffix('.json').write_text(json.dumps({'image_sha256':hashlib.sha256(image.read_bytes()).hexdigest()}))
            state=r/'out/device-tests/current.local.json';state.parent.mkdir();state.write_text(json.dumps({'phase':'manual-recovery-needed'}))
            with patch.object(probe,'ROOT',r),patch.object(sys,'argv',['probe','--image',str(image),'--label','dxe-driver-return']),patch.object(probe.subprocess,'run',side_effect=AssertionError('must not call device tools')) as command:
                with self.assertRaisesRegex(ValueError,'Previous probe is not recovered'):probe.main()
                command.assert_not_called()
