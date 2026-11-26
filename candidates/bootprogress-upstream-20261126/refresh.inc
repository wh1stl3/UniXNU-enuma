// SPDX-License-Identifier: BSD-2-Clause-Patent
// Use the same r6 thread call, admission, interrupt window and release.
static void
enuma_bp_refresh(void *a __unused, void *b __unused)
{
	static int painted;
	static struct panel_page page, previous;
	const struct bp_framebuffer *fb = &enuma_bp_map;
	uint32_t state = __atomic_load_n(&enuma_bp_gate.state, __ATOMIC_ACQUIRE);
	if (state & BP_STOP)
		return;
	if (!(state & (BP_COUNT | BP_TRANSITION))) {
		const struct panel_page *old = painted ? &previous : NULL;
		panel_sample(&page);
		for (unsigned y = 0; y < fb->height; ++y) {
			if (!panel_row_changed(fb, y, &page, old))
				continue;
			boolean_t ints = ml_set_interrupts_enabled(FALSE);
			if (!bp_draw_begin(&enuma_bp_gate)) {
				ml_set_interrupts_enabled(ints);
				painted = 0; /* Never treat a partial paint as committed. */
				goto schedule;
			}
			panel_raster(fb, y, &page, old);
			__asm__ volatile("dsb st" ::: "memory");
			bp_draw_end(&enuma_bp_gate);
			ml_set_interrupts_enabled(ints);
		}
		previous = page;
		painted = 1;
	}
schedule:;
	if (__atomic_load_n(&enuma_bp_gate.state, __ATOMIC_ACQUIRE) & BP_STOP)
		return;
	uint64_t deadline;
	clock_interval_to_deadline(1, NSEC_PER_SEC, &deadline);
	thread_call_enter_delayed(&enuma_bp_call, deadline);
}
