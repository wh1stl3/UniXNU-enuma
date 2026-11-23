/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Isolated r56 diagnostic; compiled with the OSFMK private layout. */
#include <kern/clock.h>
#include <kern/misc_protos.h>
#include <kern/spl.h>
#include <kern/task.h>
#include <kern/thread.h>
#include <kern/thread_call.h>
#include <mach/arm/thread_status.h>
#include <mach/mach_time.h>
#include <pexpert/pexpert.h>

enum { ENUMA_TH_CAP = 8 };

extern task_t enuma_th_task_ref(int pid, const char *comm, const char **why);
thread_call_t enuma_th_alloc(unsigned int tick);

struct enuma_th_row {
	uint64_t tid, we, pc, lr;
	unsigned int state;
	bool busy, saved;
};

struct enuma_th_sample {
	struct enuma_th_row rows[ENUMA_TH_CAP];
	unsigned int shown;
	int total;
	uint32_t slide;
	const char *why;
};

static void
enuma_th_read_saved(thread_t thread, struct enuma_th_row *row)
{
	/* The thread ref pins the PCB, not the contents. These are independent reads. */
	const arm_saved_state_t *upcb = os_atomic_load(&thread->machine.upcb, relaxed);
	if (upcb == NULL) {
		return;
	}
	const uint32_t flavor = os_atomic_load(&upcb->ash.flavor, relaxed);
	const uint32_t count = os_atomic_load(&upcb->ash.count, relaxed);
	if (flavor != ARM_SAVED_STATE64 || count != ARM_SAVED_STATE64_COUNT) {
		return;
	}
	const uint32_t cpsr = os_atomic_load(&upcb->ss_64.cpsr, relaxed);
	const uint64_t pc = os_atomic_load(&upcb->ss_64.pc, relaxed);
	const uint64_t lr = os_atomic_load(&upcb->ss_64.lr, relaxed);
	if (PSR64_IS_USER64(cpsr) && pc != 0) {
		row->pc = pc;
		row->lr = lr;
		row->saved = true;
	}
}

static __attribute__((noinline)) void
enuma_th_capture(int pid, const char *comm, struct enuma_th_sample *sample)
{
	sample->slide = UINT32_MAX;
	task_t task = enuma_th_task_ref(pid, comm, &sample->why);
	if (task == TASK_NULL) {
		return;
	}
	if (!task_lock_try(task)) {
		task_deallocate(task);
		sample->why = "busy";
		return;
	}
	sample->slide = os_atomic_load(&task->task_shared_region_slide, relaxed);
	sample->total = task->thread_count;
	thread_t refs[ENUMA_TH_CAP], thread;
	/* This XNU assigns ascending IDs and appends under the same task lock. */
	queue_iterate(&task->threads, thread, thread_t, task_threads) {
		thread_reference(thread);
		refs[sample->shown++] = thread;
		if (sample->shown == ENUMA_TH_CAP) {
			break;
		}
	}
	task_unlock(task);
	task_deallocate(task);

	for (unsigned int i = 0; i < sample->shown; ++i) {
		thread = refs[i];
		struct enuma_th_row *row = &sample->rows[i];
		if (!thread_mtx_try(thread)) {
			row->tid = thread->thread_id; /* Immutable after publication. */
			row->busy = true;
		} else {
			spl_t s = splsched();
			thread_lock(thread);
			row->tid = thread->thread_id;
			row->state = (unsigned int)thread->state;
			row->we = thread->wait_event;
			enuma_th_read_saved(thread, row);
			thread_unlock(thread);
			splx(s);
			thread_mtx_unlock(thread);
		}
		thread_deallocate(thread);
	}
}

static void
enuma_th_print(int pid, const struct enuma_th_sample *sample)
{
	if (sample->why != NULL) {
		printf("enuma-th: p=%d n=NA shown=0 why=%s\n", pid, sample->why);
		return;
	}
	printf("enuma-th: p=%d n=%d shown=%u\n", pid, sample->total, sample->shown);
	for (unsigned int i = 0; i < sample->shown; ++i) {
		const struct enuma_th_row *row = &sample->rows[i];
		if (row->busy) {
			printf("enuma-th: %d/%llu st=NA we=NA ct=NA pc=NA lr=NA why=busy\n",
			    pid, (unsigned long long)row->tid);
			continue;
		}
		char pc[19] = "NA", lr[19] = "NA";
		if (row->saved) {
			snprintf(pc, sizeof(pc), "0x%llx", (unsigned long long)row->pc);
			snprintf(lr, sizeof(lr), "0x%llx", (unsigned long long)row->lr);
		}
		printf("enuma-th: %d/%llu st=0x%x we=0x%llx ct=NA pc=%s lr=%s\n",
		    pid, (unsigned long long)row->tid, row->state,
		    (unsigned long long)row->we, pc, lr);
	}
}

static void
enuma_th_worker(thread_call_param_t tick, thread_call_param_t self)
{
	uint64_t ns;
	absolutetime_to_nanoseconds(mach_absolute_time(), &ns);
	struct enuma_th_sample bb = {}, sb = {};
	enuma_th_capture(34, "backboardd", &bb);
	enuma_th_capture(5, "SpringBoard", &sb);
	char slide[11] = "NA";
	if (bb.slide != UINT32_MAX) {
		snprintf(slide, sizeof(slide), "0x%x", bb.slide);
	}
	printf("enuma-th: tick=%u t=%llu slide=%s saved=possibly-stale/non-atomic\n",
	    (unsigned int)(uintptr_t)tick, (unsigned long long)(ns / NSEC_PER_SEC), slide);
	enuma_th_print(34, &bb);
	enuma_th_print(5, &sb);
	thread_call_free(self);
}

thread_call_t
enuma_th_alloc(unsigned int tick)
{
	int enabled = 0;
	if (!PE_parse_boot_argn("enuma-th", &enabled, sizeof(enabled)) || enabled != 1) {
		return NULL;
	}
	return thread_call_allocate_with_options(enuma_th_worker,
	    (thread_call_param_t)(uintptr_t)tick, THREAD_CALL_PRIORITY_KERNEL,
	    THREAD_CALL_OPTIONS_ONCE);
}
