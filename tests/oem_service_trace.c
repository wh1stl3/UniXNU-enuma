// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "EnumaOemServiceTraceView.h"
#include "EnumaOemTraceTarget.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
VOID *EFIAPI CopyMem(VOID *D,CONST VOID *S,UINTN N){return memcpy(D,S,N);}
VOID *EFIAPI ZeroMem(VOID *D,UINTN N){return memset(D,0,N);}
static EFI_BOOT_SERVICES Boot,OriginalBoot;
static EFI_SYSTEM_TABLE System,OriginalSystem;
static ENUMA_SERVICE_TRACE Trace;
static ENUMA_SERVICE_TRACE_LOG Snapshot;
static EFI_TPL Current=TPL_APPLICATION;
static EFI_GUID Guid={0x12345678,1,2,{3,4,5,6,7,8,9,10}};
static unsigned LocateCalls,HandleCalls,AllocCalls,CrcCalls,CrcFail,Nested,InterruptCall;
static EFI_STATUS Returned=EFI_NOT_FOUND;
static unsigned PartialCalls;
static CHAR8 PartialBytes[7];
static BOOLEAN Sink(VOID *C,CONST CHAR8 *Line,UINTN Size){(void)C;assert(Size<256);return fwrite(Line,1,Size,stdout)==Size;}
static BOOLEAN Refuse(VOID *C,CONST CHAR8 *Line,UINTN Size){(void)C;(void)Line;(void)Size;return FALSE;}
static BOOLEAN Partial(VOID *C,CONST CHAR8 *Line,UINTN Size){(void)C;assert(Size>7);memcpy(PartialBytes,Line,7);PartialCalls++;return FALSE;}
static EFI_TPL EFIAPI Raise(EFI_TPL Next){EFI_TPL Old=Current;assert(Next>=Old);Current=Next;return Old;}
static VOID EFIAPI Restore(EFI_TPL Previous){assert(Current==TPL_HIGH_LEVEL);Current=Previous;}
static EFI_STATUS EFIAPI Crc(VOID *Data,UINTN Bytes,UINT32 *Out){
 (void)Data;assert(Bytes==sizeof(Boot)||Bytes==sizeof(System));CrcCalls++;
 if(CrcFail==CrcCalls)return EFI_DEVICE_ERROR;*Out=0x12345678;return EFI_SUCCESS;
}
static EFI_STATUS EFIAPI Allocate(EFI_MEMORY_TYPE Type,UINTN Size,VOID **Out){
 assert(Current==TPL_APPLICATION&&Type==EfiBootServicesData&&Size==99);AllocCalls++;
 if(Out)*Out=(VOID *)0x2345;return Returned;
}
static EFI_STATUS EFIAPI Handle(EFI_HANDLE H,EFI_GUID *G,VOID **Out){
 assert(Current==TPL_APPLICATION&&H==(VOID *)0x3456&&G==&Guid);HandleCalls++;if(Out)*Out=(VOID *)0x4567;return Returned;
}
static EFI_STATUS EFIAPI Locate(EFI_GUID *G,VOID *R,VOID **Out){
 assert(Current==TPL_APPLICATION&&G==&Guid&&R==(VOID *)0x5678);LocateCalls++;
 if(Nested){VOID *B=NULL;assert(Trace.Boot.AllocatePool(EfiBootServicesData,99,&B)==Returned&&B==(VOID *)0x2345);}
 if(InterruptCall){
  assert(EnumaServiceTraceSnapshot(&Snapshot));
  // A nested call may already have returned while its outer call is pending.
  assert(Snapshot.Count==9&&!Snapshot.Events[6].Returned&&Snapshot.Events[6].Call==3);
  assert(Snapshot.Events[8].Returned&&Snapshot.Events[8].Call==4);
 }
 if(Out)*Out=(VOID *)0x6789;return Returned;
}
static EFI_STATUS EFIAPI RejectNull(EFI_GUID *G,VOID *R,VOID **Out){
 assert(Current==TPL_APPLICATION&&!G&&!R);LocateCalls++;
 // Deliberately leave caller's output unchanged on failure.
 (void)Out;return EFI_INVALID_PARAMETER;
}
static VOID Setup(VOID){
 memset(&Boot,0,sizeof(Boot));memset(&System,0,sizeof(System));memset(&Trace,0,sizeof(Trace));
 mEnumaServiceTrace=NULL;LocateCalls=HandleCalls=AllocCalls=CrcCalls=CrcFail=Nested=InterruptCall=0;
 Current=TPL_APPLICATION;Returned=EFI_NOT_FOUND;
 System.Hdr.HeaderSize=sizeof(System);Boot.Hdr.HeaderSize=sizeof(Boot);System.BootServices=&Boot;
 Boot.RaiseTPL=Raise;Boot.RestoreTPL=Restore;Boot.CalculateCrc32=Crc;
 Boot.LocateProtocol=Locate;Boot.HandleProtocol=Handle;Boot.AllocatePool=Allocate;
 OriginalBoot=Boot;OriginalSystem=System;
}
int main(void){VOID *Out;unsigned I;EFI_STATUS Status;UINT32 Cursor;
 EFI_LOADED_IMAGE_PROTOCOL Loaded={0};EFI_GUID Display={0x4138022f,0x06c7,0x4f79,{0x9c,0x94,0x7e,0x33,0xb5,0x11,0xa4,0xe7}};
 Setup();assert(!EnumaServiceTraceSnapshot(&Snapshot));assert(EnumaServiceTracePrepare(&Trace,&System,0x1000,0x1000)==0);
 assert(!memcmp(&Boot,&OriginalBoot,sizeof(Boot))&&!memcmp(&System,&OriginalSystem,sizeof(System)));
 assert(Trace.System.BootServices==&Trace.Boot&&Trace.Published&&CrcCalls==2);
 assert(Trace.System.Hdr.CRC32==0x12345678&&Trace.Boot.Hdr.CRC32==0x12345678);
 assert(Trace.Boot.FreePool==Boot.FreePool&&Trace.Boot.Stall==Boot.Stall);
 assert(EnumaServiceTracePrepare(&Trace,&System,0x1000,0x1000)==EFI_ALREADY_STARTED);
 assert(Trace.Boot.LocateProtocol(&Guid,(VOID *)0x5678,&Out)==EFI_NOT_FOUND&&Out==(VOID *)0x6789&&LocateCalls==1);
 assert(Trace.Log.Count==2&&!Trace.Log.Events[0].Returned&&Trace.Log.Events[1].Returned&&Trace.Log.Events[1].Status==EFI_NOT_FOUND);
 assert(Trace.Log.Events[0].Call==Trace.Log.Events[1].Call&&Trace.Log.Events[0].CallerRva==MAX_UINT64);
 Returned=EFI_WARN_UNKNOWN_GLYPH;assert(Trace.Boot.HandleProtocol((VOID *)0x3456,&Guid,&Out)==Returned&&Out==(VOID *)0x4567);
 Returned=EFI_OUT_OF_RESOURCES;assert(Trace.Boot.AllocatePool(EfiBootServicesData,99,&Out)==Returned&&Out==(VOID *)0x2345);
 Nested=InterruptCall=1;Returned=0;assert(Trace.Boot.LocateProtocol(&Guid,(VOID *)0x5678,&Out)==0);
 assert(Trace.Log.Events[6].Call==3&&!Trace.Log.Events[6].Returned);
 assert(Trace.Log.Events[7].Call==4&&!Trace.Log.Events[7].Returned);
 assert(Trace.Log.Events[8].Call==4&&Trace.Log.Events[8].Returned);
 assert(Trace.Log.Events[9].Call==3&&Trace.Log.Events[9].Returned);
 // Snapshot was captured inside the outer call: its return must remain absent.
 Cursor=0;assert(!EnumaServiceReplayNext(&Snapshot,&Cursor,Refuse,NULL)&&Cursor==0);
 while(EnumaServiceReplayNext(&Snapshot,&Cursor,Sink,NULL)){}
 assert(Cursor==Snapshot.Count+1);
 Snapshot.Events[0].Sequence++;assert(!EnumaServiceReplayNext(&Snapshot,&Cursor,Sink,NULL));
 Nested=InterruptCall=0;
 for(I=0;I<100;I++)assert(Trace.Boot.AllocatePool(EfiBootServicesData,99,&Out)==0);
 assert(Trace.Log.Count==128&&Trace.Log.NextSequence==210&&Trace.Log.Dropped==82);
 assert(EnumaServiceTraceSnapshot(&Snapshot)&&!EnumaServiceTraceSnapshot(&Trace.Log));
 for(I=0;I<128;I++)assert(Snapshot.Events[(Snapshot.Head+I)%128].Sequence==82+I);
 EnumaServiceRecord(&Trace,100,1,0x1234,0,&Guid,FALSE,0);assert(Trace.Log.Events[(Trace.Log.Head+127)%128].CallerRva==0x234);
 Trace.Log.NextCall=MAX_UINT64;I=(unsigned)Trace.Log.NextSequence;assert(Trace.Boot.AllocatePool(EfiBootServicesData,99,&Out)==0&&Trace.Log.NextSequence==I);
 Trace.Log.NextCall=0;Trace.Log.NextSequence=MAX_UINT64;assert(Trace.Boot.AllocatePool(EfiBootServicesData,99,&Out)==0&&Trace.Log.NextSequence==MAX_UINT64);
 for(I=1;I<=2;I++){Setup();CrcFail=I;Status=EnumaServiceTracePrepare(&Trace,&System,0x1000,0x1000);assert(Status==EFI_DEVICE_ERROR&&!Trace.Published&&!mEnumaServiceTrace);}
 Setup();assert(EnumaServiceTracePrepare(&Trace,&System,MAX_UINTN,2)==EFI_INVALID_PARAMETER);
 assert(EnumaServiceTracePrepare(NULL,&System,1,2)==EFI_INVALID_PARAMETER);
 Boot.Hdr.HeaderSize--;assert(EnumaServiceTracePrepare(&Trace,&System,1,2)==EFI_UNSUPPORTED);
 Setup();Boot.AllocatePool=NULL;assert(EnumaServiceTracePrepare(&Trace,&System,1,2)==EFI_UNSUPPORTED);
 Setup();Loaded.SystemTable=&System;Loaded.ImageBase=(VOID *)0x1000;Loaded.ImageSize=0x2000;Loaded.ImageCodeType=EfiBootServicesCode;
 assert(EnumaAttachDisplayTrace(&Trace,&Guid,&Loaded,&System)==EFI_NOT_FOUND&&Loaded.SystemTable==&System);
 Loaded.ImageCodeType=EfiLoaderCode;assert(EnumaAttachDisplayTrace(&Trace,&Display,&Loaded,&System)==EFI_UNSUPPORTED);
 Loaded.ImageCodeType=EfiBootServicesCode;CrcFail=2;
 assert(EnumaAttachDisplayTrace(&Trace,&Display,&Loaded,&System)==EFI_DEVICE_ERROR&&Loaded.SystemTable==&System);
 Setup();assert(EnumaAttachDisplayTrace(&Trace,&Display,&Loaded,&System)==EFI_SUCCESS&&Loaded.SystemTable==&Trace.System);
 assert(System.BootServices==&Boot&&Trace.Original==&Boot);
 // Simulated later driver callback still has valid private tables.
 assert(Loaded.SystemTable->BootServices->AllocatePool(EfiBootServicesData,99,&Out)==EFI_NOT_FOUND);
 assert(EnumaAttachDisplayTrace(&Trace,&Display,&Loaded,&System)==EFI_UNSUPPORTED);
 // Differential call: wrapped vs original preserve failure and untouched output.
 Setup();assert(EnumaServiceTracePrepare(&Trace,&System,0x1000,0x1000)==0);
 Boot.LocateProtocol=RejectNull;Out=(VOID *)0x9876;
 assert(Boot.LocateProtocol(NULL,NULL,&Out)==EFI_INVALID_PARAMETER&&Out==(VOID *)0x9876&&LocateCalls==1);
 assert(Trace.Boot.LocateProtocol(NULL,NULL,&Out)==EFI_INVALID_PARAMETER&&Out==(VOID *)0x9876&&LocateCalls==2);
 assert(Trace.Log.Count==2&&!Trace.Log.Events[0].HasGuid&&Trace.Log.Events[1].Status==EFI_INVALID_PARAMETER);
 // Empty/invalid snapshot and partial sink failure cannot consume a row.
 assert(EnumaServiceTraceSnapshot(&Snapshot));Cursor=1;
 assert(!EnumaServiceReplayNext(&Snapshot,&Cursor,Refuse,NULL)&&Cursor==1);
 PartialCalls=0;assert(!EnumaServiceReplayNext(&Snapshot,&Cursor,Partial,NULL)&&Cursor==1&&PartialCalls==1);
 assert(!memcmp(PartialBytes,"OEM seq",7));
 Snapshot.Dropped++;assert(!EnumaServiceReplayNext(&Snapshot,&Cursor,Sink,NULL));
 puts("OEM service trace PASS: transparent status/arguments, real return pairing, nested calls, live in-flight snapshot, bounded loss, exhaustion, CRC failure, original table unchanged");return 0;
}
