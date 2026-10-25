// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <setjmp.h>
#include <stdint.h>
#include <stdio.h>
static unsigned resets,delays;
static uint64_t last_delay;
static jmp_buf stopped;
void MicroSecondDelay(uint64_t us) { assert(us>=2000000&&us<=22000000);last_delay=us;delays++; }
void ResetCold(void) { resets++; }
void CpuDeadLoop(void) { longjmp(stopped,1); }
#include DETAIL_HEADER
#include "NativeMaskResult.h"
#include "NativeRouteResult.h"
int main(void) {
  EFI_GUID good={0x1122334455667788ULL,0x8877665544332211ULL};
  EFI_GUID bad1=good,bad2=good;bad1.low^=1;bad2.high^=1;
  const EFI_GUID *guids[]={&good,&bad1,&bad2,0};
  uint64_t codes[]={0,1,2,3,4,5,6,0x8000000000000001ULL,UINT64_MAX};
  unsigned cases=0;
  EnumaDispatchCheckpoint(12);
  for(unsigned g=0;g<4;g++)for(unsigned point=12;point<=25;point++)for(unsigned c=0;c<9;c++) {
    unsigned before=resets;
    if(setjmp(stopped)==0)EnumaDispatchDetailCheckpoint(point,guids[g],codes[c]);
    unsigned expect=g==0&&point==13&&codes[c]>=1&&codes[c]<=5;
    assert(resets-before==expect);
    if(expect)assert(last_delay==2000000+5000000*(codes[c]-1));
    cases++;
  }
  assert(delays==resets);
  ENUMA_NATIVE_OBSERVATION o={0};
  ENUMA_U32 *m[]={&o.ActiveThroughoutMask,&o.TimingStableMask,&o.EnableStableMask,&o.MovingMask,&o.ExactEnable3Mask};
  for(unsigned field=1;field<=5;field++)for(unsigned value=0;value<=4;value++) {
    for(unsigned i=0;i<5;i++)*m[i]=(value+1)%4;
    *m[field-1]=value;
    assert(EnumaNativeMaskResult(EnumaInheritedOk,&o,field)==(value<4?value+1:5));
    assert(EnumaNativeMaskResult(EnumaInheritedBounds,&o,field)==5);
  }
  assert(EnumaNativeMaskResult(EnumaInheritedOk,0,1)==5);
  assert(EnumaNativeMaskResult(EnumaInheritedOk,&o,0)==5);
  assert(EnumaNativeMaskResult(EnumaInheritedOk,&o,8)==5);
  for(unsigned a=0;a<4;a++)for(unsigned b=0;b<4;b++)for(unsigned c=0;c<4;c++)for(unsigned d=0;d<4;d++) {
    o.ActiveThroughoutMask=a;o.TimingStableMask=b;o.EnableStableMask=c;o.MovingMask=d;
    o.ExactEnable3Mask=0; // exact-enable3 remains unrelated to this conjunction.
    assert(EnumaNativeMaskResult(EnumaInheritedOk,&o,6)==(a&b&c&d)+1);
    assert(EnumaNativeMaskResult(EnumaInheritedBounds,&o,6)==5);
  }
  for(unsigned i=0;i<4;i++)for(unsigned bad=0;bad<2;bad++) {
    for(unsigned j=0;j<4;j++)*m[j]=3;
    *m[i]=bad?UINT32_MAX:4;
    assert(EnumaNativeMaskResult(EnumaInheritedOk,&o,6)==5);
  }
  assert(EnumaNativeMaskResult(EnumaInheritedOk,0,6)==5);
  for(unsigned a=0;a<4;a++)for(unsigned b=0;b<4;b++)for(unsigned c=0;c<4;c++)for(unsigned z=0;z<4;z++) {
    o.ActiveThroughoutMask=a;o.EnableStableMask=b;o.MovingMask=c;
    for(unsigned i=0;i<2;i++)for(unsigned n=0;n<3;n++)o.Samples[n].Interfaces[i].Timing=(z&(1u<<i))?0:1;
    assert(EnumaNativeMaskResult(EnumaInheritedOk,&o,7)==(a&b&c&z)+1);
    assert(EnumaNativeMaskResult(EnumaInheritedBounds,&o,7)==5);
  }
  ENUMA_U32 *zero_inputs[]={&o.ActiveThroughoutMask,&o.EnableStableMask,&o.MovingMask};
  for(unsigned i=0;i<3;i++)for(unsigned bad=0;bad<2;bad++) {
    for(unsigned j=0;j<3;j++)*zero_inputs[j]=3;
    *zero_inputs[i]=bad?UINT32_MAX:4;
    assert(EnumaNativeMaskResult(EnumaInheritedOk,&o,7)==5);
  }
  assert(EnumaNativeMaskResult(EnumaInheritedOk,0,7)==5);
  for(unsigned i=0;i<2;i++)for(unsigned n=0;n<3;n++) {
    for(unsigned j=0;j<3;j++)*zero_inputs[j]=3;
    for(unsigned j=0;j<2;j++)for(unsigned k=0;k<3;k++)o.Samples[k].Interfaces[j].Timing=0;
    o.Samples[n].Interfaces[i].Timing=UINT32_MAX;
    assert(EnumaNativeMaskResult(EnumaInheritedOk,&o,7)==(3u&~(1u<<i))+1);
  }
  for(unsigned s=0;s<=14;s++)for(unsigned w=0;w<=14;w++)for(unsigned r=0;r<32;r++) {
    unsigned expected=1;
    if(s==0) { if(w==EnumaVideoReasonComplete&&r==(ENUMA_REQUIRE_ADDRESS|ENUMA_REQUIRE_TOPOLOGY))expected=5; }
    else if(s<=13&&!r&&w>=4&&w<=13&&w!=EnumaVideoReasonWait) {
      if(s==EnumaInheritedRefreshMode)expected=2;
      else if(w==EnumaVideoReasonPipeline)expected=s==EnumaInheritedTopology?3:4;
    }
    assert(EnumaNativeRouteResult(s,r,w)==expected);
  }
  for(unsigned s=0;s<=14;s++)for(unsigned w=0;w<=20;w++)for(unsigned r=0;r<32;r++) {
    unsigned expected=1;
    if(s==0&&w==EnumaVideoReasonComplete&&r==20)expected=5;
    if(s==13&&!r) {
      if(w==EnumaVideoReasonNativeCtl)expected=2;
      if(w==EnumaVideoReasonNativeStaging)expected=3;
      if(w==EnumaVideoReasonNativeMixerCapture||w==EnumaVideoReasonNativeMixerLayout||w==EnumaVideoReasonNativeDecode)expected=4;
    }
    assert(EnumaNativeRouteDetailResult(s,r,w)==expected);
  }
  for(unsigned s=0;s<=14;s++)for(unsigned w=0;w<=25;w++)for(unsigned r=0;r<32;r++) {
    unsigned expected=(s==13&&!r&&w>=21&&w<=24)?w-19:1;
    assert(EnumaNativeStagingResult(s,r,w)==expected);
  }
  for(unsigned s=0;s<=14;s++)for(unsigned w=0;w<=30;w++)for(unsigned r=0;r<32;r++) {
    unsigned expected=(s==13&&!r&&w>=26&&w<=29)?w-24:1;
    assert(EnumaNativeLayoutResult(s,r,w)==expected);
  }
  printf("PASS: 14880 layout selector cases; ");
  printf("PASS: 12480 staging selector cases; ");
  printf("PASS: 10080 detailed route mappings; ");
  printf("PASS: 7200 route result mapping cases; ");
  printf("PASS: %u actual terminal hook/status/GUID cases; 53 individual and 521 combined and 525 zero-ready mask/error selector cases; max22s cold delay\n",cases);
  return 0;
}
