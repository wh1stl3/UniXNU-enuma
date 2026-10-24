"""Fake MMIO/wait and AArch64 counter objects; no device accesses."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--firmware-root',type=Path,default=ROOT/'firmware');a=p.parse_args()
 out=ROOT/'out/scanout-geometry-host';out.mkdir(exist_ok=True);inc=ROOT/'out/gop-audit-host/MuInclude'
 flags=['clang','-std=c11','-Wall','-Wextra','-Werror','-fshort-wchar','-I'+str(inc),'-I'+str(a.firmware_root/'diagnostics')]
 for opt in ('O1','Oz'):
  exe=out/opt;subprocess.run(flags+['-I'+str(inc/'X64'),'-'+opt,'-fsanitize=address,undefined','-fno-pie','-no-pie',str(ROOT/'tests/enuma_scanout_geometry.c'),'-o',str(exe)],check=True);result=subprocess.check_output([str(exe)],text=True);print(result.strip());cases=int(result.split()[1])
 unit=out/'unit.c';unit.write_text('#include "EnumaScanoutGeometry.h"\n#include <Library/UefiBootServicesTableLib.h>\nstatic UINT32 Read(UINTN a){return *(volatile UINT32 *)a;}\nstatic EFI_STATUS Wait(UINTN u){if(gBS==NULL||gBS->Stall==NULL)return EFI_NOT_READY;return gBS->Stall(u);}\n\nEFI_STATUS Progress(void){return EnumaScanoutStagedGeometry(Read,Wait);}\n')
 obj=out/'counters.obj';subprocess.run(flags+['-I'+str(inc/'AArch64'),'-target','aarch64-unknown-windows-msvc','-ffreestanding','-Oz','-fno-builtin','-fno-stack-protector','-mno-stack-arg-probe','-mno-implicit-float','-c',str(unit),'-o',str(obj)],check=True)
 undefined=subprocess.check_output(['llvm-nm','--undefined-only',str(obj)],text=True);assert [x.split()[-1] for x in undefined.splitlines() if x.strip()]==['gBS'],undefined
 asm=subprocess.check_output(['llvm-objdump','-d',str(obj)],text=True);(out/'counters.disassembly.txt').write_text(asm)
 report=dict(scope=__doc__,all_passed=True,cases=cases,optimizations=['O1','Oz'],sanitizers=['address','undefined'],progress_max_reads=250,wait_calls_max=2,wait_microseconds=100000,maximum_frame_delta=64,delta_arithmetic='strict nonwrapping monotonic per window; two windows same interface',inactive_interfaces_sampled=False,mmio_writes=False,pixel_access=False,undefined_symbols=['gBS'],new_library_or_constructor=False,runtime=False,sources={n:hashlib.sha256((a.firmware_root/'diagnostics'/n).read_bytes()).hexdigest() for n in ['EnumaScanoutGeometry.h','EnumaScanoutRoute.h','EnumaScanoutDescriptor.h','EnumaDsiNativeProgress.h','EnumaDsiCounters.h','EnumaScanoutAudit.h']},object_sha256=hashlib.sha256(obj.read_bytes()).hexdigest())
 (ROOT/'reports/enuma-scanout-geometry-host.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
 print('PASS: DSI counter host and AArch64 qualification; only existing gBS dependency')
if __name__=='__main__':main()
