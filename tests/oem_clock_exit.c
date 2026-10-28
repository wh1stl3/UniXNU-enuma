#include <Uefi.h>
#include <assert.h>
#include <setjmp.h>
#include <Library/TimerLib.h>
#include <Library/ResetSystemLib.h>
#include <Library/BaseLib.h>
#include "EnumaOemExitClock.h"
static UINTN Last;static unsigned Resets,ReturnReset;static jmp_buf Jump;
UINTN EFIAPI MicroSecondDelay(UINTN N){Last=N;return N;}
VOID EFIAPI ResetCold(VOID){Resets++;if(!ReturnReset){longjmp(Jump,1);}}
VOID EFIAPI CpuPause(VOID){longjmp(Jump,2);}
int main(void){
  assert(EnumaOemClockClass(FALSE,TRUE,EFI_SUCCESS)==3);
  assert(EnumaOemClockClass(TRUE,FALSE,EFI_SUCCESS)==3);
  assert(EnumaOemClockClass(TRUE,TRUE,EFI_SUCCESS)==5);
  assert(EnumaOemClockClass(TRUE,TRUE,EFI_ABORTED)==4);
  assert(EnumaOemClockClass(TRUE,TRUE,EFI_WARN_UNKNOWN_GLYPH)==4);
  for(UINT32 C=0;C<8;C++){
    UINT32 Chosen=ENUMA_OEM_CLOCK_FORCE?ENUMA_OEM_CLOCK_FORCE:(C<1||C>ENUMA_OEM_CLOCK_MAX?2:C);
    assert(EnumaOemClockDelay(C)==2000000+5000000*(Chosen-1));
    Resets=ReturnReset=0;
    if(!setjmp(Jump)){EnumaOemClockExit(C);assert(0);}
    assert(Resets==1&&Last==EnumaOemClockDelay(C));
  }
  Resets=0;ReturnReset=1;
  assert(setjmp(Jump)!=1);if(!Resets){EnumaOemClockExit(2);assert(0);}
  assert(Resets==1);
  return 0;
}
