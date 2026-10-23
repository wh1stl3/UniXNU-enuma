#include <assert.h>
#include <stdint.h>
#include <setjmp.h>
static jmp_buf stopped;
static unsigned delays,resets;
void MicroSecondDelay(uint64_t us) { assert(us==ENUMA_DIAG_DELAY_US);delays++; }
void ResetCold(void) { resets++; }
void CpuDeadLoop(void) { longjmp(stopped,1); }
#include EXCEPTION_HEADER
int main(void) {
    if(setjmp(stopped)==0) EnumaUnhandledExceptionCheckpoint();
    assert(delays==(ENUMA_DIAG_STAGE==13 && ENUMA_DIAG_DETAIL_POINT==23));
    assert(delays==resets);return 0;
}
