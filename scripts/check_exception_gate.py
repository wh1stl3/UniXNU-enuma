"""Host-check actual global exception gate; no exception/driver attribution."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--firmware-root',type=Path,default=ROOT/'firmware')
    args=p.parse_args();header=args.firmware_root/'diagnostics/EnumaUnhandledExceptionCheckpoint.h'
    out=ROOT/'out/exception-gate-host';(out/'Library').mkdir(parents=True,exist_ok=True)
    for name in ('BaseLib.h','TimerLib.h','ResetSystemLib.h'):
        (out/'Library'/name).write_text('#pragma once\n#include <stdint.h>\ntypedef uintptr_t UINTN;\n#define STATIC static\n#define VOID void\n')
    cases=[(13,23,delay) for delay in (2000000,7000000)]+[(0,23,2000000),(12,23,2000000),(13,20,2000000),(13,13,2000000)]
    for i,(stage,point,delay) in enumerate(cases):
        command=['clang','-std=c11','-O1','-Wall','-Wextra','-Werror','-no-pie','-fsanitize=address,undefined',
            '-I'+str(out),'-DEXCEPTION_HEADER="'+str(header.resolve())+'"',
            '-DENUMA_DIAG_STAGE='+str(stage),'-DENUMA_DIAG_DETAIL_POINT='+str(point),
            '-DENUMA_DIAG_DELAY_US='+str(delay),str(ROOT/'tests/enuma_exception_gate.c'),'-o',str(out/('case-'+str(i)))]
        subprocess.run(command,check=True);subprocess.run([str(out/('case-'+str(i)))],check=True)
    (ROOT/'reports/enuma-exception-gate-host.json').write_text(json.dumps({
        'scope':'actual global header with host timer/reset adapters; no real exception or firmware execution',
        'header_sha256':hashlib.sha256(header.read_bytes()).hexdigest(),'cases':cases,
        'all_passed':True,'driver_attribution':False,'sanitizers':['address','undefined']},indent=2)+'\n')
    print('PASS: 6 global exception gate cases; 2/7 seconds and disabled/default stages')

if __name__=='__main__':main()
