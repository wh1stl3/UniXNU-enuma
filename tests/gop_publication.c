// SPDX-License-Identifier: BSD-2-Clause-Patent
// Real backend/Mu Blt, modeled allocation/TPL/protocol database only.
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdarg.h>
#undef NULL
#include "InheritedGopPublish.h"
#include "EnumaMenuConsole.h"
#include <Library/BaseLib.h>
#include <Library/BaseMemoryLib.h>
#include <Library/MemoryAllocationLib.h>
#include <Configuration/BootDevices.h>
EFI_GUID gEfiGraphicsOutputProtocolGuid=EFI_GRAPHICS_OUTPUT_PROTOCOL_GUID;
EFI_GUID gEfiDevicePathProtocolGuid=EFI_DEVICE_PATH_PROTOCOL_GUID;
static unsigned Allocations,FailAt,Live,Installs,Removals;
static EFI_STATUS InstallStatus,RemoveStatus,Validation;
static EFI_GRAPHICS_OUTPUT_PROTOCOL *InstalledGop;
static VOID *InstalledPath;
static EFI_HANDLE Handle=(VOID *)0x1234;
static EFI_TPL EFIAPI Raise(EFI_TPL T) { assert(T==TPL_NOTIFY);return TPL_APPLICATION; }
static VOID EFIAPI Restore(EFI_TPL T) { assert(T==TPL_APPLICATION); }
static void Pair(va_list Args,BOOLEAN Install) {
  assert(va_arg(Args,EFI_GUID *)==&gEfiGraphicsOutputProtocolGuid);
  VOID *G=va_arg(Args,VOID *);
  assert(va_arg(Args,EFI_GUID *)==&gEfiDevicePathProtocolGuid);
  VOID *P=va_arg(Args,VOID *);assert(!va_arg(Args,VOID *));
  if (Install) { InstalledGop=G;InstalledPath=P; }
  else { assert(G==InstalledGop && P==InstalledPath); }
  assert(!memcmp(P,&DisplayDevicePath,sizeof DisplayDevicePath));
}
static EFI_STATUS EFIAPI Install(EFI_HANDLE *H,...) {
  va_list Args;Installs++;assert(!*H);va_start(Args,H);Pair(Args,TRUE);va_end(Args);
  if (EFI_ERROR(InstallStatus)) { InstalledGop=NULL;InstalledPath=NULL;return InstallStatus; }
  *H=Handle;return InstallStatus;
}
static EFI_STATUS EFIAPI Remove(EFI_HANDLE H,...) {
  va_list Args;Removals++;assert(H==Handle);va_start(Args,H);Pair(Args,FALSE);va_end(Args);
  if (RemoveStatus!=EFI_SUCCESS) { return RemoveStatus; }
  InstalledGop=NULL;InstalledPath=NULL;return EFI_SUCCESS;
}
static EFI_BOOT_SERVICES BS={.RaiseTPL=Raise,.RestoreTPL=Restore,
  .InstallMultipleProtocolInterfaces=Install,.UninstallMultipleProtocolInterfaces=Remove};
EFI_BOOT_SERVICES *gBS=&BS;
VOID *EFIAPI AllocatePool(UINTN N) { if (++Allocations==FailAt) { return NULL; }VOID *P=malloc(N);if(P){Live++;}return P; }
VOID *EFIAPI AllocateZeroPool(UINTN N) { VOID *P=AllocatePool(N);if(P){memset(P,0,N);}return P; }
VOID *EFIAPI AllocateCopyPool(UINTN N,CONST VOID *S) { VOID *P=AllocatePool(N);if(P){memcpy(P,S,N);}return P; }
VOID EFIAPI FreePool(VOID *P) { assert(P&&Live);Live--;free(P); }
VOID *EFIAPI CopyMem(VOID *D,CONST VOID *S,UINTN N) { return memmove(D,S,N); }
VOID *EFIAPI SetMem(VOID *D,UINTN N,UINT8 V) { return memset(D,V,N); }
VOID *EFIAPI SetMem32(VOID *D,UINTN N,UINT32 V) { for(UINTN I=0;I<N/4;I++){((UINT32 *)D)[I]=V;}return D; }
VOID *EFIAPI SetMem64(VOID *D,UINTN N,UINT64 V) { for(UINTN I=0;I<N/8;I++){((UINT64 *)D)[I]=V;}return D; }
INTN EFIAPI HighBitSet32(UINT32 V) { return V?31-__builtin_clz(V):-1; }
static EFI_STATUS EFIAPI Validate(VOID *C,CONST ENUMA_INHERITED_FRAME *F) { assert(C==&Validation&&F->Base);return Validation; }
static unsigned char Pixels[640] __attribute__((aligned(16)));
int main(void) {
  ENUMA_GOP_PUBLICATION *P=NULL;ENUMA_INHERITED_FRAME F={0};
  F.Base=(UINTN)Pixels;F.Bytes=sizeof Pixels;F.Width=16;F.Height=8;F.Stride=80;
  F.PipeMask=3;F.CtlMask=1;F.IntfMask=6;F.RedMask=0xff0000;F.GreenMask=0xff00;F.BlueMask=255;F.ReservedMask=0xff000000;
  memset(Pixels,0xa5,sizeof Pixels);
  F.Requirements=22;assert(EnumaGopPublish(&F,Validate,&Validation,&P)==EFI_NOT_READY&&!P&&!Live&&!Installs);F.Requirements=0;
  Validation=EFI_DEVICE_ERROR;assert(EnumaGopPublish(&F,Validate,&Validation,&P)==EFI_NOT_READY&&!P&&!Live);Validation=0;
  for(unsigned I=1;I<=3;I++) {Allocations=0;FailAt=I;assert(EnumaGopPublish(&F,Validate,&Validation,&P)==EFI_OUT_OF_RESOURCES&&!P&&!Live&&!Installs);}FailAt=0;
  InstallStatus=EFI_ALREADY_STARTED;
  assert(EnumaGopPublish(&F,Validate,&Validation,&P)==EFI_ALREADY_STARTED&&!P&&!Live);
  InstallStatus=EFI_SUCCESS;
  assert(EnumaGopPublish(&F,Validate,&Validation,&P)==EFI_SUCCESS&&P&&Live==3);
  assert(EnumaGopPublicationHandle(P)==Handle&&InstalledGop&&InstalledPath);
  // Reproduce the failed 600px QEMU fixture as a non-connecting preflight.
  EFI_GRAPHICS_OUTPUT_PROTOCOL Candidate=*InstalledGop;
  EFI_GRAPHICS_OUTPUT_PROTOCOL_MODE Mode=*Candidate.Mode;
  EFI_GRAPHICS_OUTPUT_MODE_INFORMATION CandidateInfo=*Mode.Info;
  Candidate.Mode=&Mode;Mode.Info=&CandidateInfo;
  CandidateInfo.HorizontalResolution=600;CandidateInfo.VerticalResolution=800;
  assert(EnumaMenuGraphicsConsoleCheck(&Candidate)==EFI_UNSUPPORTED);
  CandidateInfo.HorizontalResolution=640;CandidateInfo.VerticalResolution=475;
  assert(EnumaMenuGraphicsConsoleCheck(&Candidate)==EFI_SUCCESS);
  CandidateInfo.VerticalResolution=474;assert(EnumaMenuGraphicsConsoleCheck(&Candidate)==EFI_UNSUPPORTED);
  Candidate.Mode=NULL;assert(EnumaMenuGraphicsConsoleCheck(&Candidate)==EFI_NOT_READY);
  assert(EnumaGopPublish(&F,Validate,&Validation,&P)==EFI_ALREADY_STARTED);
  for(unsigned I=0;I<sizeof Pixels;I++){assert(Pixels[I]==0xa5);} // publication never draws
  RemoveStatus=EFI_ACCESS_DENIED;assert(EnumaGopUnpublish(&P)==EFI_ACCESS_DENIED&&P&&Live==3);
  EFI_GRAPHICS_OUTPUT_MODE_INFORMATION *Info=NULL;UINTN Size=0;
  assert(InstalledGop->QueryMode(InstalledGop,0,&Size,&Info)==EFI_SUCCESS);FreePool(Info);
  RemoveStatus=EFI_SUCCESS;assert(EnumaGopUnpublish(&P)==EFI_SUCCESS&&!P&&!Live);
  InstallStatus=EFI_WARN_UNKNOWN_GLYPH;assert(EnumaGopPublish(&F,Validate,&Validation,&P)==EFI_WARN_UNKNOWN_GLYPH&&P&&Live==3);
  assert(EnumaGopUnpublish(&P)==EFI_SUCCESS&&!P&&!Live);assert(!EnumaGopPublicationHandle(NULL));
  assert(EnumaGopUnpublish(&P)==EFI_INVALID_PARAMETER);
  puts("PASS: same-handle GOP/BDS path, requirements22 rejection, allocations/install rollback, duplicate owner, failed uninstall retention, warning ownership and no publication pixel writes");
}
