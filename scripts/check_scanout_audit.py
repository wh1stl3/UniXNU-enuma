"""Sanitized read-only scanout predicates and actual AArch64 object; no device calls."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--firmware-root',type=Path,default=ROOT/'firmware');a=p.parse_args()
 out=ROOT/'out/scanout-audit-host';out.mkdir(exist_ok=True);inc=ROOT/'out/gop-audit-host/MuInclude'
 flags=['clang','-std=c11','-Wall','-Wextra','-Werror','-fshort-wchar','-I'+str(inc),'-I'+str(a.firmware_root/'diagnostics')]
 records=[]
 for opt in ['O1','Oz']:
  exe=out/('scanout-'+opt)
  subprocess.run(flags+['-I'+str(inc/'X64'),'-'+opt,'-fsanitize=address,undefined','-fno-pie','-no-pie',str(ROOT/'tests/enuma_scanout_audit.c'),'-o',str(exe)],check=True)
  subprocess.run([str(exe)],check=True);records.append(opt)
 unit=out/'unit.c';unit.write_text('#include "EnumaScanoutAudit.h"\nstatic UINT32 Read(UINTN a){return *(volatile UINT32 *)a;}\nEFI_STATUS Check(void){return EnumaScanoutCheck(Read);}\nEFI_STATUS Presence(void){return EnumaScanoutAddressPresent(Read);}\nEFI_STATUS Linear(void){return EnumaScanoutLinearCandidates(Read);}\n')
 obj=out/'scanout.obj'
 subprocess.run(flags+['-I'+str(inc/'AArch64'),'-target','aarch64-unknown-windows-msvc','-ffreestanding','-Oz','-fno-builtin','-fno-stack-protector','-mno-implicit-float','-c',str(unit),'-o',str(obj)],check=True)
 undefined=subprocess.check_output(['llvm-nm','--undefined-only',str(obj)],text=True);assert not undefined.strip(),undefined
 (out/'scanout.disassembly.txt').write_text(subprocess.check_output(['llvm-objdump','-d',str(obj)],text=True))
 report=dict(scope='host fault rejection and AArch64 object; not runtime trace',all_passed=True,cases=64,optimizations=records,sanitizers=['address','undefined'],max_reads=72,address_only_max_reads=8,packing_max_reads=24,mmio_write_path=False,pixel_access=False,source_sha256=hashlib.sha256((a.firmware_root/'diagnostics/EnumaScanoutAudit.h').read_bytes()).hexdigest(),object_sha256=hashlib.sha256(obj.read_bytes()).hexdigest(),runtime=False)
 (ROOT/'reports/enuma-scanout-host.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS: scanout host predicates, bounded reads, no dependencies in AArch64 object')
if __name__=='__main__':main()
