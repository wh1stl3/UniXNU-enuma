// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <Uefi.h>
#include <Library/UefiBootServicesTableLib.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "InheritedScanout.h"
#include "EnumaDeferredMenu.h"
static EFI_BOOT_SERVICES Boot;
EFI_BOOT_SERVICES *gBS=&Boot;
static unsigned Runs,Installs;
static BOOLEAN Policy=TRUE;
static EFI_STATUS InstallStatus=EFI_SUCCESS;
static ENUMA_DEFERRED_MENU_PROTOCOL *Published;
static ENUMA_INHERITED_FRAME Expected;
static BOOLEAN DeferredPolicyValid(const ENUMA_INHERITED_FRAME *F){assert(!memcmp(F,&Expected,sizeof(*F)));return Policy;}
static UINT32 RunMenuWindow(const ENUMA_INHERITED_FRAME *F){assert(!memcmp(F,&Expected,sizeof(*F)));Runs++;return 5;}
static EFI_STATUS EFIAPI Install(EFI_HANDLE *H,EFI_GUID *G,EFI_INTERFACE_TYPE Type,VOID *Interface){
 EFI_GUID Wanted=ENUMA_DEFERRED_MENU_GUID;assert(*H==(VOID *)1&&Type==EFI_NATIVE_INTERFACE&&!memcmp(G,&Wanted,sizeof(*G)));
 Published=Interface;Installs++;return InstallStatus;
}
#include "EnumaDeferredMenuProvider.h"
static ENUMA_BOOT_LOG Log;
static VOID Setup(VOID){
 EFI_GUID File={0xdcfd1e6d,0x788d,0x4ffc,{0x8e,0x1b,0xca,0x2f,0x75,0x65,0x1a,0x92}};
 memset(&mDeferredMenu,0,sizeof(mDeferredMenu));mDeferredConsumed=FALSE;memset(&Log,0,sizeof(Log));
 Runs=Installs=0;Policy=TRUE;InstallStatus=EFI_SUCCESS;Published=NULL;Boot.InstallProtocolInterface=Install;
 memset(&Expected,0x12,sizeof(Expected));EnumaBootLogAppend(&Log,13,33,&File,0);
}
static VOID RegisterAndLeave(VOID){ENUMA_INHERITED_FRAME Stack=Expected;assert(PublishDeferredMenu((VOID *)1,&Stack)==EFI_SUCCESS);memset(&Stack,0,sizeof(Stack));}
int main(void){
 Setup();RegisterAndLeave();assert(Installs==1&&Runs==0&&Published==&mDeferredMenu);
 assert(Published->Run(Published,&Log)==5&&Runs==1);assert(Published->Run(Published,&Log)==1&&Runs==1);
 assert(PublishDeferredMenu((VOID *)1,&Expected)==EFI_ALREADY_STARTED&&Installs==1);
 Setup();assert(PublishDeferredMenu(NULL,&Expected)==EFI_ALREADY_STARTED&&!Installs);
 assert(PublishDeferredMenu((VOID *)1,NULL)==EFI_ALREADY_STARTED&&!Installs);
 Setup();RegisterAndLeave();assert(DeferredMenuRun(NULL,&Log)==1&&!Runs&&!mDeferredConsumed);
 Log.Events[0].Status=EFI_DEVICE_ERROR;assert(Published->Run(Published,&Log)==1&&!Runs&&mDeferredConsumed);
 Log.Events[0].Status=0;assert(Published->Run(Published,&Log)==1&&!Runs);
 Setup();RegisterAndLeave();Policy=FALSE;assert(Published->Run(Published,&Log)==1&&!Runs&&mDeferredConsumed);
 Setup();InstallStatus=EFI_OUT_OF_RESOURCES;assert(PublishDeferredMenu((VOID *)1,&Expected)==EFI_OUT_OF_RESOURCES);
 assert(PublishDeferredMenu((VOID *)1,&Expected)==EFI_ALREADY_STARTED&&Installs==1);
 puts("deferred provider: owned frame, no early drawing, stale return/policy rejection, single-use PASS");return 0;
}
