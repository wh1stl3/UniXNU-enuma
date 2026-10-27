// SPDX-License-Identifier: BSD-2-Clause-Patent
#define ENUMA_OEM_REGISTRATION 1
#define ENUMA_OEM_MAIN_ENTRY 1
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
static unsigned Phases,Calls,Fail,Hang,Nested,MainCalls;
static EFI_GUID Main={0xb0760469,0x970c,0x487a,{0xa4,0xb5,0x28,0xdb,0x7b,0x45,0xce,0xf1}};
static UINT32 Seen[5];
static EFI_STATUS Result;
static jmp_buf Jump;
static EFI_TPL EFIAPI Raise(EFI_TPL L){EFI_TPL Old=Level;Level=L;return Old;}
static VOID EFIAPI Restore(EFI_TPL L){Level=L;}
static EFI_STATUS EFIAPI Crc(VOID *P,UINTN N,UINT32 *C){(void)P;(void)N;*C=0;return EFI_SUCCESS;}
static EFI_STATUS EFIAPI Alloc(EFI_MEMORY_TYPE M,UINTN N,VOID **B){(void)M;(void)N;(void)B;return EFI_SUCCESS;}
static EFI_STATUS EFIAPI Locate(EFI_GUID *G,VOID *R,VOID **I){
 assert(Level==TPL_APPLICATION);(void)R;(void)I;
 if(G==&Main){MainCalls++;if(Hang){longjmp(Jump,2);}return Result;}
 return EFI_NOT_FOUND;
}
static EFI_STATUS EFIAPI Handle(EFI_HANDLE H,EFI_GUID *G,VOID **I){return Locate(G,H,I);}
static EFI_STATUS EFIAPI Install(EFI_GUID *G,VOID *P){
 assert(Level==TPL_APPLICATION&&G==&Guid&&P==(VOID *)0x1234);Calls++;
 if(Nested){assert(T.Boot.AllocatePool(EfiBootServicesData,1,NULL)==0);}
 return Result;
}
static VOID Stop(VOID *P){(void)P;longjmp(Jump,1);}
static BOOLEAN Present(UINT32 Phase,CONST ENUMA_SERVICE_EVENT *E,UINT64 S){
 assert(S==123&&Level==TPL_APPLICATION&&Phases<5);Seen[Phases++]=Phase;
 assert(Phase==1||Phase==3||Phase==5);
 if(Phase==1){assert(E->Service==1&&E->CallerRva==0x3608&&E->Call>=6&&!E->Returned);}
 if(Phase==3){assert(mOemProgress.MainReturned);}
 if(Phase==5){assert(E->Returned&&E->Status==EFI_ABORTED);}
 return Fail!=Phase;
}
static void Setup(void){
 memset(&Boot,0,sizeof(Boot));memset(&System,0,sizeof(System));memset(&T,0,sizeof(T));memset(&mOemProgress,0,sizeof(mOemProgress));mEnumaServiceTrace=NULL;
 Boot.Hdr.HeaderSize=sizeof(Boot);System.Hdr.HeaderSize=sizeof(System);System.BootServices=&Boot;
 Boot.RaiseTPL=Raise;Boot.RestoreTPL=Restore;Boot.CalculateCrc32=Crc;Boot.AllocatePool=Alloc;
 Boot.LocateProtocol=Locate;Boot.HandleProtocol=Handle;Boot.InstallConfigurationTable=Install;
 Level=TPL_APPLICATION;Phases=Calls=Fail=Hang=Nested=MainCalls=0;Result=EFI_SUCCESS;
 assert(EnumaServiceTracePrepare(&T,&System,0x1000,MAX_UINTN-0x1000)==0);
 assert(T.Boot.InstallConfigurationTable!=Install&&Boot.InstallConfigurationTable==Install);
 assert(OemProgressArm(&T,123,Present,Stop)==0);
 for(unsigned I=0;I<5;I++){assert(T.Boot.AllocatePool(EfiBootServicesData,16,NULL)==0);}
 assert(!Phases&&T.Log.NextCall==5);
 assert(EnumaTraceInstallConfigurationAt(0x6cc8,&Guid,(VOID *)0x1234)==0);
 assert(!Phases&&T.Log.NextCall==6);
}
int main(void){
 EFI_STATUS Statuses[]={EFI_SUCCESS,EFI_OUT_OF_RESOURCES,EFI_WARN_UNKNOWN_GLYPH};
 for(unsigned I=0;I<3;I++){
  Setup();Result=Statuses[I];assert(EnumaTraceLocateProtocolAt(0x4608,&Main,NULL,NULL)==Result);
  assert(Phases==1&&MainCalls==1&&T.Log.NextSequence==14&&T.Log.Events[13].Returned);
  assert(T.Log.Events[13].Status==Result&&mOemProgress.MainReturned&&EnumaServiceLogValid(&T.Log));
  T.Boot.LocateProtocol(&Sid,NULL,NULL);OemProgressReturned(EFI_ABORTED);
  assert(Phases==3&&Seen[0]==1&&Seen[1]==3&&Seen[2]==5);
 }
 Setup();Hang=1;if(!setjmp(Jump)){EnumaTraceLocateProtocolAt(0x4608,&Main,NULL,NULL);assert(0);}
 assert(MainCalls==1&&Phases==1&&!mOemProgress.MainReturned);
 Setup();Fail=1;if(!setjmp(Jump)){EnumaTraceLocateProtocolAt(0x4608,&Main,NULL,NULL);assert(0);}
 assert(!MainCalls&&Phases==1&&mOemProgress.Stopped);
 Setup();assert(EnumaTraceLocateProtocolAt(0x4608,&Main,NULL,NULL)==0);Fail=3;
 if(!setjmp(Jump)){T.Boot.LocateProtocol(&Sid,NULL,NULL);assert(0);}assert(Phases==2&&mOemProgress.Stopped);
 Setup();assert(EnumaTraceLocateProtocolAt(0x4604,&Main,NULL,NULL)==0);assert(!Phases&&MainCalls==1);
 assert(EnumaTraceLocateProtocolAt(0x4608,&Main,NULL,NULL)==0);assert(Phases==1&&MainCalls==2);
 Setup();if(!setjmp(Jump)){EnumaTraceLocateProtocolAt(0x4608,&Guid,NULL,NULL);assert(0);}assert(!Phases&&!MainCalls);
 Setup();Level=TPL_CALLBACK;if(!setjmp(Jump)){EnumaTraceLocateProtocolAt(0x4608,&Main,NULL,NULL);assert(0);}assert(!MainCalls&&!Phases);
 Setup();OemProgressReturned(EFI_ABORTED);assert(Phases==1&&Seen[0]==5); // real early error is still observed
 puts("PASS: v6 no registration/return pages; main/SID/real Core progress; original status, wrong caller/GUID, nonreturn, TPL and sink failures");
}
