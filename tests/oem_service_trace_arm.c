// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "EnumaOemServiceTrace.h"
#include "EnumaOemTraceTarget.h"
// Object-only AArch64 ABI qualification; no board/FV entry or activation.
EFI_STATUS EnumaOemTraceCompile(ENUMA_SERVICE_TRACE *C,EFI_SYSTEM_TABLE *S,UINTN Base,UINTN Size) {
  return EnumaServiceTracePrepare(C,S,Base,Size);
}
BOOLEAN EnumaOemTraceSnapshotCompile(ENUMA_SERVICE_TRACE_LOG *Out) {return EnumaServiceTraceSnapshot(Out);}
EFI_STATUS EnumaOemAttachCompile(ENUMA_SERVICE_TRACE *C,CONST EFI_GUID *G,EFI_LOADED_IMAGE_PROTOCOL *L,EFI_SYSTEM_TABLE *S){return EnumaAttachDisplayTrace(C,G,L,S);}
