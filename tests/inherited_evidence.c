// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "Evidence.h"
typedef struct { unsigned Reads,Window,Fail,FailWait,StallRight,Changed,Transient,BadCounter; } MODEL;
static int allowed(unsigned O) {
  static const unsigned Fields[11]={0,8,12,16,20,36,48,52,56,0x170,0x70};
  if(!O) { return 1; }
  for(unsigned C=0;C<6;C++) { if(O==0x2000+C*0x200+0xf4) { return 1; } }
  if(O==0x2414) { return 1; }
  for(unsigned M=0;M<6;M++) {
    if(O==0x2400+(M==5?0x24:M*4)||O==0x2440+M*4||O==0x2470+M*4||O==0x24a0+M*4) { return 1; }
  }
  for(unsigned P=0;P<2;P++) { for(unsigned J=0;J<11;J++) { if(O==0x5000+P*0x2000+Fields[J]) { return 1; } } }
  for(unsigned M=0;M<2;M++) {
    unsigned B=M?0x49000:0x45000;
    if(O==B||O==B+4) { return 1; }
    for(unsigned J=0;J<11;J++) { if(O==B+0x20+J*0x18||O==B+0x24+J*0x18) { return 1; } }
  }
  for(unsigned I=0;I<2;I++) { unsigned B=0x6b800+I*0x800; if(O==B||O==B+0xa8||O==B+0x26c||O==B+0xac) { return 1; } }
  return 0;
}
static int wait_window(void *Ctx,ENUMA_U32 Us) { MODEL *M=Ctx; assert(Us==100000); M->Window++; return M->FailWait==M->Window?-1:1; }
static int read_reg(void *Ctx,ENUMA_U32 O,ENUMA_U32 *V) {
  MODEL *M=Ctx; assert(!(O&3)&&O<=0x6c26c&&allowed(O)); if(++M->Reads==M->Fail) { return -1; } *V=0;
  if(O>=0x45000&&O<=0x4a114) { assert(O<0x46000||(O>=0x49000&&O<0x4a000)); }
  if(!O) { *V=0x60000000; }
  if(O==0x24f4) { *V=6; }
  if(O==0x2410) { *V=1; } // mixer4 LEFT pipe0 base stage
  if(O==0x2400) { *V=8; } // mixer0 RIGHT pipe1 base stage
  if(O==0x45000) { *V=1u<<31; }
  if(O==0x45004||O==0x49004) { *V=(2560u<<16)|800; }
  if(M->Transient&&(O==0x241c||O==0x2418)) { *V=M->Window; }
  for(unsigned P=0;P<2;P++) {
    unsigned B=0x5000+P*0x2000;
    if(O==B||O==B+12) { *V=(2560u<<16)|800; }
    if(O==B+20) { *V=0x10100000+P*3200+(M->Changed&&M->Window?4:0); }
    if(O==B+36) { *V=6400; }
    if(O==B+48) { *V=0x236ff; }
    if(O==B+52) { *V=0x03020001; }
  }
  for(unsigned I=0;I<2;I++) {
    unsigned B=0x6b800+I*0x800;
    if(O==B||O==B+0x26c) { *V=1; }
    if(O==B+0xa8) { *V=M->BadCounter?1:3; }
    if(O==B+0xac) { *V=10+(M->StallRight&&I?0:M->Window*12); }
  }
  return 1;
}
int main(void) {
  ENUMA_INHERITED_LIMITS L={.SplashBase=0x10000000,.SplashBytes=0x2000000,.Width=1600,.Height=2560};
  ENUMA_VIDEO_EVIDENCE E,Before; memset(&E,0xa5,sizeof(E)); Before=E; MODEL M={0};
  assert(!EnumaSampleVideo(read_reg,wait_window,&M,&L,&E)&&M.Reads==330&&M.Window==2);
  assert(E.Samples[0].Scope.PipeMask==3&&E.Samples[0].Scope.CtlRouteMask==4&&E.Samples[0].Scope.MixerMask==17&&!E.Samples[0].Scope.CommandRefreshMask&&!E.Samples[0].Scope.CtlTransientMask);
  assert(E.Frame.Base==0x10100000&&E.Frame.Requirements==(ENUMA_REQUIRE_ADDRESS|ENUMA_REQUIRE_TOPOLOGY));
  assert(E.Limits.OriginX[1]==800&&E.Samples[2].Interfaces[1].Frame==34);
  for(unsigned F=1;F<=330;F++) { M=(MODEL){.Fail=F}; E=Before; assert(EnumaSampleVideo(read_reg,wait_window,&M,&L,&E)==EnumaInheritedBounds&&M.Reads==F&&!memcmp(&E,&Before,sizeof(E))); }
  for(unsigned W=1;W<=2;W++) { M=(MODEL){.FailWait=W}; E=Before; assert(EnumaSampleVideo(read_reg,wait_window,&M,&L,&E)==EnumaInheritedRefreshMode&&!memcmp(&E,&Before,sizeof(E))); }
  M=(MODEL){.StallRight=1}; E=Before; assert(EnumaSampleVideo(read_reg,wait_window,&M,&L,&E)==EnumaInheritedRefreshMode&&!memcmp(&E,&Before,sizeof(E)));
  M=(MODEL){.Changed=1}; E=Before; assert(EnumaSampleVideo(read_reg,wait_window,&M,&L,&E)==EnumaInheritedRefreshMode&&!memcmp(&E,&Before,sizeof(E)));
  M=(MODEL){.Transient=1}; assert(!EnumaSampleVideo(read_reg,wait_window,&M,&L,&E)&&!E.Samples[2].Scanout.Ctls[2].Flush&&!E.Samples[2].Scope.CtlTransientMask);
  M=(MODEL){.BadCounter=1}; E=Before; assert(EnumaSampleVideo(read_reg,wait_window,&M,&L,&E)==EnumaInheritedRefreshMode&&M.Reads==5&&!M.Window&&!memcmp(&E,&Before,sizeof(E)));
  puts("PASS: 3 video-only samples, 330 callback failures, 2 wait failures, no PP/command/unused pipe reads, explicit observation masks; address/downstream requirements retained");
}
