// SPDX-License-Identifier: BSD-2-Clause-Patent
// Reuse the upstream GENI register model, including its complete test suite.
#define main upstream_geni_tests
#include GENI_TEST_SOURCE
#undef main
#include "EnumaGeniSpi.h"

static unsigned observed_writes;
static void counted_write(void *ctx, uint32_t reg, uint32_t value) {
    ++observed_writes;
    se_wr(ctx, reg, value);
}
static void delay(void *ctx, unsigned us) { (void)ctx; (void)us; }

int main(void) {
    CHECK(upstream_geni_tests() == 0);
    struct sim model; struct geni_spi generic; struct enuma_spi port;
    make(&model, &generic);
    struct geni_io se = {&model, se_rd, counted_write, delay};
    struct geni_io wrapper = {&model, wr_rd, wr_wr, delay};
    // Force nondefault hardware state, then require the adapter to program it.
    model.reg[SE_SPI_CPHA/4] = 1; model.reg[SE_SPI_CPOL/4] = 4;
    model.reg[SE_SPI_DEMUX_SEL/4] = 7; model.reg[SE_SPI_DEMUX_OUTPUT_INV/4] = 1;
    CHECK(enuma_spi_open(&port, se, wrapper, 19200000, 0, 19200000, 100) == 0);
    CHECK(model.reg[SE_SPI_CPHA/4] == 0 && model.reg[SE_SPI_CPOL/4] == 0);
    CHECK(model.reg[SE_SPI_DEMUX_SEL/4] == 0 && model.reg[SE_SPI_DEMUX_OUTPUT_INV/4] == 0);
    uint8_t tx[66], rx[66]; fill(tx, sizeof tx, 13);
    CHECK(enuma_spi_transfer(&port, tx, rx, sizeof tx) == 0);
    for (size_t i=0; i<sizeof rx; ++i) CHECK(rx[i] == slave(tx[i], i));
    CHECK(!port.engine.use_dma && model.reg[SE_IRQ_EN/4] == 0);
    CHECK(enuma_spi_transfer(&port, tx, rx, ENUMA_TOUCH_MAX_TRANSFER+1) == GENI_ERR_PARAM);
    model.stuck = 1;
    CHECK(enuma_spi_transfer(&port, tx, rx, sizeof tx) == GENI_ERR_TIMEOUT);
    CHECK(!port.ready && enuma_spi_transfer(&port, tx, rx, sizeof tx) == GENI_ERR_NODEV);
    make(&model, &generic); observed_writes = 0; model.if_disable = 1;
    CHECK(enuma_spi_open(&port, se, wrapper, 19200000, 0, 1000000, 100) == GENI_ERR_NOTSUP);
    CHECK(observed_writes == 0 && !port.ready);
    make(&model, &generic); model.reg[SE_GENI_STATUS/4] = GENI_STATUS_M_ACTIVE;
    CHECK(enuma_spi_open(&port, se, wrapper, 19200000, 0, 1000000, 100) == GENI_ERR_NOTSUP);
    CHECK(observed_writes == 0);
    make(&model, &generic); model.fw_rev = 0;
    CHECK(enuma_spi_open(&port, se, wrapper, 19200000, 0, 1000000, 100) == GENI_ERR_PROTO);
    CHECK(observed_writes == 0);
    make(&model, &generic);
    CHECK(enuma_spi_open(&port, se, wrapper, 19200000, 0, 19200001, 100) == GENI_ERR_PARAM);
    CHECK(enuma_spi_open(&port, se, wrapper, 19200000, 0, 1, 100) == GENI_ERR_PARAM);
    CHECK(enuma_spi_open(&port, se, wrapper, 0, 0, 1000000, 100) == GENI_ERR_PARAM);
    CHECK(enuma_spi_open(&port, se, wrapper, 19200000, 8, 1000000, 100) == GENI_ERR_PARAM);
    CHECK(observed_writes == 0);
    puts("PASS: enuma FIFO transport, actual mode programming, rejection before writes, timeout invalidation");
    return 0;
}
