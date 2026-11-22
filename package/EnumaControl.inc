/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Included after the r29 counter declarations, only in the r30 candidate. */
struct enuma_ctl_entry {
	_Atomic(enuma_fb_comm_t) name;
	_Atomic(uint64_t) count;
};
static struct enuma_ctl_entry enuma_ctl_entries[8];
static _Atomic(uint64_t) enuma_ctl_all, enuma_ctl_bb, enuma_ctl_overflow;

static void
enuma_ctl_record(void)
{
	char comm[17] = {0};
	proc_t p = current_proc();
	if (p != PROC_NULL)
		strlcpy(comm, p->p_comm, sizeof(comm));
	if (!comm[0])
		comm[0] = '-';
	enuma_fb_comm_t name;
	__builtin_memcpy(&name, comm, sizeof(name));
	__c11_atomic_fetch_add(&enuma_ctl_all, 1, __ATOMIC_RELAXED);
	if (strcmp(comm, "backboardd") == 0)
		__c11_atomic_fetch_add(&enuma_ctl_bb, 1, __ATOMIC_RELAXED);
	for (unsigned int i = 0; i < 8; i++) {
		enuma_fb_comm_t found = __c11_atomic_load(&enuma_ctl_entries[i].name,
		    __ATOMIC_RELAXED);
		if (!found) {
			enuma_fb_comm_t empty = 0;
			if (__c11_atomic_compare_exchange_strong(&enuma_ctl_entries[i].name,
			    &empty, name, __ATOMIC_RELAXED, __ATOMIC_RELAXED))
				found = name;
			else
				found = empty;
		}
		if (found == name) {
			__c11_atomic_fetch_add(&enuma_ctl_entries[i].count, 1, __ATOMIC_RELAXED);
			return;
		}
	}
	__c11_atomic_fetch_add(&enuma_ctl_overflow, 1, __ATOMIC_RELAXED);
}

static void
enuma_ctl_dump(void)
{
	printf("enuma-ctl: begin all=%llu bb=%llu overflow=%llu\n",
	    (unsigned long long)__c11_atomic_load(&enuma_ctl_all, __ATOMIC_RELAXED),
	    (unsigned long long)__c11_atomic_load(&enuma_ctl_bb, __ATOMIC_RELAXED),
	    (unsigned long long)__c11_atomic_load(&enuma_ctl_overflow, __ATOMIC_RELAXED));
	for (unsigned int i = 0; i < 8; i++) {
		enuma_fb_comm_t name = __c11_atomic_load(&enuma_ctl_entries[i].name,
		    __ATOMIC_RELAXED);
		if (name) {
			char comm[17] = {0};
			__builtin_memcpy(comm, &name, sizeof(name));
			printf("enuma-ctl: [com] %s=%llu\n", comm,
			    (unsigned long long)__c11_atomic_load(&enuma_ctl_entries[i].count,
			    __ATOMIC_RELAXED));
		}
	}
	printf("enuma-ctl: end\n");
}
