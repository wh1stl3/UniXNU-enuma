#include "EnumaDsiNativeProgress.h"
#include <stdio.h>
#include <assert.h>
static UINT32 version[2], active[2][3], timing[2][3], enable[2][3], frame[2][3];
static UINTN reads,waits,vr,fr,cases; static EFI_STATUS ws[2];
static void reset(void){
  UINTN i,j;reads=waits=vr=fr=0;version[0]=version[1]=0x60000000;
  ws[0]=ws[1]=EFI_SUCCESS;
  for(i=0;i<2;i++)for(j=0;j<3;j++){
    active[i][j]=1;timing[i][j]=1;enable[i][j]=0;frame[i][j]=100+(UINT32)j*6;
  }
}
static UINT32 rd(UINTN a){
  UINTN i;reads++;assert(reads<=26);
  if(a==0xae00000){assert(vr<2);return version[vr++];}
  for(i=0;i<2;i++){
    UINTN b=i?0xae6c000:0xae6b800;
    if(a==b+0x26c)return active[i][waits];
    if(a==b)return timing[i][waits];
    if(a==b+0xa8)return enable[i][waits];
    if(a==b+0xac){fr++;assert(active[i][0]&1);return frame[i][waits];}
  }
  assert(0);return 0;
}
static EFI_STATUS wt(UINTN u){EFI_STATUS s;assert(u==100000 && waits<2);s=ws[waits];waits++;return s;}
static void progress(EFI_STATUS expected){assert(EnumaDsiNativeProgress(rd,wt)==expected);cases++;}
int main(void){
  UINTN i,j;
  reset();assert(EnumaDsiNativeProgress(NULL,wt)==EFI_INVALID_PARAMETER && reads==0);cases++;
  reset();assert(EnumaDsiNativeProgress(rd,NULL)==EFI_INVALID_PARAMETER && reads==0);cases++;
  reset();assert(EnumaDsiNativeActive(NULL)==EFI_INVALID_PARAMETER);cases++;
  reset();assert(EnumaDsiNativeActive(rd)==EFI_SUCCESS && reads==3);cases++;
  reset();version[0]=0x50000000;assert(EnumaDsiNativeActive(rd)==EFI_UNSUPPORTED && reads==1);cases++;
  reset();version[0]=0xffffffff;progress(EFI_UNSUPPORTED);assert(reads==1 && !waits && !fr);
  reset();active[0][0]=active[1][0]=0;assert(EnumaDsiNativeActive(rd)==EFI_NOT_READY && reads==3);cases++;
  reset();active[0][0]=active[1][0]=0;progress(EFI_NOT_READY);assert(reads==7 && !waits && !fr);
  reset();progress(EFI_SUCCESS);assert(reads==26 && waits==2 && fr==6);
  reset();for(j=0;j<3;j++)active[1][j]=0;progress(EFI_SUCCESS);assert(reads==17 && fr==3);
  reset();for(i=0;i<2;i++)for(j=0;j<3;j++)frame[i][j]=100;progress(EFI_NOT_READY);
  reset();for(i=0;i<2;i++)frame[i][2]=frame[i][1];progress(EFI_NOT_READY);
  reset();frame[0][1]=100;frame[0][2]=106;frame[1][1]=106;frame[1][2]=106;progress(EFI_NOT_READY);
  reset();for(i=0;i<2;i++)for(j=0;j<3;j++)frame[i][j]=100+(UINT32)j;progress(EFI_SUCCESS);
  reset();for(i=0;i<2;i++)for(j=0;j<3;j++)frame[i][j]=100+(UINT32)j*64;progress(EFI_SUCCESS);
  reset();frame[0][1]=165;progress(EFI_NOT_READY);
  reset();frame[0][0]=0xffffffff;frame[0][1]=0;progress(EFI_NOT_READY);
  reset();frame[0][1]=99;progress(EFI_NOT_READY);
  reset();active[0][1]=0;progress(EFI_NOT_READY);
  reset();active[0][1]=3;progress(EFI_SUCCESS);
  reset();timing[0][1]=2;progress(EFI_NOT_READY);
  reset();enable[0][1]=3;progress(EFI_NOT_READY);
  reset();version[1]++;progress(EFI_NOT_READY);
  reset();ws[0]=EFI_DEVICE_ERROR;progress(EFI_DEVICE_ERROR);assert(waits==1 && fr==2);
  reset();ws[1]=EFI_DEVICE_ERROR;progress(EFI_DEVICE_ERROR);assert(waits==2 && fr==4);
  reset();ws[0]=1;progress(EFI_NOT_READY);
  reset();for(i=0;i<2;i++)for(j=0;j<3;j++)enable[i][j]=0xffffffff;progress(EFI_SUCCESS);
  printf("PASS: %u native status/two-window cases\n",(unsigned)cases);return 0;
}
