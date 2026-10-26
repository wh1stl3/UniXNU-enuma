// SPDX-License-Identifier: BSD-2-Clause-Patent
// Host-only production formatter/rasterizer output; no callbacks or hardware.
#define ENUMA_BOOT_LOG_REPLAY 1
#include "PixelTransaction.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <inttypes.h>
int main(void) {
  ENUMA_BOOT_LOG Log; ENUMA_INHERITED_FRAME Frame={0};
  Frame.ReservedMask=0xff000000;
  for(unsigned N=0;N<96;N++) {
    UINT64 Status=N<64?((UINT64)1<<N):N==64?0:N==65?MAX_UINT64:0x0123456789abcdefULL*(N-65);
    UINT32 Ordinal=0x1020304u*(N+1);
    memset(&Log,0,sizeof Log);
    // Exercise a wrapped ring, actual return then later nonreturn record.
    for(unsigned I=0;I<128;I++) assert(EnumaBootLogAppend(&Log,13,I,NULL,0));
    assert(EnumaBootLogAppend(&Log,13,Ordinal,NULL,Status));
    assert(EnumaBootLogAppend(&Log,20,0xdeadbeef,NULL,0));
    assert(EnumaLogPageFromSnapshot(&Log,&mEnumaLogPage));
    printf("%08x %016" PRIx64 "\n",Ordinal,(uint64_t)Status);
    for(unsigned Row=0;Row<3;Row++) puts(mEnumaLogPage.Text[Row]);
    for(unsigned Y=0;Y<96;Y++) {
      for(unsigned X=0;X<256;X++) {
        ENUMA_U32 Pixel=EnumaPixelLogAt(&Frame,Y*256+X);
        assert(Pixel==0xffffffffu||Pixel==Frame.ReservedMask);
        putchar(Pixel==0xffffffffu?'1':'0');
      }
      putchar('\n');
    }
  }
  return 0;
}
