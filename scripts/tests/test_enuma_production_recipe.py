#!/usr/bin/env python3
"""Offline checks against the generated plan and pinned official implementation."""
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    from pip._vendor import tomli as tomllib
    sys.modules['tomllib'] = tomllib

DEVICE = Path(__file__).resolve().parents[2]
BASE = DEVICE.parents[1] / 'UniXNU'
SOC = DEVICE.parent / 'UniXNU-sm8250-common'
OUT = DEVICE / 'out/production-recipe-r3'
TOOL = DEVICE / 'scripts/enuma-production-recipe.py'
sys.path.insert(0, str(BASE / 'scripts'))
from unixnu import config, profiles, feeds

spec = importlib.util.spec_from_file_location('recipe', TOOL)
recipe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recipe)


class RecipeTests(unittest.TestCase):
    def test_official_load_and_build_options(self):
        args = types.SimpleNamespace(config=str(OUT / 'build.toml'), target=None, device=None, out=None)
        config.load_build_options(args)
        self.assertEqual(Path(args.device), OUT / 'device')
        self.assertEqual(Path(args.out), OUT / 'build-output')
        ctx = types.SimpleNamespace(root=BASE, device=OUT / 'device', raw_board=config.load_toml(OUT / 'device/board.toml'),
                                    args=types.SimpleNamespace(os=None))
        original = feeds.resolve_soc
        feeds.resolve_soc = lambda *unused: types.SimpleNamespace(path=SOC)
        try:
            merged = profiles.load(ctx)
        finally:
            feeds.resolve_soc = original
        archives = merged['kernel']['archives']
        self.assertEqual(archives, ctx.raw_board['kernel']['archives'])
        self.assertNotIn('build-enuma-ufs-observe.py', archives)
        self.assertNotIn('build-enuma-ram-block-store.py', archives)
        self.assertEqual(merged['payload']['adt']['root_match_volume_uuid'], recipe.OS_UUID)
        args = merged['payload']['kernel_args']
        self.assertIn('native-ufs-root=1', args)
        self.assertIn('sheng-data-persist=2', args)
        self.assertIn('sheng-pmgr=2', args)
        self.assertFalse(any(x.startswith(('rd=md0-ramblock', 'native-ufs-observe-reuse=')) for x in args))
        self.assertTrue(config.parse_config((OUT / 'device/configs/enuma_production_defconfig').read_text())['XNU_NATIVE_RAM_BLOCK'])
        for name in ('dts/enuma.dts', 'patches/xnu/series', 'patches/xnu/os-series',
                     'scripts/prepare-ram-block-audit.py', 'scripts/build-enuma-platform-power.py'):
            self.assertTrue((OUT / 'device' / name).is_file(), name)

    def test_seed_formula_against_official(self):
        spec = importlib.util.spec_from_file_location('seed', BASE / 'scripts/seed-data-grow.py')
        seed = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(seed)
        plan = json.loads((OUT / 'inputs.json').read_text())
        root = 9382658048
        seed.root_image_bytes = lambda: root
        for capacity in (242455916544, 40 * recipe.GIB, 60 * recipe.GIB):
            self.assertEqual(recipe.auto(capacity, root, 1024)[0], seed.auto_gib(capacity, 1024))
        data = plan['data_plan']
        self.assertGreaterEqual(data['store_start_bytes'], root + data['guard_bytes'])
        self.assertEqual(data['store_start_bytes'] + data['store_bytes'] + data['reserve_mib'] * recipe.MIB,
                         plan['geometry']['capacity_bytes'])
        windows = plan['windows']
        self.assertLessEqual(windows[0]['offset'] + windows[0]['bytes'], windows[1]['offset'])
        self.assertLessEqual(windows[1]['offset'] + windows[1]['bytes'], root)

    def test_check_blocked_and_no_overwrite(self):
        paths = [DEVICE / 'board.toml', DEVICE / 'configs/enuma_defconfig', OUT / 'device/board.toml']
        before = [hashlib.sha256(p.read_bytes()).digest() for p in paths]
        result = subprocess.run([sys.executable, str(TOOL), 'check', '--recipe', str(OUT)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('BLOCKED', result.stdout)
        self.assertIn('input readiness not authenticated', result.stdout)
        result = subprocess.run([sys.executable, str(TOOL), 'generate', '--device', str(DEVICE), '--unixnu', str(BASE),
                                 '--output', str(OUT), '--capacity', '242455916544', '--image', '/nonexistent',
                                 '--report', '/nonexistent', '--provenance', '/nonexistent'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(before, [hashlib.sha256(p.read_bytes()).digest() for p in paths])

    def test_invalid_snapshots_rejected_by_cli(self):
        cases = ('archives', 'nativeufs', 'nativeufs-unset', 'duplicate-root', 'duplicate-pmgr', 'blockers', 'status',
                 'reserve-negative', 'reserve-2048')
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temp:
                target = Path(temp)
                for name in ('build.toml', 'inputs.json', 'device/board.toml',
                             'device/configs/enuma_production_defconfig', 'device/dts/enuma.dts',
                             'device/patches/xnu/series', 'device/patches/xnu/os-series',
                             'device/scripts/prepare-ram-block-audit.py', 'device/scripts/build-enuma-platform-power.py'):
                    destination = target / name
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(OUT / name, destination)
                board = target / 'device/board.toml'
                config_file = target / 'device/configs/enuma_production_defconfig'
                manifest = target / 'inputs.json'
                if case == 'archives':
                    board.write_text(re.sub(r'^archives = \[.*?^\]', 'archives = []', board.read_text(), flags=re.M | re.S))
                    reason = 'archives differ'
                elif case.startswith('nativeufs'):
                    contents = config_file.read_text()
                    contents = (contents.replace('CONFIG_XNU_NATIVE_UFS=y', 'CONFIG_XNU_NATIVE_UFS=n') if case == 'nativeufs'
                                else contents + '\n# CONFIG_XNU_NATIVE_UFS is not set\n')
                    config_file.write_text(contents)
                    reason = 'CONFIG_XNU_NATIVE_UFS'
                elif case.startswith('duplicate-'):
                    key = 'native-ufs-root' if case.endswith('root') else 'sheng-pmgr'
                    board.write_text(board.read_text().replace('"' + key + ('=1"' if key == 'native-ufs-root' else '=2"'),
                                                              '"' + key + ('=1", "' if key == 'native-ufs-root' else '=2", "') + key + '=0"'))
                    reason = 'kernel arguments'
                else:
                    plan = json.loads(manifest.read_text())
                    if case == 'blockers':
                        plan['blockers'] = []
                        reason = 'blockers differ'
                    elif case == 'status':
                        plan['status'] = 'ready'
                        reason = 'snapshot status'
                    else:
                        plan['data_plan']['reserve_mib'] = -1 if case.endswith('negative') else 2048
                        reason = 'reserve_mib must be 1024'
                    manifest.write_text(json.dumps(plan))
                result = subprocess.run([sys.executable, str(TOOL), 'check', '--recipe', str(target)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(reason, result.stderr)

    def test_generate_rejects_other_reserves(self):
        for reserve in (-1, 0, 2048):
            result = subprocess.run([sys.executable, str(TOOL), 'generate', '--device', str(DEVICE), '--unixnu', str(BASE),
                                     '--output', str(DEVICE / 'out/unused-reserve-test'), '--capacity', '242455916544',
                                     '--image', '/nonexistent', '--report', '/nonexistent', '--provenance', '/nonexistent',
                                     '--reserve-mib=' + str(reserve)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('reserve_mib must be 1024', result.stderr)

    def test_corrupt_layout_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            (target / 'device').mkdir()
            for name in ('build.toml', 'inputs.json'):
                (target / name).write_bytes((OUT / name).read_bytes())
            (target / 'device/board.toml').write_bytes((OUT / 'device/board.toml').read_bytes())
            plan = json.loads((target / 'inputs.json').read_text())
            plan['windows'][1]['offset'] -= 4096
            (target / 'inputs.json').write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError, 'policy windows'):
                recipe.check_plan(target)

    def test_official_porting_record(self):
        spec = importlib.util.spec_from_file_location('porting_record', BASE / 'scripts/porting-record.py')
        record = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(record)
        record.check(DEVICE)


if __name__ == '__main__':
    unittest.main()
