// SPDX-License-Identifier: BSD-2-Clause-Patent
// GopTestSupport.h is the unchanged allocation/TPL/RAM support prefix extracted
// from tests/inherited_gop.c into the new output directory, never old reports.
#include "GopTestSupport.h"
#include "InheritedGopAccess.h"
static unsigned Reads,Writes,Syncs,FailRead,FailWrite,FailSync;
static ENUMA_INHERITED_FRAME *AccessFrame;
static EFI_STATUS EFIAPI Read32(VOID *C,UINT64 A,UINT32 *V) {
  assert(C==AccessFrame&&A>=AccessFrame->Base&&A+4<=AccessFrame->Base+AccessFrame->Bytes&&!(A&3));
  Reads++;if(Reads==FailRead){return EFI_DEVICE_ERROR;}*V=*(UINT32 *)(UINTN)A;return EFI_SUCCESS;
}
static EFI_STATUS EFIAPI Write32(VOID *C,UINT64 A,UINT32 V) {
  assert(C==AccessFrame&&A>=AccessFrame->Base&&A+4<=AccessFrame->Base+AccessFrame->Bytes&&!(A&3));
  assert((V&AccessFrame->ReservedMask)==AccessFrame->ReservedMask);
  Writes++;if(Writes==FailWrite){return EFI_DEVICE_ERROR;}*(UINT32 *)(UINTN)A=V;return EFI_SUCCESS;
}
static EFI_STATUS EFIAPI Sync(VOID *C) {assert(C==AccessFrame);Syncs++;return Syncs==FailSync?EFI_DEVICE_ERROR:EFI_SUCCESS;}
static void Reset(void) {Reads=Writes=Syncs=FailRead=FailWrite=FailSync=0;Validation=0;FailAt=0;memset(Memory,0xa5,sizeof Memory);}
static EFI_GRAPHICS_OUTPUT_PROTOCOL *CreateWt(ENUMA_INHERITED_FRAME *F) {
  EFI_GRAPHICS_OUTPUT_PROTOCOL *G=NULL;AccessFrame=F;
  ENUMA_GOP_ACCESS A={1,sizeof A,3,F,Read32,Write32,Sync};
  assert(EnumaGopCreateWtOpaque(F,validate,&Validation,&A,&G)==EFI_SUCCESS&&G);return G;
}
int main(void) {
  ENUMA_INHERITED_FRAME F=frame();EFI_GRAPHICS_OUTPUT_PROTOCOL *G=NULL;
  ENUMA_GOP_ACCESS A={1,sizeof A,3,&F,Read32,Write32,Sync};AccessFrame=&F;Reset();
  F.Requirements=22;assert(EnumaGopCreateWtOpaque(&F,validate,&Validation,&A,&G)==EFI_NOT_READY&&!G&&!Live);F.Requirements=0;
  A.Policy=2;assert(EnumaGopCreateWtOpaque(&F,validate,&Validation,&A,&G)==EFI_INVALID_PARAMETER&&!G);A.Policy=3;
  A.Synchronize=NULL;assert(EnumaGopCreateWtOpaque(&F,validate,&Validation,&A,&G)==EFI_INVALID_PARAMETER&&!G);A.Synchronize=Sync;
  unsigned Permutations=0;
  for(unsigned R=0;R<4;R++)for(unsigned B=0;B<4;B++)for(unsigned Green=0;Green<4;Green++) {
    if(R==B||R==Green||B==Green){continue;}unsigned Alpha=6-R-B-Green;
    Reset();F=frame();F.RedMask=255u<<(R*8);F.BlueMask=255u<<(B*8);F.GreenMask=255u<<(Green*8);F.ReservedMask=255u<<(Alpha*8);
    G=CreateWt(&F);assert(!Reads&&!Writes&&!Syncs);
    EFI_GRAPHICS_OUTPUT_BLT_PIXEL Pixel={0x12,0x34,0x56,0},Pixels[12]={{0}};
    assert(G->Blt(G,&Pixel,EfiBltVideoFill,0,0,2,1,3,2,0)==EFI_SUCCESS);
    assert(Writes==6&&Syncs==2&&!Reads&&Memory[32+80+8+R]==0x56&&Memory[32+80+8+Alpha]==255);
    assert(G->Blt(G,Pixels,EfiBltVideoToBltBuffer,2,1,1,1,3,2,16)==EFI_SUCCESS);
    assert(Pixels[5].Red==0x56&&Pixels[10].Blue==0x12&&Pixels[5].Reserved==0);
    assert(G->Blt(G,Pixels,EfiBltBufferToVideo,1,1,6,3,3,2,16)==EFI_SUCCESS);
    // Independently model overlapping copy, both down/right and up/left.
    for(unsigned Reverse=0;Reverse<2;Reverse++) {
      unsigned Sx=Reverse?3:1,Sy=Reverse?2:1,Dx=Reverse?1:3,Dy=Reverse?1:2;
      UINT32 Expected[8][16];
      for(unsigned Y=0;Y<8;Y++)for(unsigned X=0;X<16;X++) {
        Expected[Y][X]=(0x12345678u+Y*16+X)|F.ReservedMask;
        *(UINT32 *)(Memory+32+Y*80+X*4)=Expected[Y][X];
      }
      UINT32 Copy[4][5];for(unsigned Y=0;Y<4;Y++)for(unsigned X=0;X<5;X++){Copy[Y][X]=Expected[Sy+Y][Sx+X];}
      for(unsigned Y=0;Y<4;Y++)for(unsigned X=0;X<5;X++){Expected[Dy+Y][Dx+X]=Copy[Y][X];}
      assert(G->Blt(G,NULL,EfiBltVideoToVideo,Sx,Sy,Dx,Dy,5,4,0)==EFI_SUCCESS);
      for(unsigned Y=0;Y<8;Y++)for(unsigned X=0;X<16;X++){assert(*(UINT32 *)(Memory+32+Y*80+X*4)==Expected[Y][X]);}
    }
    unsigned Before=Writes;
    assert(G->Blt(G,(VOID *)(MAX_UINTN-3),EfiBltVideoFill,0,0,0,0,1,1,0)==EFI_INVALID_PARAMETER);
    assert(G->Blt(G,(VOID *)F.Base,EfiBltBufferToVideo,0,0,0,0,1,1,4)==EFI_INVALID_PARAMETER&&Writes==Before);
    assert(G->SetMode(G,0)==EFI_SUCCESS);
    for(unsigned Y=0;Y<8;Y++)for(unsigned X=0;X<16;X++){assert(*(UINT32 *)(Memory+32+Y*80+X*4)==F.ReservedMask);}
    guards();EnumaGopDestroy(G);assert(!Live);Permutations++;
  }
  for(unsigned Fault=0;Fault<5;Fault++) {
    Reset();F=frame();G=CreateWt(&F);EFI_GRAPHICS_OUTPUT_BLT_PIXEL P={1,2,3,0};
    if(Fault==0){FailWrite=2;}if(Fault==1){FailRead=1;}if(Fault==2){FailSync=1;}if(Fault==3){FailSync=2;}if(Fault==4){Validation=EFI_DEVICE_ERROR;}
    EFI_STATUS S=Fault==1?G->Blt(G,&P,EfiBltVideoToBltBuffer,0,0,0,0,1,1,0):G->Blt(G,&P,EfiBltVideoFill,0,0,0,0,3,1,0);
    assert(S!=EFI_SUCCESS);ENUMA_GOP_ACCESS_STATE State;
    assert(EnumaGopGetAccessState(G,&State)==EFI_SUCCESS&&State.Latched&&State.Fault==EFI_DEVICE_ERROR);
    unsigned Before=Writes;Validation=0;FailWrite=FailRead=FailSync=0;
    assert(G->SetMode(G,0)==EFI_NOT_READY&&Writes==Before);EnumaGopDestroy(G);assert(!Live);
  }
  assert(Permutations==24);puts("PASS: WT opaque 24 byte layouts, four Blt operations, overlap, stride/guard/overflow, opaque clear, I/O and validation faults latch without later writes; requirements22 still rejected");
}
