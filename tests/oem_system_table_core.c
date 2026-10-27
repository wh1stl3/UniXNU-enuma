// SPDX-License-Identifier: BSD-2-Clause-Patent
// Built with the actual patched CoreInstallConfigurationTable source.
#define main ExistingTraceRegressionMain
#include "oem_service_trace.c"
#undef main
#include <stdlib.h>
#include <setjmp.h>
EFI_SYSTEM_TABLE *gDxeCoreST=&System;
extern UINTN mSystemTableAllocateSize;
extern EFI_STATUS EFIAPI CoreInstallConfigurationTable(EFI_GUID *,VOID *);
static unsigned Notifies,Frees,FreeReentries,Recursive,InRecursive,FailAllocation,FailCrc;
static jmp_buf StopJump;
static EFI_STATUS EFIAPI RealCrc(VOID *Data,UINTN N,UINT32 *Out) {
  UINT32 C=~0U;UINT8 *P=Data;
  if(FailCrc){return EFI_DEVICE_ERROR;}
  for(UINTN I=0;I<N;I++){C^=P[I];for(unsigned B=0;B<8;B++){C=(C>>1)^((0U-(C&1))&0xedb88320U);}}
  *Out=~C;return EFI_SUCCESS;
}
static void Coherent(void) {
  EFI_SYSTEM_TABLE Copy=Trace.System;UINT32 C=Copy.Hdr.CRC32,Computed;
  assert(Copy.ConfigurationTable==System.ConfigurationTable);
  assert(Copy.NumberOfTableEntries==System.NumberOfTableEntries);
  assert(Copy.BootServices==&Trace.Boot&&System.BootServices==&Boot);
  Copy.Hdr.CRC32=0;assert(RealCrc(&Copy,sizeof(Copy),&Computed)==0&&C==Computed);
}
VOID EnumaOemCoreSyncSystemTable(EFI_SYSTEM_TABLE *S) {
  if(EFI_ERROR(EnumaServiceTraceSyncSystem(S))){longjmp(StopJump,1);}
}
BOOLEAN EFIAPI CompareGuid(CONST GUID *A,CONST GUID *B){return memcmp(A,B,sizeof(*A))==0;}
GUID *EFIAPI CopyGuid(GUID *A,CONST GUID *B){return memcpy(A,B,sizeof(*A));}
VOID *AllocateRuntimePool(UINTN N){return FailAllocation?NULL:calloc(1,N);}
EFI_STATUS CoreFreePool(VOID *P){
  EFI_GUID G=Guid;G.Data1=0;
  Coherent();assert(Trace.System.ConfigurationTable!=P);Frees++;
  assert(CoreInstallConfigurationTable(&G,(VOID *)4)==0);FreeReentries++;Coherent();
  free(P);return 0;
}
VOID CalculateEfiHdrCrc(EFI_TABLE_HEADER *H){H->CRC32=0;assert(RealCrc(H,H->HeaderSize,&H->CRC32)==0);}
VOID CoreNotifySignalList(CONST EFI_GUID *G){
  Coherent();Notifies++;
  if(Recursive&&!InRecursive){
    EFI_GUID Next=*G;Next.Data1+=100;InRecursive=1;
    assert(CoreInstallConfigurationTable(&Next,(VOID *)0x8888)==0);
    Coherent();InRecursive=0;
  }
}
int main(void) {
  EFI_GUID G=Guid;
  Setup();Boot.CalculateCrc32=RealCrc;Boot.InstallConfigurationTable=CoreInstallConfigurationTable;
  assert(EnumaServiceTraceSyncSystem(&System)==0); // no published trace
  assert(EnumaServiceTracePrepare(&Trace,&System,0x1000,0x1000)==0);
  assert(EnumaServiceTraceSyncSystem(&OriginalSystem)==EFI_INVALID_PARAMETER);
  assert(CoreInstallConfigurationTable(NULL,(VOID *)1)==EFI_INVALID_PARAMETER);
  assert(CoreInstallConfigurationTable(&G,NULL)==EFI_NOT_FOUND);
  FailAllocation=1;assert(CoreInstallConfigurationTable(&G,(VOID *)1)==EFI_OUT_OF_RESOURCES);
  // Core's allocation-size increment on failure is existing upstream behavior.
  // Reset the fixture's allocation bookkeeping before testing successful calls.
  mSystemTableAllocateSize=0;FailAllocation=0;Coherent();
  for(unsigned I=0;I<17;I++){G.Data1=I;assert(CoreInstallConfigurationTable(&G,(VOID *)1)==0);Coherent();}
  assert(Frees==1&&FreeReentries==1&&System.NumberOfTableEntries==17);
  Recursive=1;assert(Trace.System.BootServices->InstallConfigurationTable(&G,(VOID *)2)==0);
  assert(System.NumberOfTableEntries==18);Recursive=0;
  assert(CoreInstallConfigurationTable(&G,NULL)==0);Coherent();assert(System.NumberOfTableEntries==17);
  unsigned Before=Notifies;G.Data1=0;FailCrc=1;
  if(!setjmp(StopJump)){CoreInstallConfigurationTable(&G,(VOID *)3);assert(0);}
  assert(Notifies==Before);FailCrc=0;
  free(System.ConfigurationTable);
  puts("PASS: real Core add/update/delete/growth/free, notification reentry, allocation failure, CRC and fail-closed before notify");
  return 0;
}
