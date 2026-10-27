// SPDX-License-Identifier: BSD-2-Clause-Patent
#ifndef ENUMA_RAM_DISK_H
#define ENUMA_RAM_DISK_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
enum enuma_ram_status { ENUMA_RAM_OK, ENUMA_RAM_ARGUMENT, ENUMA_RAM_OFFLINE,
    ENUMA_RAM_MEMORY, ENUMA_RAM_IO, ENUMA_RAM_BUSY };
struct enuma_ram_result { uint32_t status; uint64_t done; };
struct enuma_ram_ops {
    void *context;
    // External gate outlives disk, start, all I/O and stop; serializes all of
    // them. Callbacks must not reenter. Allocate returns distinct owned memory
    // aligned for pointers; implementation zeroes it before use.
    void (*lock)(void *);
    void (*unlock)(void *);
    void *(*allocate)(void *, uint64_t);
    void (*release)(void *, void *, uint64_t);
};
// Caller zero-initializes once before publication, then keeps ops immutable.
// Stop safely rejects later I/O; caller drains invocations before freeing this
// structure/gate. No pointer may be retained by transfer after it returns.
struct enuma_ram_disk { const struct enuma_ram_ops *ops; void *implementation; };
struct enuma_ram_info { uint64_t logical_bytes, resident_bytes, page_table_bytes, budget_bytes; };
uint32_t enuma_ram_start(struct enuma_ram_disk *,const void *packed,uint64_t bytes,uint64_t resident_budget);
uint32_t enuma_ram_info(struct enuma_ram_disk *,struct enuma_ram_info *);
// transfer returns actual bytes <= requested. For write it copies INTO page;
// for read it copies OUT. Request offsets are relative to caller descriptor.
// Any completion callback belongs AFTER return, outside the gate. Short writes
// may modify a prefix and report it; caller must not claim atomic disk writes.
struct enuma_ram_result enuma_ram_io(struct enuma_ram_disk *,int write,uint64_t sector,uint64_t count,
    uint64_t descriptor_bytes,void *request,uint64_t (*transfer)(void *,uint64_t,void *,uint64_t));
uint32_t enuma_ram_stop(struct enuma_ram_disk *);
#ifdef __cplusplus
}
#endif
#endif
