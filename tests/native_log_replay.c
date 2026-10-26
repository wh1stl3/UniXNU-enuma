// SPDX-License-Identifier: BSD-2-Clause-Patent
#define ENUMA_BOOT_LOG_REPLAY 1
#include "PixelTransaction.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static ENUMA_INHERITED_FRAME F;
static ENUMA_U32 Pixels[24576],Original[24576],R,W,B,H,V,Restore,FailR,FailW,FailB,FailH,FailV;
static ENUMA_BOOT_LOG Log;
static unsigned Index(ENUMA_U64 A) {
  assert(A>=F.Base&&!(A&3));ENUMA_U64 D=A-F.Base;unsigned Y=D/F.Stride,X=(D%F.Stride)/4;
  assert(Y<96&&X<256);return Y*256+X;
}
static int Read(void *C,ENUMA_U64 A,ENUMA_U32 *Out) {
  assert(C==&F&&R<73728);unsigned I=Index(A);R++;*Out=Pixels[I];return R!=FailR;
}
static int Write(void *C,ENUMA_U64 A,ENUMA_U32 Value) {
  assert(C==&F&&V==1&&W<49152);unsigned I=Index(A);W++;
  if(!H) { assert(I==W-1&&Value==EnumaPixelLogAt(&F,I)); }
  else { assert(I==Restore++&&Value==Original[I]); }
  if(W==FailW) { return 0; }Pixels[I]=Value;return 1;
}
static int Validate(void *C,const ENUMA_INHERITED_FRAME *Frame) { assert(C==&F&&Frame==&F&&R==24576&&!W&&!V&&!H&&B==1);V++;return !FailV; }
static int Barrier(void *C) { assert(C==&F&&B<3);B++;return B!=FailB; }
static int Hold(void *C,ENUMA_U32 Us) { assert(C==&F&&!H&&Us==2000000);H++;return !FailH; }
static void Init(unsigned Stride) {
  memset(&F,0,sizeof F);F.Base=0x9c000004;F.Width=1600;F.Height=2560;F.Stride=Stride;F.Bytes=(ENUMA_U64)Stride*2560;F.Requirements=22;
  F.RedMask=0xff0000;F.GreenMask=0xff00;F.BlueMask=0xff;F.ReservedMask=0xff000000;
  for(unsigned I=0;I<24576;I++) { Pixels[I]=Original[I]=0x10203040u+I; }
  R=W=B=H=V=Restore=FailR=FailW=FailB=FailH=FailV=0;
}
static unsigned Run(void) { return EnumaPixelTransaction(&F,3,4,Read,Write,Validate,Barrier,Hold,&F); }
int main(void) {
  assert(ENUMA_PIXEL_WIDTH==256&&ENUMA_PIXEL_ROWS==96&&ENUMA_PIXEL_WORDS==24576);
  memset(&Log,0,sizeof Log);assert(!EnumaLogPageFromSnapshot(&Log,&mEnumaLogPage));
  Init(6404);assert(Run()==1&&!R&&!W);
  assert(EnumaBootLogAppend(&Log,13,0x1234,NULL,0x8000000000000001ULL));
  assert(EnumaBootLogAppend(&Log,20,0x9999,NULL,0)); // select actual RETURN, not before-entry success
  assert(EnumaLogPageFromSnapshot(&Log,&mEnumaLogPage));
  assert(!memcmp(mEnumaLogPage.Text[0],"C0d O00001234",13));
  assert(!memcmp(mEnumaLogPage.Text[1],"S80000000",9));
  assert(!memcmp(mEnumaLogPage.Text[2]," 00000001",9));
  Log.Dropped=1;assert(EnumaLogPageFromSnapshot(&Log,&mEnumaLogPage)&&mEnumaLogPage.Text[0][13]=='+');
  unsigned Patterns=0;
  for(unsigned A=0;A<4;A++) for(unsigned Red=0;Red<4;Red++) for(unsigned Green=0;Green<4;Green++) {
    if(A==Red||A==Green||Red==Green) { continue; }unsigned Blue=6-A-Red-Green;Init(6404);
    F.ReservedMask=255u<<(A*8);F.RedMask=255u<<(Red*8);F.GreenMask=255u<<(Green*8);F.BlueMask=255u<<(Blue*8);
    unsigned White=0;for(unsigned I=0;I<24576;I++) { unsigned P=EnumaPixelLogAt(&F,I);assert(P==0xffffffffu||P==F.ReservedMask);White+=P==0xffffffffu; }
    assert(White>0&&White<24576);Patterns++;
    assert(Run()==5&&R==73728&&W==49152&&B==3&&H==1&&Restore==24576&&!memcmp(Pixels,Original,sizeof Pixels));
  }
  unsigned Cases=0;
  for(unsigned Pass=0;Pass<3;Pass++) for(unsigned Row=0;Row<96;Row++) for(unsigned Edge=0;Edge<2;Edge++) {
    Init(8192);FailR=Pass*24576+Row*256+(Edge?256:1);
    assert(Run()==(Pass==0?1:Pass==1?2:4));
    if(Pass==0) { assert(!W&&!V&&!H); } else { assert(Restore==24576); }
    assert(!memcmp(Pixels,Original,sizeof Pixels));Cases++;
  }
  for(unsigned Pass=0;Pass<2;Pass++) for(unsigned Row=0;Row<96;Row++) for(unsigned Edge=0;Edge<2;Edge++) {
    Init(6404);FailW=Pass*24576+Row*256+(Edge?256:1);assert(Run()==(Pass?4:2));assert(Restore==24576);
    if(!Pass) { assert(!memcmp(Pixels,Original,sizeof Pixels)); }Cases++;
  }
  for(unsigned N=1;N<=3;N++) { Init(6404);FailB=N;assert(Run()==(N==1?1:N==2?2:4)); }
  Init(6404);FailV=1;assert(Run()==1&&!W);
  Init(6404);FailH=1;assert(Run()==3&&!memcmp(Pixels,Original,sizeof Pixels));
  Log.Head=128;assert(!EnumaLogPageFromSnapshot(&Log,&mEnumaLogPage));Init(6404);assert(Run()==1&&!R&&!W);
  printf("PASS: live-status page from newest point13/full64 status; %u channel layouts; %u row/pass read-write failure boundaries;256x96/2s/full restore; no hardware\n",Patterns,Cases);
}
