"""Exercise real SimpleFb + pinned Mu configure prefix + DarwinBoot video helper.

No physical framebuffer is mapped. Configure stores an opaque fake address;
diagnostic Blt remains disabled. Host execution is not firmware/ABI evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--firmware-root', type=Path, default=ROOT/'firmware')
    parser.add_argument('--expect-unfixed', action='store_true', help='require the two known baseline assertion failures; save a separate regression report')
    args = parser.parse_args()
    out = ROOT/'out/simplefb-handoff-host'
    out.mkdir(exist_ok=True)
    name = 'Silicon/Silicium/SiliciumPkg/Drivers/SimpleFbDxe/SimpleFb.c'
    probe = 'Platforms/Xiaomi/enumaPkg/Application/EnumaProbe/EnumaProbe.c'
    for relative in (name, probe):
        p = out/relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((args.firmware_root/relative).read_bytes().replace(b'\r\n', b'\n'))
    patch = args.firmware_root/'patches/simplefb-contract.patch'
    for check in (True, False):
        subprocess.run(['git','-C',str(out),'apply',*(['--check'] if check else []),str(patch.resolve())], check=True)
    lock = json.loads((ROOT/'config/firmware-build.lock.json').read_text())
    archive = ROOT/'out/firmware-build/mu-basecore.tar.gz'
    assert digest(archive.read_bytes()) == lock['archive_sha256']['mu-basecore.tar.gz']
    source_name = 'MdeModulePkg/Library/FrameBufferBltLib/FrameBufferBltLib.c'
    with tarfile.open(archive) as source:
        member = next(m for m in source.getmembers() if m.name.endswith('/'+source_name))
        full = source.extractfile(member).read()
    normalized = full.replace(b'\r\n', b'\n')
    end = normalized.index(b'\n/**\n  Performs a UEFI Graphics Output Protocol Blt Video Fill.')
    prefix = normalized[:end]
    assert prefix.endswith(b'  return RETURN_SUCCESS;\n}\n')
    actual_configure = out/'real-configure.inc'
    actual_configure.write_bytes(prefix)
    video_name = 'drivers/DarwinBoot/DarwinBootPkg/Driver/BootVideo.h'
    video = ROOT/'out/sources/UniXNU'/video_name
    interfaces = json.loads((ROOT/'config/porting-sources.lock.json').read_text())['unixnu_interface_sha256']
    assert digest(video.read_bytes()) == interfaces[video_name]
    for header in ('Uefi.h','Uefi/UefiBaseType.h','Protocol/GraphicsOutput.h','Library/BaseLib.h',
                   'Library/DebugLib.h','Library/FrameBufferBltLib.h','Library/UefiBootServicesTableLib.h',
                   'Library/MemoryAllocationLib.h','Library/MemoryMapHelperLib.h','Library/BaseMemoryLib.h',
                   'Library/PcdLib.h','Configuration/BootDevices.h'):
        p = out/header
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('/* Host adapter types are declared by simplefb_test_uefi.h. */\n')
    cases = [('region-span',True,False),('real-configure-retry-and-loader',False,True)]
    if not args.expect_unfixed:
        cases.append(('combined-region-real-configure-loader',True,True))
    results = []
    for label, bounds, real in cases:
        cmd = ['clang','-std=c11','-O1','-Wall','-Wextra','-Werror','-Wno-unused-parameter',
               '-fsanitize=address,undefined','-no-pie','-DENUMA_DIAG_SIMPLEFB=1',
               '-DSIMPLEFB_SOURCE="'+str(out/name)+'"','-I'+str(out),'-I'+str(ROOT/'tests')]
        if bounds:cmd += ['-DSIMPLEFB_RANGE_CHECKS=1']
        if real:cmd += ['-DSIMPLEFB_REAL_CONFIGURE="'+str(actual_configure)+'"','-DSIMPLEFB_LOADER_SOURCE="'+str(video)+'"']
        cmd += [str(ROOT/'tests/simplefb_contract.c'),'-o',str(out/label)]
        subprocess.run(cmd, check=True)
        run = subprocess.run([cmd[-1]], cwd=out, capture_output=True, text=True, timeout=15)
        if args.expect_unfixed:
            assert run.returncode != 0 and 'assertion' in run.stderr.lower(), run.stderr
            expected = 'EFI_BAD_BUFFER_SIZE' if bounds else 'EFI_DEVICE_ERROR'
            assert expected in run.stderr, run.stderr
        else:
            assert run.returncode == 0, run.stderr
        results.append(dict(case=label,exit_code=run.returncode,stderr=run.stderr))
    report = dict(scope='host integration with real Mu configure prefix and pinned DarwinBoot video helper; no mapped framebuffer/UEFI ABI/device execution',
        firmware_contract_patch_sha256=digest(patch.read_bytes()),
        patched_simplefb_sha256=digest((out/name).read_bytes()),
        mu_commit=lock['reference_gitlinks']['Mu_Basecore'],mu_archive_sha256=digest(archive.read_bytes()),
        mu_library_path=source_name,mu_library_raw_sha256=digest(full),
        mu_exact_prefix_sha256=digest(prefix),mu_extraction='exact prefix before first VideoFill Doxygen block; library body unchanged, configure symbol renamed by C macro in fixture',
        darwin_boot_video_sha256=digest(video.read_bytes()),
        adapter_limit='UEFI services/allocators and HighBitSet32 adapted; full Blt implementation and MMIO/cache/physical ownership not exercised',
        expected_baseline_failures=args.expect_unfixed,results=results,
        new_device_trials=0)
    filename = 'enuma-simplefb-handoff-regressions.json' if args.expect_unfixed else 'enuma-simplefb-handoff-host.json'
    (ROOT/'reports'/filename).write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: '+('baseline failures reproduced' if args.expect_unfixed else 'real configure retries, region bounds and loader video handoff'))


if __name__ == '__main__':
    main()
