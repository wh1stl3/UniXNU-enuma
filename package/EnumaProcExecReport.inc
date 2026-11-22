/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Included only by the isolated r45 kern_exec.c build. */
#include <kern/locks.h>

enum { EPS_NAME = 16, EPS_PER_LINE = 6, EPS_KEEP = 23 * EPS_PER_LINE, EEX_LAST = 3 };
_Static_assert(MAXCOMLEN >= EPS_NAME, "short proc name must fit the snapshot");

static void
enuma_short_name(char dst[EPS_NAME + 1], const char *src, size_t size)
{
	size_t i = 0;
	if (src != NULL) {
		for (; i < EPS_NAME && i < size; ++i) {
			unsigned char ch = src[i];
			if (ch == 0) {
				break;
			}
			dst[i] = (ch <= ' ' || ch >= 127 || ch == ':') ? '_' : ch;
		}
	}
	dst[i] = '\0';
}

struct enuma_ps_row { pid_t pid; char name[EPS_NAME + 1]; };

/* Only the existing single-shot report uses this buffer. */
static struct enuma_ps_row enuma_ps_rows[EPS_KEEP];

static void
enuma_ps_down(struct enuma_ps_row *rows, unsigned int size, unsigned int pos)
{
	struct enuma_ps_row row = rows[pos];
	for (unsigned int child = pos * 2 + 1; child < size; child = pos * 2 + 1) {
		if (child + 1 < size && rows[child + 1].pid > rows[child].pid) {
			++child;
		}
		if (row.pid >= rows[child].pid) {
			break;
		}
		rows[pos] = rows[child];
		pos = child;
	}
	rows[pos] = row;
}

static __attribute__((noinline)) void
enuma_ps_dump(void)
{
	struct enuma_ps_row *rows = enuma_ps_rows;
	unsigned int total = 0, kept = 0;
	proc_t p;

	proc_list_lock();
	ALLPROC_FOREACH(p) {
		pid_t pid = proc_getpid(p);
		++total;
		if (kept == EPS_KEEP && pid >= rows[0].pid) {
			continue;
		}
		struct enuma_ps_row row = {.pid = pid};
		enuma_short_name(row.name, p->p_comm, sizeof(p->p_comm));
		if (kept == EPS_KEEP) {
			rows[0] = row;
			enuma_ps_down(rows, kept, 0);
		} else {
			unsigned int pos = kept++;
			while (pos && rows[(pos - 1) / 2].pid < pid) {
				rows[pos] = rows[(pos - 1) / 2];
				pos = (pos - 1) / 2;
			}
			rows[pos] = row;
		}
	}
	proc_list_unlock();

	for (unsigned int end = kept; end > 1;) {
		struct enuma_ps_row largest = rows[0];
		rows[0] = rows[--end];
		rows[end] = largest;
		enuma_ps_down(rows, end, 0);
	}
	printf("enuma-ps: n=%u\n", total);
	for (unsigned int i = 0; i < kept;) {
		char line[EPS_PER_LINE * (11 + 1 + EPS_NAME + 1) + 1];
		size_t len = 0;
		for (unsigned int j = 0; j < EPS_PER_LINE && i < kept; ++j, ++i) {
			len += snprintf(line + len, sizeof(line) - len, "%s%d:%s",
			    j ? " " : "", rows[i].pid, rows[i].name[0] ? rows[i].name : "-");
		}
		printf("enuma-ps: %s\n", line);
	}
	if (total > kept) {
		printf("enuma-ps: +%umore\n", total - kept);
	}
}

enum { EEX_SP, EEX_DYLD, EEX_NOENT, EEX_PERM, EEX_OTH, EEX_BUCKETS };
static const char *const enuma_ex_tags[EEX_BUCKETS] = {"sp", "dyld", "noent", "perm", "oth"};
struct enuma_exec_observation {
	bool reached, failed;
	unsigned int bucket, ns;
	uint64_t code;
	int error;
	char name[EPS_NAME + 1];
};

static void
enuma_ex_failure(struct enuma_exec_observation *obs, os_reason_t why, int error,
    const char *name, size_t size)
{
	if (obs->failed) {
		return;
	}
	obs->failed = true;
	obs->error = error;
	if (why != OS_REASON_NULL) {
		obs->ns = why->osr_namespace;
		obs->code = why->osr_code;
	}
	if (obs->ns == OS_REASON_EXEC && obs->code == EXEC_EXIT_REASON_SECURITY_POLICY) {
		obs->bucket = EEX_SP;
	} else if (obs->ns == OS_REASON_EXEC && (obs->code == EXEC_EXIT_REASON_COPYOUT_DYNLINKER ||
	    obs->code == EXEC_EXIT_REASON_SET_DYLD_INFO)) {
		obs->bucket = EEX_DYLD;
	} else if (obs->ns == 0 && error == ENOENT) {
		obs->bucket = EEX_NOENT;
	} else if (obs->ns == 0 && (error == EPERM || error == EACCES)) {
		obs->bucket = EEX_PERM;
	} else {
		obs->bucket = EEX_OTH;
	}
	enuma_short_name(obs->name, name, size);
}

static LCK_GRP_DECLARE(enuma_ex_group, "enuma-ex");
static LCK_SPIN_DECLARE(enuma_ex_lock, &enuma_ex_group);
static unsigned int enuma_ex_ok, enuma_ex_fail, enuma_ex_bins[EEX_BUCKETS], enuma_ex_next, enuma_ex_used;
static unsigned int enuma_ex_report_done;
static struct enuma_exec_observation enuma_ex_last[EEX_LAST];

static __attribute__((noinline)) void
enuma_ex_finish(const struct enuma_exec_observation *obs)
{
	if (!obs->failed) {
		if (obs->reached) {
			os_atomic_inc(&enuma_ex_ok, relaxed);
		}
		return;
	}
	lck_spin_lock(&enuma_ex_lock);
	++enuma_ex_fail;
	++enuma_ex_bins[obs->bucket];
	enuma_ex_last[enuma_ex_next] = *obs;
	enuma_ex_next = (enuma_ex_next + 1) % EEX_LAST;
	if (enuma_ex_used < EEX_LAST) {
		++enuma_ex_used;
	}
	lck_spin_unlock(&enuma_ex_lock);
}

static __attribute__((noinline)) void
enuma_ex_dump(void)
{
	struct enuma_exec_observation last[EEX_LAST];
	unsigned int bins[EEX_BUCKETS];
	lck_spin_lock(&enuma_ex_lock);
	unsigned int fail = enuma_ex_fail, used = enuma_ex_used;
	__builtin_memcpy(bins, enuma_ex_bins, sizeof(bins));
	for (unsigned int i = 0; i < used; ++i) {
		last[i] = enuma_ex_last[(enuma_ex_next + EEX_LAST - 1 - i) % EEX_LAST];
	}
	lck_spin_unlock(&enuma_ex_lock);
	printf("enuma-ex: ok=%u fail=%u\n", os_atomic_load(&enuma_ex_ok, relaxed), fail);
	char line[EEX_BUCKETS * 18 + 1];
	size_t len = 0;
	for (unsigned int i = 0; i < EEX_BUCKETS; ++i) {
		if (bins[i]) {
			len += snprintf(line + len, sizeof(line) - len, "%sr%s=%u",
			    len ? " " : "", enuma_ex_tags[i], bins[i]);
		}
	}
	if (len) {
		printf("enuma-ex: %s\n", line);
	}
	/* A single logical line, up to three records. Namespace 0 means errno. */
	char recent[EEX_LAST * (EPS_NAME + 1 + 5 + 11 + 1 + 20 + 1) + 1];
	len = 0;
	for (unsigned int i = 0; i < used; ++i) {
		const struct enuma_exec_observation *r = &last[i];
		len += snprintf(recent + len, sizeof(recent) - len, "%s%s%s%s/%u.%llu",
		    i ? " " : "", r->name, r->name[0] ? ":" : "",
		    enuma_ex_tags[r->bucket], r->ns,
		    (unsigned long long)(r->ns ? r->code : (unsigned int)r->error));
	}
	if (len) {
		printf("enuma-ex: last %s\n", recent);
	}
}
