// Standalone real Core binding: do not supply legacy capture headers via fixtures.
#include <Uefi.h>
#include <Protocol/LoadedImage.h>
EFI_HANDLE EnumaStartingImage;
CONST EFI_GUID *EnumaStartingFile;
EFI_SYSTEM_TABLE *gDxeCoreST;
extern EFI_GUID gEfiLoadedImageProtocolGuid,gEfiFirmwareVolume2ProtocolGuid;
EFI_STATUS CoreHandleProtocol(EFI_HANDLE H,EFI_GUID *G,VOID **P);
#include "EnumaOemCoreBinding.h"
EFI_STATUS CheckClockBinding(EFI_HANDLE H,EFI_HANDLE Fv,CONST EFI_GUID *File,EFI_LOADED_IMAGE_PROTOCOL *P,UINTN Entry){
  EnumaStartingImage=H;EnumaStartingFile=File;EnumaOemStartingFv=Fv;
  return EnumaOemCoreBeforeEntry(H,P,Entry);
}
