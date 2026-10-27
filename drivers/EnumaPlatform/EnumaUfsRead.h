// SPDX-License-Identifier: BSD-2-Clause-Patent
// READ CAPACITY(10)/READ(10) request preparation only. No disk-write API.
#ifndef ENUMA_UFS_READ_H
#define ENUMA_UFS_READ_H
#include <stdint.h>
struct enuma_ufs_geometry { uint64_t blocks;uint32_t block_bytes;uint8_t lun; };
struct enuma_ufs_read { uint8_t cdb[10],lun;uint32_t bytes; };
// 0xffffffff is the protocol's capacity16 sentinel, never a real geometry.
int enuma_ufs_capacity10(const uint8_t *,unsigned,uint8_t,struct enuma_ufs_geometry *);
// window_first/count are verified root-window extents on the actual LUN.
// A false return leaves the command unchanged, so no partial request is sent.
int enuma_ufs_prepare_read(const struct enuma_ufs_geometry *,uint64_t window_first,
    uint64_t window_blocks,uint64_t relative_lba,uint32_t blocks,uint32_t dma_bytes,
    struct enuma_ufs_read *);
#endif
