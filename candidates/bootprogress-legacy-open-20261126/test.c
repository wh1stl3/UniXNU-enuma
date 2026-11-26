/* SPDX-License-Identifier: BSD-2-Clause-Patent */
#include <assert.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
#include "framebuffer.h"
#include "page.h"
#include "proc-events.h"

struct proc_ident { uint64_t p_uniqueid; int p_pid, p_idversion; };
struct fake_proc { struct proc_ident id; unsigned task; };
typedef struct fake_proc *proc_t;
#define PROC_NULL ((proc_t)0)
static _Thread_local struct fake_proc proc;
static _Thread_local unsigned task;
static proc_t current_proc(void) { return &proc; }
static struct proc_ident proc_ident(proc_t p) { return p->id; }
static unsigned proc_task(proc_t p) { return p->task; }
static unsigned current_task(void) { return task; }
#define LCK_GRP_DECLARE(n, s) __attribute__((unused)) int n
#define LCK_SPIN_DECLARE(n, grp) pthread_mutex_t n = PTHREAD_MUTEX_INITIALIZER
static bool lck_spin_try_lock(pthread_mutex_t *lock) { return !pthread_mutex_trylock(lock); }
static void lck_spin_lock(pthread_mutex_t *lock) { assert(!pthread_mutex_lock(lock)); }
static void lck_spin_unlock(pthread_mutex_t *lock) { assert(!pthread_mutex_unlock(lock)); }
#include "proc-recorder.inc"
#include "record.inc"
#include "page.inc"
#include "display-page.inc"

static const struct enuma_bp_identity bb = {UINT64_MAX, INT_MIN, INT_MIN};
static const struct enuma_bp_identity other = {43, INT_MIN, INT_MIN};
static void set_current(struct enuma_bp_identity who)
{
	task = 1;
	proc = (struct fake_proc){{who.uniqueid, who.pid, who.idversion}, 1};
}

static void reset(void)
{
	memset(&enuma_bp_events, 0, sizeof(enuma_bp_events));
	memset(enuma_bp_matching_exit, 0, sizeof(enuma_bp_matching_exit));
	memset(&enuma_open_slot, 0, sizeof(enuma_open_slot));
	enuma_open_claimed = enuma_method_claimed = 0;
	enuma_open_registry = 0;
	set_current(bb);
}

static struct enuma_open_snapshot read_slot(void)
{
	struct enuma_open_snapshot s = {0};
	enuma_legacy_open_read(&s);
	return s;
}

static void check_page(const struct enuma_open_snapshot *s, const struct enuma_bp_event *exec,
    const char *open, const char *final, const char *method)
{
	struct panel_page page = {0}, old = {0};
	panel_line(&page.main[5], "stage sentry", 1, 0);
	panel_line(&page.main[13], "run-state sentry", 1, 0);
	const char logs[] = "old\n1\n2\n3\n4\n5\n6\n7\nlatest log\n";
	panel_logs(&page, logs, sizeof(logs) - 1, 119);
	panel_legacy_open(&page, s, exec);
	const struct enuma_bp_display_sample display = {0};
	panel_display_events(&page, &display);
	assert(strstr(page.main[4].text, open) && strstr(page.main[11].text, final));
	assert(strstr(page.main[12].text, method));
	assert(!strcmp(page.main[5].text, "stage sentry") && !strcmp(page.main[13].text, "run-state sentry"));
	assert(strstr(page.main[9].text, "registered=0") && strstr(page.main[10].text, "VALIDATE") &&
	    strstr(page.main[15].text, "PREPARE"));
	assert(!strcmp(page.extra[0].text, "1") && !strcmp(page.extra[7].text, "latest log") &&
	    !page.extra[8].text[0] && !page.main[23].text[0]);
	for (unsigned row = 0; row < PANEL_ROWS; ++row)
		assert(strlen(page.main[row].text) < PANEL_COLS - 1);
	static uint32_t pixels[200][720];
	struct bp_framebuffer fb = {.base = (void *)pixels, .mapped = sizeof(pixels),
	    .width = 714, .height = 200, .stride = sizeof(pixels[0])};
	assert(panel_row_changed(&fb, 3 * 14, &page, &old));
	panel_raster(&fb, 3 * 14, &page, &old);
	assert(!pixels[3 * 14][714]);
}

static void *claim(void *arg)
{
	set_current(bb);
	return (void *)(uintptr_t)enuma_legacy_open_claim((uint32_t)(uintptr_t)arg);
}

static void *method(void *arg)
{
	set_current(bb);
	enuma_legacy_method_note((uint32_t)(uintptr_t)arg, ENUMA_METHOD_ASYNC);
	return NULL;
}

int main(void)
{
	const unsigned slot = ENUMA_BP_BACKBOARDD - 1;
	reset();
	struct enuma_open_snapshot s = read_slot();
	check_page(&s, NULL, "not attributed", "unknown", "not tracked");
	assert(!enuma_legacy_open_claim(0)); /* no exec */
	enuma_bp_record_exec(ENUMA_BP_LAUNCHD, bb, 31);
	assert(!enuma_legacy_open_claim(0));
	enuma_bp_record_exec(ENUMA_BP_BACKBOARDD, bb, 31);
	set_current(other);
	assert(!enuma_legacy_open_claim(0));
	set_current(bb);
	proc.task = 2;
	assert(!enuma_legacy_open_claim(0));
	proc.task = task;
	lck_spin_lock(&enuma_bp_proc_lock);
	assert(!enuma_legacy_open_claim(0));
	lck_spin_unlock(&enuma_bp_proc_lock);
	enuma_bp_events.slot[slot].exec.count = UINT32_MAX;
	assert(!enuma_legacy_open_claim(0));
	enuma_bp_events.slot[slot].exec.count = 1;
	enuma_bp_record_exit(ENUMA_BP_BACKBOARDD, bb, 1);
	assert(!enuma_legacy_open_claim(0));

	reset();
	enuma_bp_record_exec(ENUMA_BP_BACKBOARDD, bb, 31);
	assert(enuma_legacy_open_claim(UINT32_MAX) && !enuma_legacy_open_claim(0));
	assert(!enuma_legacy_method_key());
	s = read_slot();
	check_page(&s, NULL, "4294967295", "pending", "not tracked");
	enuma_legacy_open_raw(0, "1234567890123456789012345678901234567890");
	s = read_slot();
	assert(s.phase == ENUMA_OPEN_RAW && s.raw.truncated && strlen(s.raw.client_class) == 31);
	check_page(&s, NULL, "678901...", "pending", "not tracked");
	enuma_legacy_open_final(0, -1, false, 42);
	assert(!enuma_legacy_method_key());
	s = read_slot();
	check_page(&s, NULL, "newUserClient=0x00000000", "result=0xffffffff client=0", "not tracked");
	enuma_legacy_method_note(0, ENUMA_METHOD_SYNC);
	assert(!read_slot().method_kind);

	reset();
	enuma_bp_record_exec(ENUMA_BP_BACKBOARDD, bb, 31);
	assert(enuma_legacy_open_claim(0));
	enuma_legacy_open_raw(-2, NULL);
	enuma_legacy_open_final(-3, -2, false, 0);
	s = read_slot();
	assert(s.raw.result == -2 && !s.raw.client_class[0] && s.final.err == -3 && !s.method_eligible);

	reset();
	enuma_bp_record_exec(ENUMA_BP_BACKBOARDD, bb, 31);
	assert(enuma_legacy_open_claim(0));
	enuma_legacy_open_raw(0, "Client");
	enuma_legacy_open_final(0, 0, true, 42);
	assert(enuma_legacy_method_key() == 42);
	s = read_slot();
	check_page(&s, NULL, "class=Client", "client=1", "not observed yet");
	lck_spin_lock(&enuma_bp_proc_lock);
	enuma_legacy_method_note(0, ENUMA_METHOD_SYNC);
	lck_spin_unlock(&enuma_bp_proc_lock);
	assert(!read_slot().method_kind);
	set_current(other);
	enuma_legacy_method_note(0, ENUMA_METHOD_SYNC);
	assert(!read_slot().method_kind);
	set_current(bb);
	enuma_legacy_method_note(0, ENUMA_METHOD_SYNC);
	enuma_legacy_method_note(99, ENUMA_METHOD_VAR);
	s = read_slot();
	check_page(&s, NULL, "class=Client", "client=1", "sync sel=0");
	assert(!enuma_legacy_method_key());

	reset();
	enuma_bp_record_exec(ENUMA_BP_BACKBOARDD, bb, 31);
	assert(enuma_legacy_open_claim(0));
	enuma_legacy_open_raw(0, "Client");
	enuma_legacy_open_final(0, 0, true, 42);
	enuma_bp_record_exec(ENUMA_BP_BACKBOARDD, bb, 32);
	enuma_legacy_method_note(123, ENUMA_METHOD_VAR);
	assert(!read_slot().method_kind); /* re-exec, same tuple */

	reset();
	enuma_bp_record_exec(ENUMA_BP_BACKBOARDD, bb, 31);
	pthread_t a[8];
	for (uintptr_t i = 0; i < 8; ++i)
		assert(!pthread_create(&a[i], NULL, claim, (void *)i));
	unsigned wins = 0;
	for (unsigned i = 0; i < 8; ++i) {
		void *ret;
		assert(!pthread_join(a[i], &ret));
		wins += (uintptr_t)ret;
	}
	assert(wins == 1);
	enuma_legacy_open_raw(0, "Client");
	enuma_legacy_open_final(0, 0, true, 42);
	for (uintptr_t i = 0; i < 8; ++i)
		assert(!pthread_create(&a[i], NULL, method, (void *)i));
	for (unsigned i = 0; i < 8; ++i)
		assert(!pthread_join(a[i], NULL));
	s = read_slot();
	assert(s.method_kind == ENUMA_METHOD_ASYNC && s.selector < 8);
	/* Reference function retained; this fixture does not execute run-state. */
	(void)enuma_bp_run_snapshot;
	return 0;
}
