// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "ConsoleGop.h"
#include <assert.h>
#include <stdio.h>
EFI_GUID gEfiGraphicsOutputProtocolGuid=EFI_GRAPHICS_OUTPUT_PROTOCOL_GUID;
static EFI_GRAPHICS_OUTPUT_PROTOCOL Gop;
static EFI_GRAPHICS_OUTPUT_PROTOCOL_MODE Mode;
static EFI_GRAPHICS_OUTPUT_MODE_INFORMATION Info;
static EFI_STATUS HandleStatus,LocateStatus;
static unsigned HandleCalls,LocateCalls;
static BOOLEAN NullHandleResult,NullLocateResult;
static EFI_STATUS EFIAPI Handle(EFI_HANDLE H,EFI_GUID *Guid,VOID **P) {
  assert(H==(VOID *)1&&Guid==&gEfiGraphicsOutputProtocolGuid);HandleCalls++;
  *P=NullHandleResult?NULL:&Gop;return HandleStatus;
}
static EFI_STATUS EFIAPI Locate(EFI_GUID *Guid,VOID *Registration,VOID **P) {
  assert(Guid==&gEfiGraphicsOutputProtocolGuid&&!Registration);LocateCalls++;
  *P=NullLocateResult?NULL:&Gop;return LocateStatus;
}
static EFI_STATUS EFIAPI Query(EFI_GRAPHICS_OUTPUT_PROTOCOL *This,UINT32 Number,UINTN *Size,EFI_GRAPHICS_OUTPUT_MODE_INFORMATION **Output) {
  (void)This;(void)Number;(void)Size;(void)Output;assert(0);return EFI_DEVICE_ERROR;
}
static EFI_STATUS EFIAPI SetMode(EFI_GRAPHICS_OUTPUT_PROTOCOL *This,UINT32 Number) {
  (void)This;(void)Number;assert(0);return EFI_DEVICE_ERROR;
}
static EFI_STATUS EFIAPI Blt(EFI_GRAPHICS_OUTPUT_PROTOCOL *This,EFI_GRAPHICS_OUTPUT_BLT_PIXEL *Buffer,
  EFI_GRAPHICS_OUTPUT_BLT_OPERATION Op,UINTN Sx,UINTN Sy,UINTN Dx,UINTN Dy,UINTN W,UINTN H,UINTN Delta) {
  (void)This;(void)Buffer;(void)Op;(void)Sx;(void)Sy;(void)Dx;(void)Dy;(void)W;(void)H;(void)Delta;assert(0);return EFI_DEVICE_ERROR;
}
int main(void) {
  EFI_BOOT_SERVICES BS={.HandleProtocol=Handle,.LocateProtocol=Locate};EFI_GRAPHICS_OUTPUT_PROTOCOL *Found=(VOID *)1;
  Info.HorizontalResolution=1600;Info.VerticalResolution=2560;Mode.Info=&Info;Mode.SizeOfInfo=sizeof Info;Mode.MaxMode=1;
  Gop.Mode=&Mode;Gop.QueryMode=Query;Gop.SetMode=SetMode;Gop.Blt=Blt;
  assert(EnumaLookupConsoleGop(NULL,NULL,&Found)==EFI_NOT_READY&&!Found);
  assert(EnumaLookupConsoleGop(&BS,(VOID *)1,NULL)==EFI_INVALID_PARAMETER);
  assert(EnumaLookupConsoleGop(&BS,(VOID *)1,&Found)==EFI_SUCCESS&&Found==&Gop&&HandleCalls==1&&!LocateCalls);
  EFI_STATUS Errors[]={EFI_UNSUPPORTED,EFI_NOT_FOUND,EFI_DEVICE_ERROR,EFI_WARN_UNKNOWN_GLYPH};
  for(unsigned I=0;I<4;I++) {
    HandleStatus=Errors[I];assert(EnumaLookupConsoleGop(&BS,(VOID *)1,&Found)==EFI_SUCCESS&&Found==&Gop);
  }
  HandleStatus=0;NullHandleResult=TRUE;
  assert(EnumaLookupConsoleGop(&BS,(VOID *)1,&Found)==EFI_SUCCESS&&Found==&Gop);
  LocateStatus=EFI_NOT_FOUND;Found=&Gop;
  assert(EnumaLookupConsoleGop(&BS,NULL,&Found)==EFI_NOT_FOUND&&!Found);
  LocateStatus=EFI_WARN_UNKNOWN_GLYPH;assert(EnumaLookupConsoleGop(&BS,NULL,&Found)==EFI_WARN_UNKNOWN_GLYPH&&!Found);
  LocateStatus=0;NullLocateResult=TRUE;assert(EnumaLookupConsoleGop(&BS,NULL,&Found)==EFI_NOT_READY&&!Found);
  NullLocateResult=FALSE;Gop.Mode=NULL;assert(EnumaLookupConsoleGop(&BS,NULL,&Found)==EFI_NOT_READY&&!Found);
  Gop.Mode=&Mode;Mode.SizeOfInfo--;assert(EnumaLookupConsoleGop(&BS,NULL,&Found)==EFI_NOT_READY&&!Found);Mode.SizeOfInfo++;
  Mode.Mode=1;assert(EnumaLookupConsoleGop(&BS,NULL,&Found)==EFI_NOT_READY&&!Found);Mode.Mode=0;
  Gop.Blt=NULL;assert(EnumaLookupConsoleGop(&BS,NULL,&Found)==EFI_NOT_READY&&!Found);Gop.Blt=Blt;
  Info.HorizontalResolution=0;assert(EnumaLookupConsoleGop(&BS,NULL,&Found)==EFI_NOT_READY&&!Found);
  puts("PASS: borrowed GOP lookup/fallback, missing/null/warning/malformed protocol rejection, no stale output, and no drawing/mode/alias installation");
}
