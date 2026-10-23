// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <stdint.h>
#include <setjmp.h>
static unsigned delays, resets, fallthrough;
static jmp_buf stopped;
void MicroSecondDelay(uint64_t us) { assert(us==7000000); ++delays; }
void ResetCold(void) { ++resets; }
void CpuDeadLoop(void) { longjmp(stopped,1); }
#include COMPLETION_HEADER
int main(void) {
    // Compile and exercise both original stage function and completion hook.
    EnumaStageCheckpoint(0);
    assert(delays==0 && resets==0);
    if(setjmp(stopped)==0) { EnumaDispatchCompletionCheckpoint(); ++fallthrough; }
    assert(resets==ENUMA_DIAG_DISPATCH_FALLBACK);
    assert(delays==resets);
    assert(fallthrough==!ENUMA_DIAG_DISPATCH_FALLBACK);
    return 0;
}
