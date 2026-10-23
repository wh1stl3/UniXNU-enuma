"""Check the actual pool search header; adapters allocate/log nothing under lock."""
import argparse, hashlib, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--firmware-root',type=Path,default=ROOT/'firmware');a=p.parse_args()
    header=a.firmware_root/'diagnostics/EnumaPoolSearchCheckpoint.h';out=ROOT/'out/pool-gate-host';(out/'Library').mkdir(parents=True,exist_ok=True)
    adapter='#pragma once\n#include <stdint.h>\ntypedef uintptr_t UINTN;\ntypedef uint64_t UINT64;\n#define STATIC static\n#define VOID void\n'
    for n in ('BaseLib.h','TimerLib.h','ResetSystemLib.h'):(out/'Library'/n).write_text(adapter)
    cases=[(13,point,start,delay) for point in (26,27) for start in (0,4096,2**64-1) for delay in (2000000,7000000)]
    cases += [(0,26,0,2000000),(12,27,4096,2000000),(13,13,0,2000000),(13,23,0,2000000),(13,24,4096,2000000)]
    for i,(stage,point,start,delay) in enumerate(cases):
        cmd=['clang','-std=c11','-O1','-Wall','-Wextra','-Werror','-no-pie','-fsanitize=address,undefined','-I'+str(out),
             '-DPOOL_HEADER="'+str(header.resolve())+'"','-DENUMA_DIAG_STAGE='+str(stage),'-DENUMA_DIAG_DETAIL_POINT='+str(point),
             '-DENUMA_DIAG_DELAY_US='+str(delay),'-DTEST_START='+str(start)+'ULL',str(ROOT/'tests/enuma_pool_gate.c'),'-o',str(out/('case-'+str(i)))]
        subprocess.run(cmd,check=True);subprocess.run([cmd[-1]],check=True)
    (ROOT/'reports/enuma-pool-gate-host.json').write_text(json.dumps(dict(scope='actual global pool header with host Timer/PSCI adapters; not real allocation or hardware',header_sha256=hashlib.sha256(header.read_bytes()).hexdigest(),cases=cases,all_passed=True,driver_attribution=False,sanitizers=['address','undefined']),indent=2)+'\n')
    print('PASS: 17 actual pool-header cases; result branches, 2/7 delays, disabled stages and held-lock adapters')
if __name__=='__main__':main()
