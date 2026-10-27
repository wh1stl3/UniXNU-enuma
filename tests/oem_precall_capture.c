// SPDX-License-Identifier: BSD-2-Clause-Patent
#define _POSIX_C_SOURCE 200809L
#include "EnumaOemPrecallCapture.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <setjmp.h>
#include <unistd.h>
VOID *EFIAPI CopyMem(VOID *D,CONST VOID *S,UINTN N){return memcpy(D,S,N);}
VOID *EFIAPI ZeroMem(VOID *D,UINTN N){return memset(D,0,N);}
static EFI_BOOT_SERVICES Boot;
static EFI_SYSTEM_TABLE System;
static ENUMA_SERVICE_TRACE Trace;
static ENUMA_PRECALL_CAPTURE Capture;
static EFI_TPL Current;
static unsigned Calls,SinkCalls,FailLine,Mode,Nest,Escape,FileMode;
static CHAR8 Bytes[40000];static UINTN Length;
static jmp_buf Jump;
static FILE *File;
static const char *EnteredPath;
static EFI_TPL EFIAPI Raise(EFI_TPL Next){EFI_TPL Old=Current;assert(Next>=Old);Current=Next;return Old;}
static VOID EFIAPI Restore(EFI_TPL Old){assert(Current==TPL_HIGH_LEVEL);Current=Old;}
static EFI_STATUS EFIAPI Crc(VOID *P,UINTN N,UINT32 *Out){(void)P;(void)N;*Out=123;return EFI_SUCCESS;}
static EFI_STATUS EFIAPI Allocate(EFI_MEMORY_TYPE Type,UINTN Size,VOID **Out){
  assert(Current!=TPL_HIGH_LEVEL&&Type==EfiBootServicesData&&Size==99);Calls++;
  if(FileMode){
    assert(Capture.State==EnumaCaptureExported);
    FILE *Entered=fopen(EnteredPath,"wx");assert(Entered);
    assert(fputs("original-service-entered-after-export\n",Entered)>=0);
    assert(!fflush(Entered)&&!fsync(fileno(Entered))&&!fclose(Entered));
    for(;;){pause();}
  }
  if(Escape==1){longjmp(Jump,1);}
  if(Out){*Out=(VOID *)0x1234;}return EFI_OUT_OF_RESOURCES;
}
static EFI_STATUS EFIAPI Locate(EFI_GUID *G,VOID *R,VOID **Out){
  (void)G;(void)R;Calls++;
  if(Nest){assert(Trace.Boot.AllocatePool(EfiBootServicesData,99,Out)==EFI_OUT_OF_RESOURCES);}
  return EFI_NOT_FOUND;
}
static EFI_STATUS EFIAPI Handle(EFI_HANDLE H,EFI_GUID *G,VOID **Out){(void)H;return Locate(G,NULL,Out);}
static BOOLEAN Sink(VOID *Opaque,CONST CHAR8 *Line,UINTN Size){
  (void)Opaque;assert(Current==TPL_APPLICATION&&Size<256&&Length+Size<sizeof(Bytes));SinkCalls++;
  if(Mode==1&&SinkCalls==2){VOID *Out;assert(Trace.Boot.AllocatePool(EfiBootServicesData,99,&Out)==EFI_OUT_OF_RESOURCES);}
  if(Mode==2&&SinkCalls==2){EnumaCaptureStop(&Capture);}
  if(Mode==3&&SinkCalls==2){longjmp(Jump,2);}
  if(FailLine==SinkCalls){memcpy(Bytes+Length,Line,Size/2);Length+=Size/2;return FALSE;}
  memcpy(Bytes+Length,Line,Size);Length+=Size;
  if(File){assert(fwrite(Line,1,Size,File)==Size);assert(!fflush(File));assert(!fsync(fileno(File)));}
  return TRUE;
}
static void Setup(UINT64 Selected){
  memset(&Boot,0,sizeof(Boot));memset(&System,0,sizeof(System));memset(&Capture,0,sizeof(Capture));
  mEnumaServiceTrace=NULL;mEnumaPrecallCapture=NULL;Current=TPL_APPLICATION;
  Calls=SinkCalls=FailLine=Mode=Nest=Escape=FileMode=0;Length=0;memset(Bytes,0,sizeof(Bytes));File=NULL;
  Boot.Hdr.HeaderSize=sizeof(Boot);System.Hdr.HeaderSize=sizeof(System);System.BootServices=&Boot;
  Boot.RaiseTPL=Raise;Boot.RestoreTPL=Restore;Boot.CalculateCrc32=Crc;
  Boot.AllocatePool=Allocate;Boot.LocateProtocol=Locate;Boot.HandleProtocol=Handle;
  assert(!EnumaServiceTracePrepare(&Trace,&System,0x1000,0x1000));
  assert(!EnumaCaptureArm(&Capture,&Trace,0x123456789,Selected,Sink,NULL));
}
static void Call(void){VOID *Out=NULL;assert(Trace.Boot.AllocatePool(EfiBootServicesData,99,&Out)==EFI_OUT_OF_RESOURCES&&Out==(VOID *)0x1234);}
int main(int argc,char **argv){
  unsigned I;VOID *Out=NULL;
  if(argc==3){Setup(0);File=fopen(argv[1],"wx");assert(File);EnteredPath=argv[2];FileMode=1;Call();return 99;}
  Setup(0);Call();assert(Calls==1&&Capture.State==EnumaCaptureExported&&Capture.Attempts==1&&SinkCalls==4);
  assert(Capture.Snapshot.Count==1&&!Capture.Snapshot.Events[0].Returned);
  assert(Trace.Log.Count==2&&Trace.Log.Events[1].Returned&&Trace.Log.Events[1].Status==EFI_OUT_OF_RESOURCES);
  for(I=0;I<140;I++){Call();}assert(SinkCalls==4&&Capture.Snapshot.Count==1&&Trace.Log.Dropped>0);
  assert(EnumaCaptureArm(&Capture,&Trace,2,0,Sink,NULL)==EFI_ALREADY_STARTED);
  // Fail at every framing or payload line, including a partial final marker.
  for(I=1;I<=4;I++){Setup(0);FailLine=I;Call();assert(Capture.State==EnumaCaptureSinkFailed&&SinkCalls==I&&Calls==1);Call();assert(SinkCalls==I);}
  Setup(0);Mode=1;Call();assert(Capture.State==EnumaCaptureReentered&&SinkCalls==2&&Calls==2);
  Setup(0);Mode=2;Call();assert(Capture.State==EnumaCaptureInterrupted&&SinkCalls==2&&Calls==1);
  Setup(0);Mode=3;
  if(!setjmp(Jump)){Call();assert(0);}assert(Capture.State==EnumaCaptureEmitting&&Calls==0);
  EnumaCaptureStop(&Capture);Mode=0;Call();assert(Capture.State==EnumaCaptureInterrupted&&SinkCalls==2&&Calls==1);
  Setup(0);Escape=1;
  if(!setjmp(Jump)){Call();assert(0);}assert(Capture.State==EnumaCaptureExported&&Trace.Log.Count==1);
  Escape=0;Call();assert(SinkCalls==4&&Trace.Log.Events[1].Call==1); // no fabricated return for call0
  Setup(0);Current=TPL_CALLBACK;Call();assert(Capture.State==EnumaCaptureBadTpl&&!SinkCalls);Current=TPL_APPLICATION;
  Setup(0);Trace.Log.NextCall=MAX_UINT64;Call();assert(Capture.State==EnumaCaptureExhausted&&!SinkCalls);
  Setup(0);Trace.Log.NextSequence=MAX_UINT64;Call();assert(Capture.State==EnumaCaptureExhausted&&!SinkCalls);
  Setup(0);Trace.Log.NextCall=1;Call();assert(Capture.State==EnumaCaptureLost&&!SinkCalls);
  Setup(1);Nest=1;assert(Trace.Boot.LocateProtocol(NULL,NULL,&Out)==EFI_NOT_FOUND);
  assert(Capture.State==EnumaCaptureExported&&Capture.Snapshot.Count==2&&Capture.Snapshot.Events[1].Call==1&&!Capture.Snapshot.Events[0].Returned);
  Setup(70);for(I=0;I<=70;I++){Call();}assert(Capture.State==EnumaCaptureExported&&Capture.Snapshot.Dropped==13&&SinkCalls==131);
  Setup(0);EnumaCaptureStop(&Capture);Call();assert(Capture.State==EnumaCaptureStopped&&!SinkCalls);
  assert(!EnumaServiceTraceSnapshot(NULL));
  puts("PASS: one-shot pre-forward capture; failure, partial sink, nested, reentry, TPL, exhaustion, longjmp, stale records and overwrite");
  return 0;
}
