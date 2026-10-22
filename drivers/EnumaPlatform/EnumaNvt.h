// SPDX-License-Identifier: BSD-2-Clause-Patent
#ifndef ENUMA_NVT_H
#define ENUMA_NVT_H
#include <stddef.h>
#include <stdint.h>
#define ENUMA_NVT_CONTACTS 10u
#define ENUMA_NVT_TOUCH_BYTES 66u
#define ENUMA_NVT_PEN_BYTES 80u
enum enuma_nvt_status {
    ENUMA_NVT_OK = 0, ENUMA_NVT_ARGUMENT = -1, ENUMA_NVT_CHECKSUM = -2,
    ENUMA_NVT_MALFORMED = -3, ENUMA_NVT_ESD = -4, ENUMA_NVT_WATCHDOG = -5
};
struct enuma_nvt_contact { uint16_t x, y, pressure; uint8_t id, width; };
struct enuma_nvt_frame {
    unsigned count;
    struct enuma_nvt_contact contacts[ENUMA_NVT_CONTACTS];
};
// Canonical CTP_SPI_READ buffer: address at byte 0, payload at 1..65,
// optional pen extension at 66..79. Not the raw SPI wire response (one dummy).
// max_x/max_y are the inclusive FWINFO maxima, not inferred display geometry.
// On any error *out is unchanged. Caller must not publish the previous frame
// as a new sample. ESD/WDT require a separate controller recovery policy.
int enuma_nvt_decode(const uint8_t *packet, size_t bytes, unsigned max_x,
                     unsigned max_y, struct enuma_nvt_frame *out);
// Produce canonical bytes from a completed 67/81-byte SPI read. No I/O here.
int enuma_nvt_unwrap(const uint8_t *wire, size_t bytes, uint8_t *packet, size_t capacity);
// Inclusive sensor range -> the existing HID descriptor's 0..32767 range.
int enuma_nvt_normalize(unsigned value, unsigned maximum, uint16_t *out);
#endif
