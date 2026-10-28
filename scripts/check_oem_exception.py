"""Actual exception parser under sanitizers and strict ARM64 exception path."""
import argparse,json,subprocess,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
 inc=ROOT/'firmware/Mu_Basecore/MdePkg/Include';fw=ROOT/'firmware/diagnostics';lib=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib'
 shutil.copytree(lib,out/'OemInherited');(out/'EnumaOemExceptionIdentity.h').write_bytes(b'#define ENUMA_EXCEPTION_SESSION 0x1234ULL\n')
 flags=['/usr/bin/clang','-std=c11','-Wall','-Wextra','-Werror','-fshort-wchar','-DMDEPKG_NDEBUG','-I'+str(inc),'-I'+str(fw),'-I'+str(ROOT/'firmware/Mu_Basecore/MdeModulePkg/Include')]
 cmd=flags+['-I'+str(inc/'X64'),'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',ROOT/'tests/oem_exception_view.c','-o',out/'view']
 subprocess.run(cmd,check=True);subprocess.run([out/'view'],check=True)
 flow=flags+['-I'+str(inc/'X64'),'-I'+str(lib),'-I'+str(out),'-Wno-unused-function','-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',ROOT/'tests/oem_exception_flow.c','-o',out/'flow']
 subprocess.run(flow,check=True);subprocess.run([out/'flow'],check=True)
 pixel=flags+['-I'+str(inc/'X64'),'-I'+str(lib),'-Wno-unused-function','-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',ROOT/'tests/oem_exception_pixel.c','-o',out/'pixel']
 subprocess.run(pixel,check=True);subprocess.run([out/'pixel'],check=True)
 arm=flags+['-target','aarch64-unknown-windows-msvc','-ffreestanding','-fno-stack-protector','-mno-stack-arg-probe','-mno-implicit-float','-Os','-Wno-unused-function']
 for path in (inc/'AArch64',ROOT/'firmware/Mu_Basecore/MdeModulePkg/Include',lib,out):arm+=['-I'+str(path)]
 subprocess.run(arm+['-c',ROOT/'tests/oem_exception_arm.c','-o',out/'exception.obj'],check=True)
 asm=subprocess.check_output(['/usr/bin/llvm-objdump','-dr',out/'exception.obj'],text=True);(out/'exception.asm').write_text(asm)
 for token in ('ExSnapshot','ExPresent','ExFindOwner','ExReadMeta','ResetCold','at\ts1e1r','PAR_EL1'):
  if token.lower() not in asm.lower():raise ValueError('exception path missing: '+token)
 for forbidden in ('LocateProtocol','GetMemoryMap','SerialPortWrite','AsciiSPrint','AllocatePool','HandleProtocol','LocateMemoryRegionByName'):
  if forbidden in asm:raise ValueError('unsafe exception dependency: '+forbidden)
 for name,args in [('flow-context',flow),('pixel-context',pixel)]:
  command=list(args);command.insert(1,'-DENUMA_OEM_CONTEXT=1');command[-1]=out/name
  subprocess.run(command,check=True);subprocess.run([out/name],check=True)
 subprocess.run(arm+['-DENUMA_OEM_CONTEXT=1','-c',ROOT/'tests/oem_exception_arm.c','-o',out/'context.obj'],check=True)
 context_asm=subprocess.check_output(['/usr/bin/llvm-objdump','-dr',out/'context.obj'],text=True);(out/'context.asm').write_text(context_asm)
 for token in ('ExContextCapture','at\ts1e1w','TTBR0_EL1','TTBR1_EL1','TCR_EL1','SCTLR_EL1'):
  if token.lower() not in context_asm.lower():raise ValueError('context missing '+token)
 names=['scripts/check_oem_exception.py','tests/oem_exception_view.c','tests/oem_exception_flow.c','tests/oem_exception_arm.c']+['firmware/diagnostics/'+n for n in ('EnumaOemExceptionContext.h','EnumaOemExceptionPage.h','EnumaOemExceptionView.h','EnumaOemExceptionDisplay.h','EnumaOemExceptionStop.h','EnumaOemCapturePixel.h')]
 names+=['tests/oem_exception_pixel.c']
 result=dict(passed=True,sanitizers=['ASan','UBSan'],arm64_object_sha256=hashlib.sha256((out/'exception.obj').read_bytes()).hexdigest(),hardware_executed=False,sources={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names})
 (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS: exception snapshot, bounded owner lookup failure cases and strict ARM64 sink')
if __name__=='__main__':main()
