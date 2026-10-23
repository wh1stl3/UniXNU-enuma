#include <assert.h>
#include <stdio.h>
#undef NULL
#include "EnumaScanoutAudit.h"
static UINT32 r[8][16];static unsigned reads;static int address_only;
static UINT32 read32(UINTN a){const UINT32 p[8]={0x5000,0x7000,0x9000,0xb000,0x25000,0x27000,0x29000,0x2b000};unsigned i;assert(a>=0xae00000&&a+4<=0xae84208&&a%4==0);reads++;for(i=0;i<8;i++)if(a>=0xae00000+p[i]&&a<0xae00000+p[i]+64){assert(!address_only||(address_only==1?a==0xae00000+p[i]+0x14:(address_only==2?(a==0xae00000+p[i]+0x14||a==0xae00000+p[i]+0x30||a==0xae00000+p[i]+0x38):(a==0xae00000+p[i]+0x14||a==0xae00000+p[i]||a==0xae00000+p[i]+0x24))));return r[i][(a-0xae00000-p[i])/4];}assert(0);return 0;}
static void clear(void){unsigned i,j;for(i=0;i<8;i++)for(j=0;j<16;j++)r[i][j]=0;reads=0;}
static void valid(unsigned i){r[i][0]=(2560U<<16)|1600;r[i][5]=0x9c000000;r[i][9]=6400;r[i][12]=3U<<9;}
static void presence_tests(void){
 unsigned i;address_only=1;
 assert(EnumaScanoutAddressPresent(NULL)==EFI_INVALID_PARAMETER);
 clear();assert(EnumaScanoutAddressPresent(read32)==EFI_UNSUPPORTED&&reads==8);
 for(i=0;i<8;i++){clear();valid(i);r[i][0]=~0U;r[i][9]=~0U;r[i][12]=~0U;assert(EnumaScanoutAddressPresent(read32)==EFI_SUCCESS&&reads==i+1);}
 clear();r[0][5]=0x9c000000;assert(EnumaScanoutAddressPresent(read32)==EFI_SUCCESS);
 clear();r[0][5]=0x9bffffff;assert(EnumaScanoutAddressPresent(read32)==EFI_UNSUPPORTED);
 clear();r[0][5]=0x9e300000;assert(EnumaScanoutAddressPresent(read32)==EFI_UNSUPPORTED);
 clear();r[0][5]=0x9e2fffff;assert(EnumaScanoutAddressPresent(read32)==EFI_SUCCESS);
 clear();valid(0);valid(1);assert(EnumaScanoutAddressPresent(read32)==EFI_SUCCESS&&reads==1);
 address_only=0;
}
static void linear_tests(void){
 unsigned i;address_only=2;
 assert(EnumaScanoutLinearCandidates(NULL)==EFI_INVALID_PARAMETER);
 clear();assert(EnumaScanoutLinearCandidates(read32)==EFI_UNSUPPORTED&&reads==8);
 for(i=0;i<8;i++){clear();valid(i);r[i][12]|=0x3f;assert(EnumaScanoutLinearCandidates(read32)==EFI_SUCCESS&&reads==10);}
 for(i=0;i<10;i++){
  clear();valid(0);r[0][12]|=0x3f;
  switch(i){case 0:r[0][12]&=~(3U<<9);break;case 1:r[0][12]|=1U<<30;break;case 2:r[0][12]|=1U<<19;break;case 3:r[0][12]&=~1U;break;case 4:r[0][12]|=1U<<22;break;case 5:r[0][14]=1;break;case 6:r[0][12]|=1U<<15;break;case 7:r[0][12]|=1U<<14;break;case 8:r[0][12]|=1U<<23;break;case 9:r[0][12]|=1U<<11;break;}
  assert(EnumaScanoutLinearCandidates(read32)==EFI_UNSUPPORTED);
 }
 clear();valid(0);valid(1);r[0][12]|=0x3f;r[1][12]|=0x3f;assert(EnumaScanoutLinearCandidates(read32)==EFI_SUCCESS&&reads==12);
 r[1][14]=1;assert(EnumaScanoutLinearCandidates(read32)==EFI_UNSUPPORTED);
 clear();valid(0);r[0][12]|=0x3f;r[0][0]=~0U;r[0][9]=~0U;assert(EnumaScanoutLinearCandidates(read32)==EFI_SUCCESS);
 clear();for(i=0;i<8;i++){valid(i);r[i][12]|=0x3f;}assert(EnumaScanoutLinearCandidates(read32)==EFI_SUCCESS&&reads==24);
 address_only=0;
}
static void geometry_tests(void){
 unsigned i;address_only=3;
 assert(EnumaScanoutGeometryCandidates(NULL)==EFI_INVALID_PARAMETER);
 clear();assert(EnumaScanoutGeometryCandidates(read32)==EFI_UNSUPPORTED&&reads==8);
 for(i=0;i<8;i++){clear();valid(i);assert(EnumaScanoutGeometryCandidates(read32)==EFI_SUCCESS&&reads==10);}
 for(i=0;i<5;i++){
  clear();valid(0);
  switch(i){case 0:r[0][0]++;break;case 1:r[0][0]+=1U<<16;break;case 2:r[0][9]++;break;case 3:r[0][5]=0x9e300000U-6400U*2560U+4;break;case 4:r[0][5]++;break;}
  assert(EnumaScanoutGeometryCandidates(read32)==EFI_UNSUPPORTED);
 }
 clear();valid(0);r[0][5]=0x9e300000U-6400U*2560U;assert(EnumaScanoutGeometryCandidates(read32)==EFI_SUCCESS);
 clear();valid(0);valid(1);assert(EnumaScanoutGeometryCandidates(read32)==EFI_SUCCESS&&reads==12);
 r[1][9]++;assert(EnumaScanoutGeometryCandidates(read32)==EFI_UNSUPPORTED);
 clear();for(i=0;i<8;i++)valid(i);assert(EnumaScanoutGeometryCandidates(read32)==EFI_SUCCESS&&reads==24);
 clear();valid(0);r[0][12]=~0U;r[0][2]=~0U;r[0][6]=~0U;assert(EnumaScanoutGeometryCandidates(read32)==EFI_SUCCESS);
 address_only=0;
}
int main(void){unsigned i;assert(EnumaScanoutCheck(NULL)==EFI_INVALID_PARAMETER);clear();assert(EnumaScanoutCheck(read32)==EFI_UNSUPPORTED&&reads==8);for(i=0;i<8;i++){clear();valid(i);assert(EnumaScanoutCheck(read32)==EFI_SUCCESS&&reads==16);}for(i=0;i<13;i++){clear();valid(0);switch(i){case 0:r[0][0]++;break;case 1:r[0][9]++;break;case 2:r[0][12]|=1U<<30;break;case 3:r[0][14]|=1;break;case 4:r[0][2]=1;break;case 5:r[0][6]=1;break;case 6:r[0][7]=1;break;case 7:r[0][8]=1;break;case 8:r[0][5]=0x9e200000;break;case 9:r[0][12]=2U<<9;break;case 10:r[0][12]|=1U<<19;break;case 11:r[0][12]|=1U<<11;break;case 12:r[0][12]|=1U<<22;break;}assert(EnumaScanoutCheck(read32)==EFI_UNSUPPORTED);}clear();valid(0);valid(1);assert(EnumaScanoutCheck(read32)==EFI_UNSUPPORTED);clear();for(i=0;i<8;i++)valid(i);assert(EnumaScanoutCheck(read32)==EFI_UNSUPPORTED&&reads==72);presence_tests();linear_tests();geometry_tests();puts("PASS: 84 scanout cases; strict, address, packing and geometry boundaries");}
