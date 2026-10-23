#include <assert.h>
#include <stdio.h>
#undef NULL
#include "EnumaDsiCounters.h"
static UINT32 timing[2], enable[2], before[2], after[2];
static UINT32 final_timing[2], final_enable[2];
static unsigned reads, frames, waits, phase, configured_only;
static EFI_STATUS wait_status;
static UINT32 read32(UINTN address) {
  unsigned i;
  assert(++reads <= 12);
  for(i=0;i<2;i++) {
    UINTN base=i==0?0x0ae6b800U:0x0ae6c000U;
    if(address==base)return phase?final_timing[i]:timing[i];
    if(address==base+0xa8)return phase?final_enable[i]:enable[i];
    if(address==base+0xac) {
      assert(!configured_only && timing[i]!=0 && (enable[i]&3)==3);
      frames++;return phase?after[i]:before[i];
    }
  }
  assert(0);return 0;
}
static EFI_STATUS wait100(UINTN us) {
  assert(us==100000 && waits++==0 && phase==0);phase=1;return wait_status;
}
static void reset(void) {
  for(unsigned i=0;i<2;i++) {timing[i]=final_timing[i]=1;enable[i]=final_enable[i]=3;before[i]=100;after[i]=101;}
  reads=frames=waits=phase=configured_only=0;wait_status=EFI_SUCCESS;
}
int main(void) {
  unsigned cases=0;
  reset();assert(EnumaDsiCountersConfigured(NULL)==EFI_INVALID_PARAMETER && reads==0);cases++;
  assert(EnumaDsiCounterProgress(NULL,wait100)==EFI_INVALID_PARAMETER && reads==0);cases++;
  assert(EnumaDsiCounterProgress(read32,NULL)==EFI_INVALID_PARAMETER && reads==0);cases++;
  for(unsigned mask=0;mask<4;mask++) {
    reset();configured_only=1;for(unsigned i=0;i<2;i++)enable[i]=((mask>>i)&1)?3:0;
    assert(EnumaDsiCountersConfigured(read32)==(mask?EFI_SUCCESS:EFI_NOT_READY));assert(reads==4&&frames==0&&waits==0);cases++;
    reset();for(unsigned i=0;i<2;i++)enable[i]=final_enable[i]=((mask>>i)&1)?3:0;
    assert(EnumaDsiCounterProgress(read32,wait100)==(mask?EFI_SUCCESS:EFI_NOT_READY));assert(reads==(mask==0?4:(mask==3?12:8)));assert(waits==(mask!=0));cases++;
  }
  for(unsigned mode=0;mode<4;mode++) {
    reset();enable[0]=enable[1]=mode;final_enable[0]=final_enable[1]=mode;
    assert(EnumaDsiCounterProgress(read32,wait100)==(mode==3?EFI_SUCCESS:EFI_NOT_READY));assert(mode==3||(!frames&&!waits&&reads==4));cases++;
  }
  reset();timing[0]=timing[1]=0;assert(EnumaDsiCounterProgress(read32,wait100)==EFI_NOT_READY&&reads==4&&!waits);cases++;
  const UINT32 starts[]={100,100,100,100,0xffffffffU,0xfffffff0U};
  const UINT32 ends[]={100,101,164,165,0,8};
  for(unsigned n=0;n<6;n++) {
    reset();enable[1]=final_enable[1]=0;before[0]=starts[n];after[0]=ends[n];
    UINT32 delta=(UINT32)(ends[n]-starts[n]);assert(EnumaDsiCounterProgress(read32,wait100)==(delta>0&&delta<=64?EFI_SUCCESS:EFI_NOT_READY));assert(reads==8&&waits==1&&frames==2);cases++;
  }
  reset();after[0]=0;assert(EnumaDsiCounterProgress(read32,wait100)==EFI_NOT_READY);cases++;
  reset();after[0]=100;assert(EnumaDsiCounterProgress(read32,wait100)==EFI_SUCCESS);cases++;
  reset();after[0]=before[0];after[1]=before[1];assert(EnumaDsiCounterProgress(read32,wait100)==EFI_NOT_READY);cases++;
  for(unsigned i=0;i<2;i++)for(unsigned change=0;change<3;change++) {
    reset();if(change==0)final_timing[i]=0;else if(change==1)final_timing[i]=2;else final_enable[i]=7;
    assert(EnumaDsiCounterProgress(read32,wait100)==EFI_NOT_READY);cases++;
  }
  reset();wait_status=EFI_DEVICE_ERROR;assert(EnumaDsiCounterProgress(read32,wait100)==EFI_DEVICE_ERROR&&reads==6&&frames==2&&waits==1);cases++;
  reset();wait_status=1;assert(EnumaDsiCounterProgress(read32,wait100)==EFI_NOT_READY&&reads==6&&frames==2);cases++;
  printf("PASS: %u DSI counter cases; disabled counters never sampled, stable config, wrap/reset/delta/wait guards\n",cases);
}
