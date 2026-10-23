#include <assert.h>
#include <stdio.h>
#undef NULL
#include "EnumaScanoutAudit.h"
static UINT32 r[8][16];static unsigned reads;
static UINT32 read32(UINTN a){const UINT32 p[8]={0x5000,0x7000,0x9000,0xb000,0x25000,0x27000,0x29000,0x2b000};unsigned i;assert(a>=0xae00000&&a+4<=0xae84208&&a%4==0);reads++;for(i=0;i<8;i++)if(a>=0xae00000+p[i]&&a<0xae00000+p[i]+64)return r[i][(a-0xae00000-p[i])/4];assert(0);return 0;}
static void clear(void){unsigned i,j;for(i=0;i<8;i++)for(j=0;j<16;j++)r[i][j]=0;reads=0;}
static void valid(unsigned i){r[i][0]=(2560U<<16)|1600;r[i][5]=0x9c000000;r[i][9]=6400;r[i][12]=3U<<9;}
int main(void){unsigned i;assert(EnumaScanoutCheck(NULL)==EFI_INVALID_PARAMETER);clear();assert(EnumaScanoutCheck(read32)==EFI_UNSUPPORTED&&reads==8);for(i=0;i<8;i++){clear();valid(i);assert(EnumaScanoutCheck(read32)==EFI_SUCCESS&&reads==16);}for(i=0;i<13;i++){clear();valid(0);switch(i){case 0:r[0][0]++;break;case 1:r[0][9]++;break;case 2:r[0][12]|=1U<<30;break;case 3:r[0][14]|=1;break;case 4:r[0][2]=1;break;case 5:r[0][6]=1;break;case 6:r[0][7]=1;break;case 7:r[0][8]=1;break;case 8:r[0][5]=0x9e200000;break;case 9:r[0][12]=2U<<9;break;case 10:r[0][12]|=1U<<19;break;case 11:r[0][12]|=1U<<11;break;case 12:r[0][12]|=1U<<22;break;}assert(EnumaScanoutCheck(read32)==EFI_UNSUPPORTED);}clear();valid(0);valid(1);assert(EnumaScanoutCheck(read32)==EFI_UNSUPPORTED);clear();for(i=0;i<8;i++)valid(i);assert(EnumaScanoutCheck(read32)==EFI_UNSUPPORTED&&reads==72);puts("PASS: 25 scanout cases; bounded reads only");}
