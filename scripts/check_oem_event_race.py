"""Reproduce the frozen v7 notification race and reject a deleted v8 hook."""
import argparse,hashlib,json,subprocess,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
 inc=ROOT/'firmware/Mu_Basecore/MdePkg/Include';fw=ROOT/'firmware/diagnostics'
 frozen=ROOT/'out/oem-far-chain-20261027/build2/source/diagnostics'
 names=['EnumaOemProgress.h','EnumaOemServiceTrace.h','EnumaOemServiceTraceView.h']
 runs=[]
 for mode in ['frozen-v7','fixed-v8','deleted-hook']:
  d=out/mode;d.mkdir()
  for name in names:shutil.copyfile((frozen if mode=='frozen-v7' else fw)/name,d/name)
  if mode=='deleted-hook':
   path=d/'EnumaOemServiceTrace.h';s=path.read_text();old='if(C->Recorded){C->Recorded(C,E);}'
   assert s.count(old)==1;path.write_text(s.replace(old,'/* mutation: no milestone delivery */'))
  cmd=['/usr/bin/clang','-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-function','-fshort-wchar','-fno-builtin','-DMDEPKG_NDEBUG',
       '-DENUMA_OEM_RAM_EVENT='+('0' if mode=='frozen-v7' else '1'),'-I'+str(d),'-I'+str(fw),'-I'+str(inc),'-I'+str(inc/'X64'),
       '-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',str(ROOT/'tests/oem_far_event.c'),'-o',str(d/'test')]
  c=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
  if c.returncode:raise ValueError(c.stderr)
  run=subprocess.run([d/'test'],capture_output=True,text=True,timeout=30)
  if (run.returncode==0)!=(mode!='deleted-hook'):raise ValueError(mode+': unexpected outcome '+run.stderr)
  runs.append(dict(mode=mode,returncode=run.returncode,stdout=run.stdout,stderr=run.stderr))
 sources=['scripts/check_oem_event_race.py','tests/oem_far_event.c','tests/oem_far_chain.c']+['firmware/diagnostics/'+n for n in names]
 result=dict(passed=True,hardware_root_cause_proven=False,runs=runs,
             sources={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in sources},
             frozen_v7_headers={n:hashlib.sha256((frozen/n).read_bytes()).hexdigest() for n in names})
 (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 print('PASS: frozen v7 race reproduced, fixed v8 under sanitizers, deleted hook rejected')
if __name__=='__main__':main()
