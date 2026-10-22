// SPDX-License-Identifier: BSD-2-Clause-Patent
// Packet-format facts: pinned MiCode NT36523 sources in sources.json.
// Independent bounded decoder; no Linux input/SPI/firmware code included.
#include "EnumaNvt.h"

int enuma_nvt_unwrap(const uint8_t *wire, size_t bytes, uint8_t *packet, size_t capacity)
{
    if (!wire || !packet || (bytes != ENUMA_NVT_TOUCH_BYTES + 1 &&
        bytes != ENUMA_NVT_PEN_BYTES + 1) || capacity < bytes - 1)
        return ENUMA_NVT_ARGUMENT;
    // Forward copy permits in-place unwrapping: rx[2] -> canonical[1].
    packet[0] = 0;
    for (size_t i = 1; i < bytes - 1; ++i) packet[i] = wire[i + 1];
    return ENUMA_NVT_OK;
}

int enuma_nvt_normalize(unsigned value, unsigned maximum, uint16_t *out)
{
    if (!out || !maximum || maximum > 4095 || value > maximum) return ENUMA_NVT_ARGUMENT;
    *out = (uint16_t)((uint32_t)value * 32767u / maximum);
    return ENUMA_NVT_OK;
}

int enuma_nvt_decode(const uint8_t *packet, size_t bytes, unsigned max_x,
                     unsigned max_y, struct enuma_nvt_frame *out)
{
    if (!packet || !out || (bytes != ENUMA_NVT_TOUCH_BYTES && bytes != ENUMA_NVT_PEN_BYTES) ||
        !max_x || !max_y || max_x > 4095 || max_y > 4095) return ENUMA_NVT_ARGUMENT;
    unsigned esd = 1, watchdog = 1, sum = 0;
    for (unsigned i = 1; i <= 6; ++i) {
        esd &= packet[i] == 0x77;
        watchdog &= packet[i] == 0xfd || packet[i] == 0xfe;
    }
    if (esd) return ENUMA_NVT_ESD;
    if (watchdog) return ENUMA_NVT_WATCHDOG;
    for (unsigned i = 1; i < ENUMA_NVT_TOUCH_BYTES; ++i) sum += packet[i];
    if (sum & 255u) return ENUMA_NVT_CHECKSUM;
    struct enuma_nvt_frame result = {0};
    unsigned seen = 0;
    for (unsigned slot = 0; slot < ENUMA_NVT_CONTACTS; ++slot) {
        const uint8_t *record = packet + 1 + slot * 6;
        unsigned state = record[0] & 7u, id = record[0] >> 3;
        if (state != 1 && state != 2) continue;
        // Reject ambiguous active IDs/coordinates instead of delivering a
        // partial set whose missing contacts could be misreported as releases.
        if (!id || id > ENUMA_NVT_CONTACTS || (seen & (1u << id))) return ENUMA_NVT_MALFORMED;
        unsigned x = ((unsigned)record[1] << 4) | (record[3] >> 4);
        unsigned y = ((unsigned)record[2] << 4) | (record[3] & 15u);
        if (x > max_x || y > max_y) return ENUMA_NVT_MALFORMED;
        unsigned pressure = record[5];
        if (slot < 2) pressure |= (unsigned)packet[63 + slot] << 8;
        if (pressure > 1000) pressure = 1000;
        if (!pressure) pressure = 1;
        result.contacts[result.count++] = (struct enuma_nvt_contact){
            (uint16_t)x, (uint16_t)y, (uint16_t)pressure,
            (uint8_t)id, record[4] ? record[4] : 1
        };
        seen |= 1u << id;
    }
    *out = result;
    return ENUMA_NVT_OK;
}
