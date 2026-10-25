// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "NativeObserve.h"
typedef struct { unsigned Reads,Waits,Fail,FailWait,Enable,Inactive,Stop,Wrap,Jump,TimingChange,EnableChange,RevisionChange,ZeroTiming,BadRevision; int FailCode; } MODEL;
static int read_reg(void *Ctx,unsigned Offset,unsigned *Value) {
  MODEL *M=Ctx;unsigned I,B;
  if(++M->Reads==M->Fail) { return M->FailCode; }
  if(!Offset) { *Value=M->BadRevision?0x50000000:0x60000000+(M->RevisionChange&&M->Waits==2); return 1; }
  for(I=0;I<2;I++) {
    B=0x6b800+I*0x800;
    if(Offset==B) { *Value=M->ZeroTiming?0:1+(M->TimingChange&&M->Waits&&I==1); return 1; }
    if(Offset==B+0xa8) { *Value=M->Enable+(M->EnableChange&&M->Waits&&I==1); return 1; }
    if(Offset==B+0x26c) { *Value=(M->Inactive&(1u<<I))?0:1; return 1; }
    if(Offset==B+0xac) {
      assert(!(M->Inactive&(1u<<I))); // active-before-frame; no inactive bank read
      *Value=(M->Wrap&&I==1)?(M->Waits?3:0xfffffff0u):10+M->Waits*((M->Stop&&I==1)?0:(M->Jump&&I==1)?65:12);
      return 1;
    }
  }
  assert(!"unexpected offset; no CTL/SSPP/LM/PP access allowed"); return 0;
}
static int wait_window(void *Ctx,unsigned Us) { MODEL *M=Ctx;assert(Us==100000);return ++M->Waits==M->FailWait?0:1; }
int main(void) {
  ENUMA_NATIVE_OBSERVATION O,Old;memset(&Old,0xa5,sizeof(Old));unsigned Cases=0;
  // Enable0/1/2 all remain observable; this is the distinction from full sampler.
  for(unsigned E=0;E<4;E++) {
    MODEL M={.Enable=E};O=Old;
    assert(EnumaObserveNativeVideo(read_reg,wait_window,&M,&O)==0);
    assert(O.ReadCount==26&&M.Reads==26&&O.WaitCount==2&&M.Waits==2);
    assert(O.ActiveThroughoutMask==3&&O.MovingMask==3&&O.TimingStableMask==3&&O.EnableStableMask==3);
    assert(O.ExactEnable3Mask==(E==3?3u:0u));Cases++;
  }
  for(unsigned F=1;F<=26;F++) { MODEL M={.Fail=F};O=Old;assert(EnumaObserveNativeVideo(read_reg,wait_window,&M,&O)==EnumaInheritedBounds&&M.Reads==F&&!memcmp(&O,&Old,sizeof(O)));Cases++; }
  for(unsigned W=1;W<=2;W++) { MODEL M={.FailWait=W};O=Old;assert(EnumaObserveNativeVideo(read_reg,wait_window,&M,&O)==EnumaInheritedRefreshMode&&!memcmp(&O,&Old,sizeof(O)));Cases++; }
  for(unsigned Mask=1;Mask<=3;Mask++) { MODEL M={.Inactive=Mask};assert(!EnumaObserveNativeVideo(read_reg,wait_window,&M,&O));assert(O.ActiveThroughoutMask==(3u&~Mask)&&O.MovingMask==(3u&~Mask));assert(O.ReadCount==26-3*((Mask&1)+((Mask>>1)&1)));for(unsigned N=0;N<3;N++)assert(O.Samples[N].FrameReadMask==(3u&~Mask));Cases++; }
  const MODEL CasesIn[]={{.Stop=1},{.Wrap=1},{.Jump=1},{.TimingChange=1},{.EnableChange=1},{.ZeroTiming=1}};
  for(unsigned I=0;I<6;I++) { MODEL M=CasesIn[I];assert(!EnumaObserveNativeVideo(read_reg,wait_window,&M,&O));if(I<3)assert(O.MovingMask==1);if(I==3)assert(O.TimingStableMask==1);if(I==4)assert(O.EnableStableMask==1);if(I==5)assert(O.TimingStableMask==0&&O.MovingMask==3);Cases++; }
  MODEL M={.RevisionChange=1};O=Old;assert(EnumaObserveNativeVideo(read_reg,wait_window,&M,&O)==EnumaInheritedInconsistent&&!memcmp(&O,&Old,sizeof(O)));Cases++;
  assert(EnumaObserveNativeVideo(0,wait_window,&M,&O)==EnumaInheritedArguments);Cases++;
  assert(EnumaObserveNativeVideo(read_reg,0,&M,&O)==EnumaInheritedArguments);Cases++;
  assert(EnumaObserveNativeVideo(read_reg,wait_window,&M,0)==EnumaInheritedArguments);Cases++;
  M=(MODEL){.BadRevision=1};O=Old;assert(EnumaObserveNativeVideo(read_reg,wait_window,&M,&O)==EnumaInheritedRevision&&M.Reads==1&&M.Waits==0&&!memcmp(&O,&Old,sizeof(O)));Cases++;
  for(int Code=-1;Code<=2;Code+=3) { M=(MODEL){.Fail=5,.FailCode=Code};O=Old;assert(EnumaObserveNativeVideo(read_reg,wait_window,&M,&O)==EnumaInheritedBounds&&M.Reads==5&&!memcmp(&O,&Old,sizeof(O)));Cases++; }
  printf("PASS: %u observation/boundary cases; <=26 reads, two100ms waits, inactive-frame suppression, no eligibility relaxation\n",Cases);
}
