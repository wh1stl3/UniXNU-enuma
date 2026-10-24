// SPDX-License-Identifier: BSD-2-Clause-Patent
// Host-only adapters around the exact pinned DarwinBoot AdtNode function.
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "WindowSize.h"

typedef uint8_t UINT8;
typedef uint32_t UINT32;
typedef uint64_t UINT64;
typedef size_t UINTN;
typedef char CHAR8;
typedef int BOOLEAN;
#define STATIC static
#define CONST const
#define TRUE 1
#define FALSE 0
#define MAX_UINTN SIZE_MAX
#define ALIGN_VALUE(v, a) (((v) + (a) - 1) & ~((a) - 1))
#define ScanMem8(p, n, v) memchr((p), (v), (n))
#define AsciiStrCmp(a, b) strcmp((a), (b))
#define CompareMem(a, b, n) memcmp((a), (b), (n))
static UINT32 U32(const void *p) { UINT32 v; memcpy(&v, p, sizeof v); return v; }
static UINT64 U64(const void *p) { UINT64 v; memcpy(&v, p, sizeof v); return v; }
#include DARWIN_ADT_SOURCE

static unsigned char data[1024];
static size_t used;
static void word(uint32_t value) {
    assert(used + 4 <= sizeof data);
    for (unsigned i = 0; i < 4; ++i) data[used++] = (unsigned char)(value >> (i * 8));
}
static void property(const char *name, const void *value, size_t bytes) {
    assert(strlen(name) < 32 && used + 36 + bytes + 3 <= sizeof data);
    memset(data + used, 0, 32); memcpy(data + used, name, strlen(name)); used += 32;
    word((uint32_t)bytes);
    memcpy(data + used, value, bytes); used += bytes;
    while (used & 3) data[used++] = 0;
}
enum variant { NORMAL, MISSING, ROOT_PROPERTY, DUPLICATE_PROPERTY, DUPLICATE_CHOSEN, SHORT_VALUE };
static void memory(uint64_t bytes, unsigned length) {
    unsigned char value[8];
    for (unsigned i = 0; i < 8; ++i) value[i] = (unsigned char)(bytes >> (i * 8));
    property("darwinboot-memory-size", value, length);
}
static void fixture(uint64_t bytes, enum variant variant) {
    used = 0; memset(data, 0, sizeof data);
    word(variant == ROOT_PROPERTY ? 2 : 1);
    word(variant == DUPLICATE_CHOSEN ? 2 : 1);
    property("name", "/", 2);
    if (variant == ROOT_PROPERTY) memory(bytes, 8);
    for (unsigned i = 0; i < (variant == DUPLICATE_CHOSEN ? 2u : 1u); ++i) {
        unsigned count = variant == MISSING || variant == ROOT_PROPERTY ? 1 : 2;
        if (variant == DUPLICATE_PROPERTY) ++count;
        word(count); word(0); property("name", "chosen", 7);
        if (count >= 2) memory(bytes, variant == SHORT_VALUE ? 4 : 8);
        if (count == 3) memory(bytes, 8);
    }
}
static int parse(size_t length, uint64_t *window) {
    size_t offset = 0, ramdisk = SIZE_MAX, trustcache = SIZE_MAX, addon = SIZE_MAX;
    int keep_packed = 0;
    *window = 0;
    return AdtNode(data, length, &offset, 0, 3, &ramdisk, &trustcache, &addon, window, &keep_packed)
           && offset == length;
}
static void addon_fixture(uint64_t bytes, unsigned length, int duplicate) {
    unsigned char placeholder[16] = {0};
    used = 0; memset(data, 0, sizeof data);
    word(1); word(1); property("name", "/", 2);
    word(2); word(1); property("name", "chosen", 7); memory(bytes, 8);
    word(duplicate ? 3 : 2); word(0); property("name", "memory-map", 11);
    property("GpuAddon", placeholder, length);
    if (duplicate) property("GpuAddon", placeholder, length);
}
static unsigned char *read_input(const char *path, size_t *size) {
    FILE *f = fopen(path, "rb"); assert(f);
    assert(fseek(f, 0, SEEK_END) == 0);
    long length = ftell(f); assert(length > 0 && length < 1024 * 1024);
    *size = (size_t)length;
    rewind(f);
    unsigned char *p = malloc(*size + 1); assert(p);
    assert(fread(p, 1, *size, f) == *size && fclose(f) == 0);
    return p;
}
static void actual_inputs(const char *adt_path, const char *trust_path, uint64_t approved) {
    size_t size, offset = 0, ramdisk = SIZE_MAX, trust = SIZE_MAX, addon = SIZE_MAX;
    uint64_t window = 0; int packed = 0;
    unsigned char *adt = read_input(adt_path, &size);
    assert(AdtNode(adt, size, &offset, 0, 3, &ramdisk, &trust, &addon, &window, &packed));
    assert(offset == size && window == approved && trust != SIZE_MAX);
    assert(ramdisk == SIZE_MAX && addon == SIZE_MAX && !packed);
    assert(U64(adt + trust) == 0 && U64(adt + trust + 8) == 0);
    for (size_t cut = 0; cut < size; ++cut) {
        offset = 0; ramdisk = trust = addon = SIZE_MAX; window = 0; packed = 0;
        assert(!AdtNode(adt, cut, &offset, 0, 3, &ramdisk, &trust, &addon, &window, &packed));
    }
    free(adt);
    unsigned char *bundle = read_input(trust_path, &size);
    assert(ValidTrustCaches(bundle, size));
    for (size_t cut = 0; cut < size; ++cut) assert(!ValidTrustCaches(bundle, cut));
    bundle[size] = 0; assert(!ValidTrustCaches(bundle, size + 1));
    unsigned char saved = bundle[4]; bundle[4] = 0;
    assert(!ValidTrustCaches(bundle, size)); bundle[4] = saved;
    size_t first = U32(bundle + 4);
    saved = bundle[first + 24 + 20]; bundle[first + 24 + 20] = 0;
    assert(!ValidTrustCaches(bundle, size)); bundle[first + 24 + 20] = saved;
    unsigned char hash[20]; memcpy(hash, bundle + first + 24 + 24, 20);
    memcpy(bundle + first + 24 + 24, bundle + first + 24, 20);
    assert(!ValidTrustCaches(bundle, size));
    memcpy(bundle + first + 24 + 24, hash, 20);
    assert(ValidTrustCaches(bundle, size)); free(bundle);
    puts("PASS: actual FAT ADT and original trust bundle accepted by pinned DarwinBoot functions; truncations and malformed trust rejected");
}
int main(int argc, char **argv) {
    assert(argc == 2 || argc == 4);
    char *end; uint64_t approved = strtoull(argv[1], &end, 0), window;
    assert(*end == 0 && approved == 0x20000000ULL);
    if (argc == 4) actual_inputs(argv[2], argv[3], approved);
    fixture(approved, NORMAL);
    assert(parse(used, &window) && window == approved);
    size_t valid_size = used;
    for (size_t i = 0; i < valid_size; ++i) assert(!parse(i, &window));
    data[used++] = 0; assert(!parse(used, &window));
    for (int v = ROOT_PROPERTY; v <= SHORT_VALUE; ++v) {
        fixture(approved, (enum variant)v); assert(!parse(used, &window));
    }
    const uint64_t bad[] = {0, 0x0fffffffULL, 0x10001000ULL, 0x200200000ULL};
    for (size_t i = 0; i < sizeof bad / sizeof bad[0]; ++i) {
        fixture(bad[i], NORMAL); assert(!parse(used, &window));
    }
    const uint64_t good[] = {0x10000000ULL, 0x200000000ULL};
    for (size_t i = 0; i < sizeof good / sizeof good[0]; ++i) {
        fixture(good[i], NORMAL); assert(parse(used, &window) && window == good[i]);
    }
    fixture(approved, MISSING); assert(parse(used, &window) && window == 0);
    addon_fixture(approved, 16, 0);
    size_t offset = 0, ramdisk = SIZE_MAX, trustcache = SIZE_MAX, addon = SIZE_MAX;
    int packed = 0; window = 0;
    assert(AdtNode(data, used, &offset, 0, 3, &ramdisk, &trustcache, &addon, &window, &packed));
    assert(offset == used && addon == used - 16 && window == approved);
    addon_fixture(approved, 8, 0); assert(!parse(used, &window));
    addon_fixture(approved, 16, 1); assert(!parse(used, &window));
    printf("PASS: real DarwinBoot AdtNode accepts 512 MiB; rejects %zu truncations, trailing bytes, invalid values, duplicate/misplaced/short properties\n", valid_size);
    return 0;
}
