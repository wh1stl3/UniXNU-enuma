#include "EnumaOemExitClock.h"
VOID ExportClock(BOOLEAN Owner,BOOLEAN Returned,EFI_STATUS Status){
  EnumaOemClockExit(EnumaOemClockClass(Owner,Returned,Status));
}
