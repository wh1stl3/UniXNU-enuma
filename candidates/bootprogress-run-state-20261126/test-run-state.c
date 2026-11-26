/* SPDX-License-Identifier: BSD-2-Clause-Patent */
#include <assert.h>
#include <limits.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "framebuffer.h"
#include "page.h"
#include "proc-events.h"
#include "run-state-page.inc"
#define LCK_GRP_DECLARE(name, label) int name __attribute__((unused))
#define LCK_SPIN_DECLARE(name, group) int name
static bool locked;
static unsigned snapshots, busy_at;
static void lck_spin_lock(int *lock) { (void)lock; assert(!locked); locked = true; }
static void lck_spin_unlock(int *lock) { (void)lock; assert(locked); locked = false; }
static bool lck_spin_try_lock(int *lock)
{
	if (++snapshots == busy_at)
		return false;
	lck_spin_lock(lock);
	return true;
}
#include "proc-recorder.inc"

struct proc_ident { int p_pid, p_idversion; uint64_t p_uniqueid; };
typedef struct mock_thread { uint64_t tid; int refs, state; } *thread_t;
typedef struct mock_task { int refs; thread_t thread; } *task_t;
typedef struct mock_proc {
	struct enuma_bp_identity ident;
	int refs;
	bool shadow, exiting, teardown;
	task_t task;
} *proc_t;
#define PROC_NULL NULL
#define TASK_NULL NULL
#define THREAD_NULL NULL
typedef int kern_return_t;
typedef int *thread_info_t;
typedef struct { int unused, run_state; } thread_basic_info_data_t;
typedef unsigned mach_msg_type_number_t;
enum { THREAD_BASIC_INFO = 3, THREAD_BASIC_INFO_COUNT = 2, KERN_SUCCESS = 0 };

enum injection { NONE, REEXEC, EXIT, UNMATCHED_EXIT, TASK_CHANGED, TEARDOWN, VANISH, REFUSED, SHORT_COUNT };
static enum injection inject;
static struct mock_thread threads[3];
static struct mock_task tasks[3];
static struct mock_proc procs[2];
static unsigned lookups, findtids, mach_calls;

static proc_t proc_find_ident(const struct proc_ident *ident)
{
	assert(!locked);
	++lookups;
	for (unsigned i = 0; i < 2; ++i) {
		proc_t p = &procs[i];
		if (enuma_bp_same_identity(p->ident, (struct enuma_bp_identity){
		    ident->p_uniqueid, ident->p_pid, ident->p_idversion })) {
			assert(!p->refs++);
			return p;
		}
	}
	return NULL;
}
static bool proc_is_shadow(proc_t p) { assert(p->refs == 1); return p->shadow; }
static bool proc_exiting(proc_t p) { assert(p->refs == 1); return p->exiting; }
static bool proc_in_teardown(proc_t p) { assert(p->refs == 1); return p->teardown; }
static task_t proc_task(proc_t p) { assert(p->refs == 1); return p->task; }
static void proc_rele(proc_t p) { assert(p->refs-- == 1); }
static void task_reference(task_t t) { assert(!t->refs++); }
static void task_deallocate(task_t t)
{
	struct enuma_bp_run_report not_yet;
	assert(!enuma_bp_run_read(&not_yet));
	assert(t->refs-- == 1);
}
static void thread_deallocate(thread_t t) { assert(t->refs-- == 1); }
static thread_t current_thread(void) { return &threads[2]; }
static uint64_t thread_tid(thread_t t) { return t->tid; }
static thread_t task_findtid(task_t t, uint64_t tid)
{
	assert(!locked && t->refs == 1 && tid && tid != current_thread()->tid);
	assert(!procs[0].refs && !procs[1].refs);
	++findtids;
	if (t->thread->tid != tid)
		return NULL;
	assert(!t->thread->refs++);
	return t->thread;
}
static kern_return_t thread_info(thread_t t, int flavor, thread_info_t out, mach_msg_type_number_t *count)
{
	assert(!locked && t->refs == 1 && flavor == THREAD_BASIC_INFO && *count == THREAD_BASIC_INFO_COUNT);
	assert(!procs[0].refs && !procs[1].refs);
	struct enuma_bp_run_report not_yet;
	assert(!enuma_bp_run_read(&not_yet));
	++mach_calls;
	((thread_basic_info_data_t *)out)->run_state = t->state;
	if (t != &threads[0])
		return KERN_SUCCESS;
	switch (inject) {
	case REEXEC: enuma_bp_record_exec(ENUMA_BP_BACKBOARDD, procs[0].ident, t->tid); break;
	case EXIT: enuma_bp_record_exit(ENUMA_BP_BACKBOARDD, procs[0].ident, 1); break;
	case UNMATCHED_EXIT: enuma_bp_record_exit(ENUMA_BP_BACKBOARDD, procs[1].ident, 1); break;
	case TASK_CHANGED: procs[0].task = &tasks[2]; break;
	case TEARDOWN: procs[0].teardown = true; break;
	case VANISH: ++procs[0].ident.uniqueid; break;
	case REFUSED: return 1;
	case SHORT_COUNT: --*count; break;
	case NONE: break;
	}
	return KERN_SUCCESS;
}
static void refresh(struct panel_page *page)
{
	struct enuma_bp_run_report report;
	bool ready = enuma_bp_run_read(&report);
	panel_run_state(page, ready ? &report : NULL);
}
#include "run-state.inc"

static void reset(unsigned target_count)
{
	enuma_bp_events = (struct enuma_bp_proc_events){0};
	memset(enuma_bp_initial_tid, 0, sizeof(enuma_bp_initial_tid));
	memset(enuma_bp_matching_exit, 0, sizeof(enuma_bp_matching_exit));
	enuma_bp_run_ready = false;
	snapshots = busy_at = lookups = findtids = mach_calls = 0;
	inject = NONE;
	for (unsigned i = 0; i < 3; ++i) {
		threads[i] = (struct mock_thread){ .tid = i + 501, .state = (int)i + 3 };
		tasks[i] = (struct mock_task){ .thread = &threads[i] };
	}
	for (unsigned i = 0; i < 2; ++i) {
		procs[i] = (struct mock_proc){ .ident = { i + 200, i + 42, 7 }, .task = &tasks[i] };
		if (i < target_count)
			enuma_bp_record_exec(i + ENUMA_BP_BACKBOARDD, procs[i].ident, threads[i].tid);
	}
}

static void check(const char *bb, const char *sb, unsigned calls)
{
	struct panel_page page = {0}, next = {0};
	refresh(&page);
	assert(!strcmp(page.main[RUN_STATE_ROW].text, "backboardd pending"));
	assert(!strcmp(page.main[RUN_STATE_ROW + 1].text, "SpringBoard pending"));
	assert(!lookups && !findtids && !mach_calls && !snapshots);
	enuma_bp_run_once();
	assert(!locked && mach_calls == calls);
	for (unsigned i = 0; i < 2; ++i)
		assert(!procs[i].refs);
	for (unsigned i = 0; i < 3; ++i)
		assert(!threads[i].refs && !tasks[i].refs);
	const unsigned before[] = {lookups, findtids, mach_calls, snapshots};
	const char *const names[] = {"backboardd", "SpringBoard"}, *states[] = {bb, sb};
	for (unsigned i = 0; i < 8; ++i) {
		memset(&page, 0, sizeof(page));
		panel_line(&page.main[RUN_STATE_ROW - 1], "previous unchanged", PANEL_WHITE, 0);
		panel_line(&page.main[RUN_STATE_ROW + 2], "next unchanged", PANEL_WHITE, 0);
		refresh(&page);
		assert(!strcmp(page.main[RUN_STATE_ROW - 1].text, "previous unchanged"));
		assert(!strcmp(page.main[RUN_STATE_ROW + 2].text, "next unchanged"));
		for (unsigned n = 0; n < 2; ++n) {
			char expected[PANEL_COLS];
			int len = snprintf(expected, sizeof(expected), "%s %s", names[n], states[n]);
			assert(len > 0 && (unsigned)len < PANEL_COLS);
			assert(!strcmp(page.main[RUN_STATE_ROW + n].text, expected));
		}
		if (i)
			assert(!memcmp(&page, &next, sizeof(page)));
		next = page;
	}
	assert(before[0] == lookups && before[1] == findtids &&
	    before[2] == mach_calls && before[3] == snapshots);
}

static void raster_boundary(void)
{
	enum { WIDTH = 1600, HEIGHT = 2560, PITCH = WIDTH + 2 };
	static uint32_t storage[HEIGHT][PITCH];
	struct bp_framebuffer fb = {(volatile unsigned char *)storage, sizeof(storage), WIDTH, HEIGHT, PITCH * 4};
	const unsigned cell = 14 * panel_scale(&fb);
	assert(cell == 28);
	struct panel_page from = {0}, to = {0};
	refresh(&to);
	const unsigned lo = RUN_STATE_ROW * cell, hi = lo + 2 * cell;
	for (unsigned y = lo - 1; y <= hi; ++y) {
		storage[y][WIDTH] = 0x11223344;
		storage[y][WIDTH + 1] = 0x55667788;
		assert(!!panel_row_changed(&fb, y, &to, &from) == (y >= lo && y < hi));
		if (y >= lo && y < hi)
			panel_raster(&fb, y, &to, &from);
		assert(storage[y][WIDTH] == 0x11223344 && storage[y][WIDTH + 1] == 0x55667788);
	}
	for (unsigned r = 0; r < 2; ++r) {
		const size_t len = strlen(to.main[RUN_STATE_ROW + r].text);
		assert(len < WIDTH / (6 * panel_scale(&fb)));
		bool ink = false;
		for (unsigned y = lo + r * cell; y < lo + (r + 1) * cell; ++y)
			for (unsigned x = (len - 1) * 12; x < len * 12; ++x)
				ink |= storage[y][x] != 0;
		assert(ink);
	}
}

int main(void)
{
	reset(2); check("run_state=3", "run_state=4", 2);
	assert(lookups == 4 && findtids == 2 && snapshots == 2);
	reset(1); check("no-sample:pre:pair-not-published", "no-sample:pre:pair-not-published", 0);
	assert(!lookups && !findtids);
	reset(0);
	enuma_bp_record_exec(ENUMA_BP_LAUNCHD, procs[0].ident, threads[0].tid);
	check("no-sample:pre:pair-not-published", "no-sample:pre:pair-not-published", 0);
	assert(!lookups && !findtids);
	reset(2); ++procs[0].ident.uniqueid; check("no-sample:target:instance-not-found", "run_state=4", 1);
	assert(lookups == 3 && findtids == 1);
	reset(2);
	enuma_bp_record_exec(ENUMA_BP_BACKBOARDD, procs[0].ident, threads[0].tid);
	procs[0].task = &tasks[2];
	check("no-sample:target:tid-not-in-task", "run_state=4", 1);
	assert(lookups == 3 && findtids == 2);
	reset(2); enuma_bp_initial_tid[ENUMA_BP_SPRINGBOARD - 1] = 0;
	check("run_state=3", "no-sample:target:invalid-tid", 1);
	reset(2); enuma_bp_initial_tid[ENUMA_BP_SPRINGBOARD - 1] = current_thread()->tid;
	check("run_state=3", "no-sample:target:invalid-tid", 1);
	reset(2); procs[0].exiting = true; check("no-sample:target:proc-unavailable", "run_state=4", 1);
	reset(2); procs[0].shadow = true; check("no-sample:target:proc-unavailable", "run_state=4", 1);
	reset(2); procs[0].task = NULL; check("no-sample:target:proc-unavailable", "run_state=4", 1);
	reset(2); busy_at = 1; check("no-sample:pre:recorder-busy", "no-sample:pre:recorder-busy", 0);
	assert(!lookups && !findtids && snapshots == 1);
	reset(2); busy_at = 2; check("no-sample:post:recorder-busy", "no-sample:post:recorder-busy", 2);
	reset(2); inject = REEXEC; check("no-sample:post:record-changed", "no-sample:post:record-changed", 2);
	reset(2); inject = UNMATCHED_EXIT; check("no-sample:post:record-changed", "no-sample:post:record-changed", 2);
	reset(2); inject = EXIT; check("no-sample:post:matching-exit", "no-sample:post:matching-exit", 2);
	reset(2);
	enuma_bp_record_exit(ENUMA_BP_BACKBOARDD, procs[0].ident, 0);
	enuma_bp_record_exit(ENUMA_BP_BACKBOARDD, procs[1].ident, 0);
	check("no-sample:pre:matching-exit", "no-sample:pre:matching-exit", 0);
	reset(2); inject = TASK_CHANGED; check("no-sample:target:proc-or-task-changed", "run_state=4", 2);
	raster_boundary();
	reset(2); inject = TEARDOWN; check("no-sample:target:proc-or-task-changed", "run_state=4", 2);
	reset(2); inject = VANISH; check("no-sample:target:instance-not-found", "run_state=4", 2);
	reset(2); inject = REFUSED; check("no-sample:target:thread-info-refused", "run_state=4", 2);
	reset(2); inject = SHORT_COUNT; check("no-sample:target:thread-info-refused", "run_state=4", 2);
	reset(2); enuma_bp_events.slot[1].exec.count = UINT32_MAX;
	check("no-sample:pre:recorder-saturated", "no-sample:pre:recorder-saturated", 0);
	assert(!lookups && !findtids);
	reset(2); threads[0].state = INT_MIN; threads[1].state = INT_MAX;
	check("run_state=-2147483648", "run_state=2147483647", 2);
	raster_boundary();
	puts("23 run-state cases passed; repeated reads, real row raster and reference balance checked");
	return 0;
}
