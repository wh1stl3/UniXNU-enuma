#include "EnumaScanoutSoleStage.h"
#include <stdio.h>
#include <assert.h>
#include <string.h>
static UINT32 descriptors[3][8][16],layers[3][6][6][4],bits[3][6],active[3][2],frame[3][2];
static UINT32 timing[3][2],enable[3][2],version[2];
static UINT32 mixers[3][6];
static EFI_STATUS ws[2];static UINTN reads,waits,vr,cases;
static const UINT32 pipes[8]={0x5000,0x7000,0x9000,0xb000,0x25000,0x27000,0x29000,0x2b000};
static void valid(UINTN p){for(UINTN w=0;w<3;w++){descriptors[w][p][0]=2560U<<16|1600;descriptors[w][p][3]=2560U<<16|1600;descriptors[w][p][5]=0x9c000000;descriptors[w][p][9]=6400;descriptors[w][p][12]=0x63f;}}
static void reset(void){
 memset(descriptors,0,sizeof(descriptors));memset(layers,0,sizeof(layers));memset(bits,0,sizeof(bits));
 reads=waits=vr=0;version[0]=version[1]=0x60000000;ws[0]=ws[1]=EFI_SUCCESS;
 valid(0);
 for(UINTN w=0;w<3;w++)for(UINTN l=0;l<6;l++)mixers[w][l]=2560U<<16|1600;
 for(UINTN w=0;w<3;w++){bits[w][0]=2;layers[w][0][0][0]=1;for(UINTN i=0;i<2;i++){active[w][i]=1;frame[w][i]=100+(UINT32)w*6;timing[w][i]=1;enable[w][i]=0;}}
}
static UINT32 rd(UINTN a){
 reads++;assert(reads<=250);assert(a>=0xae00000 && a+4<=0xae84208);
 if(a==0xae00000){assert(vr<2);return version[vr++];}
 for(UINTN i=0;i<8;i++){UINTN b=0xae00000+pipes[i];if(a>=b&&a<b+64){UINTN off=a-b;assert(off==0||off==8||off==0x0c||off==0x10||off==0x14||off==0x24||off==0x30||off==0x38);return descriptors[waits][i][off/4];}}
 for(UINTN i=0;i<2;i++){UINTN b=i?0xae6c000:0xae6b800;if(a==b+0x26c)return active[waits][i];if(a==b+0xac)return frame[waits][i];if(a==b)return timing[waits][i];if(a==b+0xa8)return enable[waits][i];}
 for(UINTN l=0;l<6;l++)if(a==0xae45004+l*0x1000)return mixers[waits][l];
 for(UINTN c=0;c<6;c++){UINTN b=0xae02000+c*0x200;if(a==b+0xf4)return bits[waits][c];for(UINTN l=0;l<6;l++)for(UINTN e=0;e<4;e++)if(a==b+EnumaRouteLayerOffset(l,e))return layers[waits][c][l][e];}
 assert(0);return 0;
}
static EFI_STATUS wt(UINTN u){assert(u==100000&&waits<2);return ws[waits++];}
static void run(EFI_STATUS expected){assert(EnumaScanoutSoleStage(rd,wt)==expected);cases++;}
int main(void){
 UINT32 l[4];const UINT8 ex[8]={0,0,0,0,0,0,2,2},sh[8]={0,3,6,26,18,21,0,4};
 const UINT32 sec[8]={1,4,16,64,65536,262144,0,0};
 reset();assert(EnumaScanoutSoleStage(NULL,wt)==EFI_INVALID_PARAMETER&&!reads);cases++;
 reset();assert(EnumaScanoutSoleStage(rd,NULL)==EFI_INVALID_PARAMETER&&!reads);cases++;
 for(UINTN i=0;i<8;i++){memset(l,0,sizeof(l));l[ex[i]]=1U<<sh[i];assert(EnumaRouteStaged(i,l));cases++;if(sec[i]){memset(l,0,sizeof(l));l[1]=sec[i];assert(EnumaRouteStaged(i,l));cases++;}}
 memset(l,0,sizeof(l));assert(!EnumaRouteStaged(8,l)&&!EnumaRouteStaged(0,NULL));cases++;
 reset();run(EFI_SUCCESS);assert(waits==2);
 reset();version[0]=0x60010000;run(EFI_UNSUPPORTED);assert(reads==1&&!waits);
 reset();memset(descriptors,0,sizeof(descriptors));run(EFI_UNSUPPORTED);assert(!waits);
 reset();active[0][0]=active[0][1]=0;run(EFI_NOT_READY);assert(!waits);
 reset();memset(bits,0,sizeof(bits));run(EFI_NOT_READY);assert(!waits);
 reset();memset(layers,0,sizeof(layers));run(EFI_NOT_READY);assert(!waits);
 reset();layers[0][0][0][0]=0;layers[0][0][0][3]=1;run(EFI_NOT_READY);assert(!waits);
 reset();bits[0][0]=1;run(EFI_NOT_READY);assert(!waits);
 reset();for(UINTN w=0;w<3;w++){bits[w][0]=4;}run(EFI_SUCCESS);
 reset();for(UINTN w=0;w<3;w++){bits[w][0]=0;bits[w][5]=2;layers[w][0][0][0]=0;layers[w][5][5][0]=1;}run(EFI_SUCCESS);
 for(UINTN i=0;i<8;i++){reset();memset(descriptors,0,sizeof(descriptors));valid(i);for(UINTN w=0;w<3;w++){layers[w][0][0][0]=0;layers[w][0][0][ex[i]]=1U<<sh[i];}run(EFI_SUCCESS);}
 reset();valid(1);for(UINTN w=0;w<3;w++)layers[w][0][0][0]=1U<<3;run(EFI_NOT_READY);assert(!waits); /* never substitute later candidate */
 reset();frame[1][0]=frame[0][0];run(EFI_NOT_READY);
 reset();frame[2][0]=frame[1][0];run(EFI_NOT_READY);
 reset();frame[1][0]=165;run(EFI_NOT_READY);
 reset();frame[0][0]=0xffffffff;frame[1][0]=0;run(EFI_NOT_READY);
 reset();for(UINTN w=0;w<3;w++)frame[w][0]=100+(UINT32)w*64;run(EFI_SUCCESS);
 reset();active[1][0]=0;run(EFI_NOT_READY);
 reset();timing[1][0]=2;run(EFI_NOT_READY);
 reset();enable[1][0]=3;run(EFI_NOT_READY);
 reset();bits[1][0]=6;run(EFI_NOT_READY);
 reset();layers[1][0][0][2]=1;run(EFI_NOT_READY);
 reset();descriptors[1][0][5]+=4;run(EFI_NOT_READY);
 reset();version[1]++;run(EFI_NOT_READY);
 reset();ws[0]=EFI_DEVICE_ERROR;run(EFI_DEVICE_ERROR);assert(waits==1);
 reset();ws[1]=1;run(EFI_NOT_READY);assert(waits==2);
 reset();for(UINTN i=0;i<8;i++)valid(i);
 for(UINTN w=0;w<3;w++){
  for(UINTN i=0;i<7;i++)descriptors[w][i][9]=0;
  for(UINTN c=0;c<6;c++)bits[w][c]=2;
  memset(layers[w],0,sizeof(layers[w]));layers[w][5][5][2]=1U<<4;
 }
 run(EFI_SUCCESS);assert(reads==250); /* all descriptors/CTLs/LMs at bound */
 reset();descriptors[0][0][3]--;run(EFI_NOT_READY);assert(!waits);
 reset();descriptors[0][0][4]=1;run(EFI_NOT_READY);assert(!waits);
 reset();mixers[0][0]=0;run(EFI_NOT_READY);assert(!waits);
 reset();mixers[0][0]=(2559U<<16)|1600;run(EFI_NOT_READY);
 reset();descriptors[1][0][3]--;run(EFI_NOT_READY);
 reset();descriptors[2][0][4]=1;run(EFI_NOT_READY);
 reset();mixers[1][0]++;run(EFI_NOT_READY);
 reset();mixers[2][0]++;run(EFI_NOT_READY);
 assert(EnumaGeometryContained(128,8,(8U<<16)|128,(3U<<16)|4,(11U<<16)|132));cases++;
 assert(!EnumaGeometryContained(128,8,(8U<<16)|128,0xffff,(8U<<16)|0xffff));cases++;
 assert(!EnumaGeometryContained(127,8,(8U<<16)|127,0,(8U<<16)|127));cases++;
 assert(!EnumaGeometryContained(128,7,(7U<<16)|128,0,(7U<<16)|128));cases++;
 reset();for(UINTN w=0;w<3;w++)layers[w][0][0][0]|=1U<<24;run(EFI_SUCCESS);
 reset();layers[0][0][0][0]|=1U<<3;run(EFI_NOT_READY);assert(!waits);
 reset();layers[0][0][0][3]=1;run(EFI_NOT_READY);
 reset();layers[0][0][0][1]=2;run(EFI_NOT_READY);
 reset();for(UINTN w=0;w<3;w++){layers[w][0][0][0]=0;layers[w][0][0][1]=1;}run(EFI_SUCCESS);
 reset();layers[1][0][0][0]|=1U<<24;run(EFI_NOT_READY);
 printf("PASS: %u staged route/two-window cases\n",(unsigned)cases);return 0;
}
