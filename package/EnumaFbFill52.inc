/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Called with VCPUTC_LOCK held; do not print or retain framebuffer pointers. */
static int enuma_fbfill_done;
volatile int g_enuma_fbfill_state = -1;
volatile unsigned g_enuma_fbfill_w, g_enuma_fbfill_h, g_enuma_fbfill_d;
volatile unsigned g_enuma_fbfill_rb, g_enuma_fbfill_avail;

static void
enuma_fb_fill_once(void)
{
	int arg = 0;
	if (enuma_fbfill_done ||
	    !PE_parse_boot_argn("enuma-fb-fill", &arg, sizeof(arg)) || arg != 1 ||
	    !ep_console_can_write(&enuma_pid1_console, gc_enabled) ||
	    lastVideoMapSize == 0) {
		return;
	}
	uintptr_t base = (uintptr_t)vinfo.v_baseaddr;
	uintptr_t virt = (uintptr_t)lastVideoVirt;
	if (base < virt || base - virt >= lastVideoMapSize) {
		g_enuma_fbfill_state = 0;
		enuma_fbfill_done = 1;
		return;
	}
	vm_size_t avail = lastVideoMapSize - (base - virt);
	g_enuma_fbfill_w = vinfo.v_width;
	g_enuma_fbfill_h = vinfo.v_height;
	g_enuma_fbfill_d = vinfo.v_depth;
	g_enuma_fbfill_rb = vinfo.v_rowbytes;
	g_enuma_fbfill_avail = (unsigned)avail;
	if (vinfo.v_depth != 32) {
		g_enuma_fbfill_state = 0;
		enuma_fbfill_done = 1;
		return;
	}
	static const uint32_t colors[4] = { 0xffffffffu, 0xffff0000u, 0xff00ff00u, 0xff0000ffu };
	uint32_t w = vinfo.v_width, h = vinfo.v_height, rb = vinfo.v_rowbytes;
	const uint32_t bw = 256, bh = 128;
	uint32_t x0 = w / 8;
	if (x0 + bw > w || h < bh) {
		g_enuma_fbfill_state = 0;
		enuma_fbfill_done = 1;
		return;
	}
	for (uint32_t b = 0; b < 4; b++) {
		uint64_t center = (uint64_t)h * (2 * b + 1) / 8;
		if (center < bh / 2 || center + bh / 2 > h) {
			g_enuma_fbfill_state = 0;
			enuma_fbfill_done = 1;
			return;
		}
		uint32_t y0 = (uint32_t)center - bh / 2;
		if ((uint64_t)(y0 + bh) * rb + (uint64_t)(x0 + bw) * 4 > avail) {
			g_enuma_fbfill_state = 0;
			enuma_fbfill_done = 1;
			return;
		}
		for (uint32_t y = y0; y < y0 + bh; y++) {
			volatile uint32_t *row = (volatile uint32_t *)(base + (uint64_t)y * rb);
			for (uint32_t x = x0; x < x0 + bw; x++) {
				row[x] = colors[b];
			}
		}
	}
	g_enuma_fbfill_state = 1;
	enuma_fbfill_done = 1;
}
