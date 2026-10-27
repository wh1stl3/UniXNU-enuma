"""Bounded clock exits: real helper, all calibration forces and ARM64 objects."""
import argparse,json,hashlib,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
 inc=ROOT/'firmware/Mu_Basecore/MdePkg/Include';fw=ROOT/'firmware/diagnostics';runs=[]
 for force in (0,1,5):
  flags=['/usr/bin/clang','-Wall','-Wextra','-Werror','-Wno-unused-function','-DMDEPKG_NDEBUG','-fshort-wchar',
   '-DENUMA_OEM_CLOCK_FORCE='+str(force),'-I'+str(inc),'-I'+str(ROOT/'firmware/Mu_Basecore/MdeModulePkg/Include'),'-I'+str(fw)]
  exe=out/('clock-'+str(force));subprocess.run(flags+['-I'+str(inc/'X64'),'-std=c11','-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',ROOT/'tests/oem_clock_exit.c','-o',exe],check=True)
  r=subprocess.run([exe],capture_output=True,text=True,timeout=20);assert not r.returncode,r.stderr
  obj=out/('clock-'+str(force)+'.obj')
  subprocess.run(flags+['-I'+str(inc/'AArch64'),'-target','aarch64-unknown-windows-msvc','-ffreestanding','-Os','-mno-stack-arg-probe','-mno-implicit-float','-c',ROOT/'tests/oem_clock_arm.c','-o',obj],check=True)
  asm=subprocess.check_output(['/usr/bin/llvm-objdump','-dr',obj],text=True);(out/('clock-'+str(force)+'.txt')).write_text(asm)
  for name in ('MicroSecondDelay','ResetCold','CpuPause'):
   if name not in asm:raise ValueError('clock exit optimized out '+name)
  runs.append(dict(force=force,host_returncode=r.returncode,arm_object_sha256=hashlib.sha256(obj.read_bytes()).hexdigest()))
 sources=['scripts/check_oem_clock.py','tests/oem_clock_exit.c','tests/oem_clock_arm.c']+['firmware/diagnostics/'+n for n in ['EnumaOemExitClock.h','EnumaOemClockCapture.h','EnumaOemExceptionStop.h','EnumaOemCoreBinding.h']]
 result=dict(passed=True,runs=runs,hardware_executed=False,sources={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in sources})
 (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS: 5 classes, invalid inputs, reset-return loop, 3 forces, sanitized and ARM64 helpers')
if __name__=='__main__':main()
