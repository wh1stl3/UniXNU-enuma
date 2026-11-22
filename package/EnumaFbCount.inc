/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Included only by the r26 copy of kern_exec.c. */
#include <kern/clock.h>
#include <kern/thread_call.h>

enum { ENUMA_FB_INTERVAL = 30, ENUMA_FB_REPORTS = 20 };
typedef unsigned __int128 enuma_fb_comm_t;
_Static_assert(__atomic_always_lock_free(sizeof(enuma_fb_comm_t), 0),
    "framebuffer count requires lock-free full-name atomics");

static _Atomic(uint64_t) enuma_fb_starts, enuma_fb_clients, enuma_fb_swaps;
static _Atomic(enuma_fb_comm_t) enuma_fb_last_comm;
static _Atomic(unsigned int) enuma_fb_started, enuma_fb_finished;
static thread_call_t enuma_fb_call;
static unsigned int enuma_fb_reports;

static void
enuma_fb_record(_Atomic(uint64_t) *count)
{
	if (__c11_atomic_load(&enuma_fb_finished, __ATOMIC_RELAXED)) {
		return;
	}
	char comm[17] = {0};
	proc_t p = current_proc();
	if (p != PROC_NULL && proc_getpid(p) != 0) {
		strlcpy(comm, p->p_comm, sizeof(comm));
	}
	enuma_fb_comm_t name;
	__builtin_memcpy(&name, comm, sizeof(name));
	__c11_atomic_store(&enuma_fb_last_comm, name, __ATOMIC_RELAXED);
	__c11_atomic_fetch_add(count, 1, __ATOMIC_RELEASE);
}

void enuma_fb_record_start(void) { enuma_fb_record(&enuma_fb_starts); }
void enuma_fb_record_client(void) { enuma_fb_record(&enuma_fb_clients); }
void enuma_fb_record_swap(void) { enuma_fb_record(&enuma_fb_swaps); }

static void
enuma_fb_dump(__unused thread_call_param_t unused0, __unused thread_call_param_t unused1)
{
	uint64_t deadline;
	clock_interval_to_deadline(ENUMA_FB_INTERVAL, NSEC_PER_SEC, &deadline);
	uint64_t starts = __c11_atomic_load(&enuma_fb_starts, __ATOMIC_ACQUIRE);
	uint64_t clients = __c11_atomic_load(&enuma_fb_clients, __ATOMIC_ACQUIRE);
	uint64_t swaps = __c11_atomic_load(&enuma_fb_swaps, __ATOMIC_ACQUIRE);
	enuma_fb_comm_t name = __c11_atomic_load(&enuma_fb_last_comm, __ATOMIC_RELAXED);
	char comm[17] = {0};
	__builtin_memcpy(comm, &name, sizeof(name));
	printf("enuma-fb: begin\n");
	printf("enuma-fb: start=%llu userclient=%llu swap=%llu last_comm=%s\n",
	    (unsigned long long)starts, (unsigned long long)clients,
	    (unsigned long long)swaps, comm[0] ? comm : "-");
	printf("enuma-fb: end\n");
	if (++enuma_fb_reports < ENUMA_FB_REPORTS) {
		thread_call_enter_delayed(enuma_fb_call, deadline);
	} else {
		__c11_atomic_store(&enuma_fb_finished, 1, __ATOMIC_RELAXED);
		thread_call_free(enuma_fb_call);
	}
}

static __attribute__((noinline)) void
enuma_fb_arm(const char *name, int pid)
{
	if (pid == 1 && strcmp(name, "launchd") == 0 &&
	    !__c11_atomic_exchange(&enuma_fb_started, 1, __ATOMIC_RELAXED)) {
		uint64_t deadline;
		enuma_fb_call = thread_call_allocate_with_options(enuma_fb_dump, NULL,
		    THREAD_CALL_PRIORITY_KERNEL, THREAD_CALL_OPTIONS_ONCE);
		clock_interval_to_deadline(ENUMA_FB_INTERVAL, NSEC_PER_SEC, &deadline);
		thread_call_enter_delayed(enuma_fb_call, deadline);
	}
}
