"""Exercise real GOP backend and Mu Blt on host RAM, never device memory."""
import hashlib
import json
import subprocess
from pathlib import Path
from check_enuma_drivers import run
ROOT=Path(__file__).resolve().parents[1]

def main():
    pkg=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library'
    core=ROOT/'firmware/Mu_Basecore'
    out=ROOT/'out/inherited-gop'; out.mkdir(exist_ok=True)
    backend=pkg/'InheritedGopLib/InheritedGop.c'
    blt=core/'MdeModulePkg/Library/FrameBufferBltLib/FrameBufferBltLib.c'
    topo=pkg/'InheritedScanoutLib/Topology.c'
    decode=pkg/'InheritedScanoutLib/Decode.c'
    capture=pkg/'InheritedScanoutLib/Capture.c'
    evidence=pkg/'InheritedScanoutLib/Evidence.c'
    video=pkg/'InheritedScanoutLib/VideoCapture.c'
    selector=pkg/'InheritedScanoutLib/VideoResult.h'
    common=['clang','-std=c11','-Wall','-Wextra','-Werror','-fno-builtin','-fshort-wchar','-DMDEPKG_NDEBUG',
            '-I'+str(pkg/'InheritedGopLib'),'-I'+str(pkg/'InheritedScanoutLib'),
            '-I'+str(core/'MdePkg/Include'),'-I'+str(core/'MdeModulePkg/Include')]
    host=[*common,'-I'+str(core/'MdePkg/Include/X64'),'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie']
    checks=[]
    baseline=out/'baseline-Evidence.c'
    baseline.write_bytes(subprocess.check_output(['git','-C',str(ROOT/'firmware'),'show','8710ebd93da7b19bb7ffd0e388f6925399231153:Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/Evidence.c']))
    checks.append(run([*[x for x in host if x!='-no-pie'],'-DEnumaSampleVideo=EnumaSampleVideoBaseline','-c',baseline,'-o',out/'baseline-Evidence.o']))
    for name,sources in [('gop',[backend,blt,ROOT/'tests/inherited_gop.c']),
                         ('topology',[topo,decode,ROOT/'tests/inherited_topology.c']),
                         ('evidence',[capture,video,topo,decode,evidence,ROOT/'tests/inherited_evidence.c',out/'baseline-Evidence.o']),
                         ('video-result',[ROOT/'tests/inherited_video_result.c'])]:
        checks.append(run([*host,*sources,'-o',out/name])); checks.append(run([out/name]))
        print(checks[-1]['stdout'].strip())
    for source in [backend,blt,topo,evidence,video]:
        checks.append(run([*common,'-I'+str(core/'MdePkg/Include/AArch64'),'-target','aarch64-none-elf','-ffreestanding','-O2','-c',source,'-o',out/(source.stem+'.o')]))
        checks.append(run(['llvm-nm','--undefined-only',out/(source.stem+'.o')]))
    wrapper=out/'video-result-freestanding.c'
    wrapper.write_text('#include "VideoResult.h"\nENUMA_U32 Select(ENUMA_U32 S,ENUMA_U32 R,ENUMA_U32 Q) { return EnumaVideoResult(S,R,Q); }\nENUMA_U32 Reason(ENUMA_U32 S,ENUMA_U32 R,ENUMA_U32 W,ENUMA_U32 T,ENUMA_U32 Q) { return EnumaVideoReasonResult(S,R,W,T,Q); }\n')
    checks.append(run([*common,'-I'+str(core/'MdePkg/Include/AArch64'),'-target','aarch64-none-elf','-ffreestanding','-O2','-c',wrapper,'-o',out/'VideoResult.o']))
    checks.append(run(['llvm-nm','--undefined-only',out/'VideoResult.o']))
    report=dict(scope='actual GOP callbacks and actual pinned Mu FrameBufferBltLib on synthetic host RAM; modeled allocation/TPL/BaseLib primitives',
      checks=checks,sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [backend,blt,topo,decode,capture,evidence,video,selector,ROOT/'tests/inherited_gop.c',ROOT/'tests/inherited_topology.c',ROOT/'tests/inherited_evidence.c',ROOT/'tests/inherited_video_result.c']},
      hardware_tested=False,physical_framebuffer_access=False,protocol_published=False,
      unresolved=['same-boot PP/DSC/DSI downstream association','CPU/SMMU address relationship and uncached mapping','live stable activity/refresh/blend qualification'])
    (ROOT/'reports/enuma-inherited-gop-host.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__': main()
