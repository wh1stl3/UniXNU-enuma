"""Repeatable offline integration qualification; never builds a deployment approval."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
 report={'passed':False,'hardware_executed':False,'board_lease_implemented':False,'execution_ready':False,'known_defects':['private SystemTable ConfigurationTable pointer/count becomes stale after global updates; reproducer success means defect exists'],'commands':[]}
 def run(argv):
  p=subprocess.run([str(x) for x in argv],cwd=ROOT,capture_output=True,text=True)
  report['commands'].append({'argv':[str(x) for x in argv],'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
  if p.returncode:raise RuntimeError(p.stderr)
  return p.stdout
 inc=ROOT/'firmware/Mu_Basecore/MdePkg/Include';diag=ROOT/'firmware/diagnostics'
 base=['clang','-std=c11','-Wall','-Wextra','-Werror','-fshort-wchar','-fno-builtin','-DMDEPKG_NDEBUG','-I'+str(inc),'-I'+str(diag)]
 try:
  for name in ['oem_integration','darwin_gop_contract','oem_system_table_lifetime']:
   run(base+['-I'+str(inc/'X64'),'-I'+str(ROOT/'out/sources/UniXNU/drivers/DarwinBoot/DarwinBootPkg/Driver'),'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',ROOT/'tests'/f'{name}.c','-o',out/name]);run([out/name])
  run(base+['-I'+str(inc/'AArch64'),'-I'+str(ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib'),'-target','aarch64-unknown-windows-msvc','-ffreestanding','-fno-stack-protector','-mno-stack-arg-probe','-mno-implicit-float','-Os','-c',ROOT/'tests/oem_board_io_arm.c','-o',out/'board.obj'])
  asm=run(['/usr/bin/llvm-objdump','-dr',out/'board.obj']);(out/'board.disassembly.txt').write_text(asm)
  for symbol in ['EnumaOemBoardRead','EnumaOemBoardWrite','EnumaOemBoardHold','EnumaOemBoardValidate']:
   assert '<'+symbol+'>:' in asm,symbol
  assert 'dsb' in asm
  host=out/'host-include';host.mkdir()
  header=(diag/'EnumaOemBoardIo.h').read_text();barrier='__asm__ volatile("dsb sy" ::: "memory");'
  assert header.count(barrier)==1
  (host/'EnumaOemBoardIo.h').write_text(header.replace(barrier,'__asm__ volatile("" ::: "memory");'))
  run(['clang','-I'+str(host)]+base[1:]+['-I'+str(inc/'X64'),'-I'+str(ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib'),'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',ROOT/'tests/oem_board_guards.c','-o',out/'board-guards'])
  run([out/'board-guards'])
  report['host_board_guards']='Only ARM barrier replaced in explicit host derivative; no physical read/write/barrier exercised'
  files=['firmware/diagnostics/EnumaOemIntegration.h','firmware/diagnostics/EnumaOemBoardIo.h','tests/oem_integration.c','tests/darwin_gop_contract.c','tests/oem_board_io_arm.c','tests/oem_service_trace.c','tests/oem_system_table_lifetime.c','tests/oem_board_guards.c','tests/oem_capture_pixel.c','out/sources/UniXNU/drivers/DarwinBoot/DarwinBootPkg/Driver/DarwinBoot.c','out/sources/UniXNU/drivers/DarwinBoot/DarwinBootPkg/Driver/BootVideo.h','out/sources/UniXNU/drivers/DarwinBoot/DarwinBootPkg/Driver/Entry.S']
  report['inputs']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files}
  report['passed']=True
 finally:(out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k not in ('commands','inputs')}))
if __name__=='__main__':main()
