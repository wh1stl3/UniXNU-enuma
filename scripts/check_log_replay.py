"""Actual page/transaction host tests and target Arm wrapper, no device."""
from pathlib import Path
import json,hashlib,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'out/log-replay-tests';out.mkdir(exist_ok=True)
 lib=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib';diag=ROOT/'firmware/diagnostics'
 edk=ROOT/'out/firmware-build/Mu_Basecore/MdePkg/Include'
 for n in ('EnumaBootJournal.h','EnumaBootJournalProtocol.h'):shutil.copyfile(diag/n,out/n)
 # Pinned Uefi headers need AArch64 ABI; host journal shim supplies equivalent scalar/GUID layout only.
 shim=ROOT/'out/boot-journal-tests'
 common=['clang','-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-function','-I'+str(lib),'-I'+str(out)]
 source=ROOT/'tests/native_log_replay.c'
 subprocess.run(common+['-I'+str(shim),'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',str(source),'-o',str(out/'test')],check=True)
 result=subprocess.check_output([str(out/'test')],text=True,cwd=out).strip();print(result)
 subprocess.run(common+['-I'+str(shim),'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie','-DENUMA_BOOT_LOG_HOLD_US=8000000','-DENUMA_EXPECT_HOLD_US=8000000',str(source),'-o',str(out/'test8')],check=True)
 result8=subprocess.check_output([str(out/'test8')],text=True,cwd=out).strip();print(result8)
 includes=out/'InheritedVideo';includes.mkdir(exist_ok=True)
 for n in ['PixelTransaction.h','PixelText.h','PixelLogPage.h','Evidence.h','Topology.h','InheritedScanout.h']:shutil.copyfile(lib/n,includes/n)
 wrapper=out/'arm.c'
 wrapper.write_text('#include <Uefi.h>\n#include <Library/UefiBootServicesTableLib.h>\n#include "Evidence.h"\nstatic ENUMA_VIDEO_EVIDENCE mEvidence;\nextern int Read(void *,ENUMA_U32,ENUMA_U32 *);\nextern int Wait(void *,ENUMA_U32);\n#include "EnumaPixelTransactionArm.h"\nENUMA_U32 Probe(const ENUMA_INHERITED_FRAME *F,ENUMA_U32 P,ENUMA_U64 El,const ENUMA_BOOT_LOG *L) { if(!EnumaLogPageFromSnapshot(L,&mEnumaLogPage)) return 1;return PixelArmProbe(F,P,El); }\n')
 cmd=common+['-I'+str(diag),'-I'+str(edk),'-I'+str(edk/'AArch64'),'-DENUMA_BOOT_LOG_REPLAY=1','-target','aarch64-none-elf','-ffreestanding','-fshort-wchar','-fstack-usage','-O2','-c',str(wrapper),'-o',str(out/'arm.o')]
 subprocess.run(cmd,check=True)
 stack=(out/'arm.su').read_text();assert max(int(line.split('\t')[1]) for line in stack.splitlines())<131072,stack
 cmd8=cmd[:-2]+['-DENUMA_BOOT_LOG_HOLD_US=8000000','-o',str(out/'arm8.o')]
 subprocess.run(cmd8,check=True)
 stack8=(out/'arm8.su').read_text();assert max(int(line.split('\t')[1]) for line in stack8.splitlines())<131072,stack8
 sources=[source,Path(__file__),diag/'EnumaBootJournal.h',diag/'EnumaBootJournalProtocol.h',diag/'EnumaPixelTransactionArm.h',lib/'PixelTransaction.h',lib/'PixelLogPage.h']
 (ROOT/'reports/enuma-log-replay-host.json').write_text(json.dumps(dict(scope='page and transaction host ASan/UBSan plus actual EDK Arm callbacks; not hardware',result=result,hold8_result=result8,hold_durations_us_tested=[2000000,8000000],arm_command=cmd,arm8_command=cmd8,stack_usage=stack,stack8_usage=stack8,hardware_executed=False,sources={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}),indent=2)+'\n')
 print('PASS: pinned EDK Arm wrapper, total reported stack frame below128KiB')
if __name__=='__main__':main()
