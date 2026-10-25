"""Exercise real GOP backend and Mu Blt on host RAM, never device memory."""
import hashlib
import json
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
    common=['clang','-std=c11','-Wall','-Wextra','-Werror','-fno-builtin','-fshort-wchar','-DMDEPKG_NDEBUG',
            '-I'+str(pkg/'InheritedGopLib'),'-I'+str(pkg/'InheritedScanoutLib'),
            '-I'+str(core/'MdePkg/Include'),'-I'+str(core/'MdeModulePkg/Include')]
    host=[*common,'-I'+str(core/'MdePkg/Include/X64'),'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie']
    checks=[]
    for name,sources in [('gop',[backend,blt,ROOT/'tests/inherited_gop.c']),
                         ('topology',[topo,decode,ROOT/'tests/inherited_topology.c']),
                         ('evidence',[capture,topo,decode,evidence,ROOT/'tests/inherited_evidence.c'])]:
        checks.append(run([*host,*sources,'-o',out/name])); checks.append(run([out/name]))
        print(checks[-1]['stdout'].strip())
    for source in [backend,blt,topo,evidence]:
        checks.append(run([*common,'-I'+str(core/'MdePkg/Include/AArch64'),'-target','aarch64-none-elf','-ffreestanding','-O2','-c',source,'-o',out/(source.stem+'.o')]))
        checks.append(run(['llvm-nm','--undefined-only',out/(source.stem+'.o')]))
    report=dict(scope='actual GOP callbacks and actual pinned Mu FrameBufferBltLib on synthetic host RAM; modeled allocation/TPL/BaseLib primitives',
      checks=checks,sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [backend,blt,topo,decode,capture,evidence,ROOT/'tests/inherited_gop.c',ROOT/'tests/inherited_topology.c',ROOT/'tests/inherited_evidence.c']},
      hardware_tested=False,physical_framebuffer_access=False,protocol_published=False,
      unresolved=['same-boot PP/DSC/DSI downstream association','CPU/SMMU address relationship and uncached mapping','live stable activity/refresh/blend qualification'])
    (ROOT/'reports/enuma-inherited-gop-host.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__': main()
