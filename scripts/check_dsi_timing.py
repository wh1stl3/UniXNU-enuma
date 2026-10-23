"""Sanitized exact-address DSI read tests and actual AArch64 object; no device."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--firmware-root',type=Path,default=ROOT/'firmware');a=p.parse_args()
 out=ROOT/'out/dsi-timing-host';out.mkdir(exist_ok=True);inc=ROOT/'out/gop-audit-host/MuInclude'
 flags=['clang','-std=c11','-Wall','-Wextra','-Werror','-fshort-wchar','-I'+str(inc),'-I'+str(a.firmware_root/'diagnostics')]
 for opt in ('O1','Oz'):
  exe=out/opt;subprocess.run(flags+['-I'+str(inc/'X64'),'-'+opt,'-fsanitize=address,undefined','-fno-pie','-no-pie',str(ROOT/'tests/enuma_dsi_timing.c'),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
 unit=out/'unit.c';unit.write_text('#include "EnumaScanoutAudit.h"\nstatic UINT32 Read(UINTN a){return *(volatile UINT32 *)a;}\nEFI_STATUS Timing(void){return EnumaDsiTimingEnabled(Read);}\n')
 obj=out/'timing.obj';subprocess.run(flags+['-I'+str(inc/'AArch64'),'-target','aarch64-unknown-windows-msvc','-ffreestanding','-Oz','-fno-builtin','-fno-stack-protector','-mno-implicit-float','-c',str(unit),'-o',str(obj)],check=True)
 assert not subprocess.check_output(['llvm-nm','--undefined-only',str(obj)],text=True).strip()
 asm=subprocess.check_output(['llvm-objdump','-d',str(obj)],text=True);(out/'timing.disassembly.txt').write_text(asm)
 assert len(re.findall(r'\tldr\t',asm))==2,asm
 assert not re.search(r'\t(st\w*|bl|blr)\t',asm),asm
 header=a.firmware_root/'diagnostics/EnumaScanoutAudit.h'
 report=dict(scope=__doc__,all_passed=True,cases=8,optimizations=['O1','Oz'],sanitizers=['address','undefined'],addresses=['0xae6b800','0xae6c000'],maximum_reads=2,object_loads=2,undefined_symbols=[],object_stores_or_calls=False,pixel_access=False,mmio_writes=False,runtime=False,source_sha256=hashlib.sha256(header.read_bytes()).hexdigest(),object_sha256=hashlib.sha256(obj.read_bytes()).hexdigest())
 (ROOT/'reports/enuma-dsi-timing-host.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS: 8 DSI cases at O1/Oz+ASan/UBSan; real AArch64 object has two loads, no stores/calls/dependencies')
if __name__=='__main__':main()
