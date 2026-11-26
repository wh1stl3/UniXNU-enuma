// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "framebuffer.h"
#include "BootProgressCore.h"
#include "BootProgressDisplay.h"

static struct bp_display display;
static char build_tag[32] = "fixture";
#define BP_BAR_LIVE 0xff1f3a68
#define BP_BAR_STOP 0xff7a1f1f
#define BP_BAR_SECTION 0xff1a2029
static void bar(unsigned n, const char *s, uint32_t fg, uint32_t bg)
{
	bp_line_bg(&display, n, s, fg, bg);
}
static void line(unsigned n, const char *s, uint32_t fg)
{
	bp_line(&display, n, s, fg);
}
static char boot_progress_ext[8][48];
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wmisleading-indentation"
#include "reference-side.inc"
#pragma GCC diagnostic pop

static unsigned vm_page_free_count, vm_page_active_count, vm_page_inactive_count;
static unsigned vm_page_wire_count, vm_page_speculative_count;
static unsigned vm_page_free_min, vm_page_free_reserved, vm_page_free_target;
static struct { unsigned long long timebase_frequency_hz; } gPEClockFrequencyInfo;
typedef struct { struct { uint64_t v_baseAddr; } Video; } boot_args;
static boot_args args;
static struct { void *bootArgs; } PE_state = {&args};
static struct bp_framebuffer enuma_bp_map;
static unsigned enuma_bp_stage;
static uint64_t cntpct_el0, cntfrq_el0, tcr_el1, ttbr0_el1, ttbr1_el1, sctlr_el1;
static uint64_t cntvct_el0, cntv_cval_el0, cntv_ctl_el0, daif;

#include "page.h"
static const char initial_logs[] =
    "discard 01\ndiscard 02\nStage: starting IOKit\nUFS published SystemOS\nUFS published OS\n"
    "APFS: root mounted\nFirst synthetic log line\nSecond synthetic log line\nLast synthetic line";
static const char next_logs[] =
    "UFS published OS\nAPFS: root mounted\nFirst synthetic log line\nSecond synthetic log line\n"
    "Last synthetic line\nlaunchd: synthetic output\t\001|\nshort\n";
static const char *log_input = initial_logs;
static void panel_console(struct panel_page *page)
{
	panel_logs(page, log_input, strlen(log_input));
}
static void PE_parse_boot_argn(const char *key, char *out, size_t n)
{
	assert(!strcmp(key, "build-tag"));
	snprintf(out, n, "%s", build_tag);
}
#include "captured-sample.inc"

/* The exact selected upstream draw() blocks, with test counters in place
 * of ARM/target inputs. Unexecuted original collectors/overlays stay absent. */
static unsigned native_virtio_ready;
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Waddress"
#pragma GCC diagnostic ignored "-Wformat"
static void upstream_draw(struct bp_core *visible)
{
	char b[BP_COLS];
	unsigned long long tcr = tcr_el1, ttbr0 = ttbr0_el1, ttbr1 = ttbr1_el1, sctlr = sctlr_el1;
#include "reference-draw.inc"
	ext_overlay_locked();
}
#pragma GCC diagnostic pop

static void ppm(const char *path, const uint32_t *p, unsigned w, unsigned h, unsigned stride)
{
	FILE *f = fopen(path, "wb");
	assert(f);
	fprintf(f, "P6\n%u %u\n255\n", w, h);
	for (unsigned y = 0; y < h; ++y)
		for (unsigned x = 0; x < w; ++x) {
			uint32_t color = p[y * stride + x];
			fputc((color >> 16) & 255, f);
			fputc((color >> 8) & 255, f);
			fputc(color & 255, f);
		}
	assert(!ferror(f) && fclose(f) == 0);
}

static void compare(unsigned w, unsigned h, int images)
{
	unsigned stride = w + 9;
	size_t bytes = (size_t)stride * h * sizeof(uint32_t);
	uint32_t *original = malloc(bytes), *candidate = malloc(bytes), *full = malloc(bytes);
	assert(original && candidate && full);
	memset(original, 0x7e, bytes);
	memset(candidate, 0x7e, bytes);
	memset(full, 0x7e, bytes);
	enuma_bp_map = (struct bp_framebuffer){(volatile unsigned char *)candidate, bytes, w, h, stride * 4};
	assert(bp_framebuffer_valid(&enuma_bp_map, 1));
	unsigned scale = panel_scale(&enuma_bp_map);
	display = (struct bp_display){.frame = (uintptr_t)original, .bound = 1,
	    .width = w, .height = h, .stride = stride * 4, .scale = scale};
	bp_clear(&display);
	cntfrq_el0 = 19200000;
	cntpct_el0 += cntfrq_el0;
	tcr_el1 = 0x1234; ttbr0_el1 = 0x2345; ttbr1_el1 = 0x3456; sctlr_el1 = 0x4567;
	native_ufs_block_reads = 1234; native_ufs_verified_blocks = 768; native_ufs_block_failures = 2;
	native_ufs_integrity_failures = 1; native_ufs_blocks_published = 2;
	max_mem = 8ull << 30; vm_page_free_count = 56; vm_page_active_count = 789;
	native_ram_block_sparse = 1; native_ram_block_bytes = 6ull << 20;
	native_ram_block_resident_bytes = 256ull << 10;
	native_data_persist_state = 3; native_data_persist_header = 1;
	native_data_persist_present = 9; native_data_persist_loaded = 7;
	native_data_persist_writes = 5; native_data_persist_syncs = 2;
	log_input = initial_logs;
	struct panel_page page, changed;
	panel_sample(&page);
	struct bp_core state = {.continuous = 1, .limit = 120, .stall = 30};
	bp_stage(&state, "Kernel startup", 0);
	enuma_bp_stage = 1; cntpct_el0 += cntfrq_el0;
	panel_sample(&page);
	bp_stage(&state, "BSD initialization", 1);
	enuma_bp_stage = 2; cntpct_el0 += cntfrq_el0;
	panel_sample(&page);
	bp_stage(&state, "Starting userspace", 2);
	for (const char *c = initial_logs; *c; ++c)
		bp_char(&state, *c);
	bp_poll(&state, 2, native_ufs_block_reads, native_ufs_verified_blocks, native_ufs_block_failures);
	snprintf(boot_progress_ext[2], 48, "%s", "DATA st=3 hdr=1 gpt=0/0 lba=0");
	snprintf(boot_progress_ext[3], 48, "%s", "pres=9 ld=7 wr=5 sy=2 er=0");
	upstream_draw(&state);
	for (unsigned y = 0; y < h; ++y)
		panel_raster(&enuma_bp_map, y, &page, NULL);

	unsigned compared = 0, differences = 0;
	for (unsigned y = 0; y < h; ++y) {
		unsigned row = y / (14 * scale);
		for (unsigned x = 0; x < w; ++x) {
			uint32_t p = candidate[y * stride + x], q = original[y * stride + x] & 0xffffffu;
			assert(p >> 24 == 0);
			if (p != q)
				++differences;
			if (x < 119 * 6 * scale &&
			    (row == 0 || row == 2 || row == 3 || (row >= 5 && row <= 11) ||
			     (row >= 17 && row <= 23) || row == 35 || row == 36)) {
				assert(p == q);
				++compared;
			}
		}
		for (unsigned x = w; x < stride; ++x)
			assert(candidate[y * stride + x] == 0x7e7e7e7e);
	}
	assert(compared && differences);
	assert(!strcmp(page.main[23].text, "Last synthetic line"));
	assert(strstr(page.main[31].text, "unavailable"));
	if (images) {
		ppm("upstream-selected-rows.ppm", original, w, h, stride);
		ppm("enuma-candidate.ppm", candidate, w, h, stride);
	}
	log_input = next_logs;
	cntpct_el0 += 30 * cntfrq_el0;
	panel_sample(&changed);
	assert(strstr(changed.main[0].text, "DEADLINE EXCEEDED"));
	assert(!strcmp(changed.main[22].text, "launchd: synthetic output |"));
	assert(!strcmp(changed.main[23].text, "short"));
	for (unsigned y = 0; y < h; ++y)
		if (panel_row_changed(&enuma_bp_map, y, &changed, &page))
			panel_raster(&enuma_bp_map, y, &changed, &page);
	enuma_bp_map.base = (volatile unsigned char *)full;
	for (unsigned y = 0; y < h; ++y)
		panel_raster(&enuma_bp_map, y, &changed, NULL);
	assert(memcmp(candidate, full, bytes) == 0);
	printf("%ux%u + padded pitch, scale=%u: %u equal selected RGB pixels; %u full-image differences; incremental == fresh\n",
	    w, h, scale, compared, differences);
	free(full);
	free(candidate);
	free(original);
}

int main(void)
{
	compare(1600, 2560, 1);
	/* The same monitor has already observed all stages; preserve that state.
	 * Re-test narrow clipping without replaying its one-shot timeline. */
	struct panel_page page = {0};
	panel_line(&page.main[0], "narrow", PANEL_WHITE, PANEL_BLUE);
	enum { W = 256, H = 128, PITCH = W + 5 };
	uint32_t buf[H][PITCH];
	memset(buf, 0x71, sizeof(buf));
	struct bp_framebuffer fb = {(volatile unsigned char *)buf, sizeof(buf), W, H, PITCH * 4};
	for (unsigned y = 0; y < H; ++y)
		panel_raster(&fb, y, &page, NULL);
	assert(buf[0][W - 1] == 0 && buf[0][W - 2] == 0 &&
	    buf[0][W - 5] == (PANEL_BLUE & 0xffffffu));
	for (unsigned y = 0; y < H; ++y)
		for (unsigned x = W; x < PITCH; ++x)
			assert(buf[y][x] == 0x71717171);
	puts("256x128 scale=1: clipped rows and pitch padding preserved");
	return 0;
}
