"""Host-check the complete patched SimpleFb source with explicit UEFI adapters."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--firmware-root',type=Path,default=ROOT/'firmware');a=p.parse_args();out=ROOT/'out/simplefb-contract-host';out.mkdir(exist_ok=True)
 n='Silicon/Silicium/SiliciumPkg/Drivers/SimpleFbDxe/SimpleFb.c';target=out/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((a.firmware_root/n).read_bytes().replace(b'\r\n',b'\n'))
 probe_name='Platforms/Xiaomi/enumaPkg/Application/EnumaProbe/EnumaProbe.c'
 probe=out/probe_name;probe.parent.mkdir(parents=True,exist_ok=True);probe.write_bytes((a.firmware_root/probe_name).read_bytes().replace(b'\r\n',b'\n'))
 patch=a.firmware_root/'patches/simplefb-contract.patch'
 for check in (True,False):
  subprocess.run(['git','--no-optional-locks','-C',str(out),'apply',*(['--check'] if check else []),str(patch.resolve())],check=True)
 for name in ('Library/DebugLib.h','Library/FrameBufferBltLib.h','Library/UefiBootServicesTableLib.h','Library/MemoryAllocationLib.h','Library/MemoryMapHelperLib.h','Library/BaseMemoryLib.h','Library/PcdLib.h','Configuration/BootDevices.h'):
  p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('/* host UEFI adapter only */\n')
 cmd=['clang','-std=c11','-O1','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-fsanitize=address,undefined','-no-pie','-DENUMA_DIAG_SIMPLEFB=1','-DSIMPLEFB_SOURCE="'+str(target)+'"','-I'+str(out),'-I'+str(ROOT/'tests'),str(ROOT/'tests/simplefb_contract.c'),'-o',str(out/'test')]
 subprocess.run(cmd,check=True);subprocess.run([cmd[-1]],check=True)
 # Compile the actual early guard prefix: the opaque AArch64 body must not run.
 text=probe.read_text();entry=text.index('EFI_STATUS EFIAPI EnumaProbeEntry (');body=text.index('{',entry);end=text.index('#endif',body)+len('#endif');prefix=text[body+1:end]
 assert 'return EFI_UNSUPPORTED;' in prefix and 'SYSREG' not in prefix and 'DiagDraw' not in prefix
 guard=out/'probe-guard.c';guard.write_text('#include <assert.h>\n#define VOID void\n#define EFI_UNSUPPORTED 3\nstatic int f(void *ImageHandle,void *SystemTable){'+prefix+'\n(void)ImageHandle;(void)SystemTable;return 7;}\nint main(void){assert(f(0,0)==EXPECTED);return 0;}\n')
 for flag,expected in ((0,7),(1,3)):
  c=['clang','-std=c11','-Wall','-Wextra','-Werror','-DENUMA_DIAG_SIMPLEFB='+str(flag),'-DEXPECTED='+str(expected),str(guard),'-o',str(out/'guard-test')]
  subprocess.run(c,check=True);subprocess.run([c[-1]],check=True)
 # Replay the selection with its real existing UFS/DSC patches as well.
 import sys
 sys.path.insert(0,str(ROOT/'scripts'))
 from build_enuma_firmware import apply_patch_series
 selection=out/'selection';selection.mkdir(exist_ok=True)
 names=['Platforms/Xiaomi/enumaPkg/enuma.dsc','Platforms/Xiaomi/enumaPkg/Include/PlatformConfig.inc',n,probe_name]
 for name in names:
  p=selection/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((a.firmware_root/name).read_bytes().replace(b'\r\n',b'\n'))
 for filename in ('Vendor.dsc.inc','Vendor.fdf.inc','Vendor.apriori.inc'):
  name='EnumaInputs/'+filename;names.append(name);p=selection/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/'out/firmware-vendor'/filename).read_bytes().replace(b'\r\n',b'\n'))
 series=[(selection,a.firmware_root/'patches'/name) for name in ('dispatch-detail-options.patch','diagnostic-ufs-selection.patch','simplefb-contract.patch','simplefb-diagnostic-selection.patch')]
 apply_patch_series(series);once={name:(selection/name).read_bytes() for name in names};apply_patch_series(series)
 assert once=={name:(selection/name).read_bytes() for name in names}
 (ROOT/'reports/enuma-simplefb-contract-host.json').write_text(json.dumps(dict(scope='complete real SimpleFb source with host UEFI/allocator adapters; no hardware/ABI proof',baseline_sha256=hashlib.sha256((a.firmware_root/n).read_bytes()).hexdigest(),patch_sha256=hashlib.sha256(patch.read_bytes()).hexdigest(),patched_source_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),all_passed=True,selection_patch_sha256=hashlib.sha256((a.firmware_root/'patches/simplefb-diagnostic-selection.patch').read_bytes()).hexdigest(),composed_selection_replay=True,metadata_only_no_pixel_calls=True,probe_guard_checked=True,patched_probe_sha256=hashlib.sha256(probe.read_bytes()).hexdigest(),checks=['lookup fallback and errors','null/invalid modes and mask copy','three allocation failure points','configure/install failure cleanup','reentry/double cleanup','64-bit span/base overflow','Blt returns unsupported without touching framebuffer'],sanitizers=['address','undefined']),indent=2)+'\n')
 print('PASS: complete patched SimpleFb, host ASan/UBSan metadata-only failure/mode/cleanup/span checks')
if __name__=='__main__':main()
