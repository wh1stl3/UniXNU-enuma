// SPDX-License-Identifier: BSD-2-Clause-Patent
#ifndef ENUMA_ROOT_READ_H
#define ENUMA_ROOT_READ_H
#include "EnumaUfsRead.h"
#ifdef __cplusplus
extern "C" {
#endif
enum enuma_root_status { ENUMA_ROOT_OK, ENUMA_ROOT_ARGUMENT, ENUMA_ROOT_IO, ENUMA_ROOT_INTEGRITY };
struct enuma_root_result { uint32_t status; uint64_t done; };
struct enuma_root_ops {
    void *context;
    // Serializes the whole read/verify/copy snapshot, not just transport.
    void (*lock)(void *);
    void (*unlock)(void *);
    // Synchronous: success means exact bytes, checked OCS/UPIU/SCSI and CPU
    // cache synchronization. On uncertain DMA completion, quarantine buffers
    // in the transport and reject subsequent requests. No automatic retry.
    uint32_t (*read)(void *, const struct enuma_ufs_read *, void *);
    // Required policy callback, never an implicit "verified" default.
    uint32_t (*verify)(void *, uint64_t window_block, const void *, uint64_t);
    uint64_t (*copy)(void *, uint64_t request_offset, const void *, uint64_t);
};
// first/blocks are a validated 4KiB window within observed LUN geometry.
// sector/count are OS 512-byte units relative to that window. bounce is a
// caller-owned CPU buffer of >=128KiB, disjoint from destination and metadata.
// All arguments stay alive/immutable under caller serialization. Complete the
// IOKit request AFTER return (lock released), using truthful result.done.
struct enuma_root_result enuma_root_read(const struct enuma_ufs_geometry *,
    uint64_t first, uint64_t blocks, uint64_t sector, uint64_t count,
    void *bounce, uint32_t bounce_bytes, const struct enuma_root_ops *);
#ifdef __cplusplus
}
#endif
#endif
