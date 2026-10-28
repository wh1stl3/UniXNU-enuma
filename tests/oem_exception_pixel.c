// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <Uefi.h>
#include <Library/BaseMemoryLib.h>
#define ENUMA_BOOT_LOG_REPLAY 3
#if ENUMA_OEM_CONTEXT
#define ENUMA_BOOT_LOG_HOLD_US 4000000
#else
#define ENUMA_BOOT_LOG_HOLD_US 8000000
#endif
#define ENUMA_CAPTURE_PREPARED_ONLY 1
#include "EnumaOemCapturePixel.h"
#include "EnumaOemExceptionView.h"
#include "EnumaOemExceptionPage.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
VOID *EFIAPI ZeroMem(VOID *D,UINTN N){return memset(D,0,N);}
VOID *EFIAPI CopyMem(VOID *D,CONST VOID *S,UINTN N){return memcpy(D,S,N);}
static ENUMA_CAPTURE_PIXEL P;
static UINT32 Pixels[ENUMA_PIXEL_WORDS],Original[ENUMA_PIXEL_WORDS];
static UINT32 Reads,Writes,Barriers,Holds,FailRead,FailWrite,FailBarrier,FailHold,FailValidate;
static UINTN Index(UINT64 A){UINT64 D=A-P.Frame.Base;UINTN Y=D/P.Frame.Stride,X=D%P.Frame.Stride/4;
 assert(A>=P.Frame.Base&&!(A&3)&&Y>=96&&Y<256&&X>=64&&X<384);return (Y-96)*320+X-64;}
static int Read(void *C,UINT64 A,UINT32 *V){(void)C;*V=Pixels[Index(A)];return ++Reads!=FailRead;}
static int Write(void *C,UINT64 A,UINT32 V){(void)C;if(++Writes==FailWrite)return 0;Pixels[Index(A)]=V;return 1;}
static int Barrier(void *C){(void)C;return ++Barriers!=FailBarrier;}
static int Hold(void *C,UINT32 U){(void)C;assert(U==ENUMA_BOOT_LOG_HOLD_US&&!Holds);Holds++;return !FailHold;}
static int Validate(void *C,const ENUMA_INHERITED_FRAME *F){(void)C;assert(F==&P.Frame&&Reads==51200&&!Writes);return !FailValidate;}
static void Setup(UINT32 Page){
 memset(&P,0,sizeof(P));P.Policy=3;P.El=4;P.Read=Read;P.Write=Write;P.Barrier=Barrier;P.Hold=Hold;P.Validate=Validate;
 P.Frame.Base=0x9c000000;P.Frame.Width=1600;P.Frame.Height=2560;P.Frame.Stride=6400;P.Frame.Bytes=6400ULL*2560;
 P.Frame.Requirements=22;P.Frame.RedMask=255;P.Frame.GreenMask=0xff00;P.Frame.BlueMask=0xff0000;P.Frame.ReservedMask=0xff000000;
 ENUMA_EXCEPTION_RECORD R={.Pc=0x9f123456,.Esr=0x96000004,.Far=0xdeadbeef,.Session=0x1234,.Lr=0x12345678,.Owner=2};
 ExPage(&P.Page,&R,Page);P.PagePrepared=TRUE;
 for(UINT32 I=0;I<ENUMA_PIXEL_WORDS;I++)Pixels[I]=Original[I]=I*19+0x98765432;
 Reads=Writes=Barriers=Holds=FailRead=FailWrite=FailBarrier=FailHold=FailValidate=0;
}
int main(void){
 for(UINT32 Page=1;Page<=(ENUMA_OEM_CONTEXT?6:3);Page++){
  Setup(Page);
  for(UINT32 Y=0;Y<5;Y++)for(UINT32 X=0;X<20;X++){CHAR8 C=P.Page.Text[Y][X];UINT32 B=0;
   for(UINT32 I=0;I<5;I++)B|=EnumaLogGlyph(C,I);assert(C==' '||B);}
  assert(EnumaCapturePixelRun(&P)==5&&!memcmp(Pixels,Original,sizeof(Pixels)));
  assert(Reads==153600&&Writes==102400&&Holds==1&&Barriers==3);
  assert(EnumaCapturePixelRun(&P)==5&&Writes==102400);
  Setup(Page);FailValidate=1;assert(EnumaCapturePixelRun(&P)==1&&!Writes&&!Holds);
  Setup(Page);P.PagePrepared=FALSE;assert(EnumaCapturePixelRun(&P)==1&&!Reads);
  Setup(Page);FailHold=1;assert(EnumaCapturePixelRun(&P)==3&&!memcmp(Pixels,Original,sizeof(Pixels)));
  for(UINT32 I=1;I<=3;I++){Setup(Page);FailBarrier=I;assert(EnumaCapturePixelRun(&P)==(I==1?1:I==2?2:4));assert(!memcmp(Pixels,Original,sizeof(Pixels)));}
  UINT32 Positions[]={1,25600,51200,51201,76800,102400,102401,153600};
  for(UINT32 I=0;I<8;I++){Setup(Page);FailRead=Positions[I];assert(EnumaCapturePixelRun(&P)==(FailRead<=51200?1:FailRead<=102400?2:4));assert(!memcmp(Pixels,Original,sizeof(Pixels)));}
  for(UINT32 I=0;I<6;I++){Setup(Page);FailWrite=Positions[I];assert(EnumaCapturePixelRun(&P)==(FailWrite<=51200?2:4));if(FailWrite<=51200)assert(!memcmp(Pixels,Original,sizeof(Pixels)));}
 }
 puts("PASS: actual prepared-only exception pages, glyphs, bounded transaction and failures");return 0;
}
