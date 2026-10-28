#include <Uefi.h>
#include <Library/BaseMemoryLib.h>
#include <assert.h>
#include <setjmp.h>
#include <string.h>
#define ENUMA_BOOT_LOG_REPLAY 3
#define ENUMA_BOOT_LOG_HOLD_US 8000000
#define ENUMA_CAPTURE_PREPARED_ONLY 1
#include "EnumaOemCapturePixel.h"
#include "EnumaOemExceptionView.h"
#include "EnumaOemExceptionPage.h"
static BOOLEAN ExPresent(CONST ENUMA_EXCEPTION_RECORD *R,UINT32 Page);
#if ENUMA_OEM_CONTEXT
static VOID ExContextCapture(ENUMA_EXCEPTION_RECORD *R,CONST EFI_SYSTEM_CONTEXT_AARCH64 *C){R->X0=C->X0;R->X8=C->X8;R->X9=C->X9;R->X10=C->X10;R->Ttbr0=0x1234000;R->Ttbr1=0;R->Tcr=0x5678;R->Sctlr=1;R->El=4;R->ProbeValid=1;R->ParR=R->ParW=0xf;R->X20=0xb00b0;}
#endif
static BOOLEAN ExReadMeta(VOID *C,UINTN A,VOID *D,UINTN N);
#define ENUMA_OEM_EXCEPTION 1
#define ENUMA_OEM_EXIT_CLOCK 1
#define ENUMA_OEM_GOP_MODE 1
#define ENUMA_EXCEPTION_HOST_FIXTURE 1
#include "EnumaOemExceptionStop.h"
static jmp_buf Jump;
static unsigned Count,FailPage,Reenter,Resets;static UINTN Delay;
static EFI_SYSTEM_CONTEXT_AARCH64 Saved;
EFI_SYSTEM_TABLE *gST;
VOID *EFIAPI ZeroMem(VOID *P,UINTN N){return memset(P,0,N);}
UINTN EFIAPI MicroSecondDelay(UINTN N){Delay=N;return N;}
VOID EFIAPI CpuPause(VOID){longjmp(Jump,2);}
VOID EFIAPI ResetCold(VOID){Resets++;longjmp(Jump,1);}
static BOOLEAN ExReadMeta(VOID *C,UINTN A,VOID *D,UINTN N){(void)C;(void)A;(void)D;(void)N;return FALSE;}
static BOOLEAN ExPresent(CONST ENUMA_EXCEPTION_RECORD *R,UINT32 Page){
 ENUMA_LOG_PAGE P;assert(R->Pc==Saved.ELR&&R->Far==Saved.FAR&&R->Esr==Saved.ESR);Count++;
 ExPage(&P,R,Page);assert(P.Ready&&P.Text[0][0]=='E'&&P.Text[4][0]=='G');
 if(Page==1){assert(!memcmp(P.Text[1]+1,"000000001234abcd",16));}
 if(Page==2){assert(R->Owner==5&&!R->GuidValid);}
#if ENUMA_OEM_CONTEXT
 if(Page>=4){
  static const char *Expected[3][4]={
   {"0000000000000002","0000000000000003","000000000aeb00b0","000000000ae00000"},
   {"0000000001234000","0000000000000000","0000000000005678","0000000000000001"},
   {"0000000000000104","000000000000000f","000000000000000f","00000000000b00b0"}};
  assert(!memcmp(P.Text[0]+4,Expected[Page-4][0],16));
  for(unsigned i=1;i<4;i++){assert(P.Text[i][0]=="OSC"[i-1]);assert(!memcmp(P.Text[i]+1,Expected[Page-4][i],16));}
 }
#endif
 if(Reenter){EFI_SYSTEM_CONTEXT C={0};C.SystemContextAArch64=&Saved;EnumaUnhandledExceptionCheckpoint(0,C);assert(0);}
 return Page!=FailPage;
}
int main(void){
 Saved.ELR=0x1234abcd;Saved.ESR=0x96000004;Saved.FAR=0xfedcba9876543210ULL;Saved.LR=0x8888;Saved.SPSR=0x3c5;
 Saved.X0=2;Saved.X8=3;Saved.X9=0xaeb00b0;Saved.X10=0xae00000;
 for(unsigned fail=0;fail<=(ENUMA_OEM_CONTEXT?6:3);fail++){
  mExActive=FALSE;Count=Delay=Resets=0;FailPage=fail;EFI_SYSTEM_CONTEXT C={0};C.SystemContextAArch64=&Saved;
  if(!setjmp(Jump)){EnumaUnhandledExceptionCheckpoint(0,C);assert(0);}
  assert(Resets==1&&Delay==2000000&&Count==(fail?fail:(ENUMA_OEM_CONTEXT?6:3)));
 }
 mExActive=FALSE;Count=Delay=Resets=0;Reenter=1;FailPage=0;EFI_SYSTEM_CONTEXT C={0};C.SystemContextAArch64=&Saved;
 if(!setjmp(Jump)){EnumaUnhandledExceptionCheckpoint(0,C);assert(0);}
 assert(Resets==1&&Count==1&&!Delay&&mExRecord.Pc==Saved.ELR);
 mExActive=FALSE;Count=Delay=Resets=Reenter=0;C.SystemContextAArch64=NULL;
 if(!setjmp(Jump)){EnumaUnhandledExceptionCheckpoint(0,C);assert(0);}
 assert(Resets==1&&Count==0&&Delay==2000000);
 return 0;
}
