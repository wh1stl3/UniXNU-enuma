// SPDX-License-Identifier: BSD-2-Clause-Patent
#define ENUMA_OEM_REGISTRATION 1
#include <Uefi.h>
#include <Library/BaseMemoryLib.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <setjmp.h>
VOID *EFIAPI CopyMem(VOID *D,CONST VOID *S,UINTN N){return memcpy(D,S,N);}
VOID *EFIAPI ZeroMem(VOID *D,UINTN N){return memset(D,0,N);}
INTN EFIAPI CompareMem(CONST VOID *A,CONST VOID *B,UINTN N){return memcmp(A,B,N);}
#include "EnumaOemProgress.h"
static EFI_BOOT_SERVICES Boot;
static EFI_SYSTEM_TABLE System;
static ENUMA_SERVICE_TRACE T;
static EFI_TPL Level;
static EFI_GUID Guid={1,0,0,{0}},Sid={0x54b6d3b4,0x5d33,0x4f91,{0x86,0,0x6c,0x41,0xd5,0xde,0xb1,0x9a}};
static unsigned Phases,Calls,Fail,Hang,Nested;
static UINT32 Seen[5];
static EFI_STATUS Result;
static jmp_buf Jump;
static EFI_TPL EFIAPI Raise(EFI_TPL L){EFI_TPL Old=Level;Level=L;return Old;}
static VOID EFIAPI Restore(EFI_TPL L){Level=L;}
static EFI_STATUS EFIAPI Crc(VOID *P,UINTN N,UINT32 *C){(void)P;(void)N;*C=0;return EFI_SUCCESS;}
static EFI_STATUS EFIAPI Alloc(EFI_MEMORY_TYPE M,UINTN N,VOID **B){(void)M;(void)N;(void)B;return EFI_SUCCESS;}
static EFI_STATUS EFIAPI Locate(EFI_GUID *G,VOID *R,VOID **I){(void)G;(void)R;(void)I;return EFI_NOT_FOUND;}
static EFI_STATUS EFIAPI Handle(EFI_HANDLE H,EFI_GUID *G,VOID **I){return Locate(G,H,I);}
static EFI_STATUS EFIAPI Install(EFI_GUID *G,VOID *P){
 assert(Level==TPL_APPLICATION&&G==&Guid&&P==(VOID *)0x1234);Calls++;
 if(Hang){longjmp(Jump,2);}
 if(Nested){assert(T.Boot.AllocatePool(EfiBootServicesData,1,NULL)==0);}
 return Result;
}
static VOID Stop(VOID *P){(void)P;longjmp(Jump,1);}
static BOOLEAN Present(UINT32 Phase,CONST ENUMA_SERVICE_EVENT *E,UINT64 S){
 assert(S==123&&Level==TPL_APPLICATION&&Phases<5);Seen[Phases++]=Phase;
 if(Phase<=2){assert(E->Service==4&&E->CallerRva==0x5cc8&&E->Call==5);if(Phase==2){assert(E->Status==Result);}}
 return Fail!=Phase;
}
static void Setup(void){
 memset(&Boot,0,sizeof(Boot));memset(&System,0,sizeof(System));memset(&T,0,sizeof(T));memset(&mOemProgress,0,sizeof(mOemProgress));mEnumaServiceTrace=NULL;
 Boot.Hdr.HeaderSize=sizeof(Boot);System.Hdr.HeaderSize=sizeof(System);System.BootServices=&Boot;
 Boot.RaiseTPL=Raise;Boot.RestoreTPL=Restore;Boot.CalculateCrc32=Crc;Boot.AllocatePool=Alloc;
 Boot.LocateProtocol=Locate;Boot.HandleProtocol=Handle;Boot.InstallConfigurationTable=Install;
 Level=TPL_APPLICATION;Phases=Calls=Fail=Hang=Nested=0;Result=EFI_SUCCESS;
 assert(EnumaServiceTracePrepare(&T,&System,0x1000,MAX_UINTN-0x1000)==0);
 assert(T.Boot.InstallConfigurationTable!=Install&&Boot.InstallConfigurationTable==Install);
 assert(OemProgressArm(&T,123,Present,Stop)==0);
 for(unsigned I=0;I<5;I++){assert(T.Boot.AllocatePool(EfiBootServicesData,16,NULL)==0);}
 assert(!Phases&&T.Log.NextCall==5);
}
int main(void){
 EFI_STATUS Statuses[]={EFI_SUCCESS,EFI_OUT_OF_RESOURCES,EFI_WARN_UNKNOWN_GLYPH};
 for(unsigned I=0;I<3;I++){
  Setup();Result=Statuses[I];assert(EnumaTraceInstallConfigurationAt(0x6cc8,&Guid,(VOID *)0x1234)==Result);
  assert(Phases==2&&Calls==1&&T.Log.NextSequence==12&&T.Log.Events[11].Returned);
  assert(EnumaServiceLogValid(&T.Log));
  T.Boot.LocateProtocol(&Sid,NULL,NULL);OemProgressReturned(EFI_ABORTED);
  assert(Phases==5);for(unsigned J=0;J<5;J++){assert(Seen[J]==J+1);}
 }
 Setup();assert(EnumaTraceInstallConfigurationAt(0x6cc4,&Guid,(VOID *)0x1234)==0);assert(!Phases&&Calls==1&&T.Log.NextCall==5);
 assert(EnumaTraceInstallConfigurationAt(1,&Guid,(VOID *)0x1234)==0);assert(!Phases&&Calls==2&&T.Log.NextCall==5);
 Setup();Nested=1;assert(EnumaTraceInstallConfigurationAt(0x6cc8,&Guid,(VOID *)0x1234)==0);assert(Phases==2&&T.Log.NextCall==7);
 Setup();Hang=1;if(!setjmp(Jump)){EnumaTraceInstallConfigurationAt(0x6cc8,&Guid,(VOID *)0x1234);assert(0);}assert(Calls==1&&Phases==1&&!T.Log.Events[10].Returned);
 for(unsigned I=1;I<=2;I++){
  Setup();Fail=I;if(!setjmp(Jump)){EnumaTraceInstallConfigurationAt(0x6cc8,&Guid,(VOID *)0x1234);assert(0);}
  assert(Phases==I&&Calls==(I==2)&&mOemProgress.Stopped);
 }
 Setup();Level=TPL_CALLBACK;if(!setjmp(Jump)){EnumaTraceInstallConfigurationAt(0x6cc8,&Guid,(VOID *)0x1234);assert(0);}assert(!Calls&&!Phases);
 puts("PASS: target registration transparent status/pointers, unrelated caller, nested forwarding, nonreturn, sink failure and TPL gates");
}
