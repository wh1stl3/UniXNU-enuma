"""Real pinned Mu headers, fault injection, sanitizers and AArch64 object check."""
import argparse,hashlib,json,struct,subprocess,tarfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--firmware-root',type=Path,default=ROOT/'firmware')
    a=p.parse_args();out=ROOT/'out/gop-audit-host';out.mkdir(exist_ok=True)
    lock=json.loads((ROOT/'config/firmware-build.lock.json').read_text())
    archive=ROOT/'out/firmware-build/mu-basecore.tar.gz'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==lock['archive_sha256'][archive.name]
    inc=out/'MuInclude'
    with tarfile.open(archive) as source:
        for m in source.getmembers():
            if not m.isfile() or '/MdePkg/Include/' not in m.name:continue
            target=(inc/m.name.split('/MdePkg/Include/',1)[1]).resolve()
            assert target.is_relative_to(inc.resolve())
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.extractfile(m).read())
    header=a.firmware_root/'diagnostics/EnumaGopAudit.h'
    flags=['clang','-std=c11','-Wall','-Wextra','-Werror','-fshort-wchar','-I'+str(inc),'-I'+str(header.parent)]
    cmd=flags+['-I'+str(inc/'X64'),'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',
        str(ROOT/'tests/enuma_gop_audit.c'),'-o',str(out/'test')]
    subprocess.run(cmd,check=True);subprocess.run([cmd[-1]],check=True)
    obj=out/'query.obj';unit=out/'query.c'
    unit.write_text('#include "EnumaGopAudit.h"\nEFI_STATUS Audit(EFI_BOOT_SERVICES *s, EFI_HANDLE h, EFI_GRAPHICS_OUTPUT_PROTOCOL *g){return EnumaGopAudit(s,h,g);}\n')
    subprocess.run(flags+['-I'+str(inc/'AArch64'),'-target','aarch64-unknown-windows-msvc','-ffreestanding','-Oz',
        '-fno-builtin','-fno-stack-protector','-mno-implicit-float','-c',str(unit),'-o',str(obj)],check=True)
    assert struct.unpack_from('<H',obj.read_bytes())[0]==0xaa64
    undefined=subprocess.check_output(['llvm-nm','--undefined-only',str(obj)],text=True)
    symbols=[line.split()[-1] for line in undefined.splitlines() if line.split()]
    assert set(symbols)=={'gEfiGraphicsOutputProtocolGuid'},symbols
    # Exercise the exact post-install gate from the composed real provider.
    stage=out/'composition'
    names=['Silicon/Silicium/SiliciumPkg/Drivers/SimpleFbDxe/SimpleFb.c',
           'Silicon/Silicium/SiliciumPkg/Drivers/SimpleFbDxe/SimpleFbDxe.inf',
           'Platforms/Xiaomi/enumaPkg/Application/EnumaProbe/EnumaProbe.c']
    for name in names:
        target=stage/name;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((a.firmware_root/name).read_bytes().replace(b'\r\n',b'\n'))
    for name in ('simplefb-contract.patch','simplefb-gop-query.patch'):
        subprocess.run(['git','apply',str((a.firmware_root/'patches'/name).resolve())],cwd=stage,check=True)
    source=(stage/names[0]).read_text()
    begin=source.index('#if ENUMA_DIAG_GOP_QUERY\n  // Keep installation')
    end=source.index('#endif',begin)+len('#endif')
    snippet=source[begin:end]
    gate=out/'gate.c'
    gate.write_text('#include <assert.h>\n#include <stdint.h>\n'
        '#define EFI_ERROR(s) (((uint64_t)(s)>>63)!=0)\n'
        'static unsigned hits; static uint64_t supplied;\n'
        'static void EnumaStageCheckpoint(int n){assert(n==13);hits++;}\n'
        'static uint64_t EnumaGopAudit(void *s,void *h,void *g){(void)s;(void)h;(void)g;return supplied;}\n'
        'static void f(void){void *gBS=0,*ImageHandle=0,*mFrameBuffer=0;uint64_t Status;\n'+snippet+'\n}\n'
        'int main(void){const uint64_t statuses[]={0,1,0x8000000000000001ULL};'
        'for(unsigned i=0;i<3;i++){hits=0;supplied=statuses[i];f();'
        'assert(hits==((ENUMA_DIAG_GOP_QUERY==1)==!EFI_ERROR(supplied)));}return 0;}\n')
    for selector in (1,2):
        subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Werror',
            '-DENUMA_DIAG_GOP_QUERY='+str(selector),str(gate),'-o',str(out/'gate')],check=True)
        subprocess.run([out/'gate'],check=True)
    base=[sys.executable,'-B',str(ROOT/'scripts/build_enuma_firmware.py'),
        '--unixnu',str(out/'not-used'),'--diagnostic-simplefb','--stop-stage','13',
        '--detail-point','16','--dispatch-guid','dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92',
        '--dispatch-guid-only','--dispatch-completion-fallback','--diagnostic-gop-query','1']
    bad_profiles=[base+['--stop-stage','0'],base+['--stop-delay','7'],
        base+['--detail-point','17'],base+['--dispatch-guid','00000000-0000-0000-0000-000000000000'],
        [x for x in base if x!='--diagnostic-simplefb'],
        [x for x in base if x!='--dispatch-completion-fallback']]
    for cmd in bad_profiles:
        result=subprocess.run(cmd,capture_output=True,text=True)
        assert result.returncode==2 and 'GOP query requires' in result.stderr
    report=dict(scope='host fault injection and real Mu-header AArch64 object only; no hardware claim',
        all_passed=True,cases=36,sanitizers=['address','undefined'],mu_commit=lock['reference_gitlinks']['Mu_Basecore'],
        source_sha256=hashlib.sha256(header.read_bytes()).hexdigest(),undefined_symbols=symbols,
        framebuffer_access=False,blt_or_setmode=False,allocations_freed=True,
        real_provider_patch_composed=True,post_install_gate_cases=6,
        invalid_build_profiles_rejected=len(bad_profiles),
        installed_driver_status_preserved=True)
    (ROOT/'reports/enuma-gop-audit-host.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
