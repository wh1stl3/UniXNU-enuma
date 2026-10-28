#include "EnumaOemGopMode.h"
BOOLEAN CheckGopMode(EFI_BOOT_SERVICES *B,UINTN A,UINTN N){return OemGopAdvance(B,A,N);}
