// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "InheritedScanout.h"
static ENUMA_INHERITED_SNAPSHOT S;
static ENUMA_INHERITED_LIMITS L;
static ENUMA_INHERITED_FRAME F;
static unsigned Cases;
static void setup(void) {
  memset(&S,0,sizeof(S)); memset(&L,0,sizeof(L));
  L.SplashBase=0x10000000; L.SplashBytes=0x2000000; L.Width=1600; L.Height=2560;
  L.OriginMask=1;
  S.Revision=0x60000000; S.Ctls[0].IntfActive=2; S.Ctls[0].Layers[0][0]=1;
  S.Pipes[0].Size=S.Pipes[0].OutSize=(2560u<<16)|1600u;
  S.Pipes[0].Address=0x10100000; S.Pipes[0].Stride=6400;
  S.Pipes[0].Format=0x236ff; S.Pipes[0].Unpack=0x03020001;
}
static void check(unsigned expected) {
  memset(&F,0xa5,sizeof(F));
  assert(EnumaDecodeInherited(&S,&L,&F)==expected); Cases++;
  if(expected) { const unsigned char *P=(const void *)&F; for(unsigned I=0;I<sizeof(F);I++) { assert(!P[I]); } }
  else { assert(F.Requirements==ENUMA_REQUIRE_ALL); assert(F.Base>=L.SplashBase); }
}
typedef struct { unsigned Count,Fail,Max; } READER;
static int read_reg(void *Context,ENUMA_U32 Offset,ENUMA_U32 *Value) {
  READER *R=Context; assert(!(Offset&3)); assert(Offset<0x85000);
  R->Count++; if(Offset>R->Max) { R->Max=Offset; }
  if(R->Fail==R->Count) { return 0; }
  *Value=Offset?Offset:0x60000000; return 1;
}
static int negative_read(void *Context,ENUMA_U32 Offset,ENUMA_U32 *Value) {
  (void)Context; (void)Offset; (void)Value; return -1;
}
int main(void) {
  setup(); check(EnumaInheritedOk);
  assert(F.Width==1600 && F.Height==2560 && F.Stride==6400 && F.ManualCtlMask==0);
  // Stale command auto-refresh fields cannot reject video mode.
  S.IntfAutoRefresh[0]=0x80000000; check(EnumaInheritedOk);
  S.Ctls[0].Top=1u<<17; check(EnumaInheritedMode);
  L.Mode=ENUMA_MODE_COMMAND; S.IntfAutoRefresh[0]=0; check(EnumaInheritedOk); assert(F.ManualCtlMask==1);
  S.IntfAutoRefresh[0]=0x80000001; check(EnumaInheritedOk); assert(!F.ManualCtlMask);
  S.IntfAutoRefresh[0]=0x80000000; check(EnumaInheritedRefreshMode);
  setup(); S.Revision=0x50000000; check(EnumaInheritedRevision);
  setup(); S.Ctls[0].IntfActive=1; check(EnumaInheritedRoute);
  setup(); S.Ctls[0].Layers[0][0]=0; check(EnumaInheritedRoute);
  setup(); S.Ctls[0].Layers[0][3]=1; check(EnumaInheritedVirtualRect);
  setup(); S.Pipes[0].Secure=1; check(EnumaInheritedSecure);
  setup(); S.Pipes[0].Multirect=1; check(EnumaInheritedVirtualRect);
  setup(); S.Pipes[0].OpMode=1; check(EnumaInheritedFormat);
  setup(); S.Pipes[0].Stride|=1u<<16; check(EnumaInheritedGeometry);
  setup(); S.Pipes[0].Size--; check(EnumaInheritedGeometry);
  setup(); S.Pipes[0].Unpack=0; check(EnumaInheritedFormat);
  setup(); S.Pipes[0].Address=0x1000; check(EnumaInheritedBounds);
  setup(); L.SplashBytes=1024; check(EnumaInheritedBounds);
  setup(); L.SplashBase=~0ULL-10; L.SplashBytes=20; check(EnumaInheritedArguments);
  setup(); L.Width=65536; check(EnumaInheritedArguments);
  setup(); L.Height=0; check(EnumaInheritedArguments);
  setup(); L.OriginMask=0; check(EnumaInheritedTopology);
  // Same allocation split into two adjacent rectangles; no copied panel constants.
  setup(); S.Pipes[0].Size=S.Pipes[0].OutSize=(2560u<<16)|800;
  S.Pipes[1]=S.Pipes[0]; S.Pipes[1].OutXy=800; S.Pipes[1].Address+=3200;
  L.OriginMask=3;
  S.Ctls[0].Layers[0][0]=1|(1<<3); check(EnumaInheritedOk); assert(F.PipeMask==3);
  // A local right-hand mixer at X0 needs an explicitly supplied X800 origin.
  S.Pipes[1].OutXy=0; L.OriginX[1]=800; check(EnumaInheritedOk);
  L.OriginX[1]=1601; check(EnumaInheritedTopology);
  L.OriginX[1]=0; S.Pipes[1].OutXy=800;
  S.Pipes[1].OutXy=801; S.Pipes[1].Address+=4; check(EnumaInheritedGeometry);
  S.Pipes[1].OutXy=801; S.Pipes[1].Size=S.Pipes[1].OutSize=(2560u<<16)|799;
  check(EnumaInheritedCoverage);
  S.Pipes[1].OutXy=800; S.Pipes[1].Address-=4;
  S.Pipes[1].Size=S.Pipes[1].OutSize=(2560u<<16)|800;
  S.Pipes[1].Address+=4096; check(EnumaInheritedInconsistent);
  setup(); assert(EnumaDecodeInherited(0,&L,&F)==EnumaInheritedArguments);
  assert(EnumaDecodeInherited(&S,0,&F)==EnumaInheritedArguments);
  assert(EnumaDecodeInherited(&S,&L,0)==EnumaInheritedArguments);
  ENUMA_INHERITED_SNAPSHOT Out,Before; READER R={0};
  assert(EnumaCaptureInherited(read_reg,&R,&Out)==EnumaInheritedOk);
  assert(R.Count==267 && R.Max==0x73830 && Out.Pipes[0].Secure==0x5070 && Out.Pipes[0].Multirect==0x5170);
  // Every failed callback leaves the entire caller snapshot unchanged.
  for(unsigned I=1;I<=267;I++) {
    memset(&Out,0xa5,sizeof(Out)); Before=Out; R=(READER){0,I,0};
    assert(EnumaCaptureInherited(read_reg,&R,&Out)==EnumaInheritedBounds);
    assert(!memcmp(&Out,&Before,sizeof(Out))); assert(R.Count==I);
  }
  assert(EnumaCaptureInherited(0,&R,&Out)==EnumaInheritedArguments);
  assert(EnumaCaptureInherited(read_reg,&R,0)==EnumaInheritedArguments);
  Before=Out;
  assert(EnumaCaptureInherited(negative_read,&R,&Out)==EnumaInheritedBounds);
  assert(!memcmp(&Out,&Before,sizeof(Out)));
  printf("PASS: %u decode scenarios, split/gap/bounds/mode rejection,267 callback failures, no MMIO/pixel access\n",Cases);
  return 0;
}
