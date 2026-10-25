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
  assert(EnumaNativeMaskResult(EnumaInheritedOk,&o,7)==5);
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
  printf("PASS: %u actual terminal hook/status/GUID cases; 53 individual and 521 combined mask/error selector cases; max22s cold delay\n",cases);
  return 0;
}
