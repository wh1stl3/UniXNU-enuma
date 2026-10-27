// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <Uefi.h>
#include <assert.h>
#include <stdio.h>
#define ENUMA_DIAG_STAGE 13
#define ENUMA_DIAG_DETAIL_POINT 16
static unsigned Calls;
static EFI_STATUS Seen;
static VOID EnumaDispatchDetailCheckpoint(UINTN Point,CONST EFI_GUID *Guid,EFI_STATUS Status){(void)Point;(void)Guid;Calls++;Seen=Status;}
#include "EnumaImageEntryCheckpoint.h"
int main(void){
 EFI_GUID Guid={0};EFI_HANDLE Parent=(VOID *)1,Child=(VOID *)2;UINTN Point;
 EnumaStartingImage=Parent;EnumaStartingFile=&Guid;
 for(Point=20;Point<=22;Point++){
  EnumaImageEntryCheckpoint(Point,Child,0);EnumaImageEntryCheckpoint(Point,Child,2);EnumaImageEntryCheckpoint(Point,Child,EFI_ABORTED);
 }
 assert(!Calls);
 EnumaImageEntryCheckpoint(21,Parent,5);assert(Calls==1&&Seen==5);
 assert(EnumaStartingImage==Parent&&EnumaStartingFile==&Guid);
 EnumaStartingImage=NULL;EnumaImageEntryCheckpoint(21,Parent,5);assert(Calls==1);
 EnumaStartingImage=Parent;EnumaStartingFile=NULL;EnumaImageEntryCheckpoint(21,Parent,5);assert(Calls==1);
 puts("nested child cannot impersonate scheduled provider: PASS");return 0;
}
