// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "Evidence.h"
typedef struct { unsigned Reads,Window,Fail,FailWait,StallRight,Changed,Transient,BadCounter; } MODEL;
static int wait_window(void *Ctx,ENUMA_U32 Us) { MODEL *M=Ctx; assert(Us==100000); M->Window++; return M->FailWait==M->Window?-1:1; }
static int read_reg(void *Ctx,ENUMA_U32 O,ENUMA_U32 *V) {
  MODEL *M=Ctx; assert(!(O&3)&&O<0x85000); if(++M->Reads==M->Fail) { return -1; } *V=0;
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
  assert(!EnumaSampleVideo(read_reg,wait_window,&M,&L,&E)&&M.Reads==969&&M.Window==2);
  assert(E.Frame.Base==0x10100000&&E.Frame.Requirements==(ENUMA_REQUIRE_ADDRESS|ENUMA_REQUIRE_TOPOLOGY));
  assert(E.Limits.OriginX[1]==800&&E.Samples[2].Interfaces[1].Frame==34);
  for(unsigned F=1;F<=969;F++) { M=(MODEL){.Fail=F}; E=Before; assert(EnumaSampleVideo(read_reg,wait_window,&M,&L,&E)==EnumaInheritedBounds&&M.Reads==F&&!memcmp(&E,&Before,sizeof(E))); }
  for(unsigned W=1;W<=2;W++) { M=(MODEL){.FailWait=W}; E=Before; assert(EnumaSampleVideo(read_reg,wait_window,&M,&L,&E)==EnumaInheritedRefreshMode&&!memcmp(&E,&Before,sizeof(E))); }
  M=(MODEL){.StallRight=1}; E=Before; assert(EnumaSampleVideo(read_reg,wait_window,&M,&L,&E)==EnumaInheritedRefreshMode&&!memcmp(&E,&Before,sizeof(E)));
  M=(MODEL){.Changed=1}; E=Before; assert(EnumaSampleVideo(read_reg,wait_window,&M,&L,&E)==EnumaInheritedRefreshMode&&!memcmp(&E,&Before,sizeof(E)));
  M=(MODEL){.Transient=1}; assert(!EnumaSampleVideo(read_reg,wait_window,&M,&L,&E)&&E.Samples[2].Scanout.Ctls[2].Flush==2);
  M=(MODEL){.BadCounter=1}; E=Before; assert(EnumaSampleVideo(read_reg,wait_window,&M,&L,&E)==EnumaInheritedRefreshMode&&M.Reads==271&&!M.Window&&!memcmp(&E,&Before,sizeof(E)));
  puts("PASS: 3 same-boot samples, both DSI counters, 969 read failure injections, 2 wait failures, route mutation and right-link stall rejected; address/downstream requirements retained");
}
