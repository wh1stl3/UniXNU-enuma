// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "EnumaOemPrecallCapture.h"
EFI_STATUS CaptureCompile(ENUMA_PRECALL_CAPTURE *C,ENUMA_SERVICE_TRACE *T,
  EFI_SYSTEM_TABLE *S,ENUMA_BOOT_LOG_SINK Sink){
  EFI_STATUS Status=EnumaServiceTracePrepare(T,S,0x1000,0x1000);
  if(Status!=EFI_SUCCESS){return Status;}
  return EnumaCaptureArm(C,T,1,0,Sink,NULL);
}
VOID CaptureStopCompile(ENUMA_PRECALL_CAPTURE *C){EnumaCaptureStop(C);}
