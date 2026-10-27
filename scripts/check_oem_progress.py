"""Offline progression and pixel failure tests; no hardware success claim."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    inc=ROOT/'firmware/Mu_Basecore/MdePkg/Include';commands=[]
    flags=['/usr/bin/clang','-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-function','-fshort-wchar','-fno-builtin','-DMDEPKG_NDEBUG',
        '-I'+str(inc),'-I'+str(inc/'X64'),'-I'+str(ROOT/'firmware/diagnostics'),
        '-I'+str(ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib'),
        '-O1','-fsanitize=address,undefined','-fno-pie','-no-pie']
    names=['oem_progress','oem_capture_pixel','oem_precall_capture','oem_service_trace','oem_system_table_lifetime','oem_registration']
    result=dict(passed=False,commands=commands,hardware_executed=False)
    try:
        for name in names:
            for argv in (flags+[str(ROOT/'tests'/f'{name}.c'),'-o',str(out/name)],[str(out/name)]):
                r=subprocess.run(argv,capture_output=True,text=True,timeout=90)
                commands.append(dict(argv=argv,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
                if r.returncode:raise ValueError(r.stderr+r.stdout)
        for argv in (flags+['-DENUMA_OEM_EARLY=1',str(ROOT/'tests/oem_progress.c'),'-o',str(out/'oem_early')],[str(out/'oem_early')]):
            r=subprocess.run(argv,capture_output=True,text=True,timeout=90)
            commands.append(dict(argv=argv,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
            if r.returncode:raise ValueError(r.stderr+r.stdout)
        for argv in (flags+['-DENUMA_OEM_POST_KERNEL=1',str(ROOT/'tests/oem_progress.c'),'-o',str(out/'oem_post')],[str(out/'oem_post')]):
            r=subprocess.run(argv,capture_output=True,text=True,timeout=90)
            commands.append(dict(argv=argv,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
            if r.returncode:raise ValueError(r.stderr+r.stdout)
        source=ROOT/'firmware/Mu_Basecore/MdeModulePkg/Core/Dxe/Misc/InstallConfigurationTable.c'
        relative=Path('MdeModulePkg/Core/Dxe/Misc/InstallConfigurationTable.c')
        staged=out/relative;staged.parent.mkdir(parents=True);staged.write_text(source.read_text())
        subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(ROOT/'firmware/patches/oem-system-table-sync.patch')],cwd=out,check=True)
        staged.write_text(staged.read_text().replace('#include "DxeMain.h"','#include "oem_system_table_core_fixture.h"'))
        for argv in (flags+['-I'+str(ROOT/'tests'),str(ROOT/'tests/oem_system_table_core.c'),str(staged),'-o',str(out/'system_core')],[str(out/'system_core')]):
            r=subprocess.run(argv,capture_output=True,text=True,timeout=90)
            commands.append(dict(argv=argv,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
            if r.returncode:raise ValueError(r.stderr+r.stdout)
        patched=staged.read_text();negative=[]
        for label,old,new in (
            ('before-free','EnumaOemCoreSyncSystemTable (gDxeCoreST);\n        CoreFreePool','CoreFreePool'),
            ('before-notify','EnumaOemCoreSyncSystemTable (gDxeCoreST);\n  CoreNotifySignalList','CoreNotifySignalList')):
            if old not in patched:raise ValueError('missing sync site '+label)
            mutated=out/(label+'.c');mutated.write_text(patched.replace(old,new))
            exe=out/(label+'-negative')
            subprocess.run(flags+['-I'+str(ROOT/'tests'),str(ROOT/'tests/oem_system_table_core.c'),str(mutated),'-o',str(exe)],check=True)
            r=subprocess.run([str(exe)],capture_output=True,text=True,timeout=90)
            if not r.returncode:raise ValueError('missing sync admitted: '+label)
            negative.append(dict(site=label,returncode=r.returncode,stderr=r.stderr))
        result['sync_deletion_checks']=negative
        result['passed']=True
    finally:
        files=['tests/oem_system_table_core.c','tests/oem_system_table_core_fixture.h','firmware/patches/oem-system-table-sync.patch','firmware/Mu_Basecore/MdeModulePkg/Core/Dxe/Misc/InstallConfigurationTable.c']+[f'tests/{n}.c' for n in names]+['scripts/check_oem_progress.py']
        files += ['firmware/diagnostics/'+n for n in ('EnumaOemServiceTraceView.h','EnumaOemProgress.h','EnumaOemProgressPage.h','EnumaOemServiceTrace.h','EnumaOemPrecallCapture.h','EnumaOemCapturePixel.h','EnumaOemBoardCapture.h','EnumaOemCoreBinding.h')]
        result['sources']={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in files}
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: progress state machine and existing pixel/precall/service regressions under ASan/UBSan')
if __name__=='__main__':main()
