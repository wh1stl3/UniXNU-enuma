// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "Topology.h"
static ENUMA_INHERITED_SNAPSHOT S; static ENUMA_MIXER_SNAPSHOT T;
static ENUMA_INHERITED_LIMITS L,O; static ENUMA_INHERITED_FRAME F;
typedef struct { unsigned Count,Fail; } READER;
static int read_reg(void *Ctx,ENUMA_U32 Offset,ENUMA_U32 *V) {
  READER *R=Ctx; assert(Offset>=0x45000&&Offset<=0x4a114&&!(Offset&3));
  if(++R->Count==R->Fail) { return -1; } *V=Offset; return 1;
}
static void setup(void) {
  memset(&S,0,sizeof(S)); memset(&T,0,sizeof(T)); memset(&L,0,sizeof(L));
  S.Revision=0x60000000; S.Ctls[2].IntfActive=6;
  // Mixer 4 is LEFT, mixer 0 RIGHT. Numeric ordering is intentionally reversed.
  S.Ctls[2].Layers[4][0]=1; S.Ctls[2].Layers[0][0]=8;
  T.Mixers[4].Size=T.Mixers[0].Size=(2560u<<16)|800;
  T.Mixers[0].Mode=1u<<31;
  S.Pipes[0].Size=S.Pipes[0].OutSize=(2560u<<16)|800;
  S.Pipes[0].Address=0x10100000; S.Pipes[0].Stride=6400; S.Pipes[0].Format=0x236ff; S.Pipes[0].Unpack=0x03020001;
  S.Pipes[1]=S.Pipes[0]; S.Pipes[1].Address+=3200;
  L.Width=1600; L.Height=2560; L.SplashBase=0x10000000; L.SplashBytes=0x2000000;
}
static void bad(void) {
  ENUMA_INHERITED_LIMITS Before; memset(&O,0xa5,sizeof(O)); Before=O;
  assert(EnumaResolveMixerOrigins(&S,&T,&L,&O)==EnumaInheritedTopology&&!memcmp(&Before,&O,sizeof(O)));
}
int main(void) {
  setup(); assert(!EnumaResolveMixerOrigins(&S,&T,&L,&O)); assert(O.OriginMask==3&&O.OriginX[0]==0&&O.OriginX[1]==800);
  assert(!EnumaDecodeInherited(&S,&O,&F)&&F.Base==0x10100000&&F.Requirements==ENUMA_REQUIRE_ALL);
  T.Mixers[0].Mode=0; bad(); setup(); T.Mixers[4].Mode=1u<<31; bad();
  setup(); T.Mixers[0].Mode|=1u<<30; bad();
  setup(); S.Ctls[2].IntfActive=2; bad();
  setup(); S.Ctls[1].IntfActive=6; bad();
  setup(); S.Ctls[2].Layers[4][0]|=1u<<24; bad();
  setup(); S.Ctls[2].Layers[4][3]=1; bad();
  setup(); S.Ctls[2].Layers[4][0]=8; bad(); // one pipe belongs to both mixers
  setup(); T.Mixers[4].Blend[10]=1u<<16; bad();
  setup(); S.Pipes[0].OutXy=1; bad();
  setup(); T.Mixers[4].Size--; bad();
  // Stage 9 = low1 + ext bit. Requires stage-index7 alpha, not base.
  setup(); S.Ctls[2].Layers[4][1]=1; bad();
  T.Mixers[4].Blend[7]=0x100; T.Mixers[4].Alpha[7]=0xff0000;
  assert(!EnumaResolveMixerOrigins(&S,&T,&L,&O));
  ENUMA_MIXER_SNAPSHOT Out,Before; memset(&Out,0xa5,sizeof(Out)); Before=Out;
  for(unsigned Fail=1;Fail<=144;Fail++) { READER R={0,Fail}; assert(EnumaCaptureMixers(read_reg,&R,&Out)==EnumaInheritedBounds&&R.Count==Fail&&!memcmp(&Out,&Before,sizeof(Out))); }
  READER R={0}; assert(!EnumaCaptureMixers(read_reg,&R,&Out)&&R.Count==144);
  setup(); S.Ctls[2].IntfActive=2; R=(READER){0}; Out=Before;
  assert(EnumaCaptureRoutedMixers(&S,read_reg,&R,&Out)==EnumaInheritedTopology&&!R.Count&&!memcmp(&Out,&Before,sizeof(Out)));
  for(unsigned mask=0;mask<64;mask++) {
    setup();for(unsigned m=0;m<6;m++)if(mask&(1u<<m))S.Ctls[2].Layers[m][0]|=1u<<24;
    ENUMA_INHERITED_SNAPSHOT before=S;
    assert(EnumaClassifyVideoStaging(&S)==(mask?EnumaStagingBorderOnly:EnumaStagingOther));
    assert(!memcmp(&S,&before,sizeof(S)));
  }
  for(unsigned m=0;m<6;m++)for(unsigned j=0;j<4;j++)for(unsigned bit=0;bit<32;bit++) {
    setup();S.Ctls[2].Layers[m][j]^=1u<<bit;
    ENUMA_INHERITED_SNAPSHOT before=S,norm=S;
    for(unsigned k=0;k<6;k++)norm.Ctls[2].Layers[k][0]&=~(1u<<24);
    unsigned ctl=99,mixers=99,pipes=99;
    unsigned normalized_ok=EnumaSelectVideoRoute(&norm,&ctl,&mixers,&pipes)==EnumaInheritedOk;
    unsigned classified=EnumaClassifyVideoStaging(&S);
    assert((classified==EnumaStagingBorderOnly)==(normalized_ok&&j==0&&bit==24));
    assert(!memcmp(&S,&before,sizeof(S)));
  }
  setup();S.Ctls[2].Layers[4][0]|=8;assert(EnumaClassifyVideoStaging(&S)==EnumaStagingSourceShape);
  setup();S.Ctls[2].Layers[4][3]=1;assert(EnumaClassifyVideoStaging(&S)==EnumaStagingUnknownFields);
  setup();S.Ctls[2].Layers[4][0]=8;assert(EnumaClassifyVideoStaging(&S)==EnumaStagingCardinality);
  setup();S.Ctls[2].Layers[4][0]=0;assert(EnumaClassifyVideoStaging(&S)==EnumaStagingCardinality);
  setup();S.Ctls[2].IntfActive=2;assert(EnumaClassifyVideoStaging(&S)==EnumaStagingOther);
  assert(EnumaClassifyVideoStaging(0)==EnumaStagingOther);
  puts("PASS: pure staging classification, all64 border masks, 768 single-bit perturbations, source/unknown/cardinality cases, no mutation");
  puts("PASS: reversed mixer identities, explicit right flag, dual tile decode, 12 topology rejects and 144 callback failures; downstream/CPU proof remains required");
}
