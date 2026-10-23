// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <stdint.h>
#include <setjmp.h>
static jmp_buf stopped;
static unsigned delays, resets;
static int memory_lock_held = 1;
void MicroSecondDelay(uint64_t us) { assert(memory_lock_held && us==ENUMA_DIAG_DELAY_US);delays++; }
void ResetCold(void) { assert(memory_lock_held);resets++; }
void CpuDeadLoop(void) { longjmp(stopped,1); }
#include POOL_HEADER
int main(void) {
    const uint64_t start=TEST_START;
    if(setjmp(stopped)==0) EnumaPoolSearchCheckpoint(start);
    const unsigned expected=ENUMA_DIAG_STAGE==13 &&
        ((ENUMA_DIAG_DETAIL_POINT==26 && start==0) || (ENUMA_DIAG_DETAIL_POINT==27 && start!=0));
    assert(delays==expected && resets==expected && memory_lock_held);
    assert(start==TEST_START);return 0;
}
