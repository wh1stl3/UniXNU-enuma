// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "framebuffer.h"
#include <assert.h>
#include <pthread.h>
#include <sched.h>
#include <stdatomic.h>
#include <string.h>
#ifdef ENUMA_BP_LEGACY_LAYOUT
#include "NativeLegacyRequest.h"
#endif

static struct bp_gate gate;
static atomic_int awaiting_drain, finished;
static _Alignas(8) unsigned char a[128][1032], b[128][1032];
static unsigned char *mapping = &a[0][0];

static void
waiting(void *unused)
{
    (void)unused;
    atomic_store(&awaiting_drain, 1);
    sched_yield();
}

static void *
remap(void *unused)
{
    (void)unused;
    assert(bp_transition_begin(&gate, 1));
    bp_transition_drain(&gate, waiting, NULL);
    mapping = &b[0][0];
    bp_transition_finish(&gate, 1, 0, 0);
    atomic_store(&finished, 1);
    return NULL;
}

/* Host fixture for the production sequence: no GUI admission call occurs
 * until context, source map and layout validate; serial is not a predicate. */
static int
present(int serial, int map_ok, int layout_ok, int context_ok)
{
    (void)serial;
    if (!context_ok || !map_ok)
        return 0;
#ifdef ENUMA_BP_LEGACY_LAYOUT
    if (!native_legacy_copy_layout(mapping, sizeof(a), sizeof(a[0]), b,
        sizeof(b) - !layout_ok, sizeof(b[0]), 256, 128))
        return 0;
#else
    if (!layout_ok)
        return 0;
#endif
    int state = bp_gui_begin(&gate, context_ok);
    if (state == BP_GUI_REFUSED)
        return 0;
    if (state == BP_GUI_PENDING) {
        bp_transition_drain(&gate, waiting, NULL);
        bp_transition_finish(&gate, 1, 1, 1);
    }
#ifdef ENUMA_BP_LEGACY_LAYOUT
    b[0][0] = 0x71;
    assert(native_legacy_copy_pixels(mapping, sizeof(a), sizeof(a[0]), b,
        sizeof(b), sizeof(b[0]), 256, 128));
#else
    mapping[0] = 0x71;  /* first pixel store, not a console-output flag */
#endif
    return 1;
}

static void *
gui(void *unused)
{
    (void)unused;
    assert(present(1, 1, 1, 1));
    atomic_store(&finished, 1);
    return NULL;
}

static void
wait_for_drain(void)
{
    while (!atomic_load(&awaiting_drain))
        sched_yield();
    assert(!atomic_load(&finished));
}

static void
reset(void)
{
    gate = (struct bp_gate){0};
    atomic_store(&awaiting_drain, 0);
    atomic_store(&finished, 0);
    mapping = &a[0][0];
}

int
main(void)
{
    /* A/B plus geometry rejection and BGR byte order. */
    memset(a, 0xab, sizeof(a));
    struct bp_framebuffer fb = { &a[0][0], sizeof(a), 256, 128, 1032 };
    assert(!bp_selected(0, &fb, 1) && !bp_selected(1, &fb, 1));
    assert(!bp_selected(2, &fb, 0));
    --fb.mapped;
    assert(!bp_selected(2, &fb, 1));
    ++fb.mapped;
    assert(bp_selected(2, &fb, 1));
    assert(bp_console_begin(&gate, 0) && !bp_draw_begin(&gate) && a[0][0] == 0xab);
    assert(bp_take(&gate));
    assert(!bp_console_begin(&gate, 0) && !bp_draw_begin(&gate));
    bp_console_end(&gate);
    assert(bp_draw_begin(&gate) && !bp_draw_begin(&gate));
    for (unsigned y = 0; y < fb.height; ++y)
        bp_paint_row(&fb, y, 1, 0x112233, 0x445566);
    for (unsigned y = 0; y < fb.height; ++y) {
        assert(!memcmp(a[y], "\x66\x55\x44\x00\x33\x22\x11\x00", 8));
        for (unsigned x = 1024; x < 1032; ++x)
            assert(a[y][x] == 0xab);
    }

    /* Valid first frame drains BP despite serial output. Invalid submission
     * attempts do not even mark a pending transition. */
    uint32_t state = __atomic_load_n(&gate.state, __ATOMIC_RELAXED);
    assert(!present(1, 0, 1, 1) && !present(1, 1, 0, 1) && !present(1, 1, 1, 0));
    assert(bp_gui_begin(&gate, 0) == BP_GUI_REFUSED);
    assert(__atomic_load_n(&gate.state, __ATOMIC_RELAXED) == state);
    pthread_t worker;
    assert(!pthread_create(&worker, NULL, gui, NULL));
    wait_for_drain();
    assert(!bp_console_begin(&gate, 0) && !bp_draw_begin(&gate));
    assert(a[0][0] == 0x66);
    bp_draw_end(&gate);
    assert(!pthread_join(worker, NULL) && a[0][0] == 0x71);
    bp_panic(&gate);
    assert(!bp_take(&gate) && !bp_console_begin(&gate, 0));

    /* Simulated IRQ interrupts its own VC lease on A. It must return without
     * reserving anything. A thread then closes admission and waits for A. */
    reset();
    assert(bp_console_begin(&gate, 0));
    assert(!bp_transition_begin(&gate, 0));
    assert(!(gate.state & BP_TRANSITION) && mapping == &a[0][0]);
    assert(!pthread_create(&worker, NULL, remap, NULL));
    wait_for_drain();
    assert(!bp_console_begin(&gate, 0) && !bp_draw_begin(&gate));
    assert(mapping == &a[0][0]);
    mapping[0] = 0x31;
    bp_console_end(&gate);
    assert(!pthread_join(worker, NULL) && mapping == &b[0][0]);
    assert(bp_console_begin(&gate, 0) && !bp_take(&gate));
    mapping[0] = 0x32;
    bp_console_end(&gate);
    assert(a[0][0] == 0x31 && b[0][0] == 0x32);

    /* Panic before a row, within a row, and during a transition. */
    reset();
    assert(bp_take(&gate));
    bp_panic(&gate);
    assert(!bp_draw_begin(&gate) && bp_console_begin(&gate, 0));
    bp_console_end(&gate);
    reset();
    assert(bp_take(&gate) && bp_draw_begin(&gate));
    bp_panic(&gate);
    assert(!bp_console_begin(&gate, 0));
    bp_draw_end(&gate);
    assert(bp_console_begin(&gate, 0) && !bp_take(&gate));
    bp_console_end(&gate);
    reset();
    assert(bp_take(&gate) && bp_draw_begin(&gate));
    assert(bp_transition_begin(&gate, 1));
    bp_panic(&gate);
    bp_draw_end(&gate);
    assert(!bp_console_begin(&gate, 0) && !bp_console_begin(&gate, 1));
    bp_transition_finish(&gate, 1, 0, 0);
    assert(bp_console_begin(&gate, 0) && !bp_take(&gate));
    bp_console_end(&gate);

    reset();
    assert(bp_transition_begin(&gate, 0));
    bp_transition_finish(&gate, 0, 0, 1); /* internal vcattach release */
    assert(bp_transition_begin(&gate, 0));
    assert(bp_console_begin(&gate, 1) && !bp_console_begin(&gate, 0));
    bp_console_end(&gate);
    bp_transition_finish(&gate, 0, 0, 0); /* stock acquire */
    assert(bp_take(&gate));
#ifdef ENUMA_BP_LEGACY_LAYOUT
    assert(!native_legacy_fill_layout(b, sizeof(b) - 1, sizeof(b[0]), 256, 128));
    assert(!native_legacy_copy_layout(a, sizeof(a), sizeof(a[0]), NULL,
        sizeof(b), sizeof(b[0]), 256, 128));
    assert(!native_legacy_copy_layout(a, sizeof(a), sizeof(a[0]), &b[0][0],
        sizeof(b) - 1, sizeof(b[0]), 256, 128));
    assert(native_legacy_fill_pixels(b, sizeof(b), sizeof(b[0]), 256, 128, 0xff000000));
    _Alignas(8) static unsigned char shadow[128][1024];
    assert(native_legacy_copy_diff(a, sizeof(a), sizeof(a[0]), b, sizeof(b),
        sizeof(b[0]), 256, 128, shadow, 0) == sizeof(shadow));
#endif
    return 0;
}
