"""Run actual shared checkpoint header with host reset/delay adapters; no device I/O."""
import json
import subprocess
from pathlib import Path
from check_enuma_drivers import run
ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'out/stage-gate-test';(out/'Library').mkdir(parents=True,exist_ok=True)
    for name in ('BaseLib.h','ResetSystemLib.h','TimerLib.h'):
        (out/'Library'/name).write_text('#pragma once\n#include <stdint.h>\ntypedef uintptr_t UINTN;\n#define STATIC static\n#define VOID void\n')
    records=[]
    for stage in (0,3,4,5,6,7,8,9,10,11,12,13):
        command=['clang','-std=c11','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
          '-fno-pie','-no-pie','-I'+str(out),'-DENUMA_DIAG_STAGE='+str(stage),'-DENUMA_DIAG_DELAY_US=2000000',
          '-DSTAGE_HEADER="'+str(ROOT/'firmware/diagnostics/EnumaStageCheckpoint.h')+'"',
          ROOT/'tests/enuma_stage_gate.c','-o',out/('stage-'+str(stage))]
        records.append(run(command));records.append(run([out/('stage-'+str(stage))]))
    delayed=list(command)
    delayed[delayed.index('-DENUMA_DIAG_DELAY_US=2000000')]='-DENUMA_DIAG_DELAY_US=7000000'
    delayed[-1]=out/'stage-13-delay7'
    records.append(run(delayed));records.append(run([delayed[-1]]))
    command[command.index('-DENUMA_DIAG_STAGE=13')]='-DENUMA_DIAG_STAGE=2'
    result=subprocess.run([str(x) for x in command],capture_output=True,text=True)
    if result.returncode==0 or 'Unsupported enuma diagnostic stop stage' not in result.stderr:
        raise ValueError('unsupported stage was not rejected')
    (ROOT/'reports/enuma-stage-gates.json').write_text(json.dumps({'scope':'actual gate header with host adapters; not PSCI/firmware execution',
        'checks':records,'unsupported_stage_rejected':True},indent=2)+'\n')
    for point in (0,12,13):
        command=['clang','-std=c11','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
          '-fno-pie','-no-pie','-I'+str(out),'-DENUMA_DIAG_STAGE='+str(point),
          '-DENUMA_DIAG_DISPATCH_ORDINAL=3','-DENUMA_DIAG_DELAY_US=2000000',
          '-DDISPATCH_HEADER="'+str(ROOT/'firmware/diagnostics/EnumaDispatchCheckpoint.h')+'"',
          ROOT/'tests/enuma_dispatch_gate.c','-o',out/('dispatch-'+str(point))]
        records.append(run(command));records.append(run([out/('dispatch-'+str(point))]))
    (ROOT/'reports/enuma-dispatch-gates.json').write_text(json.dumps({'scope':'actual dispatcher header with host adapters; no firmware execution',
        'checks':records[-6:]},indent=2)+'\n')
    print('PASS: normal stage 0 never resets; stages 3..13 and dispatch ordinal selection; invalid stage rejected')


if __name__=='__main__':main()
