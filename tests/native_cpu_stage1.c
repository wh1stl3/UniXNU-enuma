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
int main(void) {
  ENUMA_INHERITED_FRAME F={0},V;unsigned I,K,Count;
  F.Base=0x9c000000ULL;F.Width=1600;F.Height=2560;F.Stride=6400;F.Bytes=(ENUMA_U64)6400*2560;F.Requirements=22;
  Count=Check(&F,0,0,5);assert(Count==8000);
  for(I=1;I<=Count;I++) { for(K=0;K<7;K++) { assert(Check(&F,I,K,K<3?1:K==3?2:K<6?3:4)==I); } }
  F.Base+=4092;F.Stride=14744;F.Bytes=(ENUMA_U64)F.Stride*2560;assert(Check(&F,0,0,5)==18432);
  for(I=0;I<9;I++) {
    V=F;
    switch(I) {case 0:V.Base=0x9bfffffc;break;case 1:V.Base=0x9e400000;break;case 2:V.Base++;break;case 3:V.Bytes++;break;case 4:V.Requirements=0;break;case 5:V.Stride=6396;break;case 6:V.Width--;break;case 7:V.Height--;break;case 8:V.Bytes=~0ULL;break;}
    assert(Check(&V,0,0,1)==0);
  }
  assert(EnumaCpuStage1(0,Translate,0)==1&&EnumaCpuStage1(&F,0,0)==1);
  puts("PASS: 56000 fail/permission/identity/attribute boundary cases,18432 maximum query path, invalid contracts before callback and unchanged frame requirements");return 0;
}
