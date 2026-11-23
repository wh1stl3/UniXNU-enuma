/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* r64-only diagnostic; compiled with the OSFMK private layout. */
#include <kern/spl.h>
#include <kern/task.h>
#include <kern/thread.h>
#include <kern/thread_call.h>
#include <mach/arm/thread_status.h>
#include <vm/vm_map.h>

extern task_t enuma_th_task_ref(int pid, const char *comm, const char **why);
void enuma_stk_submit(void);

enum { ENUMA_STK_THREADS = 8, ENUMA_STK_WORDS = 64 };
/* iPad7,1 / 21H461 libsystem_kernel, saved return PC after svc. */
static const uint64_t enuma_stk_trap_pc = 0x1cb780b58ULL;

static uint64_t
enuma_stk_wait_sp(thread_t thread, uint64_t expected_pc)
{
	uint64_t sp = 0;
	if (!thread_mtx_try(thread)) {
		return 0;
	}
	spl_t s = splsched();
	thread_lock(thread);
	if ((thread->state & (TH_WAIT | TH_RUN | TH_TERMINATE | TH_TERMINATE2)) == TH_WAIT) {
		const arm_saved_state_t *upcb = os_atomic_load(&thread->machine.upcb, relaxed);
		if (upcb != NULL &&
		    os_atomic_load(&upcb->ash.flavor, relaxed) == ARM_SAVED_STATE64 &&
		    os_atomic_load(&upcb->ash.count, relaxed) == ARM_SAVED_STATE64_COUNT &&
		    PSR64_IS_USER64(os_atomic_load(&upcb->ss_64.cpsr, relaxed)) &&
		    os_atomic_load(&upcb->ss_64.pc, relaxed) == expected_pc) {
			sp = os_atomic_load(&upcb->ss_64.sp, relaxed);
		}
	}
	thread_unlock(thread);
	splx(s);
	thread_mtx_unlock(thread);
	return sp;
}

static bool
enuma_stk_same_map(task_t task, vm_map_t map, uint32_t slide)
{
	if (!task_lock_try(task)) {
		return false;
	}
	bool same = task->active && get_task_map(task) == map &&
	    os_atomic_load(&task->task_shared_region_slide, relaxed) == slide;
	task_unlock(task);
	return same;
}

static __attribute__((noinline)) void
enuma_stk_capture(int pid, const char *comm)
{
	const char *why = NULL;
	task_t task = enuma_th_task_ref(pid, comm, &why);
	vm_map_t map = VM_MAP_NULL;
	thread_t refs[ENUMA_STK_THREADS], thread, selected = THREAD_NULL;
	unsigned int count = 0;
	uint32_t slide = 0;
	uint64_t sp = 0;
	uint64_t words[ENUMA_STK_WORDS];
	kern_return_t kr = KERN_SUCCESS;
	if (task == TASK_NULL) {
		goto out;
	}
	map = get_task_map_reference(task);
	if (map == VM_MAP_NULL) {
		why = "inactive-task";
		goto out;
	}
	if (!task_lock_try(task)) {
		why = "task-busy";
		goto out;
	}
	if (!task->active || get_task_map(task) != map) {
		task_unlock(task);
		why = "task-map-changed";
		goto out;
	}
	slide = os_atomic_load(&task->task_shared_region_slide, relaxed);
	queue_iterate(&task->threads, thread, thread_t, task_threads) {
		thread_reference(thread);
		refs[count++] = thread;
		if (count == ENUMA_STK_THREADS) {
			break;
		}
	}
	task_unlock(task);

	const uint64_t expected_pc = enuma_stk_trap_pc + slide;
	for (unsigned int i = 0; i < count; ++i) {
		thread = refs[i];
		uint64_t candidate_sp = enuma_stk_wait_sp(thread, expected_pc);
		if (candidate_sp != 0 && selected == THREAD_NULL) {
			selected = thread;
			sp = candidate_sp;
		} else {
			thread_deallocate(thread);
			if (candidate_sp != 0) {
				why = "multiple-trap-waits";
			}
		}
	}
	if (why != NULL) {
		goto out;
	}
	if (selected == THREAD_NULL) {
		why = "no-sampled-trap-wait";
		goto out;
	}
	if (!enuma_stk_same_map(task, map, slide) ||
	    enuma_stk_wait_sp(selected, expected_pc) != sp) {
		why = "sample-changed-before-copy";
		goto out;
	}
	/* Task, map and thread references only: no lock or raised IPL across copyin. */
	kr = vm_map_read_user(map, sp, words, sizeof(words));
	if (kr != KERN_SUCCESS) {
		goto out;
	}
	if (enuma_stk_wait_sp(selected, expected_pc) != sp ||
	    !enuma_stk_same_map(task, map, slide)) {
		why = "sample-changed-after-copy";
	}

out:
	if (selected != THREAD_NULL) {
		thread_deallocate(selected);
	}
	if (map != VM_MAP_NULL) {
		vm_map_deallocate(map);
	}
	if (task != TASK_NULL) {
		task_deallocate(task);
	}
	if (kr != KERN_SUCCESS) {
		printf("enuma-stk: p=%d why=vm_map_read_user kr=%d n=0\n", pid, kr);
		return;
	}
	if (why != NULL) {
		printf("enuma-stk: p=%d why=%s\n", pid, why);
		return;
	}
	printf("enuma-stk: p=%d slide=0x%x sp=0x%llx n=%u\n",
	    pid, slide, (unsigned long long)sp, (unsigned int)ENUMA_STK_WORDS);
	for (unsigned int i = 0; i < ENUMA_STK_WORDS; i += 4) {
		printf("enuma-stk: %d 0x%llx 0x%llx 0x%llx 0x%llx\n", pid,
		    (unsigned long long)words[i], (unsigned long long)words[i + 1],
		    (unsigned long long)words[i + 2], (unsigned long long)words[i + 3]);
	}
}

static void
enuma_stk_worker(__unused thread_call_param_t unused, thread_call_param_t self)
{
	enuma_stk_capture(5, "SpringBoard");
	enuma_stk_capture(34, "backboardd");
	thread_call_free(self);
}

void
enuma_stk_submit(void)
{
	thread_call_t call = thread_call_allocate_with_options(enuma_stk_worker,
	    NULL, THREAD_CALL_PRIORITY_KERNEL, THREAD_CALL_OPTIONS_ONCE);
	if (call == NULL) {
		printf("enuma-stk: p=%d why=callout-allocation\n", 5);
		printf("enuma-stk: p=%d why=callout-allocation\n", 34);
		return;
	}
	thread_call_enter1(call, call);
}
