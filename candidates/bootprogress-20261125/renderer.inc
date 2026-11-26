// SPDX-License-Identifier: BSD-2-Clause-Patent
// Full-screen layout and differential refresh adapted from the design of
// UniXNU/UniXNU-sheng@c8f92b2:package/BootProgressDisplay.h (MIT).
// Font: existing XNU iso_font in this translation unit, not a copied asset.
#include "framebuffer.h"
#include <arm/cpu_data.h>
#include <machine/machine_routines.h>
#include <sys/errno.h>

static struct bp_gate enuma_bp_gate;
static struct bp_framebuffer enuma_bp_map;
static thread_call_data_t enuma_bp_call;
static unsigned enuma_bp_mode, enuma_bp_stage;
static thread_t enuma_bp_vc_owner;

struct enuma_bp_vc_lease { int counted; };
static void
enuma_bp_vc_end(struct enuma_bp_vc_lease *lease)
{
	if (lease->counted) {
		__asm__ volatile("dsb st" ::: "memory");
		bp_console_end(&enuma_bp_gate);
	}
}
static int
enuma_bp_vc_enter(void)
{
	thread_t owner = __atomic_load_n(&enuma_bp_vc_owner, __ATOMIC_ACQUIRE);
	return bp_console_begin(&enuma_bp_gate, owner && !ml_at_interrupt_context() &&
	    owner == current_thread());
}
#define ENUMA_BP_VC_OR_RETURN(result)                                         \
	struct enuma_bp_vc_lease bp_lease __attribute__((cleanup(enuma_bp_vc_end))) = {enuma_bp_vc_enter()}; \
	if (!bp_lease.counted)                                                   \
		return result

/* Used only before VC starts, so no uncounted boot VC operation can span
 * subsequent transfer of ownership. The caller supplies the mapping length
 * from ml_io_map_unmappable, not width*height or the GOP allocation alone. */
static void
enuma_bp_initial_mapping(const struct bp_framebuffer *fb, int verified_bgrx)
{
	unsigned mode = 0;
	if (PE_parse_boot_argn("boot-progress", &mode, sizeof(mode)) &&
	    bp_selected(mode, fb, verified_bgrx)) {
		enuma_bp_map = *fb;
		__atomic_store_n(&enuma_bp_mode, 2, __ATOMIC_RELEASE);
	}
}

static int
enuma_bp_waitable(void)
{
	return ml_get_interrupts_enabled() && !ml_at_interrupt_context() &&
	    get_preemption_level() == 0;
}

extern bool enuma_bp_scanout_context(void);
bool
enuma_bp_scanout_context(void)
{
	return enuma_bp_waitable() &&
	    !(__atomic_load_n(&enuma_bp_gate.state, __ATOMIC_ACQUIRE) & BP_PANIC);
}

/* Called before either console lock is acquired. Lease bodies themselves
 * do not wait for a transition or acquire any additional locks on ARM iOS.
 * A timed scheduler wait lets an interrupted/preempted writer complete. */
static void
enuma_bp_wait(void *unused __unused)
{
	if (assert_wait_timeout((event_t)&enuma_bp_gate, THREAD_UNINT, 1, NSEC_PER_MSEC) == THREAD_WAITING)
		thread_block(THREAD_CONTINUE_NULL);
}

extern void enuma_bp_panic(void);
void
enuma_bp_panic(void)
{
	bp_panic(&enuma_bp_gate);
}

extern void enuma_bp_checkpoint(unsigned stage);
void
enuma_bp_checkpoint(unsigned stage)
{
	__atomic_store_n(&enuma_bp_stage, stage, __ATOMIC_RELAXED);
}

static void
enuma_bp_glyph_row(unsigned y, unsigned top, unsigned scale, const char *text, unsigned color)
{
	const struct bp_framebuffer *fb = &enuma_bp_map;
	unsigned gy = (y - top) / scale;
	unsigned cell = 8 * scale;
	unsigned count = (unsigned)strlen(text);
	if (count > fb->width / cell)
		count = fb->width / cell;
	unsigned left = (fb->width - count * cell) / 2;
	volatile unsigned char *row = fb->base + (size_t)y * fb->stride;
	for (unsigned i = 0; i < count; ++i) {
		unsigned bits = iso_font[(unsigned char)text[i] * 16 + gy];
		for (unsigned x = 0; x < cell; ++x) {
			if (!(bits & (1u << (x / scale))))
				continue;
			volatile unsigned char *pixel = row + 4 * (left + cell * i + x);
			pixel[0] = (unsigned char)color;
			pixel[1] = (unsigned char)(color >> 8);
			pixel[2] = (unsigned char)(color >> 16);
		}
	}
}

static void
enuma_bp_refresh(void *a __unused, void *b __unused)
{
	static unsigned previous;
	static int painted;
	const struct bp_framebuffer *fb = &enuma_bp_map;
	unsigned stage = __atomic_load_n(&enuma_bp_stage, __ATOMIC_RELAXED);
	uint32_t state = __atomic_load_n(&enuma_bp_gate.state, __ATOMIC_ACQUIRE);
	if (state & BP_STOP)
		return;
	if (!(state & (BP_COUNT | BP_TRANSITION)) && (!painted || stage != previous)) {
		unsigned scale = fb->width >= 1024 && fb->height >= 512 ? 4 : 2;
		unsigned title_top = (fb->height - 52 * scale) / 2;
		unsigned stage_top = title_top + 20 * scale;
		unsigned bar_top = stage_top + 24 * scale;
		unsigned bar_end = bar_top + 6 * scale;
		unsigned end = painted ? bar_end : fb->height;
		for (unsigned y = painted ? stage_top : 0; y < end; ++y) {
			/* Keep the writer unpreemptible for at most one raster row.
			 * An interrupt-context revoke cannot wait on its own row. */
			boolean_t ints = ml_set_interrupts_enabled(FALSE);
			if (!bp_draw_begin(&enuma_bp_gate)) {
				ml_set_interrupts_enabled(ints);
				goto schedule;
			}
			unsigned bar = y >= bar_top && y < bar_end ? (fb->width / 3) * (stage + 1) : 0;
			bp_paint_row(fb, y, bar, 0x131c29, 0x54c1ed);
			if (y >= title_top && y < title_top + 16 * scale)
				enuma_bp_glyph_row(y, title_top, scale, "UniXNU enuma", 0xf0f4fa);
			if (y >= stage_top && y < stage_top + 16 * scale)
				enuma_bp_glyph_row(y, stage_top, scale, stage == 0 ? "Kernel startup" :
				    stage == 1 ? "BSD initialization" : "Starting userspace", 0xf0f4fa);
			__asm__ volatile("dsb st" ::: "memory");
			bp_draw_end(&enuma_bp_gate);
			ml_set_interrupts_enabled(ints);
		}
		previous = stage;
		painted = 1;
	}
schedule:;
	if (__atomic_load_n(&enuma_bp_gate.state, __ATOMIC_ACQUIRE) & BP_STOP)
		return;
	uint64_t deadline;
	clock_interval_to_deadline(1, NSEC_PER_SEC, &deadline);
	thread_call_enter_delayed(&enuma_bp_call, deadline);
}

static void
enuma_bp_start(void)
{
	if (__atomic_load_n(&enuma_bp_mode, __ATOMIC_ACQUIRE) != 2 || !bp_take(&enuma_bp_gate))
		return;
	thread_call_setup_with_options(&enuma_bp_call, enuma_bp_refresh, NULL,
	    THREAD_CALL_PRIORITY_HIGH, THREAD_CALL_OPTIONS_ONCE);
	thread_call_enter(&enuma_bp_call);
}
