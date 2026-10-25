"""Test actual stage1 query algorithm on synthetic PAR data, compile actual Arm wrapper."""
import hashlib,json,subprocess,re
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
    subprocess.run([*common,'--target=aarch64-none-elf','-ffreestanding','-O2','-DENUMA_NATIVE_ROUTE_CPU_ATTRIBUTE=1','-c',str(wrapper),'-o',str(out/'attribute-wrapper.o')],check=True)
    attribute_dis=subprocess.check_output(['llvm-objdump','-d',str(out/'attribute-wrapper.o')],text=True)
    (out/'attribute-wrapper.disassembly.txt').write_text(attribute_dis)
    for op in ['s1e1r','s1e1w','s1e2r','s1e2w','PAR_EL1','DAIF','SCTLR_EL1','SCTLR_EL2','TCR_EL1','TCR_EL2','HCR_EL2','CurrentEL']:
        assert op.lower() in attribute_dis.lower(),op
    subprocess.run([*common,'--target=aarch64-none-elf','-ffreestanding','-O2','-DENUMA_NATIVE_ROUTE_CPU_POLICY=1','-c',str(wrapper),'-o',str(out/'policy-wrapper.o')],check=True)
    policy_dis=subprocess.check_output(['llvm-objdump','-d',str(out/'policy-wrapper.o')],text=True)
    (out/'policy-wrapper.disassembly.txt').write_text(policy_dis)
    for op in ['s1e1r','s1e1w','s1e2r','s1e2w','PAR_EL1','DAIF','SCTLR_EL1','SCTLR_EL2','TCR_EL1','TCR_EL2','HCR_EL2','CurrentEL']:
        assert op.lower() in policy_dis.lower(),op
    read_wrapper=out/'read-wrapper.c'
    read_wrapper.write_text('#include "CpuStage1.h"\nENUMA_U32 Probe(const ENUMA_INHERITED_FRAME *F) { return EnumaCpuReadArmProbe(F,EnumaCpuStage1Arm(F)); }\n')
    subprocess.run([*common,'--target=aarch64-none-elf','-ffreestanding','-O2','-DENUMA_NATIVE_ROUTE_CPU_POLICY=1','-DENUMA_NATIVE_ROUTE_CPU_READ=1','-c',str(read_wrapper),'-o',str(out/'read-wrapper.o')],check=True)
    read_dis=subprocess.check_output(['llvm-objdump','-d',str(out/'read-wrapper.o')],text=True)
    (out/'read-wrapper.disassembly.txt').write_text(read_dis)
    assert not re.search(r'\bldr\s+wzr\s*,',read_dis,re.I),'data word must feed private volatile CPU-stack sink'
    subprocess.run([*common,'--target=aarch64-none-elf','-ffreestanding','-O2','-DENUMA_NATIVE_ROUTE_CPU_POLICY=1','-DENUMA_NATIVE_ROUTE_CPU_READ=1','-DENUMA_NATIVE_ROUTE_CPU_BARRIER=1','-c',str(read_wrapper),'-o',str(out/'barrier-wrapper.o')],check=True)
    barrier_dis=subprocess.check_output(['llvm-objdump','-d',str(out/'barrier-wrapper.o')],text=True)
    (out/'barrier-wrapper.disassembly.txt').write_text(barrier_dis)
    assert len(re.findall(r'\bdsb\s+sy\b',barrier_dis,re.I))==1
    assert not re.search(r'\bldr\s+wzr\s*,',barrier_dis,re.I)
    report=dict(scope='actual portable per-page algorithm with synthetic PAR and freestanding actual AArch64 wrapper; no hardware/data proof',result=result,
      sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,lib/'CpuStage1.h',lib/'InheritedScanout.h',Path(__file__)]},hardware_tested=False,physical_framebuffer_access=False)
    (ROOT/'reports/enuma-cpu-stage1-host.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
