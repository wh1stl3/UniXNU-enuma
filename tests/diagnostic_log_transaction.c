// SPDX-License-Identifier: BSD-2-Clause-Patent
#define ENUMA_BOOT_LOG_REPLAY 3
#define ENUMA_BOOT_LOG_HOLD_US 8000000
#define ENUMA_EXPECT_HOLD_US 8000000
#include "PixelTransaction.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static ENUMA_INHERITED_FRAME F;
static ENUMA_U32 Pixels[51200],Original[51200],R,W,B,H,V,Restore,FailR,FailW,FailB,FailH,FailV;
static ENUMA_BOOT_LOG Log;
static unsigned Index(ENUMA_U64 A) {
  assert(A>=F.Base&&!(A&3));ENUMA_U64 D=A-F.Base;unsigned Y=D/F.Stride,X=(D%F.Stride)/4;
  assert(Y>=96&&Y<256&&X>=64&&X<384);return (Y-96)*320+X-64;
}
static int Read(void *C,ENUMA_U64 A,ENUMA_U32 *Out) {
  assert(C==&F&&R<153600);unsigned I=Index(A);R++;*Out=Pixels[I];return R!=FailR;
}
static int Write(void *C,ENUMA_U64 A,ENUMA_U32 Value) {
  assert(C==&F&&V==1&&W<102400);unsigned I=Index(A);W++;
  if(!H) { assert(I==W-1&&Value==EnumaPixelLogAt(&F,I)); }
  else { assert(I==Restore++&&Value==Original[I]); }
  if(W==FailW) { return 0; }Pixels[I]=Value;return 1;
}
static int Validate(void *C,const ENUMA_INHERITED_FRAME *Frame) { assert(C==&F&&Frame==&F&&R==51200&&!W&&!V&&!H&&B==1);V++;return !FailV; }
static int Barrier(void *C) { assert(C==&F&&B<3);B++;return B!=FailB; }
#ifndef ENUMA_EXPECT_HOLD_US
#define ENUMA_EXPECT_HOLD_US 2000000
#endif
static int Hold(void *C,ENUMA_U32 Us) { assert(C==&F&&!H&&Us==ENUMA_EXPECT_HOLD_US);H++;return !FailH; }
static void Init(unsigned Stride) {
  memset(&F,0,sizeof F);F.Base=0x9c000004;F.Width=1600;F.Height=2560;F.Stride=Stride;F.Bytes=(ENUMA_U64)Stride*2560;F.Requirements=22;
  F.RedMask=0xff0000;F.GreenMask=0xff00;F.BlueMask=0xff;F.ReservedMask=0xff000000;
  for(unsigned I=0;I<51200;I++) { Pixels[I]=Original[I]=0x10203040u+I; }
  R=W=B=H=V=Restore=FailR=FailW=FailB=FailH=FailV=0;
}
static unsigned Run(void) { return EnumaPixelTransaction(&F,3,4,Read,Write,Validate,Barrier,Hold,&F); }
int main(void) {
  assert(ENUMA_PIXEL_WIDTH==320&&ENUMA_PIXEL_ROWS==160&&ENUMA_PIXEL_WORDS==51200);
  memset(&Log,0,sizeof Log);assert(!EnumaLogPageFromSnapshot(&Log,&mEnumaLogPage));
  Init(6404);assert(Run()==1&&!R&&!W);
  EFI_GUID Guid={0x12345678,0x9abc,0xdef0,{0x12,0x34,0x56,0x78,0x9a,0xbc,0xde,0xf0}};
  for(unsigned I=0;I<130;I++) { assert(EnumaBootLogAppend(&Log,15,I,&Guid,0)); }
  assert(EnumaBootLogAppend(&Log,13,0x1234,&Guid,0x8000000000000001ULL));
  assert(EnumaBootLogAppend(&Log,20,0x9999,&Guid,0));
  assert(EnumaLogPageFromSnapshot(&Log,&mEnumaLogPage));
  assert(!memcmp(mEnumaLogPage.Text[0],"E0d O00001234+",14));
  assert(!memcmp(mEnumaLogPage.Text[1],"S8000000000000001",17));
  assert(!memcmp(mEnumaLogPage.Text[2],"Q0000000000000082",17));
  assert(!memcmp(mEnumaLogPage.Text[3],"G0123456789abcdef0",18));
  assert(!memcmp(mEnumaLogPage.Text[4],"G1123456789abcdef0",18));
  ENUMA_BOOT_LOG Bad=Log;Bad.Dropped++;assert(!EnumaLogPageFromSnapshot(&Bad,&mEnumaLogPage));
  Bad=Log;Bad.Events[(Log.Head+Log.Count-2)%128].Sequence++;assert(!EnumaLogPageFromSnapshot(&Bad,&mEnumaLogPage));
  Bad=Log;Bad.Events[(Log.Head+Log.Count-2)%128].HasGuid=0;assert(!EnumaLogPageFromSnapshot(&Bad,&mEnumaLogPage));
  assert(EnumaLogPageFromSnapshot(&Log,&mEnumaLogPage));
  unsigned Patterns=0;
  for(unsigned A=0;A<4;A++) for(unsigned Red=0;Red<4;Red++) for(unsigned Green=0;Green<4;Green++) {
    if(A==Red||A==Green||Red==Green) { continue; }unsigned Blue=6-A-Red-Green;Init(6404);
    F.ReservedMask=255u<<(A*8);F.RedMask=255u<<(Red*8);F.GreenMask=255u<<(Green*8);F.BlueMask=255u<<(Blue*8);
    unsigned White=0;for(unsigned I=0;I<51200;I++) { unsigned P=EnumaPixelLogAt(&F,I);assert(P==0xffffffffu||P==F.ReservedMask);White+=P==0xffffffffu; }
    assert(White>0&&White<51200);Patterns++;
    assert(Run()==5&&R==153600&&W==102400&&B==3&&H==1&&Restore==51200&&!memcmp(Pixels,Original,sizeof Pixels));
  }
  unsigned Cases=0;
  for(unsigned Pass=0;Pass<3;Pass++) for(unsigned Row=0;Row<160;Row++) for(unsigned Edge=0;Edge<2;Edge++) {
    Init(8192);FailR=Pass*51200+Row*320+(Edge?320:1);
    assert(Run()==(Pass==0?1:Pass==1?2:4));
    if(Pass==0) { assert(!W&&!V&&!H); } else { assert(Restore==51200); }
    assert(!memcmp(Pixels,Original,sizeof Pixels));Cases++;
  }
  for(unsigned Pass=0;Pass<2;Pass++) for(unsigned Row=0;Row<160;Row++) for(unsigned Edge=0;Edge<2;Edge++) {
    Init(6404);FailW=Pass*51200+Row*320+(Edge?320:1);assert(Run()==(Pass?4:2));assert(Restore==51200);
    if(!Pass) { assert(!memcmp(Pixels,Original,sizeof Pixels)); }Cases++;
  }
  for(unsigned N=1;N<=3;N++) { Init(6404);FailB=N;assert(Run()==(N==1?1:N==2?2:4)); }
  Init(6404);FailV=1;assert(Run()==1&&!W);
  Init(6404);FailH=1;assert(Run()==3&&!memcmp(Pixels,Original,sizeof Pixels));
  Log.Head=128;assert(!EnumaLogPageFromSnapshot(&Log,&mEnumaLogPage));Init(6404);assert(Run()==1&&!R&&!W);
  printf("PASS: attributed cached return page from newest point13/full64 status; %u channel layouts; %u row/pass read-write failure boundaries;inset64,96/320x160/%uus/full restore; no hardware\n",Patterns,Cases,ENUMA_EXPECT_HOLD_US);
}
