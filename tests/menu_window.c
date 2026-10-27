// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "MenuWindow.h"
typedef struct {ENUMA_U32 *Memory,Reads,Writes,Bars,ReadFail,WriteFail,BarFail,Validate;} MOCK;
static int Read(void *P,ENUMA_U64 A,ENUMA_U32 *V) {
  MOCK *M=P;M->Reads++;
  assert(A>=0x9c000000ULL&&A<0x9cfa0000ULL&&!(A&3));
  if(M->Reads==M->ReadFail) {return 0;}*V=M->Memory[(A-0x9c000000ULL)/4];return 1;
}
static int Write(void *P,ENUMA_U64 A,ENUMA_U32 V) {
  MOCK *M=P;M->Writes++;
  assert(A>=0x9c000000ULL&&A<0x9cfa0000ULL&&!(A&3));
  if(M->Writes==M->WriteFail) {return 0;}M->Memory[(A-0x9c000000ULL)/4]=V;return 1;
}
static int Barrier(void *P) {MOCK *M=P;return ++M->Bars!=M->BarFail;}
static int Validate(void *P,const ENUMA_INHERITED_FRAME *F) {(void)F;return ((MOCK *)P)->Validate;}
static ENUMA_INHERITED_FRAME Frame={0x9c000000ULL,6400ULL*2560,1600,2560,6400,0xff0000,0xff00,255,0xff000000,16,8,0,3,1,0,6,22};
static ENUMA_U32 *Saved,*Source;static MOCK M;
static void Reset(ENUMA_MENU_WINDOW *C) {
  memset(C,0,sizeof(*C));memset(M.Memory,0x71,6400*2560);M.Reads=M.Writes=M.Bars=M.ReadFail=M.WriteFail=M.BarFail=0;M.Validate=1;
}
static void CheckOriginal(void) {ENUMA_U32 I;for(I=0;I<1600*2560;I++){assert(M.Memory[I]==0x71717171);}}
static void Save(ENUMA_MENU_WINDOW *C) {assert(EnumaMenuSave(C,&Frame,Saved,Read,Write,Barrier,Validate,&M));}
int main(void) {
  ENUMA_MENU_WINDOW C;ENUMA_U32 I,J,K,L,Tests=0,Points[]={1,ENUMA_MENU_PIXELS/2,ENUMA_MENU_PIXELS};
  ENUMA_U32 Masks[]={255,0xff00,0xff0000,0xff000000};
  M.Memory=malloc(6400*2560);Saved=malloc(ENUMA_MENU_PIXELS*4);Source=malloc(ENUMA_MENU_PIXELS*4);
  assert(M.Memory&&Saved&&Source);for(I=0;I<ENUMA_MENU_PIXELS;I++){Source[I]=(I*0x10203u)&0xffffff;}
  for(I=0;I<4;I++){for(J=0;J<4;J++){for(K=0;K<4;K++){for(L=0;L<4;L++){
    if(I==J||I==K||I==L||J==K||J==L||K==L){continue;}
    Frame.RedMask=Masks[I];Frame.GreenMask=Masks[J];Frame.BlueMask=Masks[K];Frame.ReservedMask=Masks[L];
    Reset(&C);Save(&C);assert(EnumaMenuPresent(&C,Source,0,0,800,600));
    assert((M.Memory[(96*1600)+64]&Frame.ReservedMask)==Frame.ReservedMask);
    assert(EnumaMenuRestore(&C)==5&&C.RestoreWrites==ENUMA_MENU_PIXELS);CheckOriginal();Tests++;
  }}}}
  for(I=0;I<3;I++) {
    Reset(&C);M.ReadFail=Points[I];assert(!EnumaMenuSave(&C,&Frame,Saved,Read,Write,Barrier,Validate,&M));assert(!M.Writes);Tests++;
    Reset(&C);Save(&C);M.WriteFail=Points[I];assert(!EnumaMenuPresent(&C,Source,0,0,800,600));
    J=M.Writes;assert(!EnumaMenuPresent(&C,Source,0,0,1,1)&&M.Writes==J);assert(EnumaMenuRestore(&C)==2);CheckOriginal();Tests++;
    Reset(&C);Save(&C);M.ReadFail=M.Reads+Points[I];assert(!EnumaMenuPresent(&C,Source,0,0,800,600));assert(EnumaMenuRestore(&C)==2);CheckOriginal();Tests++;
    Reset(&C);Save(&C);assert(EnumaMenuPresent(&C,Source,0,0,800,600));M.WriteFail=M.Writes+Points[I];
    assert(EnumaMenuRestore(&C)==4&&C.RestoreWrites==ENUMA_MENU_PIXELS);Tests++;
    Reset(&C);Save(&C);assert(EnumaMenuPresent(&C,Source,0,0,800,600));M.ReadFail=M.Reads+Points[I];
    assert(EnumaMenuRestore(&C)==4&&C.RestoreWrites==ENUMA_MENU_PIXELS);Tests++;
  }
  Reset(&C);M.Validate=0;assert(!EnumaMenuSave(&C,&Frame,Saved,Read,Write,Barrier,Validate,&M)&&!M.Writes);Tests++;
  Reset(&C);Save(&C);assert(!EnumaMenuPresent(&C,Source,799,599,2,1)&&!M.Writes);Tests++;
  Reset(&C);Save(&C);C.Writes=ENUMA_MENU_MAX_WRITES;assert(!EnumaMenuPresent(&C,Source,0,0,1,1)&&!M.Writes);Tests++;
  Reset(&C);Save(&C);C.Calls=ENUMA_MENU_MAX_CALLS;assert(!EnumaMenuPresent(&C,Source,0,0,1,1)&&!M.Writes);Tests++;
  for(I=1;I<=3;I++) {Reset(&C);M.BarFail=I;
    if(I==1){assert(!EnumaMenuSave(&C,&Frame,Saved,Read,Write,Barrier,Validate,&M)&&!M.Writes);}
    else {Save(&C);J=EnumaMenuPresent(&C,Source,0,0,800,600);assert(J==(I!=2));assert(EnumaMenuRestore(&C)==(I==3?4:2));}
    Tests++;
  }
  free(M.Memory);free(Saved);free(Source);printf("PASS menu window: %u cases, 24 channel masks, partial failures and full restoration\n",Tests);return 0;
}
