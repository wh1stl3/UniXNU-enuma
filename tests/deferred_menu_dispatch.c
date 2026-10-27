// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <Uefi.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#define ENUMA_DEFERRED_MENU 1
#define ENUMA_FULL_MENU 1
#define ENUMA_BOUNDED_MENU 1
#define ENUMA_BOOT_JOURNAL 1
#define ENUMA_VIDEO_TERMINAL 1
#define ENUMA_DIAG_STAGE 13
#define ENUMA_DIAG_DETAIL_POINT 16
#define ENUMA_DIAG_DISPATCH_FALLBACK 0
#include "EnumaDeferredMenu.h"
static ENUMA_BOOT_LOG EnumaDxeBootLog;
static UINTN EnumaDispatchOrdinal=33;
static ENUMA_DEFERRED_MENU_PROTOCOL Service;
static unsigned Runs,Resets,Dead,Lookups;
static UINTN Delay;
static UINT32 CallbackResult=5;
static EFI_STATUS LookupStatus;
static EFI_HANDLE Owner=(VOID *)1;
static UINT64 ReadUnaligned64(CONST UINT64 *P){UINT64 V;memcpy(&V,P,8);return V;}
static BOOLEAN EnumaDxeBootLogSnapshot(ENUMA_BOOT_LOG *Out){*Out=EnumaDxeBootLog;return TRUE;}
static EFI_STATUS CoreHandleProtocol(EFI_HANDLE H,EFI_GUID *G,VOID **Out){
 EFI_GUID Expected=ENUMA_DEFERRED_MENU_GUID;assert(H==Owner&&!memcmp(G,&Expected,sizeof(*G)));Lookups++;*Out=&Service;return LookupStatus;
}
static VOID MicroSecondDelay(UINTN V){Delay=V;}
static VOID ResetCold(VOID){Resets++;}
static VOID CpuDeadLoop(VOID){Dead++;}
static UINT32 EFIAPI Run(ENUMA_DEFERRED_MENU_PROTOCOL *This,CONST ENUMA_BOOT_LOG *Log){
 assert(This==&Service&&EnumaDeferredReturnValid(Log));assert(Log!=&EnumaDxeBootLog);Runs++;return CallbackResult;
}
#include "EnumaDeferredMenuDispatch.h"
static EFI_GUID File={0xdcfd1e6d,0x788d,0x4ffc,{0x8e,0x1b,0xca,0x2f,0x75,0x65,0x1a,0x92}};
static VOID Setup(VOID){
 memset(&EnumaDxeBootLog,0,sizeof(EnumaDxeBootLog));EnumaDeferredAttempted=FALSE;
 Service=(ENUMA_DEFERRED_MENU_PROTOCOL){1,sizeof(Service),Owner,Run};Runs=Resets=Dead=Lookups=0;Delay=0;LookupStatus=EFI_SUCCESS;CallbackResult=5;
 assert(EnumaBootLogAppend(&EnumaDxeBootLog,13,33,&File,EFI_SUCCESS));
}
int main(void){unsigned Case;EFI_GUID Wrong=File;Wrong.Data1++;
 Setup();EnumaDeferredMenuDispatch(Owner,&Wrong,0);EnumaDeferredMenuDispatch(Owner,NULL,0);assert(!Resets&&!Lookups&&!Runs);
 Setup();EnumaDeferredMenuDispatch(Owner,&File,0);assert(Runs==1&&Resets==1&&Dead==1&&Delay==22000000);
 assert(EnumaDxeBootLog.Events[0].Status==0&&EnumaDxeBootLog.Events[0].Point==13);
 assert(EnumaDxeBootLog.Events[1].Status==5&&EnumaDxeBootLog.Events[1].Point==28);
 EnumaDeferredMenuDispatch(Owner,&File,0);assert(Runs==1&&Resets==2&&Delay==2000000);
 for(Case=0;Case<11;Case++){
  Setup();
  switch(Case){
   case 0:LookupStatus=EFI_NOT_FOUND;break;
   case 1:Service.Version=2;break;
   case 2:Service.Bytes--;break;
   case 3:Service.Owner=(VOID *)2;break;
   case 4:Service.Run=NULL;break;
   case 5:EnumaDxeBootLog.Events[0].Status=EFI_DEVICE_ERROR;break;
   case 6:EnumaDxeBootLog.Events[0].Point=21;break;
   case 7:EnumaDxeBootLog.Events[0].GuidLe[15]^=1;break;
   case 8:EnumaDxeBootLog.NextSequence++;break;
   case 9:EnumaDxeBootLog.Count=0;break;
   case 10:EnumaDxeBootLog.Head=128;break;
  }
  EnumaDeferredMenuDispatch(Owner,&File,0);assert(!Runs&&Resets==1&&Dead==1&&Delay==2000000);
 }
 Setup();EnumaDeferredMenuDispatch(Owner,&File,EFI_DEVICE_ERROR);assert(!Runs&&!Lookups&&Resets==1);
 Setup();EnumaDeferredMenuDispatch(NULL,&File,0);assert(!Runs&&!Lookups&&Resets==1);
 Setup();CallbackResult=99;EnumaDeferredMenuDispatch(Owner,&File,0);assert(Runs==1&&Delay==7000000);
 puts("deferred dispatcher: exact owner/return, separate result, no retry, 17 paths PASS");return 0;
}
