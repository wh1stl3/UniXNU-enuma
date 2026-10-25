"""Offline inventory of pinned system-volume contracts; never contacts a device."""
import hashlib
import json
import subprocess
import struct
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
    # Distinguish real generated artifacts from board integration and runtime
    # readiness. A firmware-only diagnostic must not be mistaken for an OS boot.
    prelink_report = ROOT / 'reports/enuma-system-prelink.json'
    if prelink_report.exists():
        prelink = json.loads(prelink_report.read_text())
        target = ROOT / prelink['path']
        if hashlib.sha256(target.read_bytes()).hexdigest() != prelink['sha256']:
            raise ValueError('Experimental prelink artifact changed')
        report['experimental_prelink'] = {key: prelink[key] for key in
            ['path', 'bytes', 'sha256', 'selected_virtual_slide', 'virtual_span_bytes',
             'instruction_inventory', 'physical_address_selected', 'board_memory_fields_changed']}
        report['experimental_prelink']['component_count'] = len(prelink['selected_components'])
    image = ROOT / 'out/boot-candidate/display-return-aa9ec66-boot-v3.img'
    if image.exists():
        header = image.read_bytes()[:4096]
        if header[:8] != b'ANDROID!' or struct.unpack_from('<I', header, 40)[0] != 3:
            raise ValueError('Unexpected retained diagnostic image')
        report['diagnostic_image'] = {'path': str(image.relative_to(ROOT)),
            'sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
            'kernel_bytes': struct.unpack_from('<I', header, 8)[0],
            'generic_ramdisk_bytes': struct.unpack_from('<I', header, 12)[0],
            'meaning': 'BootShim/UEFI diagnostic image, not an XNU/iPadOS payload image'}
    report['gap_scope'] = 'prelink_missing means board.kernel.prelink integration; an experimental emitted file can exist separately'
    report['full_boot_ready'] = False
    bundle_report = ROOT / 'reports/enuma-full-payload.json'
    if bundle_report.exists():
        bundle = json.loads(bundle_report.read_text())
        fat = ROOT / 'out/full-boot/payload/payload.img'
        if hashlib.sha256(fat.read_bytes()).hexdigest() != bundle['payload_sha256']:
            raise ValueError('experimental FAT bundle changed')
        report['experimental_fat_payload'] = bundle
        report['gap_scope'] += '; complete_adt_tool_missing describes board integration, not absence of the offline enuma adapter/ADT/FAT output'
    qualification = ROOT / 'reports/enuma-ram-payload-qualification.json'
    if qualification.exists():
        transport = json.loads(qualification.read_text())
        image = ROOT / transport['archive'] / 'enuma-system-transport-v3.img'
        if hashlib.sha256(image.read_bytes()).hexdigest() != transport['image_sha256']:
            raise ValueError('qualified boot-v3 transport image changed')
        report['experimental_ram_transport'] = {
            'firmware_commit': transport['firmware_commit'], 'image_sha256': transport['image_sha256'],
            'image_bytes': transport['image_bytes'], 'batch_stages': 13,
            'scope': 'actual compiled and packaged driver, offline qualified; runtime FDT/SFS not observed'}
        report['firmware_initrd_publisher'] = 'implemented and offline-qualified; runtime discovery remains open'
    boundary_path = ROOT / 'reports/enuma-full-input-return-boundary.json'
    if boundary_path.exists():
        boundary = json.loads(boundary_path.read_text())
        candidate = ROOT / boundary['image']
        if hashlib.sha256(candidate.read_bytes()).hexdigest() != boundary['image_sha256']:
            raise ValueError('full-input return boundary image changed')
        report['full_input_return_boundary'] = {
            'image_sha256': boundary['image_sha256'], 'ram_payload_bytes': boundary['ram_payload_bytes'],
            'detail_point': boundary['detail_point'], 'completion_fallback_enabled': boundary['completion_fallback_enabled'],
            'scope': 'offline necessary isolation candidate; not a third device trial'}
    report['device_activity_scope'] = 'new_device_trials/device_writes describe this offline auditor only; actual trial results are separate'
    report['actual_trial_results'] = {}
    for name in ['enuma-system-transport-result.json', 'enuma-system-transport-S002-result.json']:
        result_path = ROOT / 'reports' / name
        if result_path.exists():
            trial = json.loads(result_path.read_text())
            report['actual_trial_results'][name] = {k: trial.get(k) for k in
                ['phase', 'candidate_sha256', 'candidate_consumed', 'report_stages_observed']}
    report['next_work_order'] = [
        'provide observable loader/XNU errors; do not revive failed R-002 cross-reset RAM logging',
        'observe the 13-stage transport batch in one controlled full-input trial once error output and recovery gates are met',
        'integrate offline ADT/FAT composition with board only after runtime memory/identity and loader contracts are reviewed',
        'close native root storage/PMGR/security/Data contracts before claiming iPadOS userspace',
    ]
    if not all(report['gaps'].values()):
        raise ValueError('Roadmap facts changed; re-audit before publishing')
    destination = ROOT / 'reports/enuma-system-roadmap-audit.json'
    destination.write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: {len(sources)} pinned source files; six roadmap gaps confirmed; no device access')


if __name__ == '__main__':
    main()
