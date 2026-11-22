/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Included only by r25's kern_exec.c. */
#include "EnumaProcessCensus.h"
#include <kern/clock.h>
#include <kern/thread_call.h>
#include <sys/wait.h>

#define ENUMA_CENSUS_CAPACITY 64
#define ENUMA_CENSUS_INTERVAL 30
#define ENUMA_CENSUS_REPORTS 20

typedef unsigned __int128 enuma_comm_key;
_Static_assert(__atomic_always_lock_free(sizeof(enuma_comm_key), 0),
    "census requires lock-free full-name atomics");

struct enuma_census_entry {
	_Atomic(enuma_comm_key) name;
	_Atomic(uint32_t) exec;
	/* High 32 bits: count. Low 32 bits: raw wait status of that exit. */
	_Atomic(uint64_t) exit_state;
};

static struct enuma_census_entry enuma_census_table[ENUMA_CENSUS_CAPACITY];
static _Atomic(unsigned int) enuma_census_overflow;
static _Atomic(unsigned int) enuma_census_started;
static _Atomic(unsigned int) enuma_census_finished;
static thread_call_t enuma_census_call;
static unsigned int enuma_census_reports;

static struct enuma_census_entry *
enuma_census_find(const char *name)
{
	char comm[17] = {0};
	enuma_comm_key key;

	if (__c11_atomic_load(&enuma_census_finished, __ATOMIC_RELAXED)) {
		return NULL;
	}
	strlcpy(comm, name, sizeof(comm));
	__builtin_memcpy(&key, comm, sizeof(key));
	/* Zero is the empty slot; 0x100 cannot be a zero-padded nonempty
	 * string on the little-endian target. */
	if (key == 0) {
		key = 0x100;
	}
	for (unsigned int i = 0; i < ENUMA_CENSUS_CAPACITY; i++) {
		struct enuma_census_entry *entry = &enuma_census_table[i];
		enuma_comm_key observed = 0;
		/* On failure this also reads the published, immutable key. */
		if (__c11_atomic_compare_exchange_strong(&entry->name, &observed,
		    key, __ATOMIC_ACQ_REL, __ATOMIC_ACQUIRE) || observed == key) {
			return entry;
		}
	}
	/* 0: not overflowed, 1: pending notice, 2: already reported. */
	unsigned int clear = 0;
	(void)__c11_atomic_compare_exchange_strong(&enuma_census_overflow,
	    &clear, 1, __ATOMIC_RELAXED, __ATOMIC_RELAXED);
	return NULL;
}

void
enuma_census_record_exit(const char *name, int status)
{
	struct enuma_census_entry *entry = enuma_census_find(name);
	if (entry == NULL) {
		return;
	}
	uint64_t old = __c11_atomic_load(&entry->exit_state, __ATOMIC_RELAXED);
	uint64_t next;
	do {
		next = ((old & 0xffffffff00000000ULL) + (1ULL << 32)) | (uint32_t)status;
	} while (!__c11_atomic_compare_exchange_weak(&entry->exit_state, &old,
	    next, __ATOMIC_RELEASE, __ATOMIC_RELAXED));
}

static void
enuma_census_dump(__unused thread_call_param_t unused0, __unused thread_call_param_t unused1)
{
	struct {
		enuma_comm_key name;
		uint64_t exit_state;
		uint32_t exec;
	} rows[ENUMA_CENSUS_CAPACITY];
	unsigned int n = 0;
	uint64_t deadline;

	clock_interval_to_deadline(ENUMA_CENSUS_INTERVAL, NSEC_PER_SEC, &deadline);
	for (unsigned int i = 0; i < ENUMA_CENSUS_CAPACITY; i++) {
		struct enuma_census_entry *entry = &enuma_census_table[i];
		uint32_t exec = __c11_atomic_load(&entry->exec, __ATOMIC_ACQUIRE);
		uint64_t exit_state = __c11_atomic_load(&entry->exit_state, __ATOMIC_ACQUIRE);
		/* A slot reserved by a producer but not yet counted appears
		 * in a subsequent snapshot. No producer or callout lock here. */
		if (exec == 0 && exit_state == 0) {
			continue;
		}
		rows[n].name = __c11_atomic_load(&entry->name, __ATOMIC_RELAXED);
		rows[n].exit_state = exit_state;
		rows[n].exec = exec;
		n++;
	}
	printf("enuma-census: begin n=%u\n", n);
	for (unsigned int i = 0; i < n; i++) {
		char comm[17] = {0};
		if (rows[i].name != 0x100) {
			__builtin_memcpy(comm, &rows[i].name, 16);
		}
		uint32_t exits = (uint32_t)(rows[i].exit_state >> 32);
		int status = (int)(uint32_t)rows[i].exit_state;
		int sig = WIFSIGNALED(status) ? WTERMSIG(status) : 0;
		printf("enuma-census: %s exec=%u exit=%u last_st=%d last_sig=%d\n",
		    comm, rows[i].exec, exits, status, sig);
	}
	printf("enuma-census: end\n");
	unsigned int pending = 1;
	if (__c11_atomic_compare_exchange_strong(&enuma_census_overflow,
	    &pending, 2, __ATOMIC_RELAXED, __ATOMIC_RELAXED)) {
		printf("enuma-census: table-full\n");
	}
	if (++enuma_census_reports < ENUMA_CENSUS_REPORTS) {
		thread_call_enter_delayed(enuma_census_call, deadline);
	} else {
		__c11_atomic_store(&enuma_census_finished, 1, __ATOMIC_RELAXED);
		thread_call_free(enuma_census_call);
	}
}

static __attribute__((noinline)) void
enuma_census_record_exec(const char *name, int pid)
{
	struct enuma_census_entry *entry = enuma_census_find(name);
	if (entry != NULL) {
		__c11_atomic_fetch_add(&entry->exec, 1, __ATOMIC_RELEASE);
	}
	if (pid == 1 && strcmp(name, "launchd") == 0 &&
	    !__c11_atomic_exchange(&enuma_census_started, 1, __ATOMIC_RELAXED)) {
		uint64_t deadline;
		enuma_census_call = thread_call_allocate_with_options(enuma_census_dump, NULL,
		    THREAD_CALL_PRIORITY_KERNEL, THREAD_CALL_OPTIONS_ONCE);
		clock_interval_to_deadline(ENUMA_CENSUS_INTERVAL, NSEC_PER_SEC, &deadline);
		thread_call_enter_delayed(enuma_census_call, deadline);
	}
}
