"""Host emulation of the actual R-017 stage header, no device operations."""
import hashlib
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'out/ramoops-audit/canary-host'; (out/'Library').mkdir(parents=True,exist_ok=True)
    (out/'Base.h').write_text('''#ifndef TEST_BASE_H
#define TEST_BASE_H
#include <stdint.h>
#include <stddef.h>
#define STATIC static
#define IN
#define CONST const
#define VOID void
#define STATIC_ASSERT _Static_assert
#define OFFSET_OF offsetof
typedef uint8_t UINT8;
typedef uint32_t UINT32;
typedef uintptr_t UINTN;
typedef unsigned char BOOLEAN;
#endif
''')
    (out/'Library/BaseLib.h').write_text('''#ifndef TEST_BASELIB_H
#define TEST_BASELIB_H
#include <Base.h>
static inline void MemoryFence(void) { __atomic_thread_fence(__ATOMIC_SEQ_CST); }
BOOLEAN SaveAndDisableInterrupts(void);
BOOLEAN SetInterruptState(BOOLEAN value);
void CpuDeadLoop(void);
#endif
''')
    (out/'Library/ResetSystemLib.h').write_text('void ResetWarm(void);\nvoid ResetCold(void);\n')
    (out/'Library/TimerLib.h').write_text('void MicroSecondDelay(UINTN);\n')
    flags=['-DENUMA_RAMOOPS_CANARY=1','-DENUMA_DIAG_STAGE=10','-DENUMA_DIAG_DELAY_US=2000000']
    flags+=['-DENUMA_RAMOOPS_NONCE_'+str(i)+'='+('0x01234567U' if i%2==0 else '0x89abcdefU') for i in range(4)]
    command=['clang','-std=c11','-D_GNU_SOURCE','-Wall','-Wextra','-Werror','-fsanitize=undefined',
             '-I',str(out),*flags,str(ROOT/'tests/ramoops_canary_test.c'),'-o',str(out/'canary-test')]
    subprocess.run(command,check=True)
    result=subprocess.check_output([str(out/'canary-test')],text=True).strip()
    report=dict(scope='host virtual RAM emulation; no physical memory or hardware execution',result=result,
                sanitizers=['undefined'],command=command,
                sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [
                 'firmware/diagnostics/EnumaRamoopsCanary.h','firmware/diagnostics/EnumaRamoopsStageCheckpoint.h',
                 'tests/ramoops_canary_test.c','scripts/test_ramoops_canary.py']})
    (ROOT/'reports/enuma-ramoops-canary-host.json').write_text(json.dumps(report,indent=2)+'\n')
    print(result)
if __name__=='__main__':main()
