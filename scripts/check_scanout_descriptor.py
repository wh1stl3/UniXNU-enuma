"""Read-only descriptor decoder boundary tests and AArch64 object audit."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--firmware-root',type=Path,default=ROOT/'firmware');a=p.parse_args()
 out=ROOT/'out/scanout-descriptor-host';out.mkdir(exist_ok=True);inc=ROOT/'out/gop-audit-host/MuInclude'
 flags=['clang','-std=c11','-Wall','-Wextra','-Werror','-fshort-wchar','-I'+str(inc),'-I'+str(a.firmware_root/'diagnostics')]
 for opt in ('O1','Oz'):
  exe=out/opt;subprocess.run(flags+['-I'+str(inc/'X64'),'-'+opt,'-fsanitize=address,undefined','-fno-pie','-no-pie',str(ROOT/'tests/enuma_scanout_descriptor.c'),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
 unit=out/'unit.c';unit.write_text('#include "EnumaScanoutDescriptor.h"\nstatic UINT32 Read(UINTN a){return *(volatile UINT32 *)a;}\nEFI_STATUS Descriptor(ENUMA_SCANOUT_DESCRIPTOR *d){return EnumaScanoutFindBoundedDescriptor(Read,d);}\n')
 obj=out/'descriptor.obj';subprocess.run(flags+['-I'+str(inc/'AArch64'),'-target','aarch64-unknown-windows-msvc','-ffreestanding','-Oz','-fno-builtin','-fno-stack-protector','-mno-implicit-float','-c',str(unit),'-o',str(obj)],check=True)
 assert not subprocess.check_output(['llvm-nm','--undefined-only',str(obj)],text=True).strip()
 (out/'descriptor.disassembly.txt').write_text(subprocess.check_output(['llvm-objdump','-d',str(obj)],text=True))
 report=dict(scope='offline descriptor hypothesis; not activity/IOVA or pixel proof',all_passed=True,random_samples=10000,optimizations=['O1','Oz'],sanitizers=['address','undefined'],max_register_reads=48,pixel_access=False,mmio_writes=False,source_sha256=hashlib.sha256((a.firmware_root/'diagnostics/EnumaScanoutDescriptor.h').read_bytes()).hexdigest(),object_sha256=hashlib.sha256(obj.read_bytes()).hexdigest(),runtime=False)
 (ROOT/'reports/enuma-scanout-descriptor-host.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
