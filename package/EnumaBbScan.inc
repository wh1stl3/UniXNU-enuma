/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Included only by the isolated r29 kern_exec.c. */
#include <kern/clock.h>
#include <kern/thread_call.h>

enum { ENUMA_FB_INTERVAL = 30, ENUMA_FB_REPORTS = 20 };
typedef unsigned __int128 enuma_fb_comm_t;
_Static_assert(__atomic_always_lock_free(sizeof(enuma_fb_comm_t), 0),
    "framebuffer count requires lock-free full-name atomics");
struct enuma_fb_counter {
	_Atomic(uint64_t) count;
	_Atomic(enuma_fb_comm_t) comm;
};
static struct enuma_fb_counter enuma_fb_starts, enuma_fb_clients;
static struct enuma_fb_counter enuma_fb_refreshes, enuma_fb_kicks;
static struct enuma_fb_counter enuma_fb_scanouts, enuma_fb_swaps;
struct enuma_fb_open {
	char comm[17];
	int pid;
	uint32_t type;
	int ret;
	_Atomic(unsigned int) complete;
};
static struct enuma_fb_open enuma_fb_opens[8];
static _Atomic(unsigned int) enuma_fb_open_next;
static _Atomic(unsigned int) enuma_fb_started, enuma_fb_finished;
static thread_call_t enuma_fb_call;
static unsigned int enuma_fb_reports;

struct enuma_bb_entry {
	char name[25];
	uint32_t type;
	int ret;
	_Atomic(unsigned int) complete;
};
static struct enuma_bb_entry enuma_bb_entries[12];
static _Atomic(unsigned int) enuma_bb_next;
static _Atomic(uint64_t) enuma_bb_calls, enuma_bb_overflow;

unsigned int
enuma_bb_record(const char *name, uint32_t type)
{
	proc_t p = current_proc();
	if (p == PROC_NULL || strcmp(p->p_comm, "backboardd") != 0)
		return 12;
	__c11_atomic_fetch_add(&enuma_bb_calls, 1, __ATOMIC_RELAXED);
	unsigned int slot = __c11_atomic_load(&enuma_bb_next, __ATOMIC_RELAXED);
	while (slot < 12 && !__c11_atomic_compare_exchange_weak(&enuma_bb_next,
	    &slot, slot + 1, __ATOMIC_RELAXED, __ATOMIC_RELAXED)) {}
	if (slot == 12) {
		__c11_atomic_fetch_add(&enuma_bb_overflow, 1, __ATOMIC_RELAXED);
	} else {
		strlcpy(enuma_bb_entries[slot].name, name && name[0] ? name : "-",
		    sizeof(enuma_bb_entries[slot].name));
		enuma_bb_entries[slot].type = type;
	}
	return slot;
}

void
enuma_bb_record_done(unsigned int slot, int ret)
{
	if (slot < 12) {
		enuma_bb_entries[slot].ret = ret;
		__c11_atomic_store(&enuma_bb_entries[slot].complete, 1, __ATOMIC_RELEASE);
	}
}

static void
enuma_fb_record(struct enuma_fb_counter *counter)
{
	if (__c11_atomic_load(&enuma_fb_finished, __ATOMIC_RELAXED)) return;
	char comm[17] = {0};
	proc_t p = current_proc();
	if (p != PROC_NULL && proc_getpid(p) != 0)
		strlcpy(comm, p->p_comm, sizeof(comm));
	enuma_fb_comm_t name;
	__builtin_memcpy(&name, comm, sizeof(name));
	__c11_atomic_store(&counter->comm, name, __ATOMIC_RELAXED);
	__c11_atomic_fetch_add(&counter->count, 1, __ATOMIC_RELEASE);
}
void enuma_fb_record_start(void) { enuma_fb_record(&enuma_fb_starts); }
unsigned int
enuma_fb_record_client(uint32_t type)
{
	if (__c11_atomic_load(&enuma_fb_finished, __ATOMIC_RELAXED)) return 8;
	enuma_fb_record(&enuma_fb_clients);
	unsigned int slot = __c11_atomic_load(&enuma_fb_open_next, __ATOMIC_RELAXED);
	while (slot < 8 && !__c11_atomic_compare_exchange_weak(&enuma_fb_open_next,
	    &slot, slot + 1, __ATOMIC_RELAXED, __ATOMIC_RELAXED)) {}
	if (slot < 8) {
		struct enuma_fb_open *entry = &enuma_fb_opens[slot];
		proc_t p = current_proc();
		entry->pid = p != PROC_NULL ? proc_getpid(p) : 0;
		if (p != PROC_NULL && entry->pid != 0)
			strlcpy(entry->comm, p->p_comm, sizeof(entry->comm));
		entry->type = type;
	}
	return slot;
}
void
enuma_fb_record_client_done(unsigned int slot, int ret)
{
	if (slot < 8) {
		enuma_fb_opens[slot].ret = ret;
		__c11_atomic_store(&enuma_fb_opens[slot].complete, 1, __ATOMIC_RELEASE);
	}
}
void enuma_fb_record_refresh(void) { enuma_fb_record(&enuma_fb_refreshes); }
void enuma_fb_record_kick(void) { enuma_fb_record(&enuma_fb_kicks); }
void enuma_fb_record_scanout(void) { enuma_fb_record(&enuma_fb_scanouts); }
void enuma_fb_record_swap(void) { enuma_fb_record(&enuma_fb_swaps); }

static void
enuma_fb_dump_line(struct enuma_fb_counter *counter, const char *fmt)
{
	uint64_t count = __c11_atomic_load(&counter->count, __ATOMIC_ACQUIRE);
	enuma_fb_comm_t name = __c11_atomic_load(&counter->comm, __ATOMIC_RELAXED);
	char comm[17] = {0};
	__builtin_memcpy(comm, &name, sizeof(name));
	printf(fmt, (unsigned long long)count, comm[0] ? comm : "-");
}
static void
enuma_fb_dump(__unused thread_call_param_t unused0, __unused thread_call_param_t unused1)
{
	uint64_t deadline;
	clock_interval_to_deadline(ENUMA_FB_INTERVAL, NSEC_PER_SEC, &deadline);
	printf("enuma-fb: begin\n");
	enuma_fb_dump_line(&enuma_fb_starts, "enuma-fb: start=%llu comm=%s\n");
	enuma_fb_dump_line(&enuma_fb_clients, "enuma-fb: open=%llu comm=%s\n");
	enuma_fb_dump_line(&enuma_fb_refreshes, "enuma-fb: refresh=%llu comm=%s\n");
	enuma_fb_dump_line(&enuma_fb_kicks, "enuma-fb: kick=%llu comm=%s\n");
	enuma_fb_dump_line(&enuma_fb_scanouts, "enuma-fb: scanout=%llu comm=%s\n");
	enuma_fb_dump_line(&enuma_fb_swaps, "enuma-fb: swap=%llu comm=%s\n");
	for (unsigned int i = 0; i < 8; i++) {
		struct enuma_fb_open *entry = &enuma_fb_opens[i];
		if (__c11_atomic_load(&entry->complete, __ATOMIC_ACQUIRE))
			printf("enuma-fb: open[%u]=%s pid=%d type=%u ret=%d\n", i,
			    entry->comm[0] ? entry->comm : "-", entry->pid,
			    entry->type, entry->ret);
		else
			printf("enuma-fb: open[%u]=-\n", i);
	}
	printf("enuma-fb: end\n");
	printf("enuma-bb: begin calls=%llu overflow=%llu\n",
	    (unsigned long long)__c11_atomic_load(&enuma_bb_calls, __ATOMIC_RELAXED),
	    (unsigned long long)__c11_atomic_load(&enuma_bb_overflow, __ATOMIC_RELAXED));
	for (unsigned int i = 0; i < 12; i++) {
		struct enuma_bb_entry *entry = &enuma_bb_entries[i];
		if (__c11_atomic_load(&entry->complete, __ATOMIC_ACQUIRE))
			printf("enuma-bb: [%u]=%s type=%u ret=%d\n",
			    i, entry->name, entry->type, entry->ret);
	}
	printf("enuma-bb: end\n");
	if (++enuma_fb_reports < ENUMA_FB_REPORTS)
		thread_call_enter_delayed(enuma_fb_call, deadline);
	else {
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
