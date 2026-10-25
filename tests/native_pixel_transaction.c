// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "PixelTransaction.h"
typedef struct {
  ENUMA_INHERITED_FRAME F;
  ENUMA_U32 Pixels[1024],Original[1024],R,W,B,H,V,RestoreW,FailR,FailW,FailB,FailH,FailV,CorruptR,AfterWrite,Color;
} MODEL;
static MODEL M;
static void Init(int White) {
  memset(&M,0,sizeof(M));M.F.Base=0x9c000004ULL;M.F.Width=1600;M.F.Height=2560;M.F.Stride=6404;
  M.F.Bytes=(ENUMA_U64)M.F.Stride*2560;M.F.Requirements=22;
  M.F.RedMask=0xff0000;M.F.GreenMask=0xff00;M.F.BlueMask=0xff;M.F.ReservedMask=0xff000000;
  for(unsigned I=0;I<1024;I++) { M.Pixels[I]=M.Original[I]=White?0xffffffffu:(I*0x1234567u)^0x87654321u; }
  M.Color=White?M.F.ReservedMask:0xffffffffu;
}
static unsigned Index(ENUMA_U64 A) {
  assert(A>=M.F.Base&&!(A&3));ENUMA_U64 D=A-M.F.Base;unsigned Y=D/M.F.Stride,X=(D%M.F.Stride)/4;
  assert(Y<8&&X<128);return Y*128+X;
}
static int Read(void *C,ENUMA_U64 A,ENUMA_U32 *V) {
  assert(C==&M&&M.B>=1&&M.R<3072);unsigned I=Index(A);M.R++;
  if(M.R<=1024) { assert(!M.W&&!M.H&&M.V==0&&I==M.R-1); }
  *V=M.Pixels[I];if(M.R==M.CorruptR) { *V^=1; }return M.R==M.FailR?0:1;
}
static int Write(void *C,ENUMA_U64 A,ENUMA_U32 V) {
  assert(C==&M&&M.V==1&&M.R>=1024&&M.W<2048);unsigned I=Index(A);M.W++;
  if(!M.H) { assert(I==M.W-1&&V==M.Color); }
  else { assert(I==M.RestoreW++&&V==M.Original[I]); }
  if(M.W==M.FailW&&!M.AfterWrite) { return 0; }
  M.Pixels[I]=V;return M.W==M.FailW?0:1;
}
static int Validate(void *C,const ENUMA_INHERITED_FRAME *F) {
  assert(C==&M&&M.R==1024&&!M.W&&!M.H&&!M.V&&M.B==1&&F==&M.F);M.V++;return !M.FailV;
}
static int Barrier(void *C) { assert(C==&M&&M.B<3);M.B++;return M.B==M.FailB?0:1; }
static int Hold(void *C,ENUMA_U32 Us) { assert(C==&M&&!M.H&&Us==500000);M.H++;return !M.FailH; }
static unsigned Run(void) { return EnumaPixelTransaction(&M.F,3,4,Read,Write,Validate,Barrier,Hold,&M); }
static void Restored(void) { assert(!memcmp(M.Pixels,M.Original,sizeof(M.Pixels))&&M.R<=3072&&M.W<=2048&&M.B<=3&&M.H<=1); }
static void Evidence(void) {
  ENUMA_VIDEO_EVIDENCE A={0},B={0};unsigned I;unsigned char *P;
  assert(EnumaPixelEvidenceSame(&A,&B));
  void *Parts[]={&B.Frame,&B.Limits,&B.Samples[0].Scanout,&B.Samples[0].Mixers,&B.Samples[0].Scope};
  unsigned Sizes[]={sizeof(B.Frame),sizeof(B.Limits),sizeof(B.Samples[0].Scanout),sizeof(B.Samples[0].Mixers),sizeof(B.Samples[0].Scope)};
  for(unsigned K=0;K<5;K++) { P=Parts[K];for(I=0;I<Sizes[K];I++) { P[I]^=1;assert(!EnumaPixelEvidenceSame(&A,&B));P[I]^=1; } }
  B.Samples[0].Interfaces[0].Frame=123;B.Samples[0].Interfaces[1].Active=4;
  assert(EnumaPixelEvidenceSame(&A,&B));B.Samples[0].Interfaces[0].Timing=1;assert(!EnumaPixelEvidenceSame(&A,&B));
  B.Samples[0].Interfaces[0].Timing=0;B.Samples[0].Interfaces[1].CounterEnable=1;assert(!EnumaPixelEvidenceSame(&A,&B));
}
int main(void) {
  Evidence();
  for(unsigned R=0;R<4;R++) for(unsigned G=0;G<4;G++) for(unsigned B=0;B<4;B++) {
    if(R==G||R==B||G==B) { continue; }unsigned A=6-R-G-B;
    for(int White=0;White<2;White++) {
      Init(White);M.F.RedMask=255u<<(8*R);M.F.GreenMask=255u<<(8*G);M.F.BlueMask=255u<<(8*B);M.F.ReservedMask=255u<<(8*A);M.Color=White?M.F.ReservedMask:0xffffffffu;
      assert(Run()==5&&M.R==3072&&M.W==2048&&M.B==3&&M.H==1&&M.V==1&&M.RestoreW==1024);Restored();
    }
  }
  for(unsigned N=1;N<=3072;N++) {
    Init(0);M.FailR=N;unsigned S=Run();assert(S==(N<=1024?1:N<=2048?2:4));
    if(N<=1024) { assert(!M.W&&!M.H&&!M.V); }else { assert(M.RestoreW==1024); }Restored();
  }
  for(unsigned N=1;N<=2048;N++) for(unsigned After=0;After<2;After++) {
    Init(0);M.FailW=N;M.AfterWrite=After;assert(Run()==(N<=1024?2:4));assert(M.RestoreW==1024);
    if(N<=1024||After) { Restored(); }
  }
  for(unsigned N=1;N<=3;N++) { Init(0);M.FailB=N;assert(Run()==(N==1?1:N==2?2:4));Restored(); }
  Init(0);M.FailH=1;assert(Run()==3);Restored();
  Init(0);M.FailV=1;assert(Run()==1&&M.W==0&&M.H==0);Restored();
  Init(0);M.CorruptR=1500;assert(Run()==2);Restored();
  Init(0);M.CorruptR=2500;assert(Run()==4);Restored();
  for(unsigned N=0;N<10;N++) {
    Init(0);switch(N) {case 0:M.F.Base=0x9bfffffc;break;case 1:M.F.Base=0x9e400000;break;case 2:M.F.Base++;break;case 3:M.F.Bytes++;break;case 4:M.F.Stride=6396;break;case 5:M.F.Width--;break;case 6:M.F.Height--;break;case 7:M.F.Requirements=0;break;case 8:M.F.RedMask=M.F.BlueMask;break;case 9:M.F.ReservedMask=1;break;}
    assert(Run()==1&&M.R==0&&M.W==0&&M.B==0);
  }
  Init(0);assert(EnumaPixelTransaction(&M.F,3,8,Read,Write,Validate,Barrier,Hold,&M)==1&&M.R==0&&M.W==0&&M.B==0);
  puts("PASS: 24 opaque byte permutations/white fallback;3072 read and4096 write-failure cases; full restoration attempts, failure precedence, revalidation and strict bounds; no hardware");
}
