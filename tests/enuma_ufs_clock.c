// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "EnumaUfsClock.h"
struct model { unsigned count; unsigned fail; };
static int read_gcc(void *ctx, uint32_t reg, uint32_t *value) {
    struct model *m = ctx;
    assert(reg >= 0x77000 && reg < 0x78000 && !(reg & 3));
    if (++m->count == m->fail) return -5;
    *value = reg ^ 0xa5a5a5a5;
    return 0;
}
int main(void) {
    struct enuma_ufs_clock_snapshot before, sample;
    memset(&before, 0x5a, sizeof before);
    for (unsigned fail = 1; fail <= ENUMA_UFS_CLOCK_COUNT; ++fail) {
        struct model m = {0, fail}; sample = before;
        assert(enuma_ufs_read_clocks(read_gcc, &m, &sample) == -5);
        assert(m.count == fail && memcmp(&sample, &before, sizeof sample) == 0);
    }
    struct model m = {0, 0};
    assert(enuma_ufs_read_clocks(read_gcc, &m, &sample) == 0 && m.count == ENUMA_UFS_CLOCK_COUNT);
    assert(enuma_ufs_read_clocks(0, &m, &sample) == -22);
    assert(enuma_ufs_read_clocks(read_gcc, &m, 0) == -22);
    assert(enuma_ufs_clock_offset((enum enuma_ufs_clock)-1) == UINT32_MAX);
    puts("PASS: nine GCC observations, each read failure preserves output, no HC/DMA/write interface");
    return 0;
}
