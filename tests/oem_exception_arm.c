#include <Uefi.h>
#include <Protocol/DebugSupport.h>
#define ENUMA_OEM_EXCEPTION 1
#define ENUMA_OEM_EXIT_CLOCK 1
#define ENUMA_OEM_GOP_MODE 1
#include "EnumaOemExceptionStop.h"
VOID ProbeException(EFI_EXCEPTION_TYPE Type,EFI_SYSTEM_CONTEXT Context){EnumaUnhandledExceptionCheckpoint(Type,Context);}
