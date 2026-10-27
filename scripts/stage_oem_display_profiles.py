"""Stage two isolated, disabled OEM display profiles from one vendor snapshot.

This does not run the firmware builder or qualify a device trial.
"""
import argparse
import hashlib
import json
from pathlib import Path
from prepare_enuma_mmu_experiment import prepare
from plan_enuma_panel_handoff import contract

ROOT = Path(__file__).resolve().parents[1]
PE = 'Binaries/enuma/DisplayDxe/DisplayDxe.efi'
XML = 'raw/Panel_K81_42_02_0a_dualdsi_cphy_lcd_vid.xml'
REQUIRED = [PE, XML, 'Binaries/enuma/DisplayDxe/DisplayDxe.inf',
            'Vendor.dsc.inc', 'Vendor.fdf.inc', 'Vendor.apriori.inc', 'Vendor.raw.fdf.inc']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(root):
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('vendor symlink refused')
        if path.is_file():
            result[path.relative_to(root).as_posix()] = path.read_bytes()
    for name in REQUIRED:
        if name not in result:
            raise ValueError('missing vendor input: ' + name)
    return result


def hashes(files):
    return {name: digest(data) for name, data in files.items()}


def verify_pair(output):
    output = Path(output)
    m = json.loads((output/'profiles.json').read_text())
    control = snapshot(output/'oem-control/vendor')
    experiment = snapshot(output/'oem-mmu-only/vendor')
    if hashes(control) != m['source_files']:
        raise ValueError('control snapshot mismatch')
    patched, patch = prepare(control[PE])
    expected = dict(control); expected[PE] = patched
    if hashes(experiment) != hashes(expected):
        raise ValueError('experiment contains changes outside the exact patch')
    if m['patch'] != patch or m['panel'] != contract(control[XML]):
        raise ValueError('contract mismatch')
    if m['enabled'] is not False or m['firmware_packaged'] is not False or m['hardware_executed'] is not False:
        raise ValueError('staging cannot grant execution qualification')
    if m['profiles'] != {'oem-control': digest(control[PE]), 'oem-mmu-only': digest(patched)}:
        raise ValueError('profile identity mismatch')
    return dict(passed=True, files_per_profile=len(control), different_files=[PE],
                profile_pe_sha256=m['profiles'], firmware_packaged=False, hardware_executed=False)


def stage(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    output.relative_to(ROOT/'out')
    if output == ROOT/'out' or source == output or source in output.parents or output in source.parents:
        raise ValueError('source and output must be separate')
    files = snapshot(source)
    patched, patch = prepare(files[PE])
    panel = contract(files[XML])
    output.mkdir(parents=True, exist_ok=False)
    for profile in ('oem-control', 'oem-mmu-only'):
        for name, data in files.items():
            dest = output/profile/'vendor'/name
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open('xb') as stream:
                stream.write(patched if profile == 'oem-mmu-only' and name == PE else data)
    if hashes(snapshot(source)) != hashes(files):
        raise ValueError('shared source changed during staging; no qualification emitted')
    manifest = dict(schema=1, enabled=False, firmware_packaged=False, hardware_executed=False,
                    source_files=hashes(files), patch=patch, panel=panel,
                    profiles={'oem-control': digest(files[PE]), 'oem-mmu-only': digest(patched)},
                    integration_gaps=['builder vendor-root selection not yet wired',
                                      'actual FV extraction and identity verification',
                                      'same-handle Core trace binding and persistent context',
                                      'board capture and independent termination/recovery'])
    (output/'profiles.json').write_text(json.dumps(manifest, indent=2))
    result = verify_pair(output)
    (output/'staging-check.json').write_text(json.dumps(result, indent=2))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-vendor', type=Path)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--prepare-pair', action='store_true')
    p.add_argument('--verify', action='store_true')
    a = p.parse_args()
    if a.prepare_pair == a.verify:
        p.error('explicitly choose --prepare-pair or --verify')
    if a.prepare_pair and a.source_vendor is None:
        p.error('--prepare-pair requires --source-vendor')
    print(json.dumps(stage(a.source_vendor, a.output) if a.prepare_pair else verify_pair(a.output), indent=2))


if __name__ == '__main__':
    main()
