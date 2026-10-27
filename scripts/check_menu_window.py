"""Execute bounded menu window transactions on host RAM; never device I/O."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    lib=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib'
    commands=[];passed=False;error=None
    try:
        for argv in (["clang","-std=c11","-Wall","-Wextra","-Werror","-O1","-fsanitize=address,undefined","-fno-pie","-no-pie",
                      "-I"+str(lib),str(ROOT/'tests/menu_window.c'),"-o",str(out/'test')],[str(out/'test')]):
            p=subprocess.run(argv,text=True,capture_output=True,cwd=ROOT,timeout=60)
            commands.append(dict(argv=argv,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
            if p.returncode:raise ValueError(p.stdout+p.stderr)
        if '46 cases, 24 channel masks' not in commands[-1]['stdout']:raise ValueError('incomplete fault coverage')
        passed=True
    except Exception as exc:error=str(exc)
    files=[ROOT/'tests/menu_window.c',Path(__file__),lib/'MenuWindow.h',lib/'PixelTransaction.h',lib/'Evidence.h',lib/'InheritedScanout.h']
    report=dict(passed=passed,error=error,hardware_executed=False,commands=commands,
                sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                cases=46,channel_masks=24,whole_restore_after_partial_fault=True)
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=passed,error=error,output=str(out))));return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
