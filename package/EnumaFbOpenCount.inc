/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Included only by the r27 copy of kern_exec.c. */
#include <kern/clock.h>
#include <kern/thread_call.h>

enum { ENUMA_FB_INTERVAL = 30, ENUMA_FB_REPORTS = 20 };
typedef unsigned __int128 enuma_fb_comm_t;
_Static_assert(sizeof(enuma_fb_comm_t) == MAXCOMLEN &&
    __atomic_always_lock_free(sizeof(enuma_fb_comm_t), 0),
    "framebuffer open probe requires lock-free full-comm atomics");

static _Atomic(uint64_t) enuma_fb_clients;
static _Atomic(enuma_fb_comm_t) enuma_fb_last_comm;
static _Atomic(unsigned int) enuma_fb_started;
static thread_call_t enuma_fb_call;
static unsigned int enuma_fb_reports;

void enuma_fb_record_open(void);

void
enuma_fb_record_open(void)
{
	char comm[MAXCOMLEN + 1] = {0};
	proc_t p = current_proc();
	if (p != PROC_NULL && proc_getpid(p) != 0) {
		strlcpy(comm, p->p_comm, sizeof(comm));
	}
	enuma_fb_comm_t name;
	__builtin_memcpy(&name, comm, sizeof(name));
	__c11_atomic_store(&enuma_fb_last_comm, name, __ATOMIC_RELAXED);
	__c11_atomic_fetch_add(&enuma_fb_clients, 1, __ATOMIC_RELEASE);
}

static void
enuma_fb_dump(__unused thread_call_param_t param0, __unused thread_call_param_t param1)
{
	uint64_t deadline;
	clock_interval_to_deadline(ENUMA_FB_INTERVAL, NSEC_PER_SEC, &deadline);
	uint64_t clients = __c11_atomic_load(&enuma_fb_clients, __ATOMIC_ACQUIRE);
	enuma_fb_comm_t name = __c11_atomic_load(&enuma_fb_last_comm, __ATOMIC_RELAXED);
	char comm[MAXCOMLEN + 1] = {0};
	__builtin_memcpy(comm, &name, sizeof(name));
	printf("enuma-fb: begin\n");
	printf("enuma-fb: fb_client=%llu last_comm=%s\n",
	    (unsigned long long)clients, clients && comm[0] ? comm : "-");
	printf("enuma-fb: end\n");
	if (++enuma_fb_reports < ENUMA_FB_REPORTS) {
		thread_call_enter_delayed(enuma_fb_call, deadline);
	} else {
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
