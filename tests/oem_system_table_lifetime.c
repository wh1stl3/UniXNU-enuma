// SPDX-License-Identifier: BSD-2-Clause-Patent
// Reproduce the current private-table lifetime defect; not a firmware fix.
#define main ExistingTraceRegressionMain
#include "oem_service_trace.c"
#undef main
static EFI_CONFIGURATION_TABLE OldTables[1], NewTables[2];
static EFI_STATUS EFIAPI Install(EFI_GUID *G, VOID *Table) {
  assert(G==&Guid);
  // Model CoreInstallConfigurationTable's real global count/pointer updates.
  // Keep old storage allocated so this diagnostic never dereferences freed data.
  System.ConfigurationTable=NewTables;
  System.NumberOfTableEntries=Table?2:0;
  return EFI_SUCCESS;
}
int main(void) {
  Setup();
  System.ConfigurationTable=OldTables;System.NumberOfTableEntries=1;
  Boot.InstallConfigurationTable=Install;
  assert(EnumaServiceTracePrepare(&Trace,&System,0x1000,0x1000)==EFI_SUCCESS);
  assert(Trace.System.BootServices->InstallConfigurationTable(&Guid,NewTables)==EFI_SUCCESS);
  assert(System.ConfigurationTable==NewTables&&System.NumberOfTableEntries==2);
  assert(Trace.System.ConfigurationTable==OldTables&&Trace.System.NumberOfTableEntries==1);
  assert(Trace.System.BootServices->InstallConfigurationTable(&Guid,NULL)==EFI_SUCCESS);
  assert(System.NumberOfTableEntries==0&&Trace.System.NumberOfTableEntries==1);
  puts("REPRODUCED: successful original service leaves private SystemTable pointer/count stale on growth and deletion; hardware cause unproven");
  return 0;
}
