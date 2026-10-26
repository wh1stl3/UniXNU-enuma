// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "../firmware/diagnostics/EnumaBootJournal.h"
#ifndef BOOT_JOURNAL_COMPILE_ONLY
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static char accepted[ENUMA_BOOT_LOG_LINE_BYTES];
static int refuse;
static BOOLEAN sink(VOID *context, CONST CHAR8 *line, UINTN bytes) {
  unsigned *calls = context; (*calls)++;
  assert(bytes < sizeof accepted && line[bytes] == 0 && line[bytes-1] == '\n');
  memcpy(accepted, line, bytes+1);
  return !refuse;
}
int main(void) {
  ENUMA_BOOT_LOG log = {0}, snapshot;
  EFI_GUID guid = {0x11223344,0x5566,0x7788,{0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff,0}};
  UINT32 cursor;
  unsigned calls = 0;
  assert(!EnumaBootLogAppend(NULL, 13, 1, NULL, 0));
  assert(!EnumaBootLogReplayNext(NULL, &cursor, sink, &calls));
  for (unsigned i = 0; i < 10000; i++) {
    assert(EnumaBootLogAppend(&log, 13+i%10, i, i%2 ? &guid : NULL, 0x8000000000000001ULL+i));
    assert(log.Count == (i+1 < 128 ? i+1 : 128));
    assert(log.Dropped == (i+1 < 128 ? 0 : i+1-128));
    // Independent arithmetic expectation for every retained event after wrap.
    for (unsigned j = 0; j < log.Count; j++) {
      ENUMA_BOOT_EVENT *e = &log.Events[(log.Head+j)%128];
      UINT64 seq = i+1-log.Count+j;
      assert(e->Sequence == seq && e->Ordinal == seq && e->Point == 13+seq%10);
      assert(e->Status == 0x8000000000000001ULL+seq);
      assert(e->HasGuid == (seq%2 != 0));
      assert(memcmp(e->GuidLe, seq%2 ? (void*)&guid : (void*)(UINT8[16]){0}, 16) == 0);
    }
  }
  snapshot = log; cursor = 0;
  assert(EnumaBootLogReplayNext(&snapshot, &cursor, sink, &calls));
  assert(strcmp(accepted, "DXE replay dropped=0000000000002690\n") == 0);
  assert(cursor == 1);
  refuse = 1;
  assert(!EnumaBootLogReplayNext(&snapshot, &cursor, sink, &calls) && cursor == 1);
  char retry[128]; strcpy(retry, accepted);
  // Live producer can advance while the caller replays its isolated snapshot.
  assert(EnumaBootLogAppend(&log, 99, 99, NULL, 0));
  refuse = 0;
  assert(EnumaBootLogReplayNext(&snapshot, &cursor, sink, &calls) && cursor == 2);
  assert(strcmp(retry, accepted) == 0);
  assert(strcmp(accepted, "DXE seq=0000000000002690 p=0000000f o=00002690 s=8000000000002691 g=-\n") == 0);
  assert(EnumaBootLogReplayNext(&snapshot, &cursor, sink, &calls));
  assert(strstr(accepted, "g=443322116655887799aabbccddeeff00\n"));
  while (cursor <= snapshot.Count) { assert(EnumaBootLogReplayNext(&snapshot, &cursor, sink, &calls)); }
  assert(!EnumaBootLogReplayNext(&snapshot, &cursor, sink, &calls));
  assert(!EnumaBootLogReplayNext(&snapshot, NULL, sink, &calls));
  assert(!EnumaBootLogReplayNext(&snapshot, &cursor, NULL, &calls));
  log.NextSequence = MAX_UINT64;
  snapshot = log;
  assert(!EnumaBootLogAppend(&log, 1, 1, NULL, 0) && memcmp(&snapshot,&log,sizeof log)==0);
  log.NextSequence = 1; log.Dropped = MAX_UINT64;
  assert(EnumaBootLogAppend(&log, 1, 1, NULL, 0) && log.Dropped == MAX_UINT64);
  log.Head = 128; assert(!EnumaBootLogAppend(&log, 0, 0, NULL, 0));
  cursor = 0; assert(!EnumaBootLogReplayNext(&log, &cursor, sink, &calls));
  log.Head = 0; log.Count = 129;
  assert(!EnumaBootLogAppend(&log, 0, 0, NULL, 0));
  assert(!EnumaBootLogReplayNext(&log, &cursor, sink, &calls));
  memset(&log, 0, sizeof log);
  assert(EnumaBootLogReplayNext(&log, &cursor, sink, &calls));
  assert(!EnumaBootLogReplayNext(&log, &cursor, sink, &calls));
  puts("PASS: 10000 events, wrap/order/loss, full GUID and status, snapshot isolation, sink retry, invalid input and saturation");
  return 0;
}
#else
// Exercise all production APIs with actual pinned EDK Uefi.h on AArch64.
BOOLEAN BootJournalCompile(ENUMA_BOOT_LOG *log, UINT32 *cursor, ENUMA_BOOT_LOG_SINK sink, VOID *context) {
  if (!EnumaBootLogAppend(log, 13, 7, NULL, 0x8000000000000001ULL)) { return FALSE; }
  return EnumaBootLogReplayNext(log, cursor, sink, context);
}
#endif
