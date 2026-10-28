// Host replay of the actual pinned page-table C implementation. No device I/O.
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#undef NULL
#include "replay_core.c"
static unsigned Allocations,Failure,Live;
VOID *EFIAPI AllocatePages(UINTN N){
  if(++Allocations==Failure)return NULL;
  void *p=aligned_alloc(4096,N*4096);assert(p);Live++;return p;
}
VOID EFIAPI FreePages(VOID *P,UINTN N){(void)N;assert(Live);Live--;free(P);}
VOID *EFIAPI ZeroMem(VOID *P,UINTN N){return memset(P,0,N);}
UINTN EFIAPI ArmReadCurrentEL(VOID){return 4;}
UINTN EFIAPI ArmReadHcr(VOID){return 0;}
UINTN EFIAPI ArmGetTCR(VOID){return 16;}
BOOLEAN EFIAPI ArmLpa2Enabled(VOID){return FALSE;}
BOOLEAN EFIAPI ArmMmuEnabled(VOID){return FALSE;}
VOID *EFIAPI InvalidateDataCacheRange(VOID *P,UINTN N){(void)N;return P;}
VOID EFIAPI ArmUpdateTranslationTableEntry(VOID *E,VOID *A){(void)E;(void)A;}
VOID EFIAPI ArmReplaceLiveTranslationEntry(UINT64 *E,UINT64 V,UINT64 A,BOOLEAN D){(void)A;(void)D;*E=V;}
VOID EFIAPI DebugAssert(CONST CHAR8 *F,UINTN L,CONST CHAR8 *D){fprintf(stderr,"%s:%llu %s\n",F,L,D);abort();}
BOOLEAN EFIAPI DebugAssertEnabled(VOID){return TRUE;}
BOOLEAN EFIAPI DebugPrintEnabled(VOID){return FALSE;}
BOOLEAN EFIAPI DebugPrintLevelEnabled(CONST UINTN L){(void)L;return FALSE;}
VOID EFIAPI DebugPrint(UINTN L,CONST CHAR8 *F,...){(void)L;(void)F;}
static UINT64 leaf(UINT64 *T,UINT64 A){
 for(unsigned l=0;l<4;l++){
  UINT64 e=T[(A>>(39-9*l))&511];
  if(!IsTableEntry(e,l))return e;
  T=(void*)(uintptr_t)GetOutputAddress(e,FALSE,0);
 }
 abort();
}
#include "replay_map.c"
static void run(int omit,unsigned fail){
 UINT64 *t=aligned_alloc(4096,4096);memset(t,0,4096);
 Allocations=0;Failure=fail;Live=1;EFI_STATUS s=0;
 for(unsigned i=0;i<sizeof(mRegions)/sizeof(mRegions[0]);i++){
  if(mRegions[i].HobOption==HobOnlyNoCacheSetting)continue;
  if(omit&&mRegions[i].Address==0xaeb0000)continue;
  ARM_MEMORY_REGION_DESCRIPTOR m={mRegions[i].Address,mRegions[i].Address,mRegions[i].Length,mRegions[i].ArmAttributes};
  s=FillTranslationTable(t,&m,FALSE);if(EFI_ERROR(s))break;
 }
 if(!fail){
  for(UINT64 a=0xaeb0000;a<0xaeb3000;a+=4096){
   UINT64 e=leaf(t,a);
   if(omit)assert(!(e&1));else {assert((e&3)==3);assert((e&TT_ADDRESS_MASK_BLOCK_ENTRY)==a);assert(e&TT_AF);}
  }
  assert(leaf(t,0xae94000)&1);assert(leaf(t,0xae96000)&1);assert(leaf(t,0xaf02000)&1);
 }else assert(s==EFI_OUT_OF_RESOURCES);
 FreePageTablesRecursive(t,0,FALSE,0);assert(!Live);
}
int main(void){run(0,0);unsigned n=Allocations;run(1,0);for(unsigned i=1;i<=n;i++)run(0,i);printf("PASS actual recursive mapper, all regions, VBIF omission and %u allocation failures\n",n);}
