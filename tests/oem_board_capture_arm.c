// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <Uefi.h>
#include <Library/BaseMemoryLib.h>
#include "EnumaOemBoardCapture.h"
BOOLEAN TestBoard(EFI_BOOT_SERVICES *Boot,ENUMA_PRECALL_CAPTURE *C,CONST CHAR8 *L,UINTN N){
  mOemOriginalBoot=Boot;return OemBoardSink(C,L,N);
}
