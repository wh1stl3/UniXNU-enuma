#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#undef NULL
#include <Uefi.h>
#include <Protocol/GraphicsOutput.h>
#include "EnumaGopAudit.h"

EFI_GUID gEfiGraphicsOutputProtocolGuid;
static EFI_BOOT_SERVICES bs;
static EFI_GRAPHICS_OUTPUT_PROTOCOL gop, other;
static EFI_GRAPHICS_OUTPUT_PROTOCOL_MODE mode;
static EFI_GRAPHICS_OUTPUT_MODE_INFORMATION info;
static int fault, live, query_calls, handle_calls, locate_calls;
static EFI_HANDLE owner = (EFI_HANDLE)(UINTN)1234;
static EFI_STATUS EFIAPI release(VOID *p) {
  assert(p != NULL);free(p);live--;return fault==28?EFI_DEVICE_ERROR:EFI_SUCCESS;
}
static EFI_STATUS EFIAPI locate(EFI_LOCATE_SEARCH_TYPE type, EFI_GUID *guid,
  VOID *key, UINTN *count, EFI_HANDLE **handles) {
  assert(type==ByProtocol && guid==&gEfiGraphicsOutputProtocolGuid && key==NULL);
  locate_calls++;
  if(fault==1)return EFI_NOT_FOUND;
  *count=fault==2?2:1;
  if(fault==3)return EFI_SUCCESS;
  *handles=malloc(2*sizeof(**handles));assert(*handles);live++;
  (*handles)[0]=fault==4?(EFI_HANDLE)(UINTN)5678:owner;
  return EFI_SUCCESS;
}
static EFI_STATUS EFIAPI handle(EFI_HANDLE h, EFI_GUID *guid, VOID **out) {
  assert(h==owner && guid==&gEfiGraphicsOutputProtocolGuid);handle_calls++;
  if(fault==5)return EFI_UNSUPPORTED;
  *out=fault==6?&other:&gop;return EFI_SUCCESS;
}
static EFI_STATUS EFIAPI query(EFI_GRAPHICS_OUTPUT_PROTOCOL *self,
  UINT32 number, UINTN *size, EFI_GRAPHICS_OUTPUT_MODE_INFORMATION **out) {
  assert(self==&gop && number==0);query_calls++;
  if(fault==18)return EFI_OUT_OF_RESOURCES;
  *size=sizeof(info);
  if(fault==19)return EFI_SUCCESS;
  *out=malloc(sizeof(info));assert(*out);live++;**out=info;
  if(fault==20)*size=sizeof(info)-1;
  if(fault>=21 && fault<=27) {
    switch(fault) {
      case 21:(*out)->Version++;break;
      case 22:(*out)->HorizontalResolution++;break;
      case 23:(*out)->VerticalResolution++;break;
      case 24:(*out)->PixelFormat=PixelRedGreenBlueReserved8BitPerColor;break;
      case 25:(*out)->PixelsPerScanLine++;break;
      case 26:(*out)->PixelInformation.RedMask++;break;
      case 27:(*out)->PixelInformation.ReservedMask++;break;
    }
  }
  return EFI_SUCCESS;
}
static void setup(int f) {
  assert(live==0);fault=f;query_calls=handle_calls=locate_calls=0;
  memset(&bs,0,sizeof(bs));memset(&gop,0,sizeof(gop));
  memset(&mode,0,sizeof(mode));memset(&info,0,sizeof(info));
  bs.LocateHandleBuffer=locate;bs.HandleProtocol=handle;bs.FreePool=release;
  gop.Mode=&mode;gop.QueryMode=query;mode.Info=&info;
  mode.MaxMode=1;mode.SizeOfInfo=sizeof(info);
  mode.FrameBufferBase=0x12340000;mode.FrameBufferSize=1600*2560*4;
  info.HorizontalResolution=1600;info.VerticalResolution=2560;
  info.PixelsPerScanLine=1600;info.PixelFormat=PixelBlueGreenRedReserved8BitPerColor;
  switch(f) {
    case 7:gop.Mode=NULL;break;
    case 8:gop.QueryMode=NULL;break;
    case 9:mode.Info=NULL;break;
    case 10:mode.MaxMode=2;break;
    case 11:mode.Mode=1;break;
    case 12:mode.SizeOfInfo--;break;
    case 13:info.HorizontalResolution=0;break;
    case 14:info.PixelsPerScanLine--;break;
    case 15:info.PixelFormat=PixelBltOnly;break;
    case 16:mode.FrameBufferSize--;break;
    case 17:mode.FrameBufferBase=MAX_UINT64-1;break;
    case 29:info.PixelsPerScanLine=MAX_UINT32;info.VerticalResolution=MAX_UINT32;break;
    case 30:mode.FrameBufferBase=0;break;
    case 31:info.Version=1;break;
    case 32:info.VerticalResolution=0;break;
  }
}
int main(void) {
  setup(0);assert(EnumaGopAudit(NULL,owner,&gop,4)==EFI_INVALID_PARAMETER);
  assert(EnumaGopAudit(&bs,NULL,&gop,4)==EFI_INVALID_PARAMETER);
  assert(EnumaGopAudit(&bs,owner,NULL,4)==EFI_INVALID_PARAMETER);
  assert(EnumaGopAudit(&bs,owner,&gop,0)==EFI_INVALID_PARAMETER);
  assert(EnumaGopAudit(&bs,owner,&gop,8)==EFI_INVALID_PARAMETER);
  assert(locate_calls==0);
  for(unsigned step=1;step<=4;step++) for(int f=0;f<=32;f++) {
    setup(f);EFI_STATUS s=EnumaGopAudit(&bs,owner,&gop,step);
    unsigned first_failure = f==0?5:f<=4?1:f<=6?2:f<=17?3:f<=27?4:f==28?1:3;
    assert((step<first_failure)==!EFI_ERROR(s));assert(live==0);
    assert(locate_calls==1);
    if(step<2)assert(handle_calls==0);
    if(step<4)assert(query_calls==0);
    if(f==0)assert(query_calls==(step==4) && handle_calls==(step>=2));
  }
  // New steps retain cleanup and reject all faults reached before their stop.
  for(unsigned step=5;step<=7;step++) for(int f=0;f<=32;f++) {
    setup(f);EFI_STATUS s=EnumaGopAudit(&bs,owner,&gop,step);
    int error=(f>=1 && f<=8) || f==28 ||
      (step>=6 && f>=9 && f<=12) ||
      (step>=7 && ((f>=13 && f<=15) || f==31 || f==32));
    assert(EFI_ERROR(s)==error);assert(live==0);
    assert(query_calls==0 && locate_calls==1);
  }
  // Invalid addresses MUST remain untouched before the corresponding boundary.
  setup(0);gop.Mode=(VOID *)(UINTN)1;
  assert(EnumaGopAudit(&bs,owner,&gop,5)==EFI_SUCCESS);assert(live==0);
  setup(0);mode.Info=(VOID *)(UINTN)1;
  assert(EnumaGopAudit(&bs,owner,&gop,6)==EFI_SUCCESS);assert(live==0);
  setup(0);mode.FrameBufferBase=0;mode.FrameBufferSize=0;
  assert(EnumaGopAudit(&bs,owner,&gop,7)==EFI_SUCCESS);assert(live==0);
  setup(29);
  assert(EnumaGopAudit(&bs,owner,&gop,7)==EFI_SUCCESS);assert(live==0);
  // Framebuffer base is deliberately an unmapped integer. Sanitizers prove
  // these metadata checks do not dereference it; no Blt/SetMode is supplied.
  puts("PASS: 231 staged GOP cases, 5 invalid arguments, 4 boundary cases; no framebuffer access");
  return 0;
}
