// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "EnumaGeniSpi.h"

int enuma_spi_open(struct enuma_spi *out, struct geni_io se, struct geni_io wrapper,
                   unsigned source_hz, unsigned selector, unsigned speed_hz,
                   unsigned poll_limit)
{
    if (!out) return GENI_ERR_PARAM;
    *out = (struct enuma_spi){0};
    if (!se.rd || !se.wr || !wrapper.rd || !source_hz || selector > 7 ||
        !speed_hz || speed_hz > ENUMA_TOUCH_MAX_HZ || !poll_limit || poll_limit > 1000000)
        return GENI_ERR_PARAM;
    out->engine.se = se;
    out->engine.wrapper = wrapper;
    out->engine.poll_limit = poll_limit;
    out->engine.poll_only = 1;
    int rc = geni_spi_read_info(&out->engine);
    if (rc) return rc;
    if (out->engine.info.geni_status & GENI_STATUS_M_ACTIVE) return GENI_ERR_NOTSUP;
    if (out->engine.info.fifo_disabled) return GENI_ERR_NOTSUP;
    // Check the divider before init performs any writes. Same oversampling
    // rule as the pinned generic driver (QUP v1.0 uses a factor of two).
    unsigned version = out->engine.info.qup_hw_version;
    unsigned os = ((version >> 28) == 1 && ((version >> 16) & 0xfff) == 0) ? 2 : 1;
    unsigned long long denom = (unsigned long long)os * speed_hz;
    unsigned long long divider = ((unsigned long long)source_hz + denom - 1) / denom;
    if (!divider || divider > GENI_CLK_DIV_MAX) return GENI_ERR_PARAM;
    rc = geni_spi_init(&out->engine);
    if (rc) return rc;
    // Force actual mode-0/CS0 programming; the inherited hardware state may
    // differ from the generic driver's zero-initialized software cache.
    out->engine.last_mode = ~0u;
    out->engine.last_cs = -1;
    rc = geni_spi_setup(&out->engine, 0, 0);
    if (rc) return rc;
    rc = geni_spi_set_clock(&out->engine, speed_hz, source_hz, selector);
    if (!rc) out->ready = 1;
    return rc;
}

int enuma_spi_transfer(struct enuma_spi *port, const uint8_t *tx, uint8_t *rx, size_t bytes)
{
    if (!port || !port->ready) return GENI_ERR_NODEV;
    if ((!tx && !rx) || !bytes || bytes > ENUMA_TOUCH_MAX_TRANSFER) return GENI_ERR_PARAM;
    int rc = geni_spi_transfer(&port->engine, tx, rx, bytes, 0);
    // A failed transaction requires caller review/reinitialization; do not
    // keep emitting packets after a timeout or controller fault.
    if (rc) port->ready = 0;
    return rc;
}
