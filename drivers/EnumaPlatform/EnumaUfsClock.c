// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "EnumaUfsClock.h"

static const uint32_t offsets[ENUMA_UFS_CLOCK_COUNT] = {
    0x77010, 0x77018, 0x770cc, 0x7705c, 0x77064, 0x7709c, 0x7701c, 0x77020, 0x770b8
};

uint32_t enuma_ufs_clock_offset(enum enuma_ufs_clock clock)
{
    return (unsigned)clock < ENUMA_UFS_CLOCK_COUNT ? offsets[(unsigned)clock] : UINT32_MAX;
}

int enuma_ufs_read_clocks(enuma_gcc_read read, void *context, struct enuma_ufs_clock_snapshot *out)
{
    if (!read || !out) return -22;
    struct enuma_ufs_clock_snapshot sample;
    for (unsigned i = 0; i < ENUMA_UFS_CLOCK_COUNT; ++i) {
        int rc = read(context, offsets[i], &sample.value[i]);
        if (rc) return rc;
    }
    *out = sample;
    return 0;
}
