// SPDX-License-Identifier: BSD-2-Clause-Patent
// Exact upstream allocation functions, using synthetic maps and host EFI mocks.
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
typedef uint8_t UINT8;
typedef uint32_t UINT32;
typedef uint64_t UINT64;
typedef size_t UINTN;
typedef __WCHAR_TYPE__ CHAR16;
typedef int BOOLEAN;
typedef void VOID;
typedef UINT64 EFI_STATUS;
typedef UINT64 EFI_PHYSICAL_ADDRESS;
#define STATIC static
#define TRUE 1
#define FALSE 0
#define EFI_PAGE_SIZE 4096ULL
#define EFI_PAGES_TO_SIZE(n) ((n) * EFI_PAGE_SIZE)
#define EFI_SIZE_TO_PAGES(n) (((n) + EFI_PAGE_SIZE - 1) / EFI_PAGE_SIZE)
#define EFI_SUCCESS 0ULL
#define EFI_OUT_OF_RESOURCES (0x8000000000000000ULL | 9)
#define EFI_DEVICE_ERROR (0x8000000000000000ULL | 7)
#define EFI_ERROR(s) (((s) >> 63) != 0)
#define MAX_UINT64 UINT64_MAX
#define BLOCK_SIZE 0x200000ULL
#define ALIGN_VALUE(v, a) (((v) + (a) - 1) & ~((a) - 1))
#define EfiConventionalMemory 7
#define EfiReservedMemoryType 0
#define EfiLoaderCode 1
#define AllocateAddress 2
typedef struct {
    UINT32 Type, Pad;
    UINT64 PhysicalStart, VirtualStart, NumberOfPages, Attribute;
} EFI_MEMORY_DESCRIPTOR;
// Only Base is read by AllocateWindow; this is not a KERNEL ABI/layout test.
typedef struct { UINT64 Base; } KERNEL;
static unsigned char map_bytes[16 * 48];
static UINTN map_size;
static unsigned calls, frees, diagnostics, failures;
static EFI_STATUS map_status;
static UINT64 requests[16];
static void reset(void) {
    memset(map_bytes, 0, sizeof map_bytes);
    map_size = calls = frees = diagnostics = failures = 0;
    map_status = EFI_SUCCESS;
}
static void region(UINT32 type, UINT64 start, UINT64 bytes) {
    assert(map_size + 48 <= sizeof map_bytes && !(bytes & 4095));
    EFI_MEMORY_DESCRIPTOR d = {type, 0, start, 0, bytes / 4096, 0};
    memcpy(map_bytes + map_size, &d, sizeof d); map_size += 48;
}
static EFI_STATUS GetMap(EFI_MEMORY_DESCRIPTOR **map, UINTN *capacity, UINTN *size,
                         UINTN *key, UINTN *stride) {
    if (EFI_ERROR(map_status)) return map_status;
    *capacity = *size = map_size; *stride = 48; *key = 5;
    *map = malloc(map_size ? map_size : 1); assert(*map);
    memcpy(*map, map_bytes, map_size); return EFI_SUCCESS;
}
static void FreePool(void *p) { ++frees; free(p); }
static EFI_STATUS allocate(unsigned kind, unsigned type, UINTN pages, UINT64 *address) {
    assert(kind == AllocateAddress && type == EfiLoaderCode && pages == 0x20000000 / 4096);
    assert(calls < 16); requests[calls++] = *address;
    if (failures) { --failures; return EFI_OUT_OF_RESOURCES; }
    return EFI_SUCCESS;
}
static struct { EFI_STATUS (*AllocatePages)(unsigned, unsigned, UINTN, UINT64 *); } services = {allocate};
#define gBS (&services)
static void UnicodeSPrint(CHAR16 *line, UINTN bytes, const CHAR16 *format, ...) {
    (void)format; assert(bytes >= sizeof *line); *line = 0;
}
static void DiagDraw(const CHAR16 *line, UINTN row) { (void)line; (void)row; ++diagnostics; }
#include DARWIN_WINDOW_SOURCE

static EFI_STATUS request(UINT64 kernel_base, UINT64 *address) {
    KERNEL kernel = {kernel_base};
    *address = UINT64_MAX;
    return AllocateWindow(&kernel, 0x20000000, address);
}
int main(void) {
    UINT64 address;
    // All addresses are synthetic examples, never an enuma memory map.
    reset(); region(EfiConventionalMemory, 0x100000000, 0x20000000);
    assert(request(0, &address) == EFI_SUCCESS && address == 0x100000000 && calls == 1 && frees == 1);
    // Out-of-order, adjacent descriptors with a larger descriptor stride.
    reset(); region(EfiConventionalMemory, 0x110000000, 0x10000000);
    region(EfiConventionalMemory, 0x100000000, 0x10000000);
    assert(request(0, &address) == EFI_SUCCESS && address == 0x100000000 && calls == 1);
    // Total free bytes exceed 512 MiB, but reserved holes cannot be crossed.
    reset(); region(EfiConventionalMemory, 0x100000000, 0x18000000);
    region(EfiReservedMemoryType, 0x118000000, 0x200000);
    region(EfiConventionalMemory, 0x118200000, 0x18000000);
    assert(request(0, &address) == EFI_OUT_OF_RESOURCES && address == 0 && calls == 0 && diagnostics > 0);
    // Reserved regions must never satisfy the request.
    reset(); region(EfiReservedMemoryType, 0x100000000, 0x40000000);
    assert(request(0, &address) == EFI_OUT_OF_RESOURCES && address == 0 && calls == 0);
    // Alignment and the kernel's block offset consume part of a free range.
    reset(); region(EfiConventionalMemory, 0x100001000, 0x20000000);
    assert(request(0x4000, &address) == EFI_OUT_OF_RESOURCES && calls == 0);
    reset(); region(EfiConventionalMemory, 0x100001000, 0x20200000);
    assert(request(0x4000, &address) == EFI_OUT_OF_RESOURCES && calls == 0);
    reset(); region(EfiConventionalMemory, 0x100001000, 0x20400000);
    assert(request(0x4000, &address) == EFI_SUCCESS && address == 0x100204000);
    // Failed allocation may try another eligible range, but not a smaller size.
    reset(); region(EfiConventionalMemory, 0x100000000, 0x20000000);
    region(EfiConventionalMemory, 0x200000000, 0x20000000); failures = 1;
    assert(request(0, &address) == EFI_SUCCESS && address == 0x200000000 && calls == 2);
    assert(requests[0] == 0x100000000 && requests[1] == 0x200000000);
    reset(); region(EfiConventionalMemory, 0x100000000, 0x20000000); failures = 1;
    assert(request(0, &address) == EFI_OUT_OF_RESOURCES && address == 0 && calls == 1 && frees == 1);
    reset(); map_status = EFI_DEVICE_ERROR;
    assert(request(0, &address) == EFI_DEVICE_ERROR && address == 0 && calls == 0 && frees == 0);
    puts("PASS: real RunEnd/AllocateWindow with 512 MiB; contiguous/coalesced ranges, reserved holes, alignment, allocation and map failures");
    return 0;
}
