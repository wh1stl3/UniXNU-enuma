// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "CpuStage1.h"
typedef struct { unsigned Calls,Fail,Kind;ENUMA_U64 First,Last; } TEST;
static int Translate(void *Opaque,ENUMA_U64 Page,ENUMA_U32 Write,ENUMA_U64 *Par) {
  TEST *T=Opaque;unsigned N=T->Calls++;
  assert(Page==T->First+(ENUMA_U64)(N/2)*4096&&Write==(N%2));
  assert(Page>=0x9c000000ULL&&Page<0x9e400000ULL&&N<18432);
  T->Last=Page;*Par=Page|0xbb00000000000000ULL;
  if(T->Calls==T->Fail) {
    if(T->Kind==0) { return 0; }
    if(T->Kind==1) { return -1; }
    if(T->Kind==2) { return 2; }
    if(T->Kind==3) { *Par=1; }
    if(T->Kind==4) { *Par^=4096; }
    if(T->Kind==5) { *Par^=1ULL<<48; }
    if(T->Kind==6) { *Par^=1ULL<<56; }
  }
  return 1;
}
static unsigned Check(ENUMA_INHERITED_FRAME *F,unsigned Fail,unsigned Kind,unsigned Expected) {
  TEST T={0};ENUMA_INHERITED_FRAME Copy=*F;T.First=F->Base&~4095ULL;T.Fail=Fail;T.Kind=Kind;
  assert(EnumaCpuStage1(F,Translate,&T)==Expected);assert(memcmp(F,&Copy,sizeof(Copy))==0);return T.Calls;
}
typedef struct { TEST Query;unsigned Attr,Fault; } ATTRIBUTE;
static int AttrTranslate(void *Opaque,ENUMA_U64 Page,ENUMA_U32 Write,ENUMA_U64 *Par) {
  ATTRIBUTE *A=Opaque;int S=Translate(&A->Query,Page,Write,Par);
  if(A->Query.Calls==A->Query.Fail) { *Par=Page|((ENUMA_U64)A->Attr<<56)|A->Fault; }
  return S;
}
typedef struct { TEST Query;unsigned Attr,Other,ChangeAt; } POLICY;
static int PolicyTranslate(void *Opaque,ENUMA_U64 Page,ENUMA_U32 Write,ENUMA_U64 *Par) {
  POLICY *P=Opaque;int S=Translate(&P->Query,Page,Write,Par);
  if(S==1&&!(*Par&1)) {
    unsigned A=P->ChangeAt&&P->Query.Calls>=P->ChangeAt?P->Other:P->Attr;
    *Par=(*Par&0x00ffffffffffffffULL)|((ENUMA_U64)A<<56);
  }
  return S;
}
typedef struct { ENUMA_U64 Expected;unsigned Count,Value,BarrierCount,RequireBarrier;int Result,BarrierResult; } WORD;
static int WordRead(void *Opaque,ENUMA_U64 Address,ENUMA_U32 *Value) {
  WORD *W=Opaque;assert(Address==W->Expected&&!W->Count);
  if(W->RequireBarrier) { assert(W->BarrierCount==1&&W->BarrierResult==1); }
  W->Count++;*Value=W->Value;return W->Result;
}
static int WordBarrier(void *Opaque) {
  WORD *W=Opaque;assert(!W->Count&&!W->BarrierCount);W->BarrierCount++;return W->BarrierResult;
}
typedef struct { ENUMA_U64 Base;unsigned Stride,Calls,Barriers,FailAt;int BarrierResult; } ROI;
static int RoiBarrier(void *Opaque) { ROI *R=Opaque;assert(!R->Calls&&!R->Barriers);R->Barriers++;return R->BarrierResult; }
static int RoiRead(void *Opaque,ENUMA_U64 Address,ENUMA_U32 *Value) {
  ROI *R=Opaque;assert(R->Barriers==1&&R->Calls<1024);
  assert(Address==R->Base+(ENUMA_U64)(R->Calls/128)*R->Stride+(R->Calls%128)*4);
  R->Calls++;*Value=R->Calls*0x1234567u;return R->Calls==R->FailAt?0:1;
}
int main(void) {
  ENUMA_INHERITED_FRAME F={0},V;unsigned I,K,Count;
  F.Base=0x9c000000ULL;F.Width=1600;F.Height=2560;F.Stride=6400;F.Bytes=(ENUMA_U64)6400*2560;F.Requirements=22;
  Count=Check(&F,0,0,5);assert(Count==8000);
  for(I=1;I<=Count;I++) { for(K=0;K<7;K++) { assert(Check(&F,I,K,K<3?1:K==3?2:K<6?3:4)==I); } }
  for(I=0;I<256;I++) {
    unsigned Expected=I==0xbb?1:I==0x44?2:I==0xff?3:(I==0||I==4||I==8||I==12)?4:5;
    for(K=0;K<3;K++) {
      ATTRIBUTE A={0};A.Query.First=F.Base;A.Query.Fail=K==0?1:K==1?2:8000;A.Query.Kind=99;A.Attr=I;
      V=F;assert(EnumaCpuAttribute(&F,AttrTranslate,&A)==Expected);
      assert(A.Query.Calls==(I==0xbb?8000:A.Query.Fail)&&memcmp(&F,&V,sizeof(F))==0);
      A.Query.Calls=0;A.Fault=1;assert(EnumaCpuAttribute(&F,AttrTranslate,&A)==1);
    }
  }
  { TEST T={0};T.First=F.Base;T.Fail=1;T.Kind=4;assert(EnumaCpuAttribute(&F,Translate,&T)==1&&T.Calls==1); }
  assert(EnumaCpuAttribute(&F,0,0)==1);
  {
    const unsigned Table[16]={5,3,3,3,2,4,4,4,3,3,3,3,4,4,4,4};
    for(I=0;I<256;I++) {
      POLICY P={0};P.Query.First=F.Base;P.Query.Kind=99;P.Attr=I;V=F;
      unsigned Expected=Table[I>>4]==Table[I&15]?Table[I&15]:5;
      assert(EnumaCpuWholePolicy(&F,PolicyTranslate,&P)==Expected&&P.Query.Calls==8000);
      assert(!memcmp(&F,&V,sizeof(F)));
    }
    for(I=0;I<3;I++) {
      POLICY P={0};P.Query.First=F.Base;P.Query.Kind=99;P.Attr=0xaa;P.Other=0x88;P.ChangeAt=I==0?1:I==1?2:8000;
      assert(EnumaCpuWholePolicy(&F,PolicyTranslate,&P)==3&&P.Query.Calls==8000); // hint difference, same WT
      P.Query.Calls=0;P.Other=0xee;
      assert(EnumaCpuWholePolicy(&F,PolicyTranslate,&P)==(P.ChangeAt==1?4:5)&&P.Query.Calls==8000);
      for(K=0;K<6;K++) {
        P.Query.Calls=0;P.Query.Fail=P.ChangeAt;P.Query.Kind=K;
        assert(EnumaCpuWholePolicy(&F,PolicyTranslate,&P)==1&&P.Query.Calls==P.ChangeAt);
      }
    }
    assert(EnumaCpuWholePolicy(&F,0,0)==1);
  }
  for(I=0;I<7;I++) {
    WORD W={.Expected=F.Base,.Result=1};V=F;
    assert(EnumaCpuReadOnce(&F,I,WordRead,&W)==(I==3?5:I==2||I==4?2:I==5?3:1));
    assert(W.Count==(I==3)&&!memcmp(&F,&V,sizeof(F)));
  }
  for(int S=-1;S<=2;S++) { for(I=0;I<3;I++) {
    WORD W={.Expected=F.Base,.Result=S,.Value=I==0?0:I==1?~0u:0x12345678};
    assert(EnumaCpuReadOnce(&F,3,WordRead,&W)==(S==1?5:4)&&W.Count==1);
  } }
  assert(EnumaCpuReadOnce(&F,3,0,0)==4&&EnumaCpuReadOnce(0,3,WordRead,0)==4);
  for(int S=-1;S<=2;S++) {
    WORD W={.Expected=F.Base,.Result=1,.BarrierResult=S,.RequireBarrier=1};
    assert(EnumaCpuReadWithBarrier(&F,3,WordRead,WordBarrier,&W)==(S==1?5:4));
    assert(W.BarrierCount==1&&W.Count==(S==1));
  }
  for(I=0;I<7;I++) {
    WORD W={.Expected=F.Base,.Result=1,.BarrierResult=1,.RequireBarrier=1};
    assert(EnumaCpuReadWithBarrier(&F,I,WordRead,WordBarrier,&W)==(I==3?5:I==2||I==4?2:I==5?3:1));
    assert(W.BarrierCount==(I==3)&&W.Count==(I==3));
  }
  assert(EnumaCpuReadWithBarrier(&F,3,WordRead,0,0)==4);
  for(I=0;I<3;I++) {
    V=F;V.Base+=I*4;V.Stride=I==0?6400:I==1?6404:14744;V.Bytes=(ENUMA_U64)V.Stride*V.Height;
    for(K=0;K<2;K++) { ROI T={.Base=V.Base,.Stride=V.Stride,.BarrierResult=1};
      assert(EnumaCpuReadRoi(&V,3,K==0?4:8,RoiRead,RoiBarrier,&T)==(K==0?4:5)&&T.Calls==1024&&T.Barriers==1);
    }
  }
  for(I=1;I<=1024;I++) { ROI T={.Base=F.Base,.Stride=F.Stride,.FailAt=I,.BarrierResult=1};
    assert(EnumaCpuReadRoi(&F,3,4,RoiRead,RoiBarrier,&T)==3&&T.Calls==I&&T.Barriers==1);
  }
  for(I=0;I<7;I++) { ROI T={.Base=F.Base,.Stride=F.Stride,.BarrierResult=1};
    assert(EnumaCpuReadRoi(&F,I,4,RoiRead,RoiBarrier,&T)==(I==3?4:I==2||I==4?2:I==5?3:1));
    assert(T.Calls==(I==3?1024:0)&&T.Barriers==(I==3));
  }
  { ROI T={.Base=F.Base,.Stride=F.Stride,.BarrierResult=0};
    assert(EnumaCpuReadRoi(&F,3,4,RoiRead,RoiBarrier,&T)==3&&T.Calls==0&&T.Barriers==1);
    T.Barriers=0;assert(EnumaCpuReadRoi(&F,3,12,RoiRead,RoiBarrier,&T)==1&&T.Calls==0&&T.Barriers==0);
  }
  F.Base+=4092;F.Stride=14744;F.Bytes=(ENUMA_U64)F.Stride*2560;assert(Check(&F,0,0,5)==18432);
  { POLICY P={0};P.Query.First=F.Base&~4095ULL;P.Query.Kind=99;P.Attr=0xaa;assert(EnumaCpuWholePolicy(&F,PolicyTranslate,&P)==3&&P.Query.Calls==18432); }
  for(I=0;I<9;I++) {
    V=F;
    switch(I) {case 0:V.Base=0x9bfffffc;break;case 1:V.Base=0x9e400000;break;case 2:V.Base++;break;case 3:V.Bytes++;break;case 4:V.Requirements=0;break;case 5:V.Stride=6396;break;case 6:V.Width--;break;case 7:V.Height--;break;case 8:V.Bytes=~0ULL;break;}
    assert(Check(&V,0,0,1)==0);
    { WORD W={0};assert(EnumaCpuReadOnce(&V,3,WordRead,&W)==4&&W.Count==0); }
    { WORD W={0};assert(EnumaCpuReadWithBarrier(&V,3,WordRead,WordBarrier,&W)==4&&W.Count==0&&W.BarrierCount==0); }
    { ROI T={0};assert(EnumaCpuReadRoi(&V,3,4,RoiRead,RoiBarrier,&T)==3&&T.Calls==0&&T.Barriers==0); }
  }
  assert(EnumaCpuStage1(0,Translate,0)==1&&EnumaCpuStage1(&F,0,0)==1);
  puts("PASS: prior regressions;128x8 ROI stride/address/call bounds, all1024 failures, one barrier, EL1/EL2 completion and invalid prerequisites before access");return 0;
}
