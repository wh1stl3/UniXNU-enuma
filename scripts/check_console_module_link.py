"""Link the real late console application separately; never replace a diagnostic FD."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import uuid

ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();build=args.build.resolve();out=args.output.resolve()
    build.relative_to(ROOT/'out');out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    r=dict(passed=False,hardware_execution=False,packaged_in_fd=False,commands=[],inputs={})
    def bind(p): r['inputs'][str(p.relative_to(ROOT))]=sha(p)
    def run(cmd):
        p=subprocess.run(list(map(str,cmd)),cwd=out,text=True,capture_output=True)
        r['commands'].append(dict(argv=list(map(str,cmd)),returncode=p.returncode,stderr=p.stderr))
        if p.returncode: raise ValueError(p.stdout+p.stderr)
        return p.stdout
    try:
        bp=build/'build-result.json';b=json.loads(bp.read_text());assert b['complete'] and b['profile']=='diagnostic-log';bind(bp)
        fd=ROOT/b['fd'];assert sha(fd)==b['fd_sha256'];bind(fd)
        uefi=build/'work/uefi'
        app=uefi/'Platforms/Xiaomi/enumaPkg/Application/EnumaProbe'
        products=uefi/'Build/enumaPkg/DEBUG_CLANGPDB/AARCH64/enumaPkg/Application/EnumaProbe/EnumaProbe'
        cc=products/'OUTPUT/cc_resp.txt';flags=cc.read_text();bind(cc)
        assert flags.count('-DENUMA_DIAG_SIMPLEFB=1')==1
        assert '-DENUMA_PROBE_JOURNAL_REPLAY=1' in flags.split()
        flags=flags.replace('-DENUMA_DIAG_SIMPLEFB=1','-DENUMA_DIAG_SIMPLEFB=0')
        response=out/'cc_resp.txt';response.write_text(flags)
        # Same staged source, includes, AutoGen and libraries; only the existing
        # diagnostic early-return guard is disabled for this standalone module.
        for p in app.iterdir():
            if p.is_file():bind(p)
        bind(app.parent.parent/'Drivers/EnumaRamPayloadDxe/TransportReport.h')
        bind(products/'DEBUG/AutoGen.h');bind(products/'DEBUG/AutoGen.c')
        run(['clang','@'+str(response),'-mstrict-align','-c',app/'EnumaProbe.c','-o',out/'EnumaProbe.obj'])
        run(['clang','@'+str(response),'-mstrict-align','-c',products/'DEBUG/AutoGen.c','-o',out/'AutoGen.obj'])
        run(['llvm-lib','/OUT:'+str(out/'EnumaProbe.lib'),out/'EnumaProbe.obj',out/'AutoGen.obj'])
        libs=products/'OUTPUT/static_library_files.lst';bind(libs)
        paths=[Path(s) for s in libs.read_text().splitlines() if s.strip()]
        own=products/'OUTPUT/EnumaProbe.lib';assert paths.count(own)==1
        for p in paths:bind(p)
        linked=[out/'EnumaProbe.lib' if p==own else p for p in paths]
        (out/'libraries.txt').write_text('\n'.join(map(str,linked))+'\n')
        run(['lld-link','/OUT:'+str(out/'EnumaProbe.dll'),'/NOLOGO','/NODEFAULTLIB','/IGNORE:4001','/WX',
             '/OPT:REF','/OPT:ICF=10','/ALIGN:4096','/Machine:ARM64','/DLL','/DRIVER','/ENTRY:_ModuleEntryPoint',
             '/SUBSYSTEM:EFI_BOOT_SERVICE_DRIVER','/SAFESEH:NO','/BASE:0','/DEBUG:GHASH','/MLLVM:-exception-model=wineh',
             '/lldmap','@'+str(out/'libraries.txt')])
        genfw=build/'work/Mu_Basecore/BaseTools/Source/C/bin/GenFw';bind(genfw)
        run([genfw,'-e','UEFI_APPLICATION','-o',out/'EnumaProbe.efi',out/'EnumaProbe.dll','--keepexceptiontable'])
        data=(out/'EnumaProbe.efi').read_bytes()
        for label in ('DXE CACHED REPLAY %r','ENUMA PROBE 01 - UEFI, NOT XNU'):
            assert label.encode('utf-16le') in data,label
        assert uuid.UUID('a84039f7-b861-5dbe-9a09-a4f6cc746d5b').bytes_le in data
        mapping=(out/'EnumaProbe.map').read_text()
        # LTO inlines UniXNURun into EnumaProbeEntry; verify its retained menu
        # implementation plus the actual journal validation/session storage.
        for symbol in ('EnumaProbeEntry','UniXNUMenuRun','EnumaBootLogViewValid','mConsoleSnapshot','mConsoleSession'):
            assert symbol in mapping,symbol
        (out/'EnumaProbe.disassembly.txt').write_text(run(['llvm-objdump','-d','--print-imm-hex',out/'EnumaProbe.efi']))
        for name,h in r['inputs'].items():assert sha(ROOT/name)==h,name
        bind(Path(__file__))
        r.update(passed=True,pe_sha256=sha(out/'EnumaProbe.efi'),fd_unchanged=True,
                 scope='standalone real EnumaProbe/ConOut/UniXNULib PE link; diagnostic FD gate unchanged',
                 sole_profile_override={'ENUMA_DIAG_SIMPLEFB':'0'},
                 limitations=['not packaged or run on hardware','does not qualify production GOP or BDS connection'])
    except Exception as exc:
        import traceback
        r.update(error=repr(exc),traceback=traceback.format_exc())
    finally:
        (out/'result.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:r[k] for k in ('passed','error','pe_sha256') if k in r}))
    return 0 if r['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
