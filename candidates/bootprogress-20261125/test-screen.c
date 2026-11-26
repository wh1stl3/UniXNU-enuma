// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "framebuffer.h"
#include <assert.h>
#include <stdbool.h>
#include <errno.h>
#include <string.h>

/* The included functions are copied unchanged from staged XNU sources by
 * test-generated.py. This fixture supplies platform and scheduler seams. */
#define __unused __attribute__((unused))
#define TRUE 1
#define FALSE 0
enum {
    kPETextScreen = 3, kPEAcquireScreen, kPEReleaseScreen, kPEEnableScreen,
    kPEDisableScreen,
};
typedef struct { int base; unsigned v_scale; } PE_Video;
typedef void (*enuma_screen_hook)(PE_Video *, unsigned int);
static struct { PE_Video video; } PE_state;
typedef struct { int dx, dy, width, height; unsigned char count; unsigned flags; } vc_progress_element;
static vc_progress_element default_progress;
static unsigned char default_progress_data1x[1], default_progress_data2x[1],
    default_progress_data3x[1], appleClut8[1];
static int vc_progress_initialized, init_count, release_count, acquire_count, route_count;
static int stock_count, stock_base, serial, gc_graphics_boot, gc_acquired;
static bool vm_initialized, waitable = true;
static bool panic_after_release;
static int interleave_apply, interleave_publish, interleaves;
static unsigned enuma_bp_mode;
static struct bp_gate enuma_bp_gate;
static struct bp_framebuffer enuma_bp_map;
static PE_Video c;

static struct { char msg_bufc[3]; long msg_bufx; } msg = {{'X', '\n', 0}, 3};
static typeof(msg) *msgbufp = &msg;
static char replay[8];
static int replayed, starts, enuma_bp_call, vc_progress_lock;
static unsigned arg_mode;
static bool arg_given;
enum { THREAD_CALL_PRIORITY_HIGH, THREAD_CALL_OPTIONS_ONCE };

static void simple_lock_init(int *lock, int group) { (void)lock; (void)group; }
static void simple_lock(int *lock, int group) { (void)lock; (void)group; }
static void simple_unlock(int *lock) { (void)lock; }
#define LCK_GRP_NULL 0

static bool PE_parse_boot_argn(const char *key, unsigned *out, size_t size)
{
    assert(strcmp(key, "boot-progress") == 0 && size == sizeof(*out));
    if (arg_given)
        *out = arg_mode;
    return arg_given;
}

static int enuma_bp_waitable(void) { return waitable; }
static void enuma_bp_wait(void *unused) { (void)unused; assert(!"unexpected synchronous wait"); }
static void enuma_bp_refresh(void *a, void *b) { (void)a; (void)b; }
static void thread_call_setup_with_options(int *call, void (*fn)(void *, void *),
    void *arg, int priority, int options)
{
    assert(call == &enuma_bp_call && fn == enuma_bp_refresh && !arg);
    assert(priority == THREAD_CALL_PRIORITY_HIGH && options == THREAD_CALL_OPTIONS_ONCE);
}
static void thread_call_enter(int *call) { assert(call == &enuma_bp_call); ++starts; }
static void vcputc(char byte) { assert(replayed < (int)sizeof(replay)); replay[replayed++] = byte; }

static void vc_progress_initialize(vc_progress_element *p, const unsigned char *a,
    const unsigned char *b, const unsigned char *cdata, unsigned char *clut)
{
    assert(enuma_bp_gate.state & BP_TRANSITION);
    assert(p == &default_progress && !p->dx && !p->dy);
    assert(a && b && cdata && clut);
    ++init_count;
}

int PE_initialize_console(PE_Video *, int);

static void try_c(void)
{
    int before = stock_count;
    assert((enuma_bp_gate.state & BP_TRANSITION) && c.v_scale == 77);
    assert(PE_initialize_console(&c, kPEEnableScreen) == EBUSY);
    assert(c.base == 3 && c.v_scale == 77 && stock_count == before);
    ++interleaves;
}

static int switch_to_serial_console(void)
{
    assert(enuma_bp_gate.state & BP_TRANSITION);
    ++route_count;
    serial = 1;
    return 19;
}
static void switch_to_old_console(int old)
{
    assert(enuma_bp_gate.state & BP_TRANSITION);
    assert(old == 19);
    ++route_count;
    serial = 0;
}
static void kprintf(const char *fmt, ...)
{
    assert(enuma_bp_gate.state & BP_TRANSITION);
    if (interleave_publish && strstr(fmt, "kPEEnableScreen")) {
        assert(PE_state.video.base == 2 && serial);
        try_c();
    }
}

static int enuma_bp_screen_apply(PE_Video *info, unsigned int op, bool stop, bool gui)
{
    assert(enuma_bp_gate.state & BP_TRANSITION);
    ++stock_count;
    if (info) {
        stock_base = info->base;
        assert(info->v_scale == PE_state.video.v_scale);
    }
    if (op == kPEEnableScreen && interleave_apply) {
        assert(PE_state.video.base == 1);
        try_c();
    }
    if (op == kPEReleaseScreen) {
        ++release_count;
        gc_acquired = false;
        if (panic_after_release)
            bp_panic(&enuma_bp_gate);
    } else if (op == kPEAcquireScreen) {
        ++acquire_count;
        gc_acquired = true;
    }
    return op == kPEReleaseScreen || op == kPEDisableScreen ? stop || gui :
        op == kPEAcquireScreen || op == kPEEnableScreen || op == kPETextScreen ? 0 : -1;
}

#include "bp-init.inc"
#include "screen.inc"
#include "pe.inc"

static struct {
    uintptr_t v_baseaddr;
    unsigned v_width, v_height, v_depth, v_rowbytes, v_rotate;
} vinfo;
enum { kVCUsePosition = 1, kDataRotate0 = 0, kDataRotate90, kDataRotate180, kDataRotate270 };
static struct { unsigned options, x_pos, y_pos; } vc_progress_options;
static vc_progress_element *vc_progress;
static const unsigned char *vc_progress_data[3], *vc_clut8, *vc_clut;
static unsigned char vc_revclut8[256];
static unsigned vc_progress_count, vc_progress_angle, vc_progress_interval;
static uint64_t vc_progress_deadline;
static int vc_progress_enable, vc_needsave, vc_progress_white, vc_uiscale, vc_progress_call;
static void *vc_saveunder;
static bool interleave_blit;
static int schedules;

struct enuma_bp_vc_lease { int counted; };
static int enuma_bp_vc_enter(void)
{
    int allowed = bp_console_begin(&enuma_bp_gate, 0);
    if (allowed && interleave_blit) {
        assert(bp_transition_begin(&enuma_bp_gate, 1));
        assert(enuma_bp_gate.state & BP_COUNT);
        interleave_blit = false;
    }
    return allowed;
}
static void enuma_bp_vc_end(struct enuma_bp_vc_lease *lease)
{
    if (lease->counted)
        bp_console_end(&enuma_bp_gate);
}
#define ENUMA_BP_VC_OR_RETURN(result) \
    struct enuma_bp_vc_lease bp_lease __attribute__((cleanup(enuma_bp_vc_end))) = {enuma_bp_vc_enter()}; \
    if (!bp_lease.counted) return result

static uint64_t mach_absolute_time(void) { return 2; }
static void clock_deadline_for_periodic_event(unsigned interval, uint64_t now, uint64_t *deadline)
{ *deadline = interval + now; }
static void thread_call_enter_delayed(int *call, uint64_t deadline)
{
    assert(call == &vc_progress_call && deadline == 3);
    assert(!(enuma_bp_gate.state & BP_COUNT));
    ++schedules;
}

#include "blit.inc"

static void reset(void)
{
    enuma_bp_gate = (struct bp_gate){0};
    enuma_bp_mode = 0;
    vm_initialized = false;
    gc_graphics_boot = false;
    gc_acquired = false;
    panic_after_release = false;
    release_count = acquire_count = replayed = starts = stock_count = 0;
}

static void test_pe(void)
{
    reset();
    vm_initialized = true;
    PE_state.video = (PE_Video){1, 2};
    PE_Video b = {2, 99};
    c = (PE_Video){3, 77};
    default_progress.dx = default_progress.dy = 89;
    assert(bp_transition_begin(&enuma_bp_gate, 1));
    assert(PE_initialize_console(&b, kPEReleaseScreen) == EBUSY);
    assert(!init_count && !vc_progress_initialized && !stock_count && !route_count);
    assert(default_progress.dx == 89 && default_progress.dy == 89 && b.v_scale == 99);
    assert(PE_state.video.base == 1);
    bp_transition_finish(&enuma_bp_gate, 0, 0, -1);
    assert(!PE_initialize_console(NULL, kPEReleaseScreen));
    assert(!PE_initialize_console(NULL, kPEReleaseScreen));
    assert(init_count == 1 && vc_progress_initialized && release_count == 2);

    assert(!PE_initialize_console(NULL, kPEDisableScreen) && serial);
    interleave_apply = interleave_publish = true;
    assert(!PE_initialize_console(&b, kPEEnableScreen));
    assert(interleaves == 2 && stock_base == 2 && PE_state.video.base == 2 && !serial);
    assert(b.v_scale == 2 && c.v_scale == 77 && route_count == 2);
    assert(!(enuma_bp_gate.state & BP_TRANSITION));
    interleave_apply = interleave_publish = false;
    assert(!PE_initialize_console(&c, kPEEnableScreen));
    assert(stock_base == 3 && PE_state.video.base == 3 && c.v_scale == 2);
}

static void test_attach(void)
{
    waitable = false; /* PE_init_iokit's boot context has IRQs masked. */
    reset();
    gc_acquired = true;
    assert(bp_transition_begin(&enuma_bp_gate, 1));
    vcattach();
    assert(vm_initialized && !release_count && !acquire_count && !replayed && !starts);
    initialize_screen(NULL, kPEAcquireScreen); /* startup void caller on busy */
    assert(!stock_count && !replayed && !starts);

    reset();
    gc_acquired = true;
    enuma_bp_mode = 2;
    panic_after_release = true;
    vcattach();
    assert(release_count == 1 && !acquire_count && !replayed && !starts);

    _Alignas(4) static unsigned char fbmem[256 * 128 * 4];
    struct bp_framebuffer fb = {fbmem, sizeof(fbmem), 256, 128, 1024};
    for (unsigned i = 0; i != 4; ++i) {
        reset();
        gc_acquired = true;
        arg_given = i != 0;
        arg_mode = i >= 2 ? 2 : 1;
        fb.mapped = sizeof(fbmem) - (i == 2);
        enuma_bp_initial_mapping(&fb, 1);
        vcattach();
        assert(release_count == 1 && acquire_count == 1 && gc_acquired);
        assert(replayed == 3 && !memcmp(replay, "X\n\r", 3));
        assert(starts == (i == 3));
    }
    waitable = true;
}

static void test_blit(void)
{
    reset();
    uint32_t pixels[] = {0x00223344, 0x00556677};
    uint32_t back[] = {0, 0};
    vc_progress_element progress = {.width = 2, .height = 1, .count = 4};
    static const unsigned char alpha[] = {128, 64, 128, 64, 128, 64, 128, 64};
    vinfo = (typeof(vinfo)){(uintptr_t)pixels, 2, 1, 32, sizeof(pixels), 0};
    vc_progress = &progress;
    vc_progress_data[0] = alpha;
    vc_uiscale = vc_progress_enable = vc_progress_interval = vc_needsave = 1;
    vc_saveunder = back;
    interleave_blit = true;
    vc_progress_task(NULL, NULL);
    assert((enuma_bp_gate.state & BP_TRANSITION) && !(enuma_bp_gate.state & BP_COUNT));
    assert(!vc_needsave && back[0] == 0x00223344 && back[1] == 0x00556677);
    assert(pixels[0] != back[0] && pixels[1] != back[1] && schedules == 1);
    bp_transition_finish(&enuma_bp_gate, 0, 0, -1); /* aborted conversion */
    vc_progress_task(NULL, NULL);
    assert(back[0] == 0x00223344 && back[1] == 0x00556677 && schedules == 2);
    vinfo.v_depth = 0;
    vc_needsave = 1;
    vc_progress_task(NULL, NULL);
    assert(vc_needsave && schedules == 3);
    vc_blit_rect(0, 0, 0, 2, 1, 2, 1, 2, 2, alpha, back, kSave);
}

int main(void)
{
    test_pe();
    test_attach();
    test_blit();
    return 0;
}
