// SPDX-License-Identifier: BSD-2-Clause-Patent
// Enuma transport adapter around the pinned UniXNU NativeGeniSpi implementation.
#ifndef ENUMA_GENI_SPI_H
#define ENUMA_GENI_SPI_H
#include "GeniSpi.h"

#define ENUMA_TOUCH_SE_PA 0x00990000ULL
#define ENUMA_TOUCH_SE_BYTES 0x4000u
#define ENUMA_TOUCH_WRAPPER_PA 0x009c0000ULL
#define ENUMA_TOUCH_WRAPPER_BYTES 0x2000u
#define ENUMA_TOUCH_MAX_HZ 19200000u
#define ENUMA_TOUCH_MAX_TRANSFER 4096u

struct enuma_spi {
    struct geni_spi engine;
    int ready;
};

// Caller supplies mapped, ordered callbacks after arranging clocks, pinmux and
// exclusive engine ownership. This function does not program GCC/TLMM/SMMU.
// source_hz and selector must describe a measured/qualified clock source.
// FIFO-disabled engines are rejected; DMA is deliberately not configured.
int enuma_spi_open(struct enuma_spi *out, struct geni_io se, struct geni_io wrapper,
                   unsigned source_hz, unsigned selector, unsigned speed_hz,
                   unsigned poll_limit);
int enuma_spi_transfer(struct enuma_spi *port, const uint8_t *tx, uint8_t *rx, size_t bytes);
#endif
