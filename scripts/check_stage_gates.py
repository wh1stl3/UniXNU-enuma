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
    for stage in (0,3,4,5,6,7,8,9,10):
        command=['clang','-std=c11','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
          '-fno-pie','-no-pie','-I'+str(out),'-DENUMA_DIAG_STAGE='+str(stage),
          '-DSTAGE_HEADER="'+str(ROOT/'firmware/diagnostics/EnumaStageCheckpoint.h')+'"',
          ROOT/'tests/enuma_stage_gate.c','-o',out/('stage-'+str(stage))]
        records.append(run(command));records.append(run([out/('stage-'+str(stage))]))
    command[command.index('-DENUMA_DIAG_STAGE=10')]='-DENUMA_DIAG_STAGE=2'
    result=subprocess.run([str(x) for x in command],capture_output=True,text=True)
    if result.returncode==0 or 'Unsupported enuma diagnostic stop stage' not in result.stderr:
        raise ValueError('unsupported stage was not rejected')
    (ROOT/'reports/enuma-stage-gates.json').write_text(json.dumps({'scope':'actual gate header with host adapters; not PSCI/firmware execution',
        'checks':records,'unsupported_stage_rejected':True},indent=2)+'\n')
    print('PASS: normal stage 0 never resets; stages 3..10 each stop only at their target; invalid stage rejected')


if __name__=='__main__':main()
