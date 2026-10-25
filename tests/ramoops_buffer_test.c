// SPDX-License-Identifier: BSD-2-Clause-Patent
// The production header is checked against an independent linear byte queue.
#include "../firmware/diagnostics/EnumaRamoopsBuffer.h"

#ifndef RAMOOPS_COMPILE_ONLY
#include <assert.h>
#include <stdio.h>
#include <string.h>

static unsigned seed = 0x215;
static unsigned rng(void) { seed = seed * 1664525U + 1013904223U; return seed; }

int main(void) {
  union { unsigned align; unsigned char bytes[512]; } region;
  unsigned char expected[256], input[512], old[512];
  unsigned cases = 0;
  for (unsigned cap = 1; cap <= 256; cap++) {
    memset(region.bytes, 0xa5, sizeof region.bytes);
    unsigned used = 0;
    for (unsigned run = 0; run < 200; run++) {
      unsigned count = rng() % sizeof input;
      for (unsigned i = 0; i < count; i++) input[i] = (unsigned char)rng();
      assert(EnumaRamoopsAppend(region.bytes, cap + 12, input, count) == count);
      if (count == 0) continue;
      for (unsigned i = 0; i < count; i++) {
        if (used == cap) { memmove(expected, expected + 1, cap - 1); used--; }
        expected[used++] = input[i];
      }
      ENUMA_RAMOOPS_HEADER *h = (void *)region.bytes;
      assert(h->Signature == ENUMA_RAMOOPS_SIGNATURE);
      assert(h->Size == used && h->Start <= h->Size);
      // persistent_ram_save_old uses data[start:size] + data[0:start].
      for (unsigned i = 0; i < used; i++)
        assert(region.bytes[12 + (h->Start + i) % used] == expected[i]);
      for (unsigned i = cap + 12; i < sizeof region.bytes; i++)
        assert(region.bytes[i] == 0xa5); // adjacent pmsg / out-of-window guard
      cases++;
    }
  }
  // Invalid signature, size and start each reset only metadata + new payload.
  for (unsigned kind = 0; kind < 3; kind++) {
    memset(region.bytes, 0xa5, sizeof region.bytes);
    ENUMA_RAMOOPS_HEADER *h = (void *)region.bytes;
    h->Signature = kind == 0 ? 0 : ENUMA_RAMOOPS_SIGNATURE;
    h->Start = kind == 2 ? 5 : 0; h->Size = kind == 1 ? 65 : 4;
    assert(EnumaRamoopsAppend(region.bytes, 76, (const UINT8 *)"CANARY", 6) == 6);
    assert(h->Size == 6 && h->Start == 6);
    assert(memcmp(region.bytes + 12, "CANARY", 6) == 0);
    for (unsigned i = 18; i < sizeof region.bytes; i++) assert(region.bytes[i] == 0xa5);
    cases++;
  }
  // Linux accepts full-buffer start == capacity; next append normalizes it.
  memset(region.bytes, 0xa5, sizeof region.bytes);
  ENUMA_RAMOOPS_HEADER *h = (void *)region.bytes;
  h->Signature = ENUMA_RAMOOPS_SIGNATURE; h->Start = 64; h->Size = 64;
  assert(EnumaRamoopsAppend(region.bytes, 76, (const UINT8 *)"X", 1) == 1);
  assert(h->Start == 1 && h->Size == 64 && region.bytes[12] == 'X'); cases++;
  memcpy(old, region.bytes, sizeof old);
  assert(EnumaRamoopsAppend(NULL, 76, input, 1) == 0);
  assert(EnumaRamoopsAppend(region.bytes, 76, NULL, 1) == 0);
  assert(EnumaRamoopsAppend(region.bytes, 76, input, 0) == 0);
  assert(EnumaRamoopsAppend(region.bytes + 1, 76, input, 1) == 0);
  assert(EnumaRamoopsAppend(region.bytes, 12, input, 1) == 0);
  assert(EnumaRamoopsAppend(region.bytes, 0x8000000cULL, input, 1) == 0);
  assert(memcmp(old, region.bytes, sizeof old) == 0); cases += 6;
  printf("PASS: %u native ring/oracle and boundary cases\n", cases);
  return 0;
}
#endif

unsigned long append(void *region, unsigned long size, const unsigned char *data,
                     unsigned long count) {
  return EnumaRamoopsAppend(region, size, data, count);
}
