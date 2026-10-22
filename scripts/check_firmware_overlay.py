"""Check the enuma source overlay. Does not invoke EDK II or create firmware images."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from fetch_porting_references import ROOT, check_references

MODULES = (
    'UniXNUPkg/Application/UniXNU/UniXNU.inf',
    'UniXNUPkg/Driver/UniXNUDxe/UniXNUDxe.inf',
    'DarwinBootPkg/Driver/DarwinBoot.inf',
)
MISSING = (
    'Isolated complete EDK II build and OEM protocol ABI/dependency closure',
    'Native enuma DisplayDxe initialization and GOP/ExitBootServices behavior',
    'Re-entry placement and real UEFI allocation map for the OEM memory layout',
    'BootShim raw ARM64 entry acceptance with stock vendor_boot v3',
)


def clean(text):
    return '\n'.join(line.split('#', 1)[0].strip() for line in text.splitlines())


def expand_local(path, package, seen=None, external=None):
    """Expand only this overlay. External includes remain explicit unresolved edges."""
    seen = set() if seen is None else seen
    external = [] if external is None else external
    path = path.resolve()
    if not path.is_relative_to(package.resolve()):
        raise ValueError('include escapes package')
    if path in seen:
        raise ValueError(f'include cycle at {path.name}')
    seen = seen | {path}
    lines = []
    for line in clean(path.read_text()).splitlines():
        match = re.fullmatch(r'!include\s+(\S+)', line, re.I)
        if match:
            target = match[1]
            if target.startswith('enumaPkg/'):
                lines.append(expand_local(package / target[len('enumaPkg/'):], package, seen, external))
            else:
                external.append(target)
                lines.append(line)
        else:
            lines.append(line)
    return '\n'.join(lines)


def section_entries(text):
    section = ''
    entries = {}
    for line in text.splitlines():
        if line.startswith('[') and line.endswith(']'):
            section = line[1:-1].lower()
        else:
            entries.setdefault(section, []).append(line)
    return entries


def check_graph(package):
    external = []
    dsc = expand_local(package / 'enuma.dsc', package, external=external)
    fdf = expand_local(package / 'enuma.fdf', package, external=external)
    # Reject actual references; comments discussing the foreign board are fine.
    if re.search(r'(?i)(?:alioth|sheng|nabu|elish)Pkg|Binaries[/\\](?:alioth|sheng|nabu|elish)', dsc + fdf):
        raise ValueError('foreign board reference in active overlay')
    if 'SiliciumPkg/Drivers/SimpleFbDxe/' in fdf:
        raise ValueError('unqualified SimpleFb must not replace native enuma GOP')
    if 'KonaPkg/KonaPkg.dsc.inc' not in external:
        raise ValueError('Kona platform is not included')
    sections = section_entries(dsc)
    fv = section_entries(fdf).get('fv.fvmain', [])
    components = sections.get('components', [])
    for module in MODULES:
        if components.count(module) != 1 or fv.count('INF ' + module) != 1:
            raise ValueError(f'module missing/duplicated in Components or FvMain: {module}')
    for macro, document in [('ENUMA_PLATFORM_CONFIG', dsc), ('ENUMA_VENDOR_APRIORI', fdf),
                            ('ENUMA_VENDOR_DXE', fdf), ('ENUMA_VENDOR_RAW', fdf)]:
        guard = rf'!ifndef {macro}\s+!error[^\n]+\s+!endif'
        if not re.search(guard, document) or '$(' + macro + ')' not in ' '.join(external):
            raise ValueError(f'missing fail-closed input guard: {macro}')
    if '-DENUMA_PRESERVE_DISPLAY=1' not in dsc:
        raise ValueError('display preservation switch missing')
    if 'UniXNULib|UniXNUPkg/Library/UniXNULib/UniXNULib.inf' not in sections.get('libraryclasses', []):
        raise ValueError('UniXNULib not bound')
    return {'packaged_modules': list(MODULES), 'external_includes': external}


def run(argv, cwd=None, stdin=None):
    result = subprocess.run([str(x) for x in argv], cwd=cwd, input=stdin,
                            capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise ValueError(f'{argv}: {result.stdout}\n{result.stderr}')
    return result.stdout


def check_patch():
    relative = Path('Silicon/Qualcomm/KonaPkg/Library/PlatformSecLib/PlatformSec.c')
    source = ROOT / 'out/references/uefi-sheng' / relative
    stage = ROOT / 'out/firmware-overlay-check/src'
    dest = stage / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(source.read_bytes())
    patch = ROOT / 'firmware/patches/kona-preserve-display.patch'
    prefix = '--directory=' + stage.relative_to(ROOT).as_posix()
    run(['git', 'apply', '--check', prefix, patch], ROOT)
    run(['git', 'apply', prefix, patch], ROOT)
    # Test the actual patch branches using the C preprocessor. Drop includes
    # only: this is not a compile/link test against EDK II headers.
    body = re.sub(r'^\s*#include[^\n]*', '', dest.read_text(), flags=re.M)
    variants = {}
    for setting in (None, '0', '1'):
        argv = ['clang', '-E', '-P', '-x', 'c']
        if setting is not None:
            argv.append('-DENUMA_PRESERVE_DISPLAY=' + setting)
        processed = run([*argv, '-'], stdin=body)
        detach = 'ArmSmmuDetach (' in processed
        if detach != (setting != '1') or processed.count('DisableWatchDogTimer (') != 2:
            raise ValueError('patch changed watchdog or failed to gate display detach')
        variants[str(setting)] = {'display_detach_present': detach, 'watchdog_preserved': True}
    return {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'patch_sha256': hashlib.sha256(patch.read_bytes()).hexdigest(),
            'branches': variants, 'scope': 'exact patch application and preprocessing; not EDK II compilation'}


def check_sec_patch():
    relative = Path('Silicon/Silicium/SiliciumPkg/Sec/Sec.c')
    source = ROOT / 'out/references/uefi-sheng' / relative
    stage = ROOT / 'out/firmware-overlay-check/sec'
    dest = stage / relative; dest.parent.mkdir(parents=True, exist_ok=True)
    # The pinned original uses CRLF; normalize only this disposable copy.
    dest.write_bytes(source.read_bytes().replace(b'\r\n', b'\n'))
    patch = ROOT / 'firmware/patches/sec-preserve-display.patch'
    prefix = '--directory=' + stage.relative_to(ROOT).as_posix()
    run(['git', 'apply', '--check', prefix, patch], ROOT)
    run(['git', 'apply', prefix, patch], ROOT)
    body = re.sub(r'^\s*#include[^\n]*', '', dest.read_text(), flags=re.M)
    results = {}
    for setting in ('0', '1'):
        processed = run(['clang', '-E', '-P', '-x', 'c', '-DENUMA_PRESERVE_DISPLAY=' + setting, '-'], stdin=body)
        clear = 'ClearFrameBuffer (' in processed
        if clear != (setting == '0'): raise ValueError('SEC framebuffer clearing switch failed')
        results[setting] = {'framebuffer_clear_present': clear}
    return {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'patch_sha256': hashlib.sha256(patch.read_bytes()).hexdigest(), 'branches': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unixnu', type=Path, required=True)
    parser.add_argument('--firmware-root', type=Path, required=True)
    parser.add_argument('--require-image-ready', action='store_true')
    args = parser.parse_args()
    refs = check_references()
    lock = json.loads((ROOT / 'config/porting-sources.lock.json').read_text())
    pins = json.loads((ROOT / 'config/sources.lock.json').read_text())['sources']
    for relative, expected in lock['unixnu_interface_sha256'].items():
        if hashlib.sha256((args.unixnu / relative).read_bytes()).hexdigest() != expected:
            raise ValueError(f'UniXNU interface pin mismatch: {relative}')
    feeds = (args.unixnu / 'feeds.toml').read_bytes()
    if hashlib.sha256(feeds).hexdigest() != pins['UniXNU']['file_sha256']['feeds.toml']:
        raise ValueError('UniXNU feeds pin mismatch')
    gitlinks = {}
    for name, commit in lock['firmware_gitlinks'].items():
        tree = run(['git', '-c', 'safe.directory=' + args.firmware_root.as_posix(), '-C', args.firmware_root,
                    'ls-tree', pins['uefi-sheng']['commit'], name]).strip()
        if tree != f'160000 commit {commit}\t{name}':
            raise ValueError(f'firmware gitlink mismatch: {name}')
        gitlinks[name] = commit
    if ('commit = "' + gitlinks['Mu_Basecore'] + '"') not in feeds.decode():
        raise ValueError('firmware and UniXNU core pins differ')
    package = ROOT / 'firmware/Platforms/Xiaomi/enumaPkg'
    graph = check_graph(package)
    kona = (ROOT / 'out/references/uefi-sheng/Silicon/Qualcomm/KonaPkg/KonaPkg.dsc.inc').read_text()
    adt = json.loads((ROOT / 'reports/enuma-adt-plan.json').read_text())
    gic = {}
    for pcd, key in [('PcdGicDistributorBase', 'distributor_pa'),
                     ('PcdGicRedistributorsBase', 'redistributor_pa')]:
        match = re.search(r'\.' + pcd + r'\|(0x[0-9A-Fa-f]+)', kona)
        if not match or int(match[1], 16) != int(adt['gic'][key], 16):
            raise ValueError(f'Kona {pcd} disagrees with enuma ADT input plan')
        gic[key] = match[1]
    patch = check_patch()
    sec_patch = check_sec_patch()
    artifact = None
    build_path = ROOT / 'reports/enuma-firmware-build.json'
    if build_path.exists():
        built = json.loads(build_path.read_text())
        if built.get('complete'):
            fd = ROOT / built['fd']
            inputs_current = bool(built.get('source_inputs_sha256')) and all((ROOT / name).is_file() and
                                 hashlib.sha256((ROOT / name).read_bytes().replace(b'\r\n', b'\n')).hexdigest() == expected
                                 for name, expected in built.get('source_inputs_sha256', {}).items())
            if inputs_current and fd.exists() and hashlib.sha256(fd.read_bytes()).hexdigest() == built.get('fd_sha256'):
                artifact = built['fd']
    report = {'scope': 'source graph, fixed references and patch branches; not complete EDK II parsing/linking',
              'firmware_base': pins['uefi-sheng']['commit'], 'gitlinks': gitlinks,
              'references': refs, 'graph': graph, 'patch': patch, 'sec_patch': sec_patch, 'gic': gic,
              'overlay_sha256': {p.relative_to(package).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sorted(package.rglob('*')) if p.is_file()},
              'image_ready': artifact is not None, 'artifact': artifact, 'hardware_ready': False,
              'missing_inputs': [] if artifact else [MISSING[0]],
              'pending_runtime_checks': list(MISSING[1:])}
    (ROOT / 'reports/firmware-overlay-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: source overlay and patch checks; artifact=' + str(artifact is not None) + '; runtime checks pending')
    if args.require_image_ready and not artifact:
        parser.exit(2, 'NOT IMAGE READY: ' + '; '.join(MISSING) + '\n')


if __name__ == '__main__':
    main()
