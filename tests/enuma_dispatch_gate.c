// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <setjmp.h>
#include <stdint.h>
static unsigned resets, delays;
static jmp_buf stopped;
void MicroSecondDelay(uint64_t us) { assert(us == ENUMA_DIAG_DELAY_US); ++delays; }
void ResetCold(void) { ++resets; }
void CpuDeadLoop(void) { longjmp(stopped, 1); }
#include DISPATCH_HEADER
int main(void) {
    for (unsigned ordinal = 1; ordinal <= 6; ++ordinal) {
        for (unsigned point = 12; point <= 13; ++point) {
            unsigned before = resets;
            if (setjmp(stopped) == 0) EnumaDispatchCheckpoint(point);
            assert(resets - before == (ENUMA_DIAG_STAGE == point && ordinal == ENUMA_DIAG_DISPATCH_ORDINAL));
        }
    }
    assert(resets == (ENUMA_DIAG_STAGE != 0));
    assert(delays == resets);
    assert(EnumaDispatchOrdinal == (ENUMA_DIAG_STAGE == 0 ? 0 : 6));
    return 0;
}
