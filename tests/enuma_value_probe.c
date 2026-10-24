// Actual value transport with host read/wait adapters; no hardware execution.
#include "simplefb_test_uefi.h"
#include "EnumaValueProbe.h"
static unsigned reads, waits;
static UINT32 value;
static UINTN last_address, last_wait;
static EFI_STATUS wait_result;
static UINT32 read_word(UINTN address) { reads++; last_address=address; return value; }
static EFI_STATUS wait_us(UINTN delay) { waits++; last_wait=delay; return wait_result; }
int main(void) {
  for (unsigned code=0;code<16;code++) {
    reads=waits=0; wait_result=EFI_SUCCESS;
    assert(EnumaValueProbe(1,0,0,code,NULL,wait_us)==EFI_SUCCESS);
    assert(reads==0 && waits==(code!=0));
    if (code) assert(last_wait==code*3000000U);
  }
  for (unsigned shift=0;shift<=28;shift+=4) {
    reads=waits=0; value=(UINT32)10<<shift;
    assert(EnumaValueProbe(2,6,shift,0,read_word,wait_us)==EFI_SUCCESS);
    assert(reads==2 && waits==1 && last_address==0x0ae27014U && last_wait==30000000U);
  }
  reads=waits=0;
  assert(EnumaValueProbe(2,7,0,0,read_word,wait_us)==EFI_INVALID_PARAMETER);
  assert(EnumaValueProbe(2,0,32,0,read_word,wait_us)==EFI_INVALID_PARAMETER);
  assert(EnumaValueProbe(2,0,1,0,read_word,wait_us)==EFI_INVALID_PARAMETER);
  assert(EnumaValueProbe(2,0,0,1,read_word,wait_us)==EFI_INVALID_PARAMETER);
  assert(EnumaValueProbe(2,0,0,0,NULL,wait_us)==EFI_INVALID_PARAMETER);
  assert(reads==0 && waits==0);
  wait_result=EFI_DEVICE_ERROR;
  assert(EnumaValueProbe(1,0,0,1,NULL,wait_us)==EFI_DEVICE_ERROR);
  return 0;
}
