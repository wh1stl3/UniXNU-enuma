#include <Uefi.h>
#include <Library/BaseMemoryLib.h>
extern EFI_SYSTEM_TABLE *gDxeCoreST;
VOID *AllocateRuntimePool(UINTN);
EFI_STATUS CoreFreePool(VOID *);
VOID CalculateEfiHdrCrc(EFI_TABLE_HEADER *);
VOID CoreNotifySignalList(CONST EFI_GUID *);
