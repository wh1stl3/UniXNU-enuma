// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <errno.h>
#include <limits.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "framebuffer.h"
#include "page.h"
#include "proc-events.h"

/* Exercise the real recorder with host lock semantics; not an XNU lock test. */
#define LCK_GRP_DECLARE(name, label) int __attribute__((unused)) name
#define LCK_SPIN_DECLARE(name, group) pthread_mutex_t name = PTHREAD_MUTEX_INITIALIZER
static void lck_spin_lock(pthread_mutex_t *m) { assert(!pthread_mutex_lock(m)); }
static void lck_spin_unlock(pthread_mutex_t *m) { assert(!pthread_mutex_unlock(m)); }
static bool lck_spin_try_lock(pthread_mutex_t *m)
{
	int rc = pthread_mutex_trylock(m);
	assert(rc == 0 || rc == EBUSY);
	return rc == 0;
}
#include "proc-recorder.inc"
#include "proc-page.inc"

enum { WORKERS = 4, WRITES = 20000 };
static void *write_events(void *arg)
{
	uint64_t worker = *(unsigned *)arg;
	for (int n = 0; n < WRITES; ++n) {
		struct enuma_bp_identity who = {(worker << 32) | (unsigned)n, n, ~n};
		enuma_bp_record_exec(ENUMA_BP_SPRINGBOARD, who);
		enuma_bp_record_exit(ENUMA_BP_SPRINGBOARD, who, n * 3);
	}
	return NULL;
}

static void coherent(const struct enuma_bp_event *e)
{
	if (!e->count)
		return;
	assert(e->latest.uniqueid >> 32 < WORKERS);
	assert(e->latest.pid >= 0 && e->latest.pid < WRITES);
	assert((uint32_t)e->latest.uniqueid == (uint32_t)e->latest.pid);
	assert(e->latest.idversion == ~e->latest.pid);
}

int main(void)
{
	struct enuma_bp_proc_events snap;
	struct panel_page page = {0};
	panel_line(&page.main[23], "last console row", PANEL_WHITE, 0);
	panel_line(&page.main[29], "outside proc area", PANEL_WHITE, 0);
	assert(enuma_bp_classify("launchd") == ENUMA_BP_LAUNCHD);
	assert(enuma_bp_classify("backboardd") == ENUMA_BP_BACKBOARDD);
	assert(enuma_bp_classify("SpringBoard") == ENUMA_BP_SPRINGBOARD);
	assert(!enuma_bp_classify("launchd2") && !enuma_bp_classify("backboard") &&
	    !enuma_bp_classify("SpringBoardHelper") && !enuma_bp_classify("springboard"));
	assert(enuma_bp_exec_observed(true, false, 0, true, true));
	assert(!enuma_bp_exec_observed(false, false, 0, true, true));
	assert(!enuma_bp_exec_observed(true, true, 0, true, true));
	assert(!enuma_bp_exec_observed(true, false, EPERM, true, true));
	assert(!enuma_bp_exec_observed(true, false, 0, false, true));
	assert(!enuma_bp_exec_observed(true, false, 0, true, false));
	assert(enuma_bp_proc_snapshot(&snap));
	panel_proc_events(&page, &snap);
	puts(page.main[24].text);
	puts(page.main[25].text);
	assert(strstr(page.main[26].text, "not observed"));
	assert(strstr(page.main[26].text + 60, "not observed"));
	puts(page.main[26].text);

	/* Exit only: signal 9, then raw fallback 0 (neither is decoded here). */
	enuma_bp_record_exit(ENUMA_BP_BACKBOARDD, (struct enuma_bp_identity){7, 42, 9}, 9);
	assert(enuma_bp_proc_snapshot(&snap));
	panel_proc_events(&page, &snap);
	assert(!snap.slot[1].exec.count && snap.slot[1].raw_rv == 9);
	puts(page.main[27].text);
	enuma_bp_record_exit(ENUMA_BP_BACKBOARDD, (struct enuma_bp_identity){8, 42, 10}, 0);
	assert(enuma_bp_proc_snapshot(&snap));
	panel_proc_events(&page, &snap);
	assert(snap.slot[1].exit.count == 2 && strstr(page.main[27].text, "rv=0"));
	puts(page.main[27].text);

	/* Both events between samples. The recorder stores supplied identities verbatim. */
	struct enuma_bp_identity first = {1, 1, 2}, reused_pid = {10, 1, 3};
	enuma_bp_record_exec(ENUMA_BP_LAUNCHD, first);
	enuma_bp_record_exit(ENUMA_BP_LAUNCHD, first, 0x100);
	assert(enuma_bp_proc_snapshot(&snap));
	assert(snap.slot[0].exec.count == 1 && snap.slot[0].exit.count == 1 &&
	    snap.slot[0].raw_rv == 0x100);
	enuma_bp_record_exec(ENUMA_BP_LAUNCHD, first);
	assert(enuma_bp_proc_snapshot(&snap));
	assert(snap.slot[0].exec.count == 2 && snap.slot[0].exec.latest.uniqueid == 1);
	enuma_bp_record_exec(ENUMA_BP_LAUNCHD, (struct enuma_bp_identity){1, 1, 3});
	assert(enuma_bp_proc_snapshot(&snap));
	assert(snap.slot[0].exec.latest.pid == snap.slot[0].exit.latest.pid &&
	    snap.slot[0].exec.latest.uniqueid == snap.slot[0].exit.latest.uniqueid &&
	    snap.slot[0].exec.latest.idversion != snap.slot[0].exit.latest.idversion);
	enuma_bp_record_exec(ENUMA_BP_LAUNCHD, reused_pid);
	assert(enuma_bp_proc_snapshot(&snap));
	assert(snap.slot[0].exec.latest.pid == snap.slot[0].exit.latest.pid &&
	    snap.slot[0].exec.latest.uniqueid != snap.slot[0].exit.latest.uniqueid);
	panel_proc_events(&page, &snap);
	puts(page.main[26].text);

	lck_spin_lock(&enuma_bp_proc_lock);
	assert(!enuma_bp_proc_snapshot(&snap));
	lck_spin_unlock(&enuma_bp_proc_lock);
	assert(snap.slot[0].exec.latest.uniqueid == 10); /* failed copy untouched */
	memset(&page.main[24], 0, 5 * sizeof(page.main[0])); /* panel_sample clears page */
	panel_proc_events(&page, NULL);
	assert(!strcmp(page.main[24].text, "PROC snapshot busy (retry next refresh)"));
	for (unsigned row = 25; row <= 28; ++row)
		assert(!page.main[row].text[0]);
	assert(!strcmp(page.main[23].text, "last console row") && !strcmp(page.main[29].text, "outside proc area"));
	puts(page.main[24].text);

	pthread_t threads[WORKERS];
	unsigned ids[WORKERS];
	for (unsigned i = 0; i < WORKERS; ++i) {
		ids[i] = i;
		assert(!pthread_create(&threads[i], NULL, write_events, &ids[i]));
	}
	for (unsigned i = 0; i < WRITES; ++i) {
		if (enuma_bp_proc_snapshot(&snap)) {
			coherent(&snap.slot[2].exec);
			coherent(&snap.slot[2].exit);
			assert(snap.slot[2].raw_rv == 3 * snap.slot[2].exit.latest.pid);
		}
	}
	for (unsigned i = 0; i < WORKERS; ++i)
		assert(!pthread_join(threads[i], NULL));
	assert(enuma_bp_proc_snapshot(&snap));
	assert(snap.slot[2].exec.count == WORKERS * WRITES && snap.slot[2].exit.count == WORKERS * WRITES);

	enuma_bp_events.slot[2].exec.count = enuma_bp_events.slot[2].exit.count = UINT32_MAX - 1;
	struct enuma_bp_identity max = {UINT64_MAX, -1, -1};
	enuma_bp_record_exec(ENUMA_BP_SPRINGBOARD, first);
	enuma_bp_record_exit(ENUMA_BP_SPRINGBOARD, first, 0);
	enuma_bp_record_exec(ENUMA_BP_SPRINGBOARD, max);
	enuma_bp_record_exit(ENUMA_BP_SPRINGBOARD, max, -1);
	assert(enuma_bp_proc_snapshot(&snap));
	assert(snap.slot[2].exec.count == UINT32_MAX && snap.slot[2].exit.count == UINT32_MAX);
	panel_proc_events(&page, &snap);
	const char *line = page.main[28].text;
	assert(strstr(page.main[24].text, "SAT=at least 4294967295"));
	assert(strlen(line) == 117 && strlen(line) < PANEL_COLS);
	assert(!strncmp(line + 12, "SAT        ffffffff:ffffffffffffffff:ffffffff", 45));
	assert(!strcmp(line + 60, "SAT        ffffffff:ffffffffffffffff:ffffffff rv=ffffffff"));
	puts(line);
	--snap.slot[2].exec.count;
	panel_proc_events(&page, &snap);
	assert(!strncmp(line + 12, "4294967294 ", 11) && !strncmp(line + 60, "SAT ", 4));
	++snap.slot[2].exec.count;
	--snap.slot[2].exit.count;
	panel_proc_events(&page, &snap);
	assert(!strncmp(line + 12, "SAT ", 4) && !strncmp(line + 60, "4294967294 ", 11));
	assert(!strcmp(page.main[23].text, "last console row") && !strcmp(page.main[29].text, "outside proc area"));
	puts("process events: concurrent count/snapshot, saturation and panel bounds pass");
}
