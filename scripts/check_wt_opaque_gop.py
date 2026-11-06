"""New-source WT/opaque GOP tests; separate output, no board build or device."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    out=args.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    commands=[];passed=False;error=None
    def run(argv):
        r=subprocess.run(list(map(str,argv)),capture_output=True,text=True,cwd=ROOT)
        commands.append(dict(argv=list(map(str,argv)),returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
        if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    lib=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedGopLib';core=ROOT/'firmware/Mu_Basecore';inc=core/'MdePkg/Include'
    backend=lib/'InheritedGop.c';blt=core/'MdeModulePkg/Library/FrameBufferBltLib/FrameBufferBltLib.c'
    sources=[backend,blt,ROOT/'tests/inherited_gop.c',ROOT/'tests/wt_opaque_gop.c',*lib.glob('*.h')]
    try:
        support=(ROOT/'tests/inherited_gop.c').read_text().split('int main(void) {')[0]
        (out/'GopTestSupport.h').write_text(support)
        common=['clang','-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-function','-fshort-wchar','-fno-builtin','-DMDEPKG_NDEBUG',
                '-I'+str(lib),'-I'+str(out),'-I'+str(inc),'-I'+str(core/'MdeModulePkg/Include')]
        host=common+['-I'+str(inc/'X64'),'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie']
        for name,test in [('mu-regression','inherited_gop.c'),('wt-opaque','wt_opaque_gop.c')]:
            run(host+[ROOT/'tests'/test,backend,blt,'-o',out/name]);run([out/name])
        blend=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/OpaqueBlend.h'
        sources.extend([blend,ROOT/'tests/opaque_blend.c'])
        run(host+['-I'+str(blend.parent),ROOT/'tests/opaque_blend.c','-o',out/'opaque-blend']);run([out/'opaque-blend'])
        for source in [backend,lib/'InheritedGopPublish.c']:
            sources.append(source);run(common+['-I'+str(inc/'AArch64'),'-target','aarch64-none-elf','-ffreestanding','-O2','-c',source,'-o',out/(source.stem+'.o')])
        wrapper=out/'arm-access.c';wrapper.write_text('#include "InheritedGopWtArm.h"\nENUMA_GOP_ACCESS Access(ENUMA_GOP_WT_WINDOW *W) { return EnumaWtAccess(W); }\n')
        run(common+['-I'+str(inc/'AArch64'),'-target','aarch64-none-elf','-ffreestanding','-O2','-c',wrapper,'-o',out/'arm-access.o'])
        run(['llvm-objdump','-d',out/'arm-access.o'])
        assert 'dsb\tsy' in commands[-1]['stdout'] or 'dsb sy' in commands[-1]['stdout']
        passed=True
    except Exception as exc:error=str(exc)
    sources.append(Path(__file__))
    result=dict(passed=passed,error=error,commands=commands,sources={str(s.relative_to(ROOT)):hashlib.sha256(s.read_bytes()).hexdigest() for s in sources},
                scope='host ASan/UBSan on RAM and actual AArch64 volatile/DSB access objects; no real mapping or blend verification',
                device_action=False,requirements_cleared=False,hardware_qualified=False)
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=passed,error=error,commands=len(commands))))
    return 0 if passed else 1
if __name__=='__main__':sys.exit(main())
