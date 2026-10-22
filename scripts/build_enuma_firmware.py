"""Build in out/ only, using pinned writable source archives and read-only references."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'out/firmware-build'


def stage_archives(lock):
    WORK.mkdir(parents=True, exist_ok=True)
    for name, url in lock['archives'].items():
        archive = WORK / name
        if not archive.exists():
            subprocess.run(['curl', '-fL', '--retry', '2', '--connect-timeout', '10', '--max-time', '90',
                            '-o', str(archive), url], check=True)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != lock['archive_sha256'][name]:
            raise ValueError('source archive hash mismatch: ' + name)
        root = WORK / ('uefi' if name == 'uefi-source.tar.gz' else 'Mu_Basecore')
        marker = root / '.enuma-archive-staged'
        if marker.exists(): continue
        with tarfile.open(archive) as source:
            members = source.getmembers(); prefix = members[0].name.split('/')[0] + '/'
            for item in members:
                if not item.isfile(): continue
                relative = item.name.removeprefix(prefix)
                if name == 'uefi-source.tar.gz' and not relative.startswith(('Silicon/', 'BootShim/', 'Resources/MuPatches/')) and relative not in ('.gitmodules', 'LICENSE'):
                    continue
                target = (root / relative).resolve()
                if not target.is_relative_to(root.resolve()): raise ValueError('archive path escapes staging')
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.extractfile(item).read())
        marker.write_text(lock['archive_sha256'][name])


def command(argv, log, env=None, cwd=WORK):
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open('w') as stream:
        result = subprocess.run([str(x) for x in argv], cwd=cwd, env=env,
                                stdout=stream, stderr=subprocess.STDOUT)
    return {'argv': [str(x) for x in argv], 'exit_code': result.returncode,
            'log': str(log.relative_to(ROOT))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--unixnu', type=Path, required=True)
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    lock = json.loads((ROOT / 'config/firmware-build.lock.json').read_text())
    stage_archives(lock)
    uefi = WORK / 'uefi'; core = WORK / 'Mu_Basecore'
    for relative, expected in lock['reference_gitlinks'].items():
        path = args.reference / relative
        revision = subprocess.check_output(['git', '-c', 'safe.directory=' + path.as_posix(), '-C', str(path),
                                            'rev-parse', 'HEAD'], text=True).strip()
        if revision != expected: raise ValueError('reference pin mismatch: ' + relative)
    # Copy only missing nested dependencies. Build tools always belong to our writable core.
    for relative in ('BaseTools/Source/C/BrotliCompress/brotli', 'MdeModulePkg/Library/BrotliCustomDecompressLib/brotli',
                     'MdePkg/Library/BaseFdtLib/libfdt', 'MdePkg/Library/MipiSysTLib/mipisyst',
                     'SecurityPkg/DeviceSecurity/SpdmLib/libspdm'):
        target = core / relative
        if not target.exists() or not any(target.iterdir()):
            shutil.copytree(args.reference / 'Mu_Basecore' / relative, target, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns('.git', 'unit_test', 'os_stub', 'doc', 'samples'))
    # Libraries from the reference remain read-only. Only extracted OEM data and our source overlay are copied.
    shutil.copytree(ROOT / 'firmware/Platforms/Xiaomi/enumaPkg', uefi / 'Platforms/Xiaomi/enumaPkg', dirs_exist_ok=True)
    # Reuse exact upstream GOP validation, map collection, run merging and large
    # diagnostic font. All generated copies stay in out/, with original notices.
    probe = uefi / 'Platforms/Xiaomi/enumaPkg/Application/EnumaProbe'
    source_lock = json.loads((ROOT / 'config/porting-sources.lock.json').read_text())['unixnu_interface_sha256']
    upstream = args.unixnu / 'drivers/DarwinBoot/DarwinBootPkg/Driver'
    reused = {}
    for name in ('DarwinBoot.c', 'BootVideo.h', 'DiagFont.h'):
        data = (upstream / name).read_bytes()
        relative = 'drivers/DarwinBoot/DarwinBootPkg/Driver/' + name
        if hashlib.sha256(data).hexdigest() != source_lock[relative]:
            raise ValueError('probe source pin mismatch: ' + name)
        reused[relative] = source_lock[relative]
        if name != 'DarwinBoot.c': shutil.copyfile(upstream / name, probe / name)
    original = (upstream / 'DarwinBoot.c').read_text()
    begin = original.index('STATIC\nEFI_STATUS\nGetMap (')
    end = original.index('STATIC\nEFI_STATUS\nAllocateWindow (', begin)
    (probe / 'DarwinProbe.inc').write_text('// SPDX-License-Identifier: BSD-2-Clause-Patent\n' + original[begin:end])
    for relative in ('Binaries', 'raw'):
        shutil.copytree(ROOT / 'out/firmware-vendor' / relative, uefi / relative, dirs_exist_ok=True)
    includes = uefi / 'EnumaInputs'; includes.mkdir(exist_ok=True)
    for name in ('Vendor.dsc.inc', 'Vendor.fdf.inc', 'Vendor.apriori.inc', 'Vendor.raw.fdf.inc'):
        shutil.copyfile(ROOT / 'out/firmware-vendor' / name, includes / name)
    records = []
    sec_source = uefi / 'Silicon/Silicium/SiliciumPkg/Sec/Sec.c'
    sec_source.write_bytes(sec_source.read_bytes().replace(b'\r\n', b'\n'))
    # Patches are applied only to our archive staging, and only if not already present.
    for target, patch in [(uefi, ROOT / 'firmware/patches/kona-preserve-display.patch'),
                          (uefi, ROOT / 'firmware/patches/sec-preserve-display.patch'),
                          (core, uefi / 'Resources/MuPatches/Gic-Spurious.patch')]:
        # A nested staging directory must be its own patch root. Otherwise git
        # can silently skip paths outside the parent repository's current prefix.
        if not (target / '.git').exists():
            subprocess.run(['git', 'init', '-q', str(target)], check=True)
        reverse = subprocess.run(['git', 'apply', '--reverse', '--check', str(patch)], cwd=target,
                                 capture_output=True)
        if reverse.returncode:
            subprocess.run(['git', 'apply', '--check', str(patch)], cwd=target, check=True)
            subprocess.run(['git', 'apply', str(patch)], cwd=target, check=True)
    gic_source = core / 'ArmPkg/Drivers/ArmGicDxe/GicV3/ArmGicV3Dxe.c'
    if 'cannot be masked' not in gic_source.read_text():
        raise ValueError('GIC patch was not actually applied')
    tools = core / 'BaseTools'; conf = WORK / 'Conf'; conf.mkdir(exist_ok=True)
    for name in ('target', 'tools_def', 'build_rule'):
        target = conf / (name + '.txt')
        if not target.exists(): shutil.copyfile(tools / 'Conf' / (name + '.template'), target)
    packages = [uefi, uefi / 'Platforms/Xiaomi', args.unixnu / 'package', args.unixnu / 'drivers/DarwinBoot',
                core, args.reference / 'Common/Mu', args.reference / 'Common/Mu_OEM_Sample',
                uefi / 'Silicon/Qualcomm', uefi / 'Silicon/Silicium']
    env = dict(os.environ, WORKSPACE=str(uefi), EDK_TOOLS_PATH=str(tools), CONF_PATH=str(conf),
               PACKAGES_PATH=':'.join(str(x) for x in packages), PYTHON_COMMAND=sys.executable,
               PYTHONPATH=str(tools / 'Source/Python'), PYTHONDONTWRITEBYTECODE='1',
               CLANG_BIN=str(Path(shutil.which('clang')).parent) + '/', SOURCE_DATE_EPOCH='1792540800')
    env['PATH'] = ':'.join([str(tools / 'BinWrappers/PosixLike'), str(tools / 'Source/C/bin'), os.environ['PATH']])
    if not (tools / 'Source/C/bin/GenFw').exists():
        records.append(command(['make', '-C', tools / 'Source/C', '-j' + str(args.jobs)],
                               WORK / 'logs/basetools.log', env))
    if not records or records[-1]['exit_code'] == 0:
        defines = {'FD_BASE': '0x9fc00000', 'FD_SIZE': '0x300000', 'FD_BLOCKS': '768',
                   'ENABLE_SECUREBOOT': '0', 'DEVICE_MODEL': 'enuma', 'MEMORY_PROTECTION': 'TRUE',
                   'SHIP_MODE': 'FALSE', 'BUILDID_STRING': 'enuma-research',
                   'ENUMA_PLATFORM_CONFIG': 'enumaPkg/Include/PlatformConfig.inc',
                   'ENUMA_VENDOR_DSC': 'EnumaInputs/Vendor.dsc.inc',
                   'ENUMA_VENDOR_DXE': 'EnumaInputs/Vendor.fdf.inc',
                   'ENUMA_VENDOR_APRIORI': 'EnumaInputs/Vendor.apriori.inc',
                   'ENUMA_VENDOR_RAW': 'EnumaInputs/Vendor.raw.fdf.inc'}
        argv = [sys.executable, tools / 'Source/Python/build/build.py', '-p', 'Platforms/Xiaomi/enumaPkg/enuma.dsc',
                '-a', 'AARCH64', '-b', 'DEBUG', '-t', 'CLANGPDB', '-n', str(args.jobs)]
        for key, value in defines.items(): argv += ['-D', key + '=' + value]
        records.append(command(argv, WORK / 'logs/firmware.log', env, uefi))
    fd = uefi / 'Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd'
    report = {'scope': 'isolated firmware build; no device boot', 'checks': records,
              'fd': str(fd.relative_to(ROOT)), 'fd_exists': fd.exists(),
              'complete': all(r['exit_code'] == 0 for r in records) and fd.exists()}
    report['archive_sha256'] = lock['archive_sha256']
    report['reference_gitlinks'] = lock['reference_gitlinks']
    report['probe_upstream_sha256'] = reused
    report['source_inputs_sha256'] = {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
        for p in sorted((ROOT / 'firmware').rglob('*'))
        if p.is_file() and p.suffix in ('.c', '.h', '.inf', '.inc', '.dsc', '.fdf', '.patch', '.toml')
    }
    if fd.exists(): report['fd_sha256'] = hashlib.sha256(fd.read_bytes()).hexdigest()
    (ROOT / 'reports/enuma-firmware-build.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    if not report['complete']: sys.exit(1)


if __name__ == '__main__': main()
