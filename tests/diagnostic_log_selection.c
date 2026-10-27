// SPDX-License-Identifier: BSD-2-Clause-Patent
#define ENUMA_BOOT_LOG_REPLAY 3
#include "PixelTransaction.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static ENUMA_BOOT_LOG Log;
static EFI_GUID Guid={1,2,3,{4,5,6,7,8,9,10,11}};
static void Add(UINT32 Point,UINT32 Ordinal,UINT64 Status) {
  assert(EnumaBootLogAppend(&Log,Point,Ordinal,&Guid,Status));
}
static void Expect(CHAR8 Marker,CONST CHAR8 *Ordinal,UINT64 Seq) {
  assert(EnumaLogPageFromSnapshot(&Log,&mEnumaLogPage));
  assert(mEnumaLogPage.Text[0][0]==Marker);
  assert(!memcmp(mEnumaLogPage.Text[0]+5,Ordinal,8));assert(mEnumaLogPage.Sequence==Seq);
}
int main(void) {
  CONST CHAR8 Alphabet[]="0123456789abcdefOS+ QGEWC";
  for(unsigned I=0;I<sizeof Alphabet-1;I++) for(unsigned J=I+1;J<sizeof Alphabet-1;J++) {
    unsigned Diff=0;for(unsigned Y=0;Y<5;Y++) { Diff|=EnumaLogGlyph(Alphabet[I],Y)^EnumaLogGlyph(Alphabet[J],Y); }
    assert(Diff); // No label/hex/context collisions, including S/5 and O/0.
  }
  Add(13,1,0);Add(13,2,0);Expect('C',"00000002",1);
  Add(13,3,1);Add(13,4,0);Expect('W',"00000003",2);
  Add(13,5,0x8000000000000001ULL);Add(13,6,2);Expect('E',"00000005",4);
  Add(13,7,0x8000000000000002ULL);Expect('E',"00000007",6);
  Add(20,8,~0ULL);Add(21,9,~0ULL);Expect('E',"00000007",6);
  Log.Events[6].HasGuid=0;assert(!EnumaLogPageFromSnapshot(&Log,&mEnumaLogPage));
  Log.Events[6].HasGuid=1;
  for(unsigned I=0;I<128;I++) { Add(13,0x20,0); }
  Expect('C',"00000020",136);assert(mEnumaLogPage.Text[0][13]=='+');
  Log.Dropped++;assert(!EnumaLogPageFromSnapshot(&Log,&mEnumaLogPage));
  puts("PASS: all25 glyphs unique; newest highest severity; in-progress ignored; missing selected GUID rejected; ring eviction and loss validated");
}
