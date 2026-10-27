// SPDX-License-Identifier: BSD-2-Clause-Patent
#define ENUMA_BOOT_LOG_REPLAY 3
#include "PixelTransaction.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static ENUMA_BOOT_LOG Log;
int main(void) {
  ENUMA_INHERITED_FRAME F={0};F.ReservedMask=0xff000000;
  for(unsigned Case=0;Case<194;Case++) {
    memset(&Log,0,sizeof Log);EFI_GUID Guid={0};
    for(unsigned I=0;I<16;I++) { ((UINT8 *)&Guid)[I]=(UINT8)(Case*17+I); }
    if(Case>=64&&Case<192) { memset(&Guid,0,sizeof Guid);((UINT8 *)&Guid)[(Case-64)/8]=1u<<((Case-64)%8); }
    UINT64 Status=Case<64?1ULL<<Case:Case==192?0:~0ULL;
    UINT32 Ordinal=Case*0x1234567u;
    for(unsigned I=0;I<130;I++) { assert(EnumaBootLogAppend(&Log,15,I,&Guid,0)); }
    assert(EnumaBootLogAppend(&Log,13,Ordinal,&Guid,Status));
    assert(EnumaBootLogAppend(&Log,20,0,&Guid,0));
    // Full-width sequence retained with valid wrapped ring invariants.
    UINT64 Delta=Case<64?(1ULL<<Case):0;
    if(Case==63) { Delta=0x8000000000000000ULL; }
    for(unsigned I=0;I<Log.Count;I++) { Log.Events[(Log.Head+I)%128].Sequence+=Delta; }
    Log.NextSequence+=Delta;Log.Dropped+=Delta;
    assert(EnumaLogPageFromSnapshot(&Log,&mEnumaLogPage));
    printf("%08x %016llx %016llx ",Ordinal,(unsigned long long)Status,(unsigned long long)(130+Delta));
    for(unsigned I=0;I<16;I++) { printf("%02x",((UINT8 *)&Guid)[I]); }puts("");
    for(unsigned I=0;I<5;I++) { puts(mEnumaLogPage.Text[I]); }
    for(unsigned Y=0;Y<160;Y++) { for(unsigned X=0;X<320;X++) { putchar(EnumaPixelLogAt(&F,Y*320+X)==0xffffffffu?'1':'0'); }puts(""); }
  }
}
