// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <Uefi.h>
#include <Library/BaseMemoryLib.h>
#include "EnumaOemBoardCapture.h"
BOOLEAN TestBoard(EFI_BOOT_SERVICES *Boot,ENUMA_PRECALL_CAPTURE *C,CONST CHAR8 *L,UINTN N){
  mOemOriginalBoot=Boot;return OemBoardSink(C,L,N);
}
#if defined(ENUMA_OEM_PROGRESS) && ENUMA_OEM_PROGRESS
BOOLEAN TestProgress(EFI_BOOT_SERVICES *Boot,UINT32 Phase,CONST ENUMA_SERVICE_EVENT *E,UINT64 Session){
  mOemOriginalBoot=Boot;return OemProgressPresent(Phase,E,Session);
}
#endif
