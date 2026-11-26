/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Included by the pinned r5 kern_exec.c, immediately after the recorder. */
#include "run-state-result.h"

/* Sole writer: launchd report 4. Never modified after the release store. */
static struct enuma_bp_run_report enuma_bp_run_published;
static bool enuma_bp_run_ready;

__attribute__((noinline)) bool
enuma_bp_run_read(struct enuma_bp_run_report *report)
{
	if (!__atomic_load_n(&enuma_bp_run_ready, __ATOMIC_ACQUIRE))
		return false;
	*report = enuma_bp_run_published;
	return true;
}

static bool
enuma_bp_proc_sampleable(proc_t p)
{
	return !proc_is_shadow(p) && !proc_exiting(p) && !proc_in_teardown(p);
}

static __attribute__((noinline)) struct enuma_bp_run_result
enuma_bp_run_target(struct enuma_bp_identity who, uint64_t tid)
{
	struct enuma_bp_run_result result = { .where = RUN_TARGET, .reason = RUN_INVALID_TID };
	if (!tid || tid == thread_tid(current_thread()))
		return result;

	const struct proc_ident ident = {
		.p_pid = who.pid, .p_uniqueid = who.uniqueid, .p_idversion = who.idversion,
	};
	proc_t p = proc_find_ident(&ident);
	if (p == PROC_NULL)
		return (struct enuma_bp_run_result){ .where = RUN_TARGET, .reason = RUN_INSTANCE_NOT_FOUND };

	task_t task = enuma_bp_proc_sampleable(p) ? proc_task(p) : TASK_NULL;
	if (task != TASK_NULL)
		task_reference(task);
	proc_rele(p);
	if (task == TASK_NULL)
		return (struct enuma_bp_run_result){ .where = RUN_TARGET, .reason = RUN_PROC_UNAVAILABLE };

	result.reason = RUN_TID_NOT_IN_TASK;
	thread_t thread = task_findtid(task, tid);
	if (thread != THREAD_NULL) {
		thread_basic_info_data_t basic;
		mach_msg_type_number_t count = THREAD_BASIC_INFO_COUNT;
		const kern_return_t kr = thread_info(thread, THREAD_BASIC_INFO,
		    (thread_info_t)&basic, &count);
		result.reason = RUN_INFO_REFUSED;
		if (kr == KERN_SUCCESS && count == THREAD_BASIC_INFO_COUNT) {
			p = proc_find_ident(&ident);
			result.reason = RUN_INSTANCE_NOT_FOUND;
			if (p != PROC_NULL) {
				result.reason = RUN_PROC_OR_TASK_CHANGED;
				if (enuma_bp_proc_sampleable(p) && proc_task(p) == task)
					result = (struct enuma_bp_run_result){ .run_state = basic.run_state };
				proc_rele(p);
			}
		}
		thread_deallocate(thread);
	}
	task_deallocate(task);
	return result;
}

static enum enuma_bp_run_reason
enuma_bp_run_guard(const struct enuma_bp_run_events *s)
{
	for (unsigned i = ENUMA_BP_BACKBOARDD - 1; i < ENUMA_BP_PROC_SLOTS; ++i) {
		if (s->events.slot[i].exec.count == UINT32_MAX ||
		    s->events.slot[i].exit.count == UINT32_MAX)
			return RUN_SATURATED;
		if (s->matching_exit[i])
			return RUN_EXIT;
	}
	for (unsigned i = ENUMA_BP_BACKBOARDD - 1; i < ENUMA_BP_PROC_SLOTS; ++i)
		if (!s->events.slot[i].exec.count)
			return RUN_INCOMPLETE;
	return RUN_OK;
}

static bool
enuma_bp_run_same(const struct enuma_bp_run_events *a, const struct enuma_bp_run_events *b)
{
	for (unsigned i = ENUMA_BP_BACKBOARDD - 1; i < ENUMA_BP_PROC_SLOTS; ++i) {
		if (a->tid[i] != b->tid[i] || a->matching_exit[i] != b->matching_exit[i] ||
		    a->events.slot[i].exec.count != b->events.slot[i].exec.count ||
		    a->events.slot[i].exit.count != b->events.slot[i].exit.count ||
		    a->events.slot[i].raw_rv != b->events.slot[i].raw_rv ||
		    !enuma_bp_same_identity(a->events.slot[i].exec.latest, b->events.slot[i].exec.latest) ||
		    !enuma_bp_same_identity(a->events.slot[i].exit.latest, b->events.slot[i].exit.latest))
			return false;
	}
	return true;
}

/* The caller is the existing sleepable launchd report callback, not the renderer. */
static __attribute__((noinline)) void
enuma_bp_run_once(void)
{
	struct enuma_bp_run_events before, after;
	struct enuma_bp_run_report report = {0};
	enum enuma_bp_run_where where = RUN_PRE;
	enum enuma_bp_run_reason reason = RUN_BUSY;
	if (enuma_bp_run_snapshot(&before)) {
		reason = enuma_bp_run_guard(&before);
		if (reason == RUN_OK) {
			for (unsigned n = 0; n < 2; ++n) {
				const unsigned i = n + ENUMA_BP_BACKBOARDD - 1;
				report.target[n] = enuma_bp_run_target(before.events.slot[i].exec.latest,
				    before.tid[i]);
			}
			where = RUN_POST;
			if (!enuma_bp_run_snapshot(&after))
				reason = RUN_BUSY;
			else if ((reason = enuma_bp_run_guard(&after)) == RUN_OK &&
			    !enuma_bp_run_same(&before, &after))
				reason = RUN_CHANGED;
		}
	}
	if (reason != RUN_OK)
		for (unsigned n = 0; n < 2; ++n)
			report.target[n] = (struct enuma_bp_run_result){ .where = where, .reason = reason };
	enuma_bp_run_published = report;
	__atomic_store_n(&enuma_bp_run_ready, true, __ATOMIC_RELEASE);
}
