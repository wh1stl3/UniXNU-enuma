#define ENUMA_OEM_FAR_CHAIN 1
#define ENUMA_DIAG_STAGE 13
#define ENUMA_DIAG_DETAIL_POINT 13
#define ENUMA_DIAG_GUID_ONLY 1
#define ENUMA_DIAG_GUID_ENABLED 1
#define ENUMA_DIAG_GUID_LOW64 0x4f7906c74138022fULL
#define ENUMA_DIAG_GUID_HIGH64 0xe7a411b5337e949cULL
#define ENUMA_DIAG_DISPATCH_FALLBACK 1
#define ENUMA_BOOT_JOURNAL 1
#include <Uefi.h>
#include <Library/BaseMemoryLib.h>
#include <Library/BaseLib.h>
#include <Library/TimerLib.h>
#include <Library/ResetSystemLib.h>
#include <assert.h>
#include <string.h>
#include <setjmp.h>
static unsigned Sequence;static jmp_buf Jump;
UINTN EFIAPI MicroSecondDelay(UINTN Us){assert(Us==7000000&&Sequence==1);Sequence=2;return Us;}
VOID EFIAPI ResetCold(VOID){assert(Sequence==2);Sequence=3;}
VOID EFIAPI CpuDeadLoop(VOID){assert(Sequence==3);longjmp(Jump,1);}
UINT64 EFIAPI ReadUnaligned64(CONST VOID *P){UINT64 V;memcpy(&V,P,8);return V;}
VOID EnumaOemFarDispatchComplete(VOID){assert(!Sequence);Sequence=1;}
#include "EnumaDispatchDetailCheckpoint.h"
#include "EnumaDispatchCompletionCheckpoint.h"
int main(void){
 EFI_GUID Display={0x4138022f,0x06c7,0x4f79,{0x9c,0x94,0x7e,0x33,0xb5,0x11,0xa4,0xe7}};
 EnumaDispatchDetailCheckpoint(13,&Display,EFI_DEVICE_ERROR);
 assert(!Sequence&&EnumaDxeBootLog.Count==1); // record real failure; do not stop target
 if(!setjmp(Jump)){EnumaDispatchCompletionCheckpoint();assert(0);}assert(Sequence==3);
 return 0;
}
