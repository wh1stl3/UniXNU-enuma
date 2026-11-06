"""Actual post-DXE GOP helper under sanitizers and strict ARM64 compilation."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
 inc=ROOT/'firmware/Mu_Basecore/MdePkg/Include'
 common=['/usr/bin/clang','-Wall','-Wextra','-Werror','-fshort-wchar','-fno-builtin','-DMDEPKG_NDEBUG','-I'+str(inc),'-I'+str(ROOT/'firmware/diagnostics')]
 runs=[]
 commands=[common+['-I'+str(inc/'X64'),'-std=c11','-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',str(ROOT/'tests/oem_gop_mode.c'),'-o',str(out/'host')],[str(out/'host')],common+['-I'+str(inc/'AArch64'),'-target','aarch64-unknown-windows-msvc','-ffreestanding','-mno-stack-arg-probe','-mno-implicit-float','-Os','-c',str(ROOT/'tests/oem_gop_mode_arm.c'),'-o',str(out/'arm.obj')]]
 passed=False
 try:
  for cmd in commands:
   r=subprocess.run(cmd,capture_output=True,text=True,timeout=90);runs.append(dict(argv=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
   if r.returncode:raise ValueError(r.stdout+r.stderr)
  asm=subprocess.check_output(['/usr/bin/llvm-objdump','-dr',out/'arm.obj'],text=True);(out/'arm.txt').write_text(asm)
  for name in ('OemGopAdvance','OemGopOwner','OemGopFinal'):
   if name not in asm:raise ValueError('missing ARM helper '+name)
  passed=True
 finally:
  files=['scripts/check_oem_gop_mode.py','tests/oem_gop_mode.c','tests/oem_gop_mode_arm.c','firmware/diagnostics/EnumaOemGopMode.h']
  result=dict(passed=passed,runs=runs,hardware_executed=False,sources={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in files})
  (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 print('PASS: native GOP policy/state/failure/cleanup/no-retry checks, ASan/UBSan and strict ARM64')
if __name__=='__main__':main()
