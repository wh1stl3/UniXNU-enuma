#include <assert.h>
#include <stdio.h>
#undef NULL
#include <Uefi.h>
#include <Protocol/LoadedImage.h>
#include <IndustryStandard/PeImage.h>
#include "EnumaGopResult.h"
static EFI_STATUS supplied;
static unsigned constructors, destructors, unloads;
static const UINT32 _gUefiDriverRevision=0, _gDriverUnloadImageCount=0;
static EFI_BOOT_SERVICES *gBS;
EFI_GUID gEfiLoadedImageProtocolGuid;
static EFI_STATUS EFIAPI _DriverUnloadHandler(EFI_HANDLE h) {(VOID)h;return EFI_SUCCESS;}
#define ASSERT_EFI_ERROR(Status) assert(!EFI_ERROR(Status))
static VOID ProcessLibraryConstructorList(EFI_HANDLE h, EFI_SYSTEM_TABLE *s) {
  (VOID)h;(VOID)s;constructors++;
}
static EFI_STATUS ProcessModuleEntryPointList(EFI_HANDLE h, EFI_SYSTEM_TABLE *s) {
  (VOID)h;(VOID)s;return supplied;
}
static VOID ProcessLibraryDestructorList(EFI_HANDLE h, EFI_SYSTEM_TABLE *s) {
  (VOID)h;(VOID)s;destructors++;
}
#include "WarningEntry.inc"
typedef struct {EFI_STATUS Status; UINTN Type;} IMAGE_FIXTURE;
static VOID CoreUnloadAndCloseImage(IMAGE_FIXTURE *Image, BOOLEAN free_pages) {
  (VOID)Image;assert(free_pages);unloads++;
}
#define PERF_START_IMAGE_END(Handle) ((VOID)(Handle))
static EFI_STATUS CoreReturn(IMAGE_FIXTURE *Image) {
  EFI_STATUS Status;EFI_HANDLE Handle=(EFI_HANDLE)(UINTN)1;
#include "WarningCoreReturn.inc"
}
int main(void) {
  assert(ENUMA_GOP_RESULT_PASS==EFI_WARN_UNKNOWN_GLYPH);
  assert(ENUMA_GOP_RESULT_FAIL==EFI_WARN_STALE_DATA);
  const EFI_STATUS statuses[]={EFI_SUCCESS,ENUMA_GOP_RESULT_PASS,ENUMA_GOP_RESULT_FAIL,2,EFI_DEVICE_ERROR};
  for(unsigned i=0;i<5;i++) {
    supplied=statuses[i];constructors=destructors=unloads=0;
    EFI_STATUS result=_ModuleEntryPoint(NULL,NULL);
    assert(result==supplied && constructors==1 && destructors==EFI_ERROR(supplied));
    IMAGE_FIXTURE image={result,EFI_IMAGE_SUBSYSTEM_EFI_BOOT_SERVICE_DRIVER};
    assert(CoreReturn(&image)==supplied && unloads==EFI_ERROR(supplied));
  }
  IMAGE_FIXTURE app={ENUMA_GOP_RESULT_PASS,EFI_IMAGE_SUBSYSTEM_EFI_APPLICATION};
  unloads=0;assert(CoreReturn(&app)==ENUMA_GOP_RESULT_PASS && unloads==1);
  assert(ENUMA_GOP_RESULT(EFI_SUCCESS)==ENUMA_GOP_RESULT_PASS);
  assert(ENUMA_GOP_RESULT(EFI_DEVICE_ERROR)==ENUMA_GOP_RESULT_FAIL);
  puts("PASS: real Mu entry/return excerpts preserve markers and keep warning driver resident");
  return 0;
}
