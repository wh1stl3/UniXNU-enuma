"""Offline inventory of pinned system-volume contracts; never contacts a device."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    lock = json.loads((ROOT / 'config/sources.lock.json').read_text())
    sources = []
    selections = {
        'UniXNU': [
            'scripts/unixnu/userdata.py', 'scripts/unixnu/payload.py',
            'scripts/unixnu/bootimg.py', 'docs/concepts/security.md',
        ],
        'UniXNU-sheng': ['board.toml'],
    }
    for name, files in selections.items():
        spec = lock['sources'][name]
        base = Path(spec['path'])
        commit = subprocess.check_output(['git', '-c', f'safe.directory={base.as_posix()}', '-C', str(base), 'rev-parse', 'HEAD'], text=True).strip()
        if commit != spec['commit']:
            raise ValueError(f'{name}: source revision changed')
        for relative in files:
            raw = (base / relative).read_bytes()
            tracked = subprocess.check_output(['git', '-c', f'safe.directory={base.as_posix()}', '-C', str(base), 'show', f'{commit}:{relative}'])
            if raw != tracked:
                raise ValueError(f'{name}/{relative}: differs from pinned Git blob')
            sources.append({'source': name, 'commit': commit, 'path': relative,
                            'sha256': hashlib.sha256(raw).hexdigest()})
    base = Path(lock['sources']['UniXNU']['path'])
    modules = {
        'drivers/NativeUfs': ['NativeUfs.cpp', 'GccUfs.h', 'RootLayout.h', 'RootPublication.h', 'LICENSE'],
        'drivers/NativeRamBlock': ['NativeRamBlock.cpp', 'README.md'],
    }
    for module, files in modules.items():
        pinned = lock['sources']['UniXNU']['gitlinks'][module]
        module_root = base / module
        actual = subprocess.check_output(['git', '-c', f'safe.directory={module_root.as_posix()}', '-C', str(module_root), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != pinned:
            raise ValueError(f'{module}: revision changed')
        for relative in files:
            raw = (module_root / relative).read_bytes()
            blob = subprocess.check_output(['git', '-c', f'safe.directory={module_root.as_posix()}', '-C', str(module_root), 'show', f'{pinned}:{relative}'])
            if raw != blob:
                raise ValueError(f'{module}/{relative}: modified input')
            sources.append({'source': module, 'commit': pinned, 'path': relative,
                            'sha256': hashlib.sha256(raw).hexdigest()})
    # Extract facts from this board without adding tomllib as a host dependency.
    board = (ROOT / 'board.toml').read_text()
    defconfig = (ROOT / 'configs/enuma_defconfig').read_text()
    userdata = (base / 'scripts/unixnu/userdata.py').read_text()
    dry = userdata[userdata.index('    if dry_run:'):userdata.index('    sources =')]
    payload = (base / 'scripts/unixnu/payload.py').read_text()
    report = {
        'scope': 'offline source-contract inventory, not image or hardware qualification',
        'sources': sources,
        'board_sha256': hashlib.sha256((ROOT / 'board.toml').read_bytes()).hexdigest(),
        'target': {'product': 'iPad7,1', 'device_class': 'j120ap',
                   'version': '17.7.11', 'build': '21H461'},
        'gaps': {
            'userdata_geometry_missing': '[userdata]' not in board,
            'prelink_missing': '[kernel.prelink]' not in board,
            'complete_adt_tool_missing': 'tool = ' not in board.split('[payload.adt]', 1)[1].split('[firmware]', 1)[0],
            'native_ufs_disabled': 'CONFIG_XNU_NATIVE_UFS=n' in defconfig,
            'upstream_native_root_requires_sheng_pmgr': "values.get('sheng-pmgr') != ['2']" in payload,
            'userdata_dry_run_does_not_compare_expanded_capacity': 'image_size(' not in dry and 'total > capacity' not in dry,
        },
        'firmware_initrd_publisher': 'not established by this audit',
        'root_volume_uuid': 'not measured',
        'system_images_built': False,
        'new_device_trials': 0,
        'device_writes': 0,
    }
    if not all(report['gaps'].values()):
        raise ValueError('Roadmap facts changed; re-audit before publishing')
    destination = ROOT / 'reports/enuma-system-roadmap-audit.json'
    destination.write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: {len(sources)} pinned source files; six roadmap gaps confirmed; no device access')


if __name__ == '__main__':
    main()
