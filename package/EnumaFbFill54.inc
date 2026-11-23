/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Called with VCPUTC_LOCK held. Never retain a mapping pointer or print. */
static unsigned enuma_fbfill_block, enuma_fbfill_row;
static int enuma_fbfill_done;
volatile int g_enuma_fbfill_state = -1;
volatile unsigned g_enuma_fbfill_w, g_enuma_fbfill_h, g_enuma_fbfill_d;
volatile unsigned g_enuma_fbfill_rb, g_enuma_fbfill_avail, g_enuma_fbfill_rows;

static void
enuma_fb_fill_step(void)
{
	int arg = 0;
	if (enuma_fbfill_done ||
	    !PE_parse_boot_argn("enuma-fb-fill", &arg, sizeof(arg)) || arg != 1 ||
	    !ep_console_can_write(&enuma_pid1_console, gc_enabled) ||
	    lastVideoMapSize == 0) {
		return;
	}
	uintptr_t base = (uintptr_t)vinfo.v_baseaddr, virt = (uintptr_t)lastVideoVirt;
	if (base < virt || base - virt >= lastVideoMapSize) {
		g_enuma_fbfill_state = 0;
		enuma_fbfill_done = 1;
		return;
	}
	vm_size_t avail = lastVideoMapSize - (base - virt);
	uint32_t w = vinfo.v_width, h = vinfo.v_height, rb = vinfo.v_rowbytes;
	g_enuma_fbfill_w = w;
	g_enuma_fbfill_h = h;
	g_enuma_fbfill_d = vinfo.v_depth;
	g_enuma_fbfill_rb = rb;
	g_enuma_fbfill_avail = (unsigned)avail;
	uint32_t x0 = w / 8;
	if (vinfo.v_depth != 32 || ((uint64_t)x0 + 256) * 4 > rb ||
	    (uint64_t)x0 + 256 > w) {
		g_enuma_fbfill_state = 0;
		enuma_fbfill_done = 1;
		return;
	}
	uint32_t center = (uint64_t)h * (2 * enuma_fbfill_block + 1) / 8;
	if (center < 64 || (uint64_t)center + 64 > h) {
		g_enuma_fbfill_state = 0;
		enuma_fbfill_done = 1;
		return;
	}
	uint32_t y = center - 64 + enuma_fbfill_row;
	if ((uint64_t)y * rb + ((uint64_t)x0 + 256) * 4 > avail) {
		g_enuma_fbfill_state = 0;
		enuma_fbfill_done = 1;
		return;
	}
	static const uint32_t colors[4] = { 0xffffffffu, 0xffff0000u, 0xff00ff00u, 0xff0000ffu };
	volatile uint32_t *row = (volatile uint32_t *)(base + (uint64_t)y * rb);
	for (uint32_t i = 0; i < 256; i++) {
		row[x0 + i] = colors[enuma_fbfill_block];
	}
	g_enuma_fbfill_rows++;
	if (++enuma_fbfill_row == 128) {
		enuma_fbfill_row = 0;
		if (++enuma_fbfill_block == 4) {
			g_enuma_fbfill_state = 1;
			enuma_fbfill_done = 1;
		}
	}
}
