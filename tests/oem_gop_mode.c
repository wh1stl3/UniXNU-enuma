#include <Uefi.h>
#include <Protocol/GraphicsOutput.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "EnumaOemGopMode.h"
VOID *EFIAPI ZeroMem(VOID *P,UINTN N){return memset(P,0,N);}
static EFI_GRAPHICS_OUTPUT_PROTOCOL G;
static EFI_GRAPHICS_OUTPUT_PROTOCOL_MODE Mode;
static EFI_GRAPHICS_OUTPUT_MODE_INFORMATION Live,Query;
static EFI_HANDLE Handles[10];
static EFI_BOOT_SERVICES Boot;
static UINTN Count,Queries,Sets,Frees;
static int Fault;
static EFI_TPL Level;
static VOID Descriptor(EFI_MEMORY_DESCRIPTOR *D,CONST VOID *P,UINTN N){
  D->Type=EfiBootServicesData;D->PhysicalStart=(UINTN)P&~4095ULL;
  D->NumberOfPages=(((UINTN)P+N+4095)&~4095ULL)-D->PhysicalStart;
  D->NumberOfPages/=4096;
}
static EFI_STATUS EFIAPI Memory(UINTN *N,EFI_MEMORY_DESCRIPTOR *M,UINTN *Key,UINTN *Size,UINT32 *Version){
  if(Fault==1){return EFI_BUFFER_TOO_SMALL;}
  assert(*N>=6*sizeof(*M));ZeroMem(M,6*sizeof(*M));
  Descriptor(M,&G,sizeof(G));Descriptor(M+1,&Mode,sizeof(Mode));
  Descriptor(M+2,&Live,sizeof(Live));Descriptor(M+3,&Query,sizeof(Query));
  Descriptor(M+4,Handles,sizeof(Handles));
  *N=5*sizeof(*M);*Size=sizeof(*M);*Key=1;*Version=EFI_MEMORY_DESCRIPTOR_VERSION;
  if(Fault==2){*Size=0;}if(Fault==3){*N=sizeof(mOemGopMemory)+1;}
  if(Fault==4){*Version=2;}if(Fault==5){for(UINTN I=0;I<5;I++){M[I].Type=EfiMemoryMappedIO;}}
  return EFI_SUCCESS;
}
static EFI_TPL EFIAPI Raise(EFI_TPL T){assert(T==TPL_HIGH_LEVEL);return Level;}
static VOID EFIAPI Restore(EFI_TPL T){assert(T==Level);}
static EFI_STATUS EFIAPI Locate(EFI_LOCATE_SEARCH_TYPE S,EFI_GUID *Id,VOID *K,UINTN *N,EFI_HANDLE **H){
  (VOID)Id;assert(S==ByProtocol&&!K);*N=Count;*H=Fault==6?NULL:Handles;
  return Fault==7?EFI_NOT_FOUND:EFI_SUCCESS;
}
static EFI_STATUS EFIAPI Handle(EFI_HANDLE H,EFI_GUID *Id,VOID **P){
  (VOID)H;(VOID)Id;*P=&G;return Fault==8?EFI_UNSUPPORTED:EFI_SUCCESS;
}
static EFI_STATUS EFIAPI Free(VOID *P){assert(P==Handles||P==&Query);Frees++;return Fault==9?EFI_DEVICE_ERROR:EFI_SUCCESS;}
static EFI_STATUS EFIAPI Get(EFI_GRAPHICS_OUTPUT_PROTOCOL *This,UINT32 N,UINTN *Size,EFI_GRAPHICS_OUTPUT_MODE_INFORMATION **Info){
  assert(This==&G&&N==0);Queries++;*Size=sizeof(Query);*Info=&Query;
  if(Fault==10){*Info=NULL;return EFI_DEVICE_ERROR;}
  if(Fault==11){*Info=NULL;return EFI_SUCCESS;}
  if(Fault==12){*Size=sizeof(Query)-1;}
  if(Fault==13){*Size=4097;}
  if(Fault==14){*Info=(VOID *)1;}
  return EFI_SUCCESS;
}
static EFI_STATUS EFIAPI Set(EFI_GRAPHICS_OUTPUT_PROTOCOL *This,UINT32 N){
  assert(This==&G&&N==0);Sets++;
  if(Fault==15){return EFI_DEVICE_ERROR;}if(Fault==16){return EFI_WARN_UNKNOWN_GLYPH;}
  Mode.Mode=Fault==17?MAX_UINT32:0;
  Mode.FrameBufferBase=Fault==18?0x9e400000ULL:0x9c000000ULL;
  Mode.FrameBufferSize=Fault==19?1:1600*2560*4;
  if(Fault==20){Mode.Info=(VOID *)1;}
  if(Fault==21){Live.PixelsPerScanLine=MAX_UINT32;}
  return EFI_SUCCESS;
}
static EFI_STATUS EFIAPI Blt(EFI_GRAPHICS_OUTPUT_PROTOCOL *This,EFI_GRAPHICS_OUTPUT_BLT_PIXEL *B,EFI_GRAPHICS_OUTPUT_BLT_OPERATION Op,UINTN X,UINTN Y,UINTN DX,UINTN DY,UINTN W,UINTN H,UINTN Delta){
  (VOID)This;(VOID)B;(VOID)Op;(VOID)X;(VOID)Y;(VOID)DX;(VOID)DY;(VOID)W;(VOID)H;(VOID)Delta;
  assert(!"Blt must never be called");return EFI_ABORTED;
}
static VOID Init(VOID){
  ZeroMem(&mOemGopMode,sizeof(mOemGopMode));ZeroMem(&Boot,sizeof(Boot));
  ZeroMem(&Mode,sizeof(Mode));ZeroMem(&Live,sizeof(Live));
  Live.HorizontalResolution=1600;Live.VerticalResolution=2560;Live.PixelsPerScanLine=1600;
  Live.PixelFormat=PixelBlueGreenRedReserved8BitPerColor;Query=Live;
  Mode.Mode=MAX_UINT32;Mode.MaxMode=1;Mode.Info=&Live;Mode.SizeOfInfo=sizeof(Live);
  G.QueryMode=Get;G.SetMode=Set;G.Blt=Blt;G.Mode=&Mode;
  Boot.GetMemoryMap=Memory;Boot.LocateHandleBuffer=Locate;Boot.HandleProtocol=Handle;
  Boot.FreePool=Free;Boot.RaiseTPL=Raise;Boot.RestoreTPL=Restore;
  Count=1;Fault=0;Queries=Sets=Frees=0;Level=TPL_APPLICATION;
}
static BOOLEAN Run(VOID){
  UINTN A=(UINTN)Get,B=(UINTN)Set,C=(UINTN)Blt;
  UINTN Lo=A<B?A:B;Lo=Lo<C?Lo:C;UINTN Hi=A>B?A:B;Hi=Hi>C?Hi:C;
  return OemGopAdvance(&Boot,Lo,Hi-Lo+4);
}
int main(VOID){
  Init();assert(Run()&&Queries==1&&Sets==1&&Frees==2&&mOemGopMode.Phase==5);
  assert(mOemGopMode.Validated&&mOemGopMode.FrameBase==0x9c000000ULL);
  assert(!Run()&&Queries==1&&Sets==1); // no retry
  for(int I=1;I<=21;I++){
    Init();Fault=I;assert(!Run());assert(!mOemGopMode.Validated&&Sets<=1);
    if(I<=14){assert(!Sets);}
  }
  Init();Count=0;assert(!Run()&&!Queries&&!Sets);
  Init();Count=9;assert(!Run()&&!Queries&&!Sets);
  Init();Count=2;assert(!Run()&&!Queries&&!Sets); // two native candidates
  Init();Level=TPL_CALLBACK;assert(!Run()&&!Queries&&!Sets);
  Init();G.SetMode=(VOID *)1;assert(!Run()&&!Queries&&!Sets);
  Init();G.QueryMode=(VOID *)1;assert(!Run()&&!Queries&&!Sets);
  Init();G.Blt=(VOID *)1;assert(!Run()&&!Queries&&!Sets);
  Init();G.Mode=(VOID *)1;assert(!Run()&&!Queries&&!Sets);
  Init();Mode.MaxMode=9;assert(!Run()&&!Queries&&!Sets);
  Init();Mode.MaxMode=0;assert(!Run()&&!Queries&&!Sets);
  Init();Query.HorizontalResolution=800;assert(!Run()&&Queries==1&&!Sets&&Frees==2);
  Init();Query.PixelFormat=PixelBltOnly;assert(!Run()&&!Sets);
  Init();Query.PixelsPerScanLine=1599;assert(!Run()&&!Sets);
  Init();Query.PixelFormat=PixelBitMask;Query.PixelInformation.RedMask=0xff0000;
  Query.PixelInformation.GreenMask=0xff00;Query.PixelInformation.BlueMask=0xff;
  Live=Query;assert(Run());
  Init();Query.PixelFormat=PixelBitMask;assert(!Run()&&!Sets);
  Init();Boot.GetMemoryMap=NULL;assert(!Run()&&!Queries&&!Sets);
  Init();assert(!OemGopAdvance(&Boot,MAX_UINTN-4,8));
  assert(!OemGopCode(0,1,MAX_UINTN));
  assert(!OemGopSpan((VOID *)(MAX_UINTN-1),8));
  puts("PASS: native GOP query/set/readback, ownership, bounds, cleanup, failures and no retry; no Blt");
  return 0;
}
