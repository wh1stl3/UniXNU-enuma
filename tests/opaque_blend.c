// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "OpaqueBlend.h"
#include <assert.h>
#include <stdio.h>
int main(void) {
  ENUMA_U32 F,B;
  for(unsigned Fore=0;Fore<256;Fore++)for(unsigned Back=0;Back<256;Back++) {
    unsigned C=(Fore<<16)|Back;
    unsigned R=EnumaAnalyzeOpaqueBlend(0x100,C,0,&F,&B);
    assert(F==Fore&&B==Back&&R==((Fore==255&&Back==0)?EnumaOpaqueBlendFullSource:EnumaOpaqueBlendNotOpaque));
    R=EnumaAnalyzeOpaqueBlend(0x400,C,0,&F,&B);
    assert(F==Fore&&B==255-Fore&&R==(Fore==255?EnumaOpaqueBlendFullSource:EnumaOpaqueBlendNotOpaque));
  }
  unsigned Cases[]={0x402,0x600,0x602};
  for(unsigned I=0;I<3;I++) {
    assert(EnumaAnalyzeOpaqueBlend(Cases[I],0x00ff0000,1,&F,&B)==EnumaOpaqueBlendFullSource&&F==255&&!B);
    F=123;B=234;assert(EnumaAnalyzeOpaqueBlend(Cases[I],0x00ff0000,0,&F,&B)==EnumaOpaqueBlendUnknown&&F==123&&B==234);
  }
  for(unsigned Bit=0;Bit<32;Bit++) {
    if(0x707u&(1u<<Bit)){continue;}
    F=123;B=234;assert(EnumaAnalyzeOpaqueBlend(0x100|(1u<<Bit),0x00ff0000,1,&F,&B)==EnumaOpaqueBlendUnknown&&F==123&&B==234);
  }
  assert(EnumaAnalyzeOpaqueBlend(3,0x00ff0000,1,&F,&B)==EnumaOpaqueBlendUnknown);
  assert(EnumaAnalyzeOpaqueBlend(0x100,0xffffffffu,1,&F,&B)==EnumaOpaqueBlendUnknown);
  assert(EnumaAnalyzeOpaqueBlend(0x104,0x00ff0000,1,&F,&B)==EnumaOpaqueBlendNotOpaque);
  puts("PASS: 131072 constant-alpha coefficient cases, pixel-alpha premise, inverse/unknown/modulation/dim/background-alpha rejection; no BLEND requirement cleared");
}
