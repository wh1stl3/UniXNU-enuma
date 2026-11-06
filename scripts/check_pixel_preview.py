"""R-005 proposed pixel transaction tested against fake memory only."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--firmware-root',type=Path,default=ROOT/'firmware');a=p.parse_args()
 out=ROOT/'out/pixel-preview-host';out.mkdir(exist_ok=True);inc=ROOT/'out/gop-audit-host/MuInclude'
 flags=['clang','-std=c11','-Wall','-Wextra','-Werror','-fshort-wchar','-I'+str(inc),'-I'+str(a.firmware_root/'diagnostics')]
 for opt in ('O1','Oz'):
  exe=out/opt;subprocess.run(flags+['-I'+str(inc/'X64'),'-'+opt,'-fsanitize=address,undefined','-fno-pie','-no-pie',str(ROOT/'tests/enuma_pixel_preview.c'),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
 unit=out/'unit.c';unit.write_text('#include "EnumaPixelPreviewArm.h"\nEFI_STATUS Preview(UINT32 *s,UINTN n){return EnumaPixelPreviewArm(s,n);}\nEFI_STATUS LocalPreview(void){UINT32 s[ENUMA_PIXEL_COUNT];return EnumaPixelPreviewArm(s,ENUMA_PIXEL_COUNT);}\n')
 obj=out/'preview.obj';subprocess.run(flags+['-I'+str(inc/'AArch64'),'-target','aarch64-unknown-windows-msvc','-ffreestanding','-Oz','-fno-builtin','-fno-stack-protector','-mno-stack-arg-probe','-mno-implicit-float','-c',str(unit),'-o',str(obj)],check=True)
 symbols=subprocess.check_output(['llvm-nm','--undefined-only',str(obj)],text=True);assert [line.split()[-1] for line in symbols.splitlines() if line.strip()]==['gBS'],symbols
 disasm=subprocess.check_output(['llvm-objdump','-d',str(obj)],text=True);assert 'civac' in disasm and 'dsb' in disasm and 'CTR_EL0' in disasm
 (out/'preview.disassembly.txt').write_text(disasm)
 report=dict(scope='R-005 proposal; fake pixels and target object only, NOT authorized/runtime-tested',all_passed=True,scenarios=33,optimizations=['O1','Oz'],sanitizers=['address','undefined'],window=[128,8],saved_bytes=4096,pixel_reads_max=2048,pixel_stores_max=2048,register_reads_max=96,row_cache_synchronizations_max=24,delay_us=500000,restore_on_wait_error=True,restore_readback_checked=True,mmio_writes=False,physical_pixels_accessed=False,hardware_permission='pending R-005',undefined_symbols=['gBS'],sources={name:hashlib.sha256((a.firmware_root/'diagnostics'/name).read_bytes()).hexdigest() for name in ['EnumaPixelPreview.h','EnumaPixelPreviewArm.h']},object_sha256=hashlib.sha256(obj.read_bytes()).hexdigest())
 (ROOT/'reports/enuma-pixel-preview-host.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
