// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <setjmp.h>
#include <stdint.h>
#include <stdio.h>
static unsigned delay_calls,reset_calls;
static jmp_buf reset_returned;
void MicroSecondDelay(uint64_t us) {assert(us==ENUMA_DIAG_DELAY_US);++delay_calls;}
void ResetCold(void) {++reset_calls;}
void CpuDeadLoop(void) {longjmp(reset_returned,1);}
#include STAGE_HEADER
int main(void) {
    for(unsigned stage=3;stage<=13;++stage) {
        unsigned before=reset_calls;
        if(setjmp(reset_returned)==0)EnumaStageCheckpoint(stage);
        assert(reset_calls-before==(ENUMA_DIAG_STAGE!=0 && stage==ENUMA_DIAG_STAGE));
    }
    assert(reset_calls==(ENUMA_DIAG_STAGE!=0));
    assert(delay_calls==reset_calls);
    printf("PASS: diagnostic stage %d selection, delay and no fall-through\n",ENUMA_DIAG_STAGE);
    return 0;
}
