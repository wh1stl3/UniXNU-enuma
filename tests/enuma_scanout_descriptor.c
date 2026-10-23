#include <assert.h>
#include <stdio.h>
#undef NULL
#include "EnumaScanoutDescriptor.h"
static UINT32 regs[8][16];
static unsigned reads;
static const UINT32 pipes[8]={0x5000,0x7000,0x9000,0xb000,0x25000,0x27000,0x29000,0x2b000};
static UINT32 read32(UINTN a){unsigned i;reads++;assert(reads<=48);for(i=0;i<8;i++){UINTN p=0xae00000+pipes[i];if(a>=p&&a<p+64){assert(a==p||a==p+8||a==p+0x14||a==p+0x24||a==p+0x30||a==p+0x38);return regs[i][(a-p)/4];}}assert(0);return 0;}
static void clear(void){unsigned i,j;reads=0;for(i=0;i<8;i++)for(j=0;j<16;j++)regs[i][j]=0;}
static void valid(unsigned i){regs[i][0]=(2560U<<16)|1600;regs[i][5]=0x9c000000;regs[i][9]=6400;regs[i][12]=0x63f;}
static void bounds(ENUMA_SCANOUT_DESCRIPTOR *d){assert(d->Base>=0x9c000000&&d->End<=0x9e300000ULL&&d->Start>=d->Base&&d->Start<d->End);assert(d->Width&&d->Height&&d->Pitch%4==0);assert(d->Pitch>=((UINT64)d->X+d->Width)*4);assert(d->Start+(UINT64)(d->Height-1)*d->Pitch+(UINT64)d->Width*4==d->End);}
int main(void){ENUMA_SCANOUT_DESCRIPTOR d;unsigned i;UINT32 seed=1;
 assert(EnumaScanoutDecodeDescriptor(0,0,0,0,0,0,NULL)==EFI_INVALID_PARAMETER);
 assert(EnumaScanoutFindBoundedDescriptor(NULL,&d)==EFI_INVALID_PARAMETER);
 assert(EnumaScanoutFindBoundedDescriptor(read32,NULL)==EFI_INVALID_PARAMETER);
 for(i=0;i<21;i++){UINT32 base=0x9c000000,size=(2560U<<16)|1600,pitch=6400,xy=0,fmt=0x63f,op=0;d.Base=0x1234;
  switch(i){case 0:base--;break;case 1:base=0x9e300000;break;case 2:base++;break;case 3:size&=0xffff0000;break;case 4:size&=0xffff;break;case 5:pitch=0;break;case 6:pitch++;break;case 7:pitch-=4;break;case 8:xy=1;break;case 9:base=0x9e300000U-6400U*2560U+4;break;case 10:xy=0xffff0000;break;case 11:fmt|=1U<<30;break;case 12:fmt|=1U<<19;break;case 13:fmt&=~1U;break;case 14:fmt|=1U<<15;break;case 15:fmt|=1U<<14;break;case 16:op=1;break;case 17:fmt|=1U<<22;break;case 18:fmt|=1U<<11;break;case 19:fmt|=1U<<23;break;case 20:fmt&=~(3U<<9);break;}
  assert(EnumaScanoutDecodeDescriptor(base,size,pitch,xy,fmt,op,&d)==EFI_UNSUPPORTED&&d.Base==0x1234);
 }
 assert(EnumaScanoutDecodeDescriptor(0x9e300000U-6400U*2560U,(2560U<<16)|1600,6400,0,0x63f,0,&d)==EFI_SUCCESS);bounds(&d);
 assert(EnumaScanoutDecodeDescriptor(0x9c000000,(16U<<16)|64,0xffff0200,(8U<<16)|4,0x63f,0,&d)==EFI_SUCCESS);bounds(&d);assert(d.Pitch==512&&d.Width==64&&d.Height==16&&d.X==4&&d.Y==8);
 clear();assert(EnumaScanoutFindBoundedDescriptor(read32,&d)==EFI_UNSUPPORTED&&reads==8);
 for(i=0;i<8;i++){clear();valid(i);assert(EnumaScanoutFindBoundedDescriptor(read32,&d)==EFI_SUCCESS&&reads==i+6);bounds(&d);assert(d.Source==0xae00000+pipes[i]);}
 clear();valid(0);valid(1);regs[0][9]=0;assert(EnumaScanoutFindBoundedDescriptor(read32,&d)==EFI_SUCCESS&&reads==12);assert(d.Source==0xae00000+pipes[1]);
 clear();for(i=0;i<8;i++){valid(i);regs[i][9]=0;}assert(EnumaScanoutFindBoundedDescriptor(read32,&d)==EFI_UNSUPPORTED&&reads==48);
 for(i=0;i<10000;i++){UINT32 w,h,x,y,pitch;seed=seed*1664525U+1013904223U;w=(seed&2047)+1;h=((seed>>11)&1023)+1;x=(seed>>24)&63;y=(seed>>20)&15;pitch=(w+x)*4+((seed>>28)&15)*4; if(EnumaScanoutDecodeDescriptor(0x9c000000,(h<<16)|w,pitch,(y<<16)|x,0x63f,0,&d)==EFI_SUCCESS)bounds(&d);}
 puts("PASS: descriptor boundary rejection, cropped/padded layouts, packed stride, bounded reads and 10000 samples");
}
