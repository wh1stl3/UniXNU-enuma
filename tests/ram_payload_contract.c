// SPDX-License-Identifier: BSD-2-Clause-Patent
// Actual production bounds, CRC wrapper and read-only BlockIO, host adapters.
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <zlib.h>
typedef uint8_t UINT8;
typedef uint32_t UINT32;
typedef uint64_t UINT64;
typedef uint64_t EFI_LBA;
typedef size_t UINTN;
typedef int BOOLEAN;
typedef void VOID;
typedef int EFI_STATUS;
typedef struct { UINT32 MediaId; UINT64 LastBlock; } EFI_BLOCK_IO_MEDIA;
typedef struct { int unused; } EFI_BLOCK_IO_PROTOCOL;
#define MAX_UINT64 UINT64_MAX
#define STATIC static
#define CONST const
#define EFIAPI
#define TRUE 1
#define FALSE 0
#define BLOCK_SIZE 512U
#define EFI_SUCCESS 0
#define EFI_MEDIA_CHANGED 1
#define EFI_INVALID_PARAMETER 2
#define EFI_BAD_BUFFER_SIZE 3
#define EFI_WRITE_PROTECTED 4
#define EFI_CRC_ERROR 5
#define EFI_ERROR(x) ((x) != 0)
#define DEBUG(x) ((void)0)
#define CopyMem memcpy
#include "TransportBounds.h"
#include "PayloadContract.h"
static UINT8 *mRamBase;
static EFI_BLOCK_IO_MEDIA mMedia;
static struct { UINTN Reads; } mReport;
static EFI_STATUS crc_service(void *p, size_t bytes, UINT32 *out) {
  *out = (UINT32)crc32(0, p, (uInt)bytes); return EFI_SUCCESS;
}
static struct { EFI_STATUS (*CalculateCrc32)(void *, size_t, UINT32 *); } services = {crc_service}, *gBS = &services;
#include "BlockRead.inc"
#include "CrcMatches.inc"
static UINT8 *load(const char *name, size_t *size) {
  FILE *f = fopen(name, "rb"); assert(f);
  assert(fseek(f, 0, SEEK_END) == 0); long n = ftell(f); assert(n > 0);
  *size = (size_t)n; rewind(f);
  UINT8 *p = malloc(*size); assert(p && fread(p, 1, *size, f) == *size);
  assert(fclose(f) == 0); return p;
}
int main(int argc, char **argv) {
  assert(argc == 3);
  size_t fat_size, prefix_size;
  UINT8 *fat = load(argv[1], &fat_size), *prefix = load(argv[2], &prefix_size);
  assert(fat_size == ENUMA_FAT_BYTES && prefix_size == ENUMA_PREFIX_BYTES);
  assert(CrcMatches(fat, fat_size, ENUMA_FAT_CRC) == EFI_SUCCESS);
  assert(CrcMatches(prefix, prefix_size, ENUMA_PREFIX_CRC) == EFI_SUCCESS);
  const UINT64 base = 0xa0000000, window = 0x10000000, dtb = base + 4096;
  UINT64 start = base + window - fat_size - prefix_size, end = base + window;
  assert(TransportSpan(base, window, dtb, 8192, start, end, prefix_size, fat_size));
  assert(!TransportSpan(base, window, dtb, 8192, start, end + 1, prefix_size, fat_size));
  assert(!TransportSpan(base, window, dtb, 8192, start, end - 1, prefix_size, fat_size));
  assert(!TransportSpan(base, window, start, 4096, start, end, prefix_size, fat_size));
  assert(!TransportSpan(base, window, dtb, 8192, end, start, prefix_size, fat_size));
  assert(!TransportSpan(UINT64_MAX - 3, 8, dtb, 8192, start, end, prefix_size, fat_size));
  assert(!TransportSpan(base, window, dtb, 8192, start, end, UINT64_MAX, fat_size));
  assert(!Contains(base, window, base - 1, 1));
  assert(!Contains(base, window, base + window, 1));
  assert(!Contains(base, window, base, 0));
  assert(!Contains(base, window, base, UINT64_MAX));
  // No physical FAT alignment requirement: a byte-copy block provider handles it.
  UINT8 *combined = malloc(prefix_size + fat_size); assert(combined);
  memcpy(combined, prefix, prefix_size); memcpy(combined + prefix_size, fat, fat_size);
  mRamBase = combined + prefix_size; mMedia.MediaId = 1; mMedia.LastBlock = fat_size / 512 - 1;
  UINT8 buffer[1024];
  assert(RamRead(NULL, 1, 0, 512, buffer) == EFI_SUCCESS && memcmp(buffer, fat, 512) == 0);
  assert(RamRead(NULL, 1, mMedia.LastBlock, 512, buffer) == EFI_SUCCESS && memcmp(buffer, fat + fat_size - 512, 512) == 0);
  assert(RamRead(NULL, 1, mMedia.LastBlock, 1024, buffer) == EFI_INVALID_PARAMETER);
  assert(RamRead(NULL, 1, mMedia.LastBlock + 1, 512, buffer) == EFI_INVALID_PARAMETER);
  assert(RamRead(NULL, 1, UINT64_MAX, 512, buffer) == EFI_INVALID_PARAMETER);
  assert(RamRead(NULL, 1, 0, 513, buffer) == EFI_BAD_BUFFER_SIZE);
  assert(RamRead(NULL, 1, 0, 512, NULL) == EFI_INVALID_PARAMETER);
  assert(RamRead(NULL, 1, 0, 0, NULL) == EFI_SUCCESS);
  assert(RamRead(NULL, 2, 0, 512, buffer) == EFI_MEDIA_CHANGED);
  assert(RamWrite(NULL, 1, 0, 512, buffer) == EFI_WRITE_PROTECTED);
  assert(RamReset(NULL, FALSE) == EFI_SUCCESS && RamFlush(NULL) == EFI_SUCCESS);
  combined[prefix_size - 1] ^= 1;
  assert(CrcMatches(combined, prefix_size, ENUMA_PREFIX_CRC) == EFI_CRC_ERROR);
  combined[prefix_size] ^= 1;
  assert(CrcMatches(mRamBase, fat_size, ENUMA_FAT_CRC) == EFI_CRC_ERROR);
  free(combined); free(prefix); free(fat);
  puts("PASS: real unaligned payload read/last block; bounds, overflow, overlap, media, write protection and prefix/FAT corruption rejection (host ASan/UBSan)");
  return 0;
}
