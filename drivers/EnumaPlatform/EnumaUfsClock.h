// SPDX-License-Identifier: BSD-2-Clause-Patent
// Register facts from MiCode gcc-kona.c at 52a2f180; see sources.json.
// Clock observation only: no clock writes, UFS HC reads, DMA or storage I/O.
#ifndef ENUMA_UFS_CLOCK_H
#define ENUMA_UFS_CLOCK_H
#include <stdint.h>

#define ENUMA_GCC_PA 0x00100000ULL
#define ENUMA_UFS_HC_PA 0x01d84000ULL
#define ENUMA_UFS_PHY_PA 0x01d87000ULL
#define ENUMA_UFS_CLOCK_COUNT 9u

enum enuma_ufs_clock {
    ENUMA_UFS_AXI, ENUMA_UFS_AHB, ENUMA_UFS_AGGRE, ENUMA_UFS_UNIPRO,
    ENUMA_UFS_ICE, ENUMA_UFS_AUX, ENUMA_UFS_TX0, ENUMA_UFS_RX0, ENUMA_UFS_RX1
};
struct enuma_ufs_clock_snapshot { uint32_t value[ENUMA_UFS_CLOCK_COUNT]; };
typedef int (*enuma_gcc_read)(void *context, uint32_t gcc_offset, uint32_t *value);
uint32_t enuma_ufs_clock_offset(enum enuma_ufs_clock clock);
// On callback failure out is untouched, so partial samples cannot be mistaken
// for a complete power/clock state. This API has no write callback.
int enuma_ufs_read_clocks(enuma_gcc_read read, void *context, struct enuma_ufs_clock_snapshot *out);
#endif
