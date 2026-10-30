// SPDX-License-Identifier: BSD-2-Clause-Patent
#ifndef ENUMA_ROOT_TRANSPORT_H
#define ENUMA_ROOT_TRANSPORT_H
#include "EnumaRootRead.h"
// Caller holds the root snapshot lock. read4k must be the qualified native
// hostRead4k path, with its own transport lock, cache and quarantine handling.
// Distinct lock order: root snapshot -> native host. Never reverse it.
// Geometry/window remain immutable for the lifetime of the published root.
struct enuma_root_transport {
    struct enuma_ufs_geometry geometry;
    uint64_t first, blocks;
    void *host;
    uint32_t (*read4k)(void *, uint8_t, uint64_t, uint32_t, void *);
    uint32_t native_status; // Exact last backend status, not an IOReturn cast.
};
#ifdef __cplusplus
extern "C" {
#endif
uint32_t enuma_root_transport_read(void *, const struct enuma_ufs_read *, void *);
#ifdef __cplusplus
}
#endif
#endif
