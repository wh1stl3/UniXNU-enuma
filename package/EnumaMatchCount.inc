/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Included by the isolated r42 kern_exec.c recipe. */
enum { MT_M, MT_N, MT_O, MT_KINDS, MT_FIXED = 4, MT_HASH = 28, MT_TOP = 6 };
_Static_assert(__atomic_always_lock_free(sizeof(unsigned int), 0),
    "match counters require lock-free word atomics");

struct enuma_mt_slot {
	_Atomic(unsigned int) pid;
	_Atomic(unsigned int) counts[MT_KINDS];
};

static const unsigned int enuma_mt_pids[MT_FIXED] = {34, 5, 56, 66};
static const char *const enuma_mt_names[MT_FIXED] = {"bb", "sb", "fb", "fb"};
static struct enuma_mt_slot enuma_mt_fixed[MT_FIXED], enuma_mt_hash[MT_HASH];
static struct enuma_mt_slot enuma_mt_other;
static _Atomic(unsigned int) enuma_mt_bb_exec, enuma_mt_printed;

void
enuma_matchcnt_record(unsigned int kind, int caller)
{
	unsigned int pid = (unsigned int)caller;
	struct enuma_mt_slot *slot = &enuma_mt_other;
	for (unsigned int i = 0; i < MT_FIXED; ++i) {
		if (pid == enuma_mt_pids[i]) {
			slot = &enuma_mt_fixed[i];
			goto record;
		}
	}
	if (caller > 0) {
		unsigned int index = pid % MT_HASH;
		for (unsigned int i = 0; i < MT_HASH; ++i) {
			struct enuma_mt_slot *candidate = &enuma_mt_hash[index];
			unsigned int key = __c11_atomic_load(&candidate->pid, __ATOMIC_RELAXED);
			if (key == pid || (key == 0 &&
			    (__c11_atomic_compare_exchange_strong(&candidate->pid, &key, pid,
			    __ATOMIC_RELAXED, __ATOMIC_RELAXED) || key == pid))) {
				slot = candidate;
				break;
			}
			if (++index == MT_HASH) {
				index = 0;
			}
		}
	}
record:
	__c11_atomic_fetch_add(&slot->counts[kind], 1, __ATOMIC_RELAXED);
}

struct enuma_mt_row {
	unsigned int pid;
	unsigned int counts[MT_KINDS];
	uint64_t total;
};

static struct enuma_mt_row
enuma_mt_read(struct enuma_mt_slot *slot, unsigned int pid, unsigned int *all)
{
	struct enuma_mt_row row = {.pid = pid};
	for (unsigned int i = 0; i < MT_KINDS; ++i) {
		row.counts[i] = __c11_atomic_load(&slot->counts[i], __ATOMIC_RELAXED);
		row.total += row.counts[i];
		all[i] += row.counts[i];
	}
	return row;
}

static __attribute__((noinline)) void
enuma_matchcnt_dump(void)
{
	if (!__c11_atomic_load(&enuma_mt_bb_exec, __ATOMIC_ACQUIRE) ||
	    __c11_atomic_exchange(&enuma_mt_printed, 1, __ATOMIC_RELAXED)) {
		return;
	}
	uint64_t ns;
	absolutetime_to_nanoseconds(mach_absolute_time(), &ns);
	unsigned int all[MT_KINDS] = {0};
	struct enuma_mt_row fixed[MT_FIXED], top[MT_TOP] = {0};
	struct enuma_mt_row other = enuma_mt_read(&enuma_mt_other, 0, all);
	for (unsigned int i = 0; i < MT_FIXED; ++i) {
		fixed[i] = enuma_mt_read(&enuma_mt_fixed[i], enuma_mt_pids[i], all);
	}
	for (unsigned int i = 0; i < MT_HASH; ++i) {
		unsigned int pid = __c11_atomic_load(&enuma_mt_hash[i].pid, __ATOMIC_RELAXED);
		if (!pid) {
			continue;
		}
		struct enuma_mt_row row = enuma_mt_read(&enuma_mt_hash[i], pid, all);
		if (!row.total) {
			continue;
		}
		for (unsigned int j = 0; j < MT_TOP; ++j) {
			if (row.total > top[j].total ||
			    (row.total == top[j].total && row.pid < top[j].pid)) {
				for (unsigned int k = MT_TOP - 1; k > j; --k) {
					top[k] = top[k - 1];
				}
				top[j] = row;
				break;
			}
		}
	}
	/* Unlabelled header tuples are all and other, respectively. */
	printf("enuma-mt: t=%u %x/%x/%x %x/%x/%x\n",
	    (unsigned int)(ns / NSEC_PER_SEC), all[MT_M], all[MT_N], all[MT_O],
	    other.counts[MT_M], other.counts[MT_N], other.counts[MT_O]);
	for (unsigned int i = 0; i < MT_FIXED; ++i) {
		printf("enuma-mt: %s(%u)=%x/%x/%x\n", enuma_mt_names[i], fixed[i].pid,
		    fixed[i].counts[MT_M], fixed[i].counts[MT_N], fixed[i].counts[MT_O]);
	}
	for (unsigned int i = 0; i < MT_TOP && top[i].pid; i += 2) {
		struct enuma_mt_row *a = &top[i], *b = a + 1;
		if (b->pid) {
			printf("enuma-mt: %x:%08x%08x%08x %x:%08x%08x%08x\n",
			    a->pid, a->counts[MT_M], a->counts[MT_N], a->counts[MT_O],
			    b->pid, b->counts[MT_M], b->counts[MT_N], b->counts[MT_O]);
		} else {
			printf("enuma-mt: %x:%08x%08x%08x\n",
			    a->pid, a->counts[MT_M], a->counts[MT_N], a->counts[MT_O]);
		}
	}
}
