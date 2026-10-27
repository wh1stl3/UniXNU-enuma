// SPDX-License-Identifier: BSD-2-Clause-Patent
#define ENUMA_BOOT_LOG_REPLAY 3
#define ENUMA_BOOT_LOG_HOLD_US 8000000
#include "EnumaOemCapturePixel.h"
#include "EnumaOemProgressPage.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <setjmp.h>
VOID *EFIAPI CopyMem(VOID *D,CONST VOID *S,UINTN N){return memcpy(D,S,N);}
VOID *EFIAPI ZeroMem(VOID *D,UINTN N){return memset(D,0,N);}
static ENUMA_CAPTURE_PIXEL Pixel;
static ENUMA_PRECALL_CAPTURE Capture;
static UINT32 Pixels[51200],Original[51200],R,W,B,H,V,FailR,FailW,FailB,FailH,FailV,Escape,BeforeWrite;
static jmp_buf Jump;
static VOID Stop(VOID *C){assert(C==&Pixel&&Pixel.Result==4);longjmp(Jump,2);}
static EFI_BOOT_SERVICES Boot;
static EFI_SYSTEM_TABLE System;
static ENUMA_SERVICE_TRACE Trace;
static EFI_TPL Current=TPL_APPLICATION;
static UINT32 OriginalCalls;
static EFI_TPL EFIAPI Raise(EFI_TPL T){EFI_TPL Old=Current;Current=T;return Old;}
static VOID EFIAPI Restore(EFI_TPL T){Current=T;}
static EFI_STATUS EFIAPI Crc(VOID *P,UINTN N,UINT32 *C){(void)P;(void)N;*C=1;return EFI_SUCCESS;}
static EFI_STATUS EFIAPI Alloc(EFI_MEMORY_TYPE T,UINTN N,VOID **Out){
  assert(T==EfiBootServicesData&&N==99&&Current==TPL_APPLICATION);
  assert(!Pixel.Active&&Pixel.Result==5&&Capture.State==EnumaCaptureExported);
  assert(!memcmp(Pixels,Original,sizeof(Pixels)));OriginalCalls++;*Out=(VOID *)0x1234;
  longjmp(Jump,3); // original service exits nonlocally, after the window restored
}
static EFI_STATUS EFIAPI Locate(EFI_GUID *G,VOID *R,VOID **O){(void)G;(void)R;(void)O;return EFI_NOT_FOUND;}
static EFI_STATUS EFIAPI Handle(EFI_HANDLE H,EFI_GUID *G,VOID **O){return Locate(G,H,O);}
static UINT32 Index(UINT64 A){UINT64 D=A-Pixel.Frame.Base;UINT32 Y=D/Pixel.Frame.Stride,X=(D%Pixel.Frame.Stride)/4;
  assert(A>=Pixel.Frame.Base&&!(A&3)&&Y>=96&&Y<256&&X>=64&&X<384);return (Y-96)*320+X-64;}
static int Read(void *C,UINT64 A,UINT32 *Out){assert(C==&Pixel&&R<153600);R++;*Out=Pixels[Index(A)];return R!=FailR;}
static int Write(void *C,UINT64 A,UINT32 Value){assert(C==&Pixel&&W<102400);W++;
  if(Escape&&W==2){longjmp(Jump,1);}if(BeforeWrite&&W==FailW){return 0;}
  Pixels[Index(A)]=Value;return W!=FailW;}
static int Barrier(void *C){assert(C==&Pixel&&B<3);return ++B!=FailB;}
static int Hold(void *C,UINT32 Us){assert(C==&Pixel&&!H&&Us==8000000);H++;return !FailH;}
static int Validate(void *C,const ENUMA_INHERITED_FRAME *F){assert(C==&Pixel&&F==&Pixel.Frame&&R==51200&&!W&&!V);V++;return !FailV;}
static void Setup(void){
  memset(&Pixel,0,sizeof(Pixel));memset(&Capture,0,sizeof(Capture));
  Pixel.Capture=&Capture;Pixel.Policy=3;Pixel.El=4;Pixel.Io=&Pixel;
  Pixel.Read=Read;Pixel.Write=Write;Pixel.Validate=Validate;Pixel.Barrier=Barrier;Pixel.Hold=Hold;
  Pixel.Frame.Base=0x9c000004;Pixel.Frame.Width=1600;Pixel.Frame.Height=2560;Pixel.Frame.Stride=6404;
  Pixel.Frame.Bytes=6404ULL*2560;Pixel.Frame.Requirements=22;Pixel.Frame.RedMask=0xff;
  Pixel.Frame.GreenMask=0xff00;Pixel.Frame.BlueMask=0xff0000;Pixel.Frame.ReservedMask=0xff000000;
  Capture.State=EnumaCaptureEmitting;Capture.Snapshot.Count=1;Capture.Snapshot.NextCall=Capture.Snapshot.NextSequence=1;
  Capture.Snapshot.Events[0].Service=3;Capture.Snapshot.Events[0].CallerRva=0x616c;Capture.Snapshot.Events[0].Value=99;
  for(UINT32 I=0;I<51200;I++){Pixels[I]=Original[I]=I*17+0x12345678;}
  R=W=B=H=V=FailR=FailW=FailB=FailH=FailV=Escape=BeforeWrite=0;
}
static void Restored(void){assert(!memcmp(Pixels,Original,sizeof(Pixels)));}
static void Bind(void){
  Setup();memset(&Boot,0,sizeof(Boot));memset(&System,0,sizeof(System));
  mEnumaServiceTrace=NULL;mEnumaPrecallCapture=NULL;Current=TPL_APPLICATION;OriginalCalls=0;
  Boot.Hdr.HeaderSize=sizeof(Boot);System.Hdr.HeaderSize=sizeof(System);System.BootServices=&Boot;
  Boot.RaiseTPL=Raise;Boot.RestoreTPL=Restore;Boot.CalculateCrc32=Crc;
  Boot.AllocatePool=Alloc;Boot.LocateProtocol=Locate;Boot.HandleProtocol=Handle;
  // Host fixture range only: not an OEM PE identity assertion.
  assert(!EnumaServiceTracePrepare(&Trace,&System,1,MAX_UINTN-1));
  assert(!EnumaCaptureArm(&Capture,&Trace,1,0,EnumaCapturePixelSink,&Pixel));
  Pixel.Stop=Stop;Pixel.StopContext=&Pixel;
}
int main(void){
  // Headers include integration APIs; use them to verify null/preparation guards.
  assert(EnumaServiceTracePrepare(NULL,NULL,0,0)==EFI_INVALID_PARAMETER);
  assert(EnumaCaptureArm(NULL,NULL,0,0,NULL,NULL)==EFI_INVALID_PARAMETER);EnumaCaptureStop(NULL);
  assert(!EnumaLogPageFromSnapshot(NULL,&mEnumaLogPage));
  Setup();assert(EnumaCapturePixelRun(&Pixel)==5);Restored();assert(R==153600&&W==102400&&B==3&&H==1);
  assert(!memcmp(Pixel.Page.Text[0],"E03C0000000000000000",20));
  assert(!memcmp(Pixel.Page.Text[2],"O000000000000616c",17));
  assert(EnumaCapturePixelRun(&Pixel)==5&&W==102400); // never repeat window
  UINT32 Positions[]={1,25600,51200,51201,76800,102400,102401,153600};
  for(UINT32 I=0;I<8;I++){Setup();FailR=Positions[I];UINT32 Result=EnumaCapturePixelRun(&Pixel);
    assert(Result==(FailR<=51200?1:FailR<=102400?2:4));Restored();}
  for(UINT32 I=0;I<6;I++){Setup();FailW=Positions[I];assert(EnumaCapturePixelRun(&Pixel)==(FailW<=51200?2:4));Restored();}
  for(UINT32 I=0;I<6;I++){Setup();BeforeWrite=1;FailW=Positions[I];
    assert(EnumaCapturePixelRun(&Pixel)==(FailW<=51200?2:4));
    if(FailW<=51200){Restored();}else{assert(memcmp(Pixels,Original,sizeof(Pixels)));}}
  for(UINT32 Red=0;Red<4;Red++)for(UINT32 Green=0;Green<4;Green++)for(UINT32 Blue=0;Blue<4;Blue++){
    if(Red==Green||Red==Blue||Green==Blue){continue;}Setup();
    Pixel.Frame.RedMask=255u<<(Red*8);Pixel.Frame.GreenMask=255u<<(Green*8);
    Pixel.Frame.BlueMask=255u<<(Blue*8);Pixel.Frame.ReservedMask=255u<<((6-Red-Green-Blue)*8);
    assert(EnumaCapturePixelRun(&Pixel)==5);Restored();
  }
  for(UINT32 I=1;I<=3;I++){Setup();FailB=I;assert(EnumaCapturePixelRun(&Pixel)==(I==1?1:I==2?2:4));Restored();}
  Setup();FailH=1;assert(EnumaCapturePixelRun(&Pixel)==3);Restored();
  Setup();FailV=1;assert(EnumaCapturePixelRun(&Pixel)==1&&!W&&!H);Restored();
  Setup();Capture.Snapshot.Events[0].CallerRva=MAX_UINT64;assert(EnumaCapturePixelRun(&Pixel)==1&&!R);
  Setup();Pixel.Policy=0;assert(EnumaCapturePixelRun(&Pixel)==1&&!R);
  Setup();Escape=1;if(!setjmp(Jump)){EnumaCapturePixelRun(&Pixel);assert(0);}
  assert(Pixel.Active&&Pixel.Result==4&&W==2);assert(EnumaCapturePixelRun(&Pixel)==4&&W==2);
  Setup();assert(!EnumaCapturePixelSink(&Pixel,"OEM capture end ",16)&&!R);
  Setup();Pixel.Stop=Stop;Pixel.StopContext=&Pixel;
  assert(EnumaCapturePixelSink(&Pixel,"OEM capture begin ",18)&&!R);
  assert(EnumaCapturePixelSink(&Pixel,"OEM capture end ",16));Restored();
  Setup();Pixel.Stop=Stop;Pixel.StopContext=&Pixel;FailB=3;
  if(!setjmp(Jump)){EnumaCapturePixelSink(&Pixel,"OEM capture end ",16);assert(0);}
  assert(Pixel.Result==4);Restored();
  Bind();if(!setjmp(Jump)){VOID *Out;Trace.Boot.AllocatePool(EfiBootServicesData,99,&Out);assert(0);}
  assert(OriginalCalls==1&&Trace.Log.Count==1&&Capture.State==EnumaCaptureExported);Restored();
  Bind();FailB=3;if(!setjmp(Jump)){VOID *Out;Trace.Boot.AllocatePool(EfiBootServicesData,99,&Out);assert(0);}
  assert(!OriginalCalls&&Capture.State==EnumaCaptureInterrupted&&Pixel.Result==4);Restored();
  Bind();Escape=1;if(!setjmp(Jump)){VOID *Out;Trace.Boot.AllocatePool(EfiBootServicesData,99,&Out);assert(0);}
  assert(!OriginalCalls&&Pixel.Active&&Pixel.Result==4&&Capture.State==EnumaCaptureEmitting);
  EnumaCaptureStop(&Capture);assert(Capture.State==EnumaCaptureInterrupted);
  for(UINT32 Phase=1;Phase<=5;Phase++){
    ENUMA_SERVICE_EVENT E={0};Setup();E.Call=7;E.CallerRva=0x1bce0;E.Sequence=9;
    E.Returned=Phase==2||Phase==4||Phase==5;E.Status=EFI_NOT_FOUND;
    assert(OemProgressPage(&Pixel.Page,Phase,&E,0x1234));Pixel.PagePrepared=TRUE;
    assert(Pixel.Page.Text[0][0]==(E.Returned?'S':'E'));
    assert(Pixel.Page.Text[3][0]==(E.Returned?'S':'E')&&Pixel.Page.Text[4][0]=='G');
    for(UINT32 Row=0;Row<5;Row++)for(UINT32 Col=0;Col<20;Col++){
      CHAR8 Ch=Pixel.Page.Text[Row][Col];UINT32 Bits=0;
      for(UINT32 Y=0;Y<5;Y++){Bits|=EnumaLogGlyph(Ch,Y);}assert(Ch==' '||Bits);
    }
    assert(EnumaCapturePixelRun(&Pixel)==5);Restored();
    Setup();assert(OemProgressPage(&Pixel.Page,Phase,&E,1));Pixel.PagePrepared=TRUE;FailB=3;
    assert(EnumaCapturePixelRun(&Pixel)==4);
    assert(!OemProgressPage(&Pixel.Page,Phase,&E,0));
  }
  puts("PASS: pixel lifecycle failures, five progress pages with existing glyphs, restore and session validation");
  return 0;
}
