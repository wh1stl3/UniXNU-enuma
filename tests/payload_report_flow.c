// SPDX-License-Identifier: BSD-2-Clause-Patent
// Host fault injection around the extracted production BDS payload/report tail.
#include <assert.h>
#include <stdint.h>
#include <stddef.h>
#include <wchar.h>
#include <stdio.h>
#define ENUMA_RAM_PAYLOAD 1
typedef unsigned long UINTN;
typedef uint32_t UINT32;
typedef uint64_t UINT64;
typedef wchar_t CHAR16;
typedef void VOID;
typedef int EFI_STATUS;
typedef struct { int value; } EFI_GUID;
#define EFIAPI
#define STATIC static
#define CONST const
#define EFI_SUCCESS 0
#define EFI_NOT_READY 1
#define EFI_NOT_FOUND 2
#define EFI_INCOMPATIBLE_VERSION 3
#define EFI_ABORTED 4
#define EFI_ERROR(s) ((s) != 0)
#include "TransportReport.h"
#undef ENUMA_TRANSPORT_REPORT_GUID
#define ENUMA_TRANSPORT_REPORT_GUID {0}
static ENUMA_TRANSPORT_REPORT report;
static int missing, lines, freed, flushed, stalled, ran, event;
static EFI_STATUS file_status;
static EFI_STATUS files(ENUMA_TRANSPORT_REPORT *r) { assert(r == &report); return file_status; }
static EFI_STATUS locate(EFI_GUID *guid, void *registration, void **out) {
  (void)guid; (void)registration; *out = &report; return missing ? EFI_NOT_FOUND : EFI_SUCCESS;
}
static EFI_STATUS stall(UINTN us) { assert(us == 2000000 && event == 2); event = 3; ++stalled; return EFI_SUCCESS; }
static struct { EFI_STATUS (*LocateProtocol)(EFI_GUID *, void *, void **); EFI_STATUS (*Stall)(UINTN); } services = {locate, stall}, *gBS = &services;
static void Line(UINTN row, const CHAR16 *text) { (void)text; assert(row < 13 && event == 0); ++lines; }
static void UnicodeSPrint(CHAR16 *text, UINTN bytes, const CHAR16 *fmt, const CHAR16 *name, EFI_STATUS s) {
  (void)bytes; (void)fmt; (void)name; (void)s; text[0] = 0;
}
static void FreePool(void *map) { assert(map && event == 0); ++freed; event = 1; }
static void WriteBackDataCacheRange(void *base, UINTN bytes) { assert(base && bytes == 4096 && event == 1); ++flushed; event = 2; }
#define UniXNUHostFirmware 1
static EFI_STATUS UniXNURun(void *handle, int host) { (void)handle; assert(host == 1 && event == 3); ++ran; return EFI_SUCCESS; }
static EFI_STATUS run_tail(void) {
  EFI_STATUS Status = EFI_SUCCESS, VideoStatus = EFI_SUCCESS;
  void *Map = &report, *ImageHandle = NULL;
  UINT64 Video[6] = {4096, 0, 64, 0, 64, 0};
  CHAR16 Text[128];
#include "PayloadTail.inc"
static void reset(void) {
  missing = lines = freed = flushed = stalled = ran = event = 0;
  report.Version = 1; report.Passed = 0x1f7fU; report.CheckFiles = files; file_status = EFI_SUCCESS;
}
int main(void) {
  reset(); missing = 1; assert(run_tail() == EFI_NOT_FOUND && lines == 1 && ran == 0);
  assert(freed == 1 && flushed == 1 && stalled == 1);
  reset(); report.Version = 99; assert(run_tail() == EFI_INCOMPATIBLE_VERSION && lines == 1 && ran == 0);
  assert(freed == 1 && flushed == 1 && stalled == 1);
  reset(); file_status = EFI_NOT_FOUND; assert(run_tail() == EFI_NOT_FOUND && lines == 13 && ran == 0);
  assert(freed == 1 && flushed == 1 && stalled == 1);
  reset(); report.Passed &= ~(1U << 3); assert(run_tail() == EFI_NOT_READY && lines == 13 && ran == 0);
  assert(freed == 1 && flushed == 1 && stalled == 1);
  reset(); assert(run_tail() == EFI_ABORTED && lines == 13 && ran == 1);
  assert(freed == 1 && flushed == 1 && stalled == 1);
  puts("PASS: missing/version/file/missing-stage faults flush and clean before return; success flushes and continues after two seconds; 13 rows fit");
  return 0;
}
