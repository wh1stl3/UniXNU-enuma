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
    names=['oem_progress','oem_capture_pixel','oem_precall_capture','oem_service_trace']
    result=dict(passed=False,commands=commands,hardware_executed=False)
    try:
        for name in names:
            for argv in (flags+[str(ROOT/'tests'/f'{name}.c'),'-o',str(out/name)],[str(out/name)]):
                r=subprocess.run(argv,capture_output=True,text=True,timeout=90)
                commands.append(dict(argv=argv,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
                if r.returncode:raise ValueError(r.stderr+r.stdout)
        result['passed']=True
    finally:
        files=[f'tests/{n}.c' for n in names]+['scripts/check_oem_progress.py']
        files += ['firmware/diagnostics/'+n for n in ('EnumaOemProgress.h','EnumaOemProgressPage.h','EnumaOemServiceTrace.h','EnumaOemPrecallCapture.h','EnumaOemCapturePixel.h','EnumaOemBoardCapture.h','EnumaOemCoreBinding.h')]
        result['sources']={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in files}
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: progress state machine and existing pixel/precall/service regressions under ASan/UBSan')
if __name__=='__main__':main()
