#define ENUMA_OEM_FAR_CHAIN 1
#define ENUMA_BOOT_LOG_REPLAY 3
#define ENUMA_BOOT_LOG_HOLD_US 8000000
#include "EnumaOemCapturePixel.h"
#include "EnumaOemProgressPage.h"
#include <assert.h>
#include <string.h>
VOID *EFIAPI CopyMem(VOID *D,CONST VOID *S,UINTN N){return memcpy(D,S,N);}
VOID *EFIAPI ZeroMem(VOID *D,UINTN N){return memset(D,0,N);}
INTN EFIAPI CompareMem(CONST VOID *A,CONST VOID *B,UINTN N){return memcmp(A,B,N);}
int main(void){
 ENUMA_LOG_PAGE P;ENUMA_SERVICE_EVENT E={0};E.Call=MAX_UINT64;E.CallerRva=0x3608;
 E.Value=0xc1;E.Status=EFI_ABORTED;E.Returned=TRUE;E.Sequence=17;
 assert(OemProgressPage(&P,5,&E,123));
 assert(!memcmp(P.Text[0],"S05C00000000000000c1",20));
 assert(!memcmp(P.Text[2],"O0000000000003608   ",20));
 assert(!memcmp(P.Text[3],"S8000000000000015   ",20));
 E.Returned=FALSE;assert(!OemProgressPage(&P,5,&E,123));return 0;
}
