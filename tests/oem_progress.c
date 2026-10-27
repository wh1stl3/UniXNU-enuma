// SPDX-License-Identifier: BSD-2-Clause-Patent
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
static ENUMA_SERVICE_TRACE Trace;
static EFI_TPL Current;
static unsigned Count,Original,Fail,Reenter,Hang,Phases[5];
static UINT64 Statuses[5];
static jmp_buf Jump;
static EFI_GUID Sid={0x54b6d3b4,0x5d33,0x4f91,{0x86,0x00,0x6c,0x41,0xd5,0xde,0xb1,0x9a}},Other={0};
static EFI_TPL EFIAPI Raise(EFI_TPL T){EFI_TPL Old=Current;Current=T;return Old;}
static VOID EFIAPI Restore(EFI_TPL T){Current=T;}
static EFI_STATUS EFIAPI Crc(VOID *P,UINTN N,UINT32 *V){(void)P;(void)N;*V=0;return EFI_SUCCESS;}
static EFI_STATUS EFIAPI Locate(EFI_GUID *G,VOID *R,VOID **I){(void)G;(void)R;(void)I;Original++;return EFI_NOT_FOUND;}
static EFI_STATUS EFIAPI Handle(EFI_HANDLE H,EFI_GUID *G,VOID **I){return Locate(G,H,I);}
static EFI_STATUS EFIAPI Alloc(EFI_MEMORY_TYPE T,UINTN N,VOID **B){(void)T;(void)N;(void)B;Original++;if(Hang){longjmp(Jump,2);}return EFI_OUT_OF_RESOURCES;}
static VOID Stop(VOID *C){(void)C;longjmp(Jump,1);}
static BOOLEAN Present(UINT32 P,CONST ENUMA_SERVICE_EVENT *E,UINT64 Session){
  assert(Current==TPL_APPLICATION&&Count<5&&Session==123);Phases[Count]=P;Statuses[Count++]=E->Status;
  assert(E->Returned==(P==2||P==4||P==5));
  if(Reenter){Trace.Boot.AllocatePool(EfiBootServicesData,1,NULL);}
  return Fail!=P;
}
static void Setup(void){
  memset(&Boot,0,sizeof(Boot));memset(&System,0,sizeof(System));memset(&Trace,0,sizeof(Trace));
  memset(&mOemProgress,0,sizeof(mOemProgress));mEnumaServiceTrace=NULL;
  Boot.Hdr.HeaderSize=sizeof(Boot);System.Hdr.HeaderSize=sizeof(System);System.BootServices=&Boot;
  Boot.RaiseTPL=Raise;Boot.RestoreTPL=Restore;Boot.CalculateCrc32=Crc;Boot.LocateProtocol=Locate;Boot.HandleProtocol=Handle;Boot.AllocatePool=Alloc;
  Count=Original=Fail=Reenter=Hang=0;Current=TPL_APPLICATION;
  assert(EnumaServiceTracePrepare(&Trace,&System,0,MAX_UINTN)==EFI_SUCCESS);
  assert(OemProgressArm(&Trace,123,Present,Stop)==EFI_SUCCESS);
  assert(OemProgressArm(&Trace,123,Present,Stop)==EFI_ALREADY_STARTED);
}
int main(void){
  Setup();assert(Trace.Boot.AllocatePool(EfiBootServicesData,9,NULL)==EFI_OUT_OF_RESOURCES);
  assert(Count==2&&Statuses[0]==0&&Statuses[1]==EFI_OUT_OF_RESOURCES);
  Trace.Boot.LocateProtocol(&Other,NULL,NULL);assert(Count==2);
  Trace.Boot.LocateProtocol(&Sid,NULL,NULL);assert(Count==4&&Statuses[3]==EFI_NOT_FOUND);
  Trace.Boot.LocateProtocol(&Sid,NULL,NULL);assert(Count==4);
  OemProgressReturned(EFI_ABORTED);assert(Count==5&&Statuses[4]==EFI_ABORTED);
  for(unsigned I=0;I<5;I++){assert(Phases[I]==I+1);}
  if(!setjmp(Jump)){OemProgressReturned(EFI_SUCCESS);assert(0);}assert(mOemProgress.Stopped);
  Setup();Hang=1;if(!setjmp(Jump)){Trace.Boot.AllocatePool(EfiBootServicesData,9,NULL);assert(0);}
  assert(Original==1&&Count==1&&Trace.Log.Count==1); // no fabricated return
  Setup();Fail=1;if(!setjmp(Jump)){Trace.Boot.AllocatePool(EfiBootServicesData,9,NULL);assert(0);}
  assert(!Original&&Count==1&&mOemProgress.Stopped);
  Setup();Current=TPL_CALLBACK;if(!setjmp(Jump)){Trace.Boot.AllocatePool(EfiBootServicesData,9,NULL);assert(0);}
  assert(!Original&&!Count&&mOemProgress.Stopped);
  Setup();Reenter=1;if(!setjmp(Jump)){Trace.Boot.AllocatePool(EfiBootServicesData,9,NULL);assert(0);}
  assert(!Original&&Count==1&&mOemProgress.Stopped);
  for(unsigned Phase=2;Phase<=5;Phase++){
    Setup();Fail=Phase;
    if(!setjmp(Jump)){
      Trace.Boot.AllocatePool(EfiBootServicesData,9,NULL);
      Trace.Boot.LocateProtocol(&Sid,NULL,NULL);
      OemProgressReturned(EFI_ABORTED);assert(0);
    }
    assert(mOemProgress.Stopped&&Count==Phase);
    assert(Original==(Phase<=3?1:2));
    if(Phase==2||Phase==4){assert(Trace.Log.Events[Trace.Log.Count-1].Returned);}
  }
  Setup();OemProgressReturned(EFI_DEVICE_ERROR);assert(Count==1&&Phases[0]==5&&Statuses[0]==EFI_DEVICE_ERROR);
  Setup();Trace.Boot.LocateProtocol(&Sid,NULL,NULL);assert(Count==4);OemProgressReturned(EFI_SUCCESS);assert(Count==5);
  Setup();Trace.Log.NextCall=MAX_UINT64;if(!setjmp(Jump)){Trace.Boot.AllocatePool(EfiBootServicesData,1,NULL);assert(0);}
  assert(!Original&&!Count&&mOemProgress.Stopped);
  puts("PASS: five phases, exact status, first SID only, nonreturn, no-call driver return, sink/TPL/reentry/exhaustion fail-closed");
}
