/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Included by the isolated r43 kern_exec.c recipe. */
enum { MT_M, MT_N, MT_O, MT_P, MT_I, MT_KINDS, MT_FIXED = 4, MT_HASH = 28, MT_TOP = 3 };
enum { MT_TOP_TUPLE = 5 + MT_KINDS * 8, MT_TOP_HEAD = 68 };
_Static_assert(__atomic_always_lock_free(sizeof(unsigned int), 0),
    "match counters require lock-free word atomics");
_Static_assert(PID_MAX <= 0xfffff, "top PID field must fit five hex digits");

struct enuma_mt_slot {
	_Atomic(unsigned int) pid;
	_Atomic(unsigned int) counts[MT_KINDS];
};

static const unsigned int enuma_mt_pids[MT_FIXED] = {34, 5, 56, 66};
static struct enuma_mt_slot enuma_mt_fixed[MT_FIXED], enuma_mt_hash[MT_HASH];
static struct enuma_mt_slot enuma_mt_other;
static _Atomic(unsigned int) enuma_mt_armed;

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

static void
enuma_mt_rank(struct enuma_mt_row *top, struct enuma_mt_row row)
{
	if (!row.total) {
		return;
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

static __attribute__((noinline)) void
enuma_matchcnt_dump(void)
{
	uint64_t ns;
	absolutetime_to_nanoseconds(mach_absolute_time(), &ns);
	unsigned int all[MT_KINDS] = {0};
	struct enuma_mt_row top[MT_TOP] = {0};
	struct enuma_mt_row other = enuma_mt_read(&enuma_mt_other, 0, all);
	struct enuma_mt_row bb = enuma_mt_read(&enuma_mt_fixed[0], enuma_mt_pids[0], all);
	struct enuma_mt_row sb = enuma_mt_read(&enuma_mt_fixed[1], enuma_mt_pids[1], all);
	for (unsigned int i = 2; i < MT_FIXED; ++i) {
		enuma_mt_rank(top, enuma_mt_read(&enuma_mt_fixed[i], enuma_mt_pids[i], all));
	}
	for (unsigned int i = 0; i < MT_HASH; ++i) {
		unsigned int pid = __c11_atomic_load(&enuma_mt_hash[i].pid, __ATOMIC_RELAXED);
		if (pid) {
			enuma_mt_rank(top, enuma_mt_read(&enuma_mt_hash[i], pid, all));
		}
	}
	printf("enuma-mt: t=%u all=%x/%x/%x/%x/%x\n", (unsigned int)(ns / NSEC_PER_SEC),
	    all[MT_M], all[MT_N], all[MT_O], all[MT_P], all[MT_I]);
	printf("enuma-mt: other=%x/%x/%x/%x/%x\n",
	    other.counts[MT_M], other.counts[MT_N], other.counts[MT_O], other.counts[MT_P], other.counts[MT_I]);
	printf("enuma-mt: bb(34)=%x/%x/%x/%x/%x\n",
	    bb.counts[MT_M], bb.counts[MT_N], bb.counts[MT_O], bb.counts[MT_P], bb.counts[MT_I]);
	printf("enuma-mt: sb(5)=%x/%x/%x/%x/%x\n",
	    sb.counts[MT_M], sb.counts[MT_N], sb.counts[MT_O], sb.counts[MT_P], sb.counts[MT_I]);

	/* Hex widths preserve the full word counts within two console lines. */
	char packed[MT_TOP * MT_TOP_TUPLE + 1];
	unsigned int len = 0;
	for (unsigned int i = 0; i < MT_TOP && top[i].pid; ++i) {
		struct enuma_mt_row *row = &top[i];
		snprintf(packed + len, MT_TOP_TUPLE + 1, "%05x%08x%08x%08x%08x%08x", row->pid,
		    row->counts[MT_M], row->counts[MT_N], row->counts[MT_O], row->counts[MT_P], row->counts[MT_I]);
		len += MT_TOP_TUPLE;
	}
	if (len) {
		printf("enuma-mt: A%.68s\n", packed);
	}
	if (len > MT_TOP_HEAD) {
		printf("enuma-mt: B%s\n", packed + MT_TOP_HEAD);
	}
}
