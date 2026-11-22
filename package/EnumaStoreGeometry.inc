// SPDX-License-Identifier: BSD-2-Clause-Patent
// Included only by the r40 copy of NativeUfs.cpp after reserve parsing.
#include <sys/systm.h>
#include "PersistOverlay.h"

extern "C" {
extern volatile uint32_t native_ram_block_ready;
extern volatile uint64_t native_ram_block_bytes;
}

namespace {
struct EnumaStoreGeometry {
  uint64_t first, last, imageBytes;
  uint32_t headerCrc, entriesCrc, status, magic0, magic1;
};
static EnumaStoreGeometry gEnumaStoreGeometry;
static bool gEnumaStoreGeometryReady;

static void enumaStoreGeometryCapture(const RootLayout &layout)
{
  gEnumaStoreGeometry = {layout.userdataFirst, layout.userdataLast, layout.imageBytes,
                        layout.gptHeaderCrc, layout.gptEntriesCrc, layout.manifestStatus,
                        layout.magic0, layout.magic1};
  __atomic_store_n(&gEnumaStoreGeometryReady, true, __ATOMIC_RELEASE);
}
}

extern "C" __attribute__((noinline)) void enuma_storegeom_report(void)
{
  printf("enuma-sg: begin\n");
  if (__atomic_load_n(&gEnumaStoreGeometryReady, __ATOMIC_ACQUIRE)) {
    const auto &g = gEnumaStoreGeometry;
    // Both LBAs are bounded by the existing READ(10) GPT parser.
    printf("enuma-sg: ud first=%u last=%u\n", unsigned(g.first), unsigned(g.last));
    printf("enuma-sg: crc hdr=%08x entries=%08x\n", g.headerCrc, g.entriesCrc);
    printf("enuma-sg: manifest status=%u magic=%08x/%08x\n", g.status, g.magic0, g.magic1);

    const uint64_t bytes = native_ram_block_ready ? native_ram_block_bytes : 0;
    if (bytes && !(bytes % persist::kBlock) && g.status == 0) {
      const uint64_t pages = bytes / persist::kBlock;
      const uint64_t reserve = readReserveBlocks();
      const uint64_t length = persist::windowBlocks(pages);
      // Signed coordinates retain a negative start/end rather than wrapping.
      // 64-bit byte size bounds length to <2^53 blocks; GPT LBAs are <=2^32.
      const uint64_t udEnd = g.last + 1;
      const int64_t end = int64_t(udEnd - reserve);
      const int64_t start = int64_t(udEnd - reserve - length);
      const int64_t first = int64_t(g.first);
      const int64_t rootEnd = int64_t(g.first + g.imageBytes / persist::kBlock);
      printf("enuma-sg: seed=%llu reserve=%llu blocks\n",
             (unsigned long long)pages, (unsigned long long)reserve);
      printf("enuma-sg: win start=%lld len=%llu\n", (long long)start, (unsigned long long)length);
      printf("enuma-sg: chk in_ud=%u below_first=%u hits_root=%u\n",
             unsigned(end > first && start < int64_t(udEnd)),
             unsigned(start < first), unsigned(end > first && start < rootEnd));
    } else {
      printf("enuma-sg: win n/a (%s)\n", g.status ? "manifest invalid" : "seed unavailable");
    }
  } else {
    printf("enuma-sg: ud n/a; crc: n/a; manifest n/a; win n/a\n");
  }
  printf("enuma-sg: no-new-ufs-io\n");
  printf("enuma-sg: end\n");
}
