// SPDX-License-Identifier: BSD-2-Clause-Patent
#define ENUMA_NATIVE_ROUTE_CPU_TEXT 1
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "PixelTransaction.h"
static ENUMA_INHERITED_FRAME F;
static ENUMA_U32 Pixels[4096],Original[4096],R,W,B,H,V,Restore,FailR,FailW;
static unsigned Index(ENUMA_U64 A) {
  assert(A>=F.Base&&!(A&3));ENUMA_U64 D=A-F.Base;unsigned Y=D/F.Stride,X=(D%F.Stride)/4;
  assert(Y<32&&X<128);return Y*128+X;
}
static int Read(void *C,ENUMA_U64 A,ENUMA_U32 *Out) {
  assert(C==&F&&R<12288);unsigned I=Index(A);R++;*Out=Pixels[I];return R!=FailR;
}
static int Write(void *C,ENUMA_U64 A,ENUMA_U32 Value) {
  assert(C==&F&&V==1&&W<8192);unsigned I=Index(A);W++;
  if(!H) { assert(I==W-1&&Value==EnumaPixelTextAt(&F,I)); }
  else { assert(I==Restore++&&Value==Original[I]); }
  if(W==FailW) { return 0; }Pixels[I]=Value;return 1;
}
static int Validate(void *C,const ENUMA_INHERITED_FRAME *Frame) { assert(C==&F&&Frame==&F&&R==4096&&!W&&!V&&!H&&B==1);V++;return 1; }
static int Barrier(void *C) { assert(C==&F&&B<3);B++;return 1; }
static int Hold(void *C,ENUMA_U32 Us) { assert(C==&F&&!H&&Us==500000);H++;return 1; }
static void Init(unsigned Stride) {
  memset(&F,0,sizeof(F));F.Base=0x9c000004;F.Width=1600;F.Height=2560;F.Stride=Stride;F.Bytes=(ENUMA_U64)Stride*2560;F.Requirements=22;
  F.RedMask=0xff0000;F.GreenMask=0xff00;F.BlueMask=0xff;F.ReservedMask=0xff000000;
  for(unsigned I=0;I<4096;I++) { Pixels[I]=Original[I]=0x10203040u+I; }
  R=W=B=H=V=Restore=FailR=FailW=0;
}
static unsigned Run(void) { return EnumaPixelTransaction(&F,3,4,Read,Write,Validate,Barrier,Hold,&F); }
int main(void) {
  assert(ENUMA_PIXEL_ROWS==32&&ENUMA_PIXEL_WORDS==4096);
  for(unsigned A=0;A<4;A++) for(unsigned Red=0;Red<4;Red++) for(unsigned Green=0;Green<4;Green++) {
    if(A==Red||A==Green||Red==Green) { continue; }unsigned Blue=6-A-Red-Green;Init(6404);
    F.ReservedMask=255u<<(A*8);F.RedMask=255u<<(Red*8);F.GreenMask=255u<<(Green*8);F.BlueMask=255u<<(Blue*8);
    unsigned White=0;for(unsigned I=0;I<4096;I++) { unsigned P=EnumaPixelTextAt(&F,I);assert(P==0xffffffffu||P==F.ReservedMask);White+=P==0xffffffffu; }
    assert(White==992);assert(Run()==5&&R==12288&&W==8192&&B==3&&H==1&&Restore==4096&&!memcmp(Pixels,Original,sizeof(Pixels)));
  }
  for(unsigned Stride=6400;Stride<=8192;Stride+=1792) { Init(Stride);assert(Run()==5&&!memcmp(Pixels,Original,sizeof(Pixels))); }
  for(unsigned N=1;N<=12288;N++) {
    Init(6404);FailR=N;unsigned S=Run();assert(S==(N<=4096?1:N<=8192?2:4));
    if(N<=4096) { assert(!W&&!H&&!V); }else { assert(Restore==4096); }assert(!memcmp(Pixels,Original,sizeof(Pixels)));
  }
  for(unsigned N=1;N<=8192;N++) {
    Init(6404);FailW=N;assert(Run()==(N<=4096?2:4));assert(Restore==4096);
    if(N<=4096) { assert(!memcmp(Pixels,Original,sizeof(Pixels))); }
  }
  puts("PASS: text128x32/4x bitmap992 white pixels,24 byte permutations;12288 read and8192 write failure positions; exact restore attempts/counts, real stride and no hardware");
}
