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
#include "proc-events.h"
bool enuma_bp_proc_snapshot(struct enuma_bp_proc_events *snapshot)
{
	(void)snapshot;
	return false;
}
void original_page(const struct bp_framebuffer *, const void *);
static const char initial_logs[] =
    "discard 01\ndiscard 02\nStage: starting IOKit\nUFS published SystemOS\nUFS published OS\n"
    "APFS: root mounted\nFirst synthetic log line\nSecond synthetic log line\nLast synthetic line";
static const char next_logs[] =
    "UFS published OS\nAPFS: root mounted\nFirst synthetic log line\nSecond synthetic log line\n"
    "Last synthetic line\nlaunchd: synthetic output\t\001|\nshort\n";
static const char *log_input = initial_logs;
static void panel_console(struct panel_page *page)
{
	panel_logs(page, log_input, strlen(log_input),
	    enuma_bp_map.width / (6 * panel_scale(&enuma_bp_map)));
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

static void full_page_test(void)
{
	enum { W = 1600, H = 2560, P = W + 9 };
	size_t bytes = (size_t)P * H * 4;
	uint32_t *one = malloc(bytes), *two = malloc(bytes), *fresh = malloc(bytes);
	assert(one && two && fresh);
	memset(one, 0x7e, bytes); memset(two, 0x7e, bytes); memset(fresh, 0x7e, bytes);
	struct bp_framebuffer a = {(volatile unsigned char *)one, bytes, W, H, P * 4};
	struct bp_framebuffer b = {(volatile unsigned char *)two, bytes, W, H, P * 4};
	struct panel_page page = {0}, changed;
	for (unsigned r = 0; r < PANEL_ROWS; ++r) {
		memset(page.main[r].text, '!' + r % 90, 119);
		page.main[r].text[119] = 0;
		page.main[r].fg = PANEL_WHITE; page.main[r].bg = PANEL_BLUE;
	}
	for (unsigned r = 0; r < SIDE_ROWS; ++r) {
		memset(page.side[r].text, 'A' + r, SIDE_COLS);
		page.side[r].text[SIDE_COLS] = 0;
		page.side[r].fg = PANEL_CYAN; page.side[r].bg = PANEL_SECTION;
	}
	assert(panel_scale(&b) == 2);
	original_page(&a, &page);
	for (unsigned y = 0; y < H; ++y) panel_raster(&b, y, &page, NULL);
	for (unsigned y = 0; y < 28; ++y)
		for (unsigned x = 119 * 12; x < W; ++x)
			assert(two[y * P + x] == (PANEL_BLUE & 0xffffffu));
	for (unsigned y = 0; y < DISPLAY_ROWS * 14; ++y) {
		unsigned row = y / 14;
		if (row >= 17 && row < 34) continue;
		for (unsigned x = 0; x < (row < 65 ? 119 * 6 : SIDE_COLS * 6); ++x) {
			unsigned sy = row < 17 ? y : row < 65 ? y - 17 * 14 : 13 * 14 + y - 65 * 14;
			unsigned sx = row < 65 ? x : 728 + x;
			for (unsigned dy = 0; dy < 2; ++dy)
				for (unsigned dx = 0; dx < 2; ++dx)
					assert(two[(2*y+dy)*P+2*x+dx] == one[sy*P+sx]);
		}
	}
	changed = page;
	changed.side[7].text[46] = 'z';
	unsigned rows = 0;
	for (unsigned y = 0; y < H; ++y)
		if (panel_row_changed(&b, y, &changed, &page)) {
			++rows; panel_raster(&b, y, &changed, &page);
		}
	assert(rows == 28);
	b.base = (volatile unsigned char *)fresh;
	for (unsigned y = 0; y < H; ++y) panel_raster(&b, y, &changed, NULL);
	assert(!memcmp(two, fresh, bytes));
	page = changed;
	changed.main[0].bg = PANEL_SECTION;
	b.base = (volatile unsigned char *)two;
	for (unsigned y = 0; y < H; ++y)
		if (panel_row_changed(&b, y, &changed, &page))
			panel_raster(&b, y, &changed, &page);
	b.base = (volatile unsigned char *)fresh;
	for (unsigned y = 0; y < H; ++y) panel_raster(&b, y, &changed, NULL);
	assert(!memcmp(two, fresh, bytes));
	for (unsigned y = 0; y < 28; ++y)
		for (unsigned x = 119 * 12; x < W; ++x)
			assert(two[y * P + x] == (PANEL_SECTION & 0xffffffu));
	for (unsigned y = 0; y < H; ++y)
		for (unsigned x = W; x < P; ++x) assert(two[y*P+x] == 0x7e7e7e7e);
	printf("all 48+8 maximal rows match 1x per pixel; incremental side cell: %u row leases, %u bytes raster writes\n", rows, rows * 12 * 4);
	free(one); free(two); free(fresh);
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
			unsigned refrow = row >= 34 ? row - 17 : row;
			if (x < 119 * 6 * scale && !(row >= 17 && row < 34) &&
			    (refrow == 0 || refrow == 2 || refrow == 3 || (refrow >= 5 && refrow <= 11) ||
			     (refrow >= 17 && refrow <= 23) || refrow == 35 || refrow == 36)) {
				q = original[(y - (row >= 34 ? 17 * 14 * scale : 0)) * stride + x] & 0xffffffu;
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
	{
		struct panel_page p = {0};
		char longlog[4096];
		memset(longlog, 'a', 180);
		snprintf(longlog + 180, sizeof(longlog) - 180,
		    " errno=22 UUID=04769D26-2CA0-4825-B443-E2E5F88300F2\nlast\n");
		panel_logs(&p, longlog, strlen(longlog), 40);
		assert(!strcmp(p.main[23].text, "last"));
		assert(strstr(p.main[21].text, "F88300F"));
		assert(!strcmp(p.main[22].text, "> 2"));
		assert(strstr(p.main[20].text, "errno=22"));
		memset(longlog, 'z', sizeof(longlog));
		memcpy(longlog + sizeof(longlog) - 10, " errno=22\n", 10);
		memset(&p, 0, sizeof(p));
		panel_logs(&p, longlog, sizeof(longlog), 40);
		assert(!strncmp(p.extra[0].text, "... ", 4));
		assert(strstr(p.main[23].text, "errno=22"));
		memset(longlog, 'q', 1000);
		memcpy(longlog + 1000, "\nnewest\n", 8);
		memset(&p, 0, sizeof(p));
		panel_logs(&p, longlog, 1008, 40);
		assert(!strcmp(p.main[23].text, "newest"));
		assert(!p.extra[0].text[0]);
		memset(longlog, 'b', 40);
		memcpy(longlog + 40, "\n", 1);
		memset(&p, 0, sizeof(p));
		panel_logs(&p, longlog, 41, 40);
		assert(strlen(p.main[23].text) == 40);
		assert(!p.main[22].text[0]);
		puts("wrapped record retains errno/UUID; oversized record marks omitted head");
	}
	char logs[4096]; unsigned used = 0;
	for (unsigned i = 0; i < 30; ++i) {
		int n = snprintf(logs + used, sizeof(logs) - used, "%02u %s\n", i,
		    i % 2 ? "short" : "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789");
		assert(n > 0); used += (unsigned)n;
	}
	struct panel_page logpage = {0};
	panel_logs(&logpage, logs, used, 119);
	for (unsigned i = 0; i < 24; ++i) {
		const char *text = i < 17 ? logpage.extra[i].text : logpage.main[17+i-17].text;
		char expected[4]; snprintf(expected, sizeof(expected), "%02u ", i + 6);
		assert(!strncmp(text, expected, 3));
		assert(strlen(text) == ((i + 6) % 2 ? 8u : 65u));
	}
	puts("24 chronological numbered long/short lines, newest visible");
	full_page_test();
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
	assert(buf[0][W - 1] == (PANEL_BLUE & 0xffffffu) && buf[0][W - 2] == (PANEL_BLUE & 0xffffffu) &&
	    buf[0][W - 5] == (PANEL_BLUE & 0xffffffu));
	for (unsigned y = 0; y < H; ++y)
		for (unsigned x = W; x < PITCH; ++x)
			assert(buf[y][x] == 0x71717171);
	puts("256x128 scale=1: clipped rows and pitch padding preserved");
	return 0;
}
