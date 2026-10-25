"""Test actual stage1 query algorithm on synthetic PAR data, compile actual Arm wrapper."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    lib=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib'
    out=ROOT/'out/cpu-stage1';out.mkdir(exist_ok=True)
    source=ROOT/'tests/native_cpu_stage1.c'
    common=['clang','-std=c11','-Wall','-Wextra','-Werror','-I'+str(lib)]
    subprocess.run([*common,'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',str(source),'-o',str(out/'test')],check=True)
    result=subprocess.check_output([str(out/'test')],text=True).strip();print(result)
    wrapper=out/'wrapper.c';wrapper.write_text('#include "CpuStage1.h"\nENUMA_U32 Probe(const ENUMA_INHERITED_FRAME *F) { return EnumaCpuStage1Arm(F); }\n')
    subprocess.run([*common,'--target=aarch64-none-elf','-ffreestanding','-O2','-c',str(wrapper),'-o',str(out/'wrapper.o')],check=True)
    dis=subprocess.check_output(['llvm-objdump','-d',str(out/'wrapper.o')],text=True);(out/'wrapper.disassembly.txt').write_text(dis)
    # Exact op selection and state preservation must also be manually reviewed
    # in the built, packaged provider; this only prevents toolchain omission.
    for op in ['s1e1r','s1e1w','s1e2r','s1e2w','PAR_EL1','DAIF','SCTLR_EL1','SCTLR_EL2','TCR_EL1','TCR_EL2','HCR_EL2','CurrentEL']:
        assert op.lower() in dis.lower(),op
    report=dict(scope='actual portable per-page algorithm with synthetic PAR and freestanding actual AArch64 wrapper; no hardware/data proof',result=result,
      sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,lib/'CpuStage1.h',lib/'InheritedScanout.h',Path(__file__)]},hardware_tested=False,physical_framebuffer_access=False)
    (ROOT/'reports/enuma-cpu-stage1-host.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
