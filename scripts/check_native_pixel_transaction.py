"""Model the exact transaction and compile actual Arm I/O wrapper; no device."""
from pathlib import Path
import hashlib,json,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'out/pixel-transaction';out.mkdir(exist_ok=True)
    lib=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib';diag=ROOT/'firmware/diagnostics';core=ROOT/'firmware/Mu_Basecore'
    test=ROOT/'tests/native_pixel_transaction.c';header=lib/'PixelTransaction.h';arm=diag/'EnumaPixelTransactionArm.h'
    includes=out/'InheritedVideo';includes.mkdir(exist_ok=True)
    for name in ['PixelTransaction.h','Evidence.h','Topology.h','InheritedScanout.h']:
        shutil.copyfile(lib/name,includes/name)
    common=['clang','-std=c11','-Wall','-Wextra','-Werror','-I'+str(lib)]
    subprocess.run([*common,'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',str(test),'-o',str(out/'test')],check=True)
    result=subprocess.check_output([str(out/'test')],text=True).strip();print(result)
    wrapper=out/'arm-wrapper.c'
    wrapper.write_text('#include <Uefi.h>\n#include <Library/UefiBootServicesTableLib.h>\n#include "Evidence.h"\nstatic ENUMA_VIDEO_EVIDENCE mEvidence;\nextern int Read(void *,ENUMA_U32,ENUMA_U32 *);\nextern int Wait(void *,ENUMA_U32);\n#include "EnumaPixelTransactionArm.h"\nENUMA_U32 Probe(const ENUMA_INHERITED_FRAME *F,ENUMA_U32 P,ENUMA_U64 El) { return PixelArmProbe(F,P,El); }\n')
    subprocess.run([*common,'-I'+str(out),'-I'+str(diag),'-I'+str(core/'MdePkg/Include'),'-I'+str(core/'MdePkg/Include/AArch64'),'-target','aarch64-none-elf','-ffreestanding','-fshort-wchar','-O2','-c',str(wrapper),'-o',str(out/'arm-wrapper.o')],check=True)
    dis=subprocess.check_output(['llvm-objdump','-d',str(out/'arm-wrapper.o')],text=True);(out/'arm-wrapper.disassembly.txt').write_text(dis)
    report=dict(scope='actual portable transaction on symbolic9c addresses backed by host arrays, callback failures and actual freestanding Arm wrapper compilation; no hardware',result=result,
      hardware_tested=False,pixel_writes_on_device=False,
      sources={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [header,arm,lib/'Evidence.h',lib/'Topology.h',lib/'InheritedScanout.h',test,Path(__file__)]})
    (ROOT/'reports/enuma-pixel-transaction-host.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
