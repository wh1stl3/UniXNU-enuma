// SPDX-License-Identifier: BSD-2-Clause-Patent
#ifndef ENUMA_BP_FRAMEBUFFER_H
#define ENUMA_BP_FRAMEBUFFER_H

#include <stddef.h>
#include <stdint.h>

/* One word serializes admission and lease accounting. Permanent BP stop,
 * GUI ownership, and temporary conversion exclusion are independent. */
struct bp_gate {
    uint32_t state;
};

enum {
    BP_STOP = 1u << 31,
    BP_ACTIVE = 1u << 30,
    BP_WRITING = 1u << 29,
    BP_GUI = 1u << 28,
    BP_PANIC = 1u << 27,
    BP_TRANSITION = 1u << 26,
    BP_VC_PAUSED = 1u << 25,
    BP_COUNT = BP_VC_PAUSED - 1,
};

static inline int
bp_console_begin(struct bp_gate *gate, int transition_owner)
{
    uint32_t old = __atomic_load_n(&gate->state, __ATOMIC_RELAXED);
    do {
        if ((old & BP_GUI) || (old & BP_COUNT) == BP_COUNT)
            return 0;
        if (old & BP_TRANSITION) {
            if (!transition_owner || (old & (BP_WRITING | BP_PANIC)))
                return 0;
        } else if (old & (BP_ACTIVE | BP_VC_PAUSED)) {
            return 0;
        }
    } while (!__atomic_compare_exchange_n(&gate->state, &old, old + 1, 1,
        __ATOMIC_ACQUIRE, __ATOMIC_RELAXED));
    return 1;
}

static inline void
bp_console_end(struct bp_gate *gate)
{
    __atomic_fetch_sub(&gate->state, 1, __ATOMIC_RELEASE);
}

/* Close VC admission, then let the caller drain without holding any VC lock.
 * BP cannot draw until that drain is complete. */
static inline int
bp_take(struct bp_gate *gate)
{
    uint32_t old = __atomic_load_n(&gate->state, __ATOMIC_RELAXED);
    do {
        if (old & (BP_STOP | BP_ACTIVE | BP_GUI | BP_TRANSITION | BP_VC_PAUSED))
            return 0;
    } while (!__atomic_compare_exchange_n(&gate->state, &old,
        old | BP_ACTIVE, 1, __ATOMIC_ACQ_REL, __ATOMIC_RELAXED));
    return 1;
}

static inline int
bp_draw_begin(struct bp_gate *gate)
{
    uint32_t old = BP_ACTIVE;
    return __atomic_compare_exchange_n(&gate->state, &old,
        BP_ACTIVE | BP_WRITING, 0, __ATOMIC_ACQUIRE, __ATOMIC_RELAXED);
}

static inline void
bp_draw_end(struct bp_gate *gate)
{
    uint32_t old = __atomic_load_n(&gate->state, __ATOMIC_RELAXED);
    uint32_t next;
    do {
        next = old & ~BP_WRITING;
        if (old & BP_PANIC)
            next &= ~BP_ACTIVE;
    } while (!__atomic_compare_exchange_n(&gate->state, &old, next, 1,
        __ATOMIC_RELEASE, __ATOMIC_RELAXED));
}

/* Never wait in panic. A renderer row may finish, but neither panic nor the
 * row's exit can clear a transition or GUI owner. */
static inline void
bp_panic(struct bp_gate *gate)
{
    uint32_t old = __atomic_load_n(&gate->state, __ATOMIC_RELAXED);
    uint32_t next;
    do {
        next = old | BP_STOP | BP_PANIC;
        if (!(old & BP_WRITING))
            next &= ~BP_ACTIVE;
    } while (!__atomic_compare_exchange_n(&gate->state, &old, next, 1,
        __ATOMIC_ACQ_REL, __ATOMIC_RELAXED));
}

/* A caller unable to wait cannot reserve a transition with live leases.
 * On failure it leaves all state unchanged. */
static inline int
bp_transition_begin(struct bp_gate *gate, int can_wait)
{
    uint32_t old = __atomic_load_n(&gate->state, __ATOMIC_RELAXED);
    do {
        if (old & (BP_GUI | BP_TRANSITION | BP_PANIC))
            return 0;
        if (!can_wait && (old & (BP_WRITING | BP_COUNT)))
            return 0;
    } while (!__atomic_compare_exchange_n(&gate->state, &old,
        old | BP_TRANSITION, 1, __ATOMIC_ACQ_REL, __ATOMIC_RELAXED));
    return 1;
}

enum { BP_GUI_REFUSED, BP_GUI_PENDING, BP_GUI_OWNED };

static inline int
bp_gui_begin(struct bp_gate *gate, int can_wait)
{
    if (!can_wait)
        return BP_GUI_REFUSED;
    uint32_t state = __atomic_load_n(&gate->state, __ATOMIC_ACQUIRE);
    if (state & BP_PANIC)
        return BP_GUI_REFUSED;
    if (state & BP_GUI)
        return BP_GUI_OWNED;
    return bp_transition_begin(gate, 1) ? BP_GUI_PENDING : BP_GUI_REFUSED;
}

static inline void
bp_transition_drain(struct bp_gate *gate, void (*wait)(void *), void *arg)
{
    while (__atomic_load_n(&gate->state, __ATOMIC_ACQUIRE) & (BP_WRITING | BP_COUNT))
        wait(arg);
}

/* vc_paused < 0 preserves the previous console state on cancellation. */
static inline void
bp_transition_finish(struct bp_gate *gate, int stop_bp, int gui, int vc_paused)
{
    uint32_t old = __atomic_load_n(&gate->state, __ATOMIC_RELAXED);
    uint32_t next;
    do {
        next = old & ~BP_TRANSITION;
        if (stop_bp || gui)
            next = (next | BP_STOP) & ~BP_ACTIVE;
        if (gui)
            next |= BP_GUI;
        if (vc_paused >= 0)
            next = vc_paused ? next | BP_VC_PAUSED : next & ~BP_VC_PAUSED;
    } while (!__atomic_compare_exchange_n(&gate->state, &old, next, 1,
        __ATOMIC_RELEASE, __ATOMIC_RELAXED));
}

struct bp_framebuffer {
    volatile unsigned char *base;
    size_t mapped;
    unsigned width, height, stride;
};

/* Map pitch is in bytes. Do not derive mapped capacity from mode geometry. */
static inline int
bp_framebuffer_valid(const struct bp_framebuffer *fb, int verified_bgrx)
{
    return verified_bgrx && fb->base && !((uintptr_t)fb->base & 3) &&
        fb->width >= 256 && fb->width <= 4096 && fb->height >= 128 && fb->height <= 4096 &&
        !(fb->stride & 3) && fb->width <= fb->stride / 4 &&
        fb->height <= fb->mapped / fb->stride &&
        fb->mapped <= UINTPTR_MAX - (uintptr_t)fb->base;
}

static inline int
bp_selected(unsigned mode, const struct bp_framebuffer *fb, int verified_bgrx)
{
    return mode == 2 && bp_framebuffer_valid(fb, verified_bgrx);
}

/* Only call with an admitted BP pixel writer and a validated framebuffer.
 * Write all visible pixels in the row; never touch pitch padding or the
 * reserved bytes beyond the last row. Colors are expressed as 0xRRGGBB. */
static inline void
bp_paint_row(const struct bp_framebuffer *fb, unsigned y,
    unsigned bar_pixels, uint32_t background, uint32_t foreground)
{
    volatile unsigned char *row = fb->base + (size_t)y * fb->stride;
    for (unsigned x = 0; x < fb->width; ++x, row += 4) {
        uint32_t color = x < bar_pixels ? foreground : background;
        row[0] = (unsigned char)color;
        row[1] = (unsigned char)(color >> 8);
        row[2] = (unsigned char)(color >> 16);
        row[3] = 0;
    }
}
#endif
