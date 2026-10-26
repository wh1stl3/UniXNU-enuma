// SPDX-License-Identifier: BSD-2-Clause-Patent
// Production checkpoint, only platform reset/timer/ordinal dependencies stubbed.
#include <Uefi.h>
#define ENUMA_DISPATCH_CHECKPOINT_H
#define ENUMA_DIAG_STAGE 13
#define ENUMA_DIAG_DETAIL_POINT 16
#define ENUMA_DIAG_GOP_QUERY 1
#define ENUMA_DIAG_GUID_ONLY 1
#define ENUMA_DIAG_GUID_ENABLED 1
#define ENUMA_DIAG_DISPATCH_ORDINAL 1
#define ENUMA_DIAG_GUID_LOW64 0x7788556611223344ULL
#define ENUMA_DIAG_GUID_HIGH64 0x00ffeeddccbbaa99ULL
static UINTN EnumaDispatchOrdinal = 1;
static unsigned stages;
static VOID EnumaStageCheckpoint(UINTN point) { if (point == 13) { stages++; } }
static UINT64 ReadUnaligned64(CONST UINT64 *p) {
  UINT64 value = 0;
  for (unsigned i=0; i<8; i++) { value |= (UINT64)((CONST UINT8*)p)[i] << (i*8); }
  return value;
}
#if ENUMA_BOOT_LOG_REPLAY
static unsigned publishes;
static VOID *published_interface;
static EFI_STATUS CoreInstallProtocolInterface(EFI_HANDLE *handle,EFI_GUID *guid,UINTN type,VOID *interface) {
  (void)guid;(void)type;(void)published_interface;publishes++;
#if ENUMA_TEST_PROTOCOL_FAIL
  (void)handle;(void)interface;return 0x8000000000000009ULL;
#else
  *handle=(EFI_HANDLE)1;published_interface=interface;return 0;
#endif
}
#endif
#include "../firmware/diagnostics/EnumaDispatchDetailCheckpoint.h"
#ifndef BOOT_JOURNAL_COMPILE_ONLY
#include <assert.h>
#include <stdio.h>
int main(void) {
  EFI_GUID guid = {0x11223344,0x5566,0x7788,{0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff,0}};
  EnumaDispatchDetailCheckpoint(14, &guid, 0x8000000000000001ULL);
  EnumaDispatchDetailCheckpoint(15, &guid, 0);
  EnumaDispatchDetailCheckpoint(20, &guid, 0);
  EnumaDispatchDetailCheckpoint(21, &guid, 1);
  EnumaDispatchDetailCheckpoint(22, &guid, 1);
  EnumaDispatchDetailCheckpoint(13, NULL, 1);
  EnumaDispatchDetailCheckpoint(13, &guid, 1);
  assert(stages == 1);
#if ENUMA_BOOT_JOURNAL
  ENUMA_BOOT_LOG snapshot;
  assert(!EnumaDxeBootLogSnapshot(NULL));
  assert(!EnumaDxeBootLogSnapshot((ENUMA_BOOT_LOG *)&EnumaDxeBootLog));
  assert(EnumaDxeBootLogSnapshot(&snapshot));
  assert(snapshot.Count == 7 && snapshot.Events[0].Status == 0x8000000000000001ULL);
  assert(snapshot.Events[5].HasGuid == FALSE && snapshot.Events[6].Point == 13);
  assert(snapshot.Events[2].Point == 20 && snapshot.Events[4].Point == 22);
#endif
#if ENUMA_BOOT_LOG_REPLAY
  assert(publishes==1);
#if ENUMA_TEST_PROTOCOL_FAIL
  assert(!published_interface&&!EnumaJournalHandle&&EnumaJournalPublishStatus==0x8000000000000009ULL);
#else
  assert(published_interface==&EnumaJournalProtocol);
#endif
  assert(EnumaJournalProtocol.Version==1&&EnumaJournalProtocol.Bytes==sizeof(EnumaJournalProtocol));
  assert(EnumaJournalProtocol.Snapshot(&snapshot)&&snapshot.Count==7);
#endif
  puts("PASS: production hook preserves filtering, records all pre-filter points when enabled");
}
#else
VOID BootJournalHookCompile(VOID) { EnumaDispatchDetailCheckpoint(14, NULL, 0); }
#endif
