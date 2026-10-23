#include <assert.h>
#include <stdio.h>
#undef NULL
#include "EnumaScanoutAudit.h"
static UINT32 values[2];
static unsigned reads;
static UINT32 read32(UINTN address) {
  assert(reads < 2);
  assert(address == (reads == 0 ? 0x0ae6b800U : 0x0ae6c000U));
  return values[reads++];
}
int main(void) {
  const UINT32 cases[][2]={{0,0},{1,0},{0,1},{1,1},{2,0},{0,0x80000000U},{~0U,~0U}};
  assert(EnumaDsiTimingEnabled(NULL)==EFI_INVALID_PARAMETER && reads==0);
  for (unsigned i=0;i<sizeof(cases)/sizeof(cases[0]);i++) {
    values[0]=cases[i][0];values[1]=cases[i][1];reads=0;
    EFI_STATUS expected=(values[0]!=0 || values[1]!=0)?EFI_SUCCESS:EFI_UNSUPPORTED;
    assert(EnumaDsiTimingEnabled(read32)==expected);
    assert(reads==2);
  }
  puts("PASS: 8 DSI timing cases; exact read order, both interfaces read, null guard and nonzero semantics");
}
