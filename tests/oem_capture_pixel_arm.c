// SPDX-License-Identifier: BSD-2-Clause-Patent
#define ENUMA_BOOT_LOG_REPLAY 3
#define ENUMA_BOOT_LOG_HOLD_US 8000000
#include "EnumaOemCapturePixel.h"
UINT32 PixelCompile(ENUMA_CAPTURE_PIXEL *P){return EnumaCapturePixelRun(P);}
EFI_STATUS PixelTraceCompile(ENUMA_PRECALL_CAPTURE *C,ENUMA_SERVICE_TRACE *T,EFI_SYSTEM_TABLE *S,ENUMA_BOOT_LOG_SINK Sink){
  EFI_STATUS Status=EnumaServiceTracePrepare(T,S,0x1000,0x1000);
  if(Status!=EFI_SUCCESS){return Status;}return EnumaCaptureArm(C,T,1,0,Sink,NULL);
}
VOID PixelStopCompile(ENUMA_PRECALL_CAPTURE *C){EnumaCaptureStop(C);}
int PixelOldPageCompile(CONST ENUMA_BOOT_LOG *L){return EnumaLogPageFromSnapshot(L,&mEnumaLogPage);}
BOOLEAN PixelSinkCompile(VOID *P,CONST CHAR8 *L,UINTN N){return EnumaCapturePixelSink(P,L,N);}
