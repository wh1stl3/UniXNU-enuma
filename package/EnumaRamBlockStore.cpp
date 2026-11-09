// SPDX-License-Identifier: BSD-3-Clause
// Volatile RAM-root only. Signatures: RamBlock@4be2d7e NativeRamBlock.cpp:35-40.
#include <stdint.h>
extern "C" {
unsigned native_ufs_store_mode(void) { return 0; }
int native_ufs_store_open(uint64_t, uint64_t *, const char **why) {
    if (why) *why = "enuma RAM root has no persistent store";
    return 0;
}
int native_ufs_store_read(uint64_t, uint32_t, void *) { return 0; }
int native_ufs_store_write(uint64_t, uint32_t, const void *) { return 0; }
int native_ufs_store_sync(void) { return 0; }
unsigned native_ufs_store_gpt_check(void) { return 0; }
}
