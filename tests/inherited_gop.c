// SPDX-License-Identifier: BSD-2-Clause-Patent
// Real UEFI headers + production backend + production Mu FrameBufferBltLib.
// Only allocation, boot-service TPL and BaseLib memory primitives are modeled.
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#undef NULL
#include "InheritedGop.h"
#include <Library/BaseLib.h>
#include <Library/BaseMemoryLib.h>
#include <Library/MemoryAllocationLib.h>
static unsigned AllocCalls,FailAt,Live,TplDepth; static EFI_STATUS Validation;
static EFI_TPL EFIAPI raise_tpl(EFI_TPL T) { assert(T==TPL_NOTIFY); assert(!TplDepth++); return TPL_APPLICATION; }
static VOID EFIAPI restore_tpl(EFI_TPL T) { assert(T==TPL_APPLICATION&&TplDepth==1); TplDepth--; }
static EFI_BOOT_SERVICES BS={.RaiseTPL=raise_tpl,.RestoreTPL=restore_tpl};
EFI_BOOT_SERVICES *gBS=&BS;
VOID *EFIAPI AllocatePool(UINTN N) { if(++AllocCalls==FailAt) { return NULL; } void *P=malloc(N); if(P) { Live++; } return P; }
VOID *EFIAPI AllocateZeroPool(UINTN N) { VOID *P=AllocatePool(N); if(P) { memset(P,0,N); } return P; }
VOID *EFIAPI AllocateCopyPool(UINTN N,CONST VOID *V) { VOID *P=AllocatePool(N); if(P) { memcpy(P,V,N); } return P; }
VOID EFIAPI FreePool(VOID *P) { assert(P&&Live); Live--; free(P); }
VOID *EFIAPI CopyMem(VOID *D,CONST VOID *S,UINTN N) { return memmove(D,S,N); }
VOID *EFIAPI SetMem(VOID *D,UINTN N,UINT8 V) { return memset(D,V,N); }
VOID *EFIAPI SetMem32(VOID *D,UINTN N,UINT32 V) { assert(!(N&3)); for(UINTN I=0;I<N/4;I++) { ((UINT32 *)D)[I]=V; } return D; }
VOID *EFIAPI SetMem64(VOID *D,UINTN N,UINT64 V) { assert(!(N&7)); for(UINTN I=0;I<N/8;I++) { ((UINT64 *)D)[I]=V; } return D; }
INTN EFIAPI HighBitSet32(UINT32 V) { return V?31-__builtin_clz(V):-1; }
static EFI_STATUS EFIAPI validate(VOID *C,CONST ENUMA_INHERITED_FRAME *F) { assert(C==&Validation&&F->Base); return Validation; }
static unsigned char Memory[32+80*8+32] __attribute__((aligned(16)));
static ENUMA_INHERITED_FRAME frame(void) {
  ENUMA_INHERITED_FRAME F={0}; F.Base=(UINTN)(Memory+32); F.Bytes=80*8;
  F.Width=16; F.Height=8; F.Stride=80; F.PipeMask=3; F.CtlMask=1; F.IntfMask=6;
  F.RedMask=0xff0000; F.GreenMask=0xff00; F.BlueMask=0xff; F.ReservedMask=0xff000000;
  return F;
}
static void guards(void) {
  for(unsigned I=0;I<32;I++) { assert(Memory[I]==0xa5&&Memory[sizeof(Memory)-1-I]==0xa5); }
  for(unsigned Y=0;Y<8;Y++) { for(unsigned X=64;X<80;X++) { assert(Memory[32+Y*80+X]==0xa5); } }
}
int main(void) {
  ENUMA_INHERITED_FRAME F=frame(); EFI_GRAPHICS_OUTPUT_PROTOCOL *G=(VOID *)1;
  EFI_GRAPHICS_OUTPUT_MODE_INFORMATION *Info; UINTN Size; unsigned Permutations=0;
  memset(Memory,0xa5,sizeof(Memory)); F.Requirements=ENUMA_REQUIRE_ALL;
  assert(EnumaGopCreate(&F,validate,&Validation,&G)==EFI_NOT_READY&&!G&&!Live); F.Requirements=0;
  assert(EnumaGopCreate(&F,NULL,&Validation,&G)==EFI_INVALID_PARAMETER&&!G);
  for(unsigned Fail=1;Fail<=2;Fail++) { AllocCalls=0; FailAt=Fail; assert(EnumaGopCreate(&F,validate,&Validation,&G)==EFI_OUT_OF_RESOURCES&&!G&&!Live); } FailAt=0;
  Validation=EFI_WARN_UNKNOWN_GLYPH; assert(EnumaGopCreate(&F,validate,&Validation,&G)==EFI_NOT_READY&&!G); Validation=0;
  // All 24 byte permutations use the real Mu bitmask implementation.
  for(unsigned R=0;R<4;R++) for(unsigned B=0;B<4;B++) for(unsigned Gr=0;Gr<4;Gr++) {
    if(R==B||R==Gr||B==Gr) { continue; }
    unsigned A=6-R-B-Gr; F.RedMask=255u<<(R*8); F.BlueMask=255u<<(B*8); F.GreenMask=255u<<(Gr*8); F.ReservedMask=255u<<(A*8);
    assert(EnumaGopCreate(&F,validate,&Validation,&G)==EFI_SUCCESS&&Live==2);
    for(unsigned I=0;I<sizeof(Memory);I++) { assert(Memory[I]==0xa5); } // creation has no pixel access
    assert(G->Mode->MaxMode==1&&G->Mode->Info->PixelsPerScanLine==20);
    Info=(VOID *)1; Size=1; assert(G->QueryMode(G,1,&Size,&Info)==EFI_INVALID_PARAMETER&&!Info&&!Size);
    assert(G->QueryMode(G,0,&Size,&Info)==EFI_SUCCESS&&Size==sizeof(*Info)); assert(Info!=G->Mode->Info&&Info->PixelInformation.RedMask==F.RedMask); FreePool(Info);
    FailAt=AllocCalls+1; assert(G->QueryMode(G,0,&Size,&Info)==EFI_OUT_OF_RESOURCES&&!Info&&!Size); FailAt=0;
    assert(G->SetMode(G,1)==EFI_UNSUPPORTED);
    EFI_GRAPHICS_OUTPUT_BLT_PIXEL Pixel={.Blue=0x12,.Green=0x34,.Red=0x56}, Readback[12]; memset(Readback,0,sizeof(Readback));
    assert(G->Blt(G,&Pixel,EfiBltVideoFill,0,0,2,1,3,2,0)==EFI_SUCCESS);
    assert(Memory[32+80+8+R]==0x56&&Memory[32+80+8+B]==0x12&&Memory[32+80+8+Gr]==0x34);
    assert(G->Blt(G,Readback,EfiBltVideoToBltBuffer,2,1,1,1,3,2,16)==EFI_SUCCESS);
    assert(Readback[5].Red==0x56&&Readback[5].Blue==0x12&&Readback[10].Green==0x34);
    assert(G->Blt(G,Readback,EfiBltBufferToVideo,1,1,6,3,3,2,16)==EFI_SUCCESS);
    assert(G->Blt(G,NULL,EfiBltVideoToVideo,6,3,7,4,3,2,0)==EFI_SUCCESS); // overlaps
    unsigned char Before[sizeof(Memory)]; memcpy(Before,Memory,sizeof(Memory));
    assert(G->Blt(G,NULL,EfiBltVideoFill,0,0,0,0,1,1,0)==EFI_INVALID_PARAMETER);
    assert(G->Blt(G,&Pixel,EfiBltVideoFill,0,0,MAX_UINTN,0,2,1,0)==EFI_INVALID_PARAMETER);
    assert(G->Blt(G,Readback,EfiBltVideoToBltBuffer,0,0,MAX_UINTN,0,1,1,0)==EFI_INVALID_PARAMETER);
    assert(G->Blt(G,Readback,EfiBltBufferToVideo,0,MAX_UINTN,0,0,1,1,4)==EFI_INVALID_PARAMETER);
    assert(G->Blt(G,Readback,EfiBltBufferToVideo,1,0,0,0,2,1,8)==EFI_INVALID_PARAMETER);
    Validation=EFI_DEVICE_ERROR; assert(G->SetMode(G,0)==EFI_NOT_READY);
    assert(G->Blt(G,&Pixel,EfiBltVideoFill,0,0,0,0,1,1,0)==EFI_NOT_READY);
    assert(!memcmp(Before,Memory,sizeof(Memory))&&!TplDepth); Validation=0;
    assert(G->SetMode(G,0)==EFI_SUCCESS);
    for(unsigned Y=0;Y<8;Y++) for(unsigned X=0;X<64;X++) { assert(!Memory[32+Y*80+X]); }
    guards(); EnumaGopDestroy(G); assert(!Live); memset(Memory,0xa5,sizeof(Memory)); Permutations++;
  }
  F=frame(); F.RedMask=F.BlueMask; assert(EnumaGopCreate(&F,validate,&Validation,&G)==EFI_UNSUPPORTED&&!G);
  F=frame(); F.Bytes--; assert(EnumaGopCreate(&F,validate,&Validation,&G)==EFI_UNSUPPORTED&&!G);
  F=frame(); F.Base=MAX_UINTN-3; assert(EnumaGopCreate(&F,validate,&Validation,&G)==EFI_UNSUPPORTED&&!G);
  assert(Permutations==24&&!Live&&!TplDepth); puts("PASS: real Mu GOP Blt, 24 channel permutations, 4 operations, clear, bounds, stale ownership and allocation cleanup");
}
