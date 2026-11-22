/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Isolated r32 observations; counters are not a transactional snapshot. */
static _Atomic(uint64_t) att_entry, att_entry_bb, att_mac, att_mac_bb;
static _Atomic(uint64_t) att_early, att_early_bb;
static struct enuma_ctl_entry att_names[6];

static bool
att_is_bb(void)
{
	proc_t p = current_proc();
	return p != PROC_NULL && strcmp(p->p_comm, "backboardd") == 0;
}

void
enuma_att_record(unsigned int kind)
{
	bool bb = att_is_bb();
	_Atomic(uint64_t) *all = kind == 0 ? &att_entry : kind == 1 ? &att_mac : &att_early;
	_Atomic(uint64_t) *only = kind == 0 ? &att_entry_bb : kind == 1 ? &att_mac_bb : &att_early_bb;
	__c11_atomic_fetch_add(all, 1, __ATOMIC_RELAXED);
	if (bb)
		__c11_atomic_fetch_add(only, 1, __ATOMIC_RELAXED);
	if (kind == 0) {
		char comm[17] = {0};
		proc_t p = current_proc();
		if (p != PROC_NULL)
			strlcpy(comm, p->p_comm, sizeof(comm));
		if (!comm[0])
			comm[0] = '-';
		enuma_fb_comm_t name;
		__builtin_memcpy(&name, comm, sizeof(name));
		for (unsigned int i = 0; i < 6; i++) {
			enuma_fb_comm_t found = __c11_atomic_load(&att_names[i].name, __ATOMIC_RELAXED);
			if (!found) {
				enuma_fb_comm_t empty = 0;
				if (__c11_atomic_compare_exchange_strong(&att_names[i].name,
				    &empty, name, __ATOMIC_RELAXED, __ATOMIC_RELAXED))
					found = name;
				else
					found = empty;
			}
			if (found == name) {
				__c11_atomic_fetch_add(&att_names[i].count, 1, __ATOMIC_RELAXED);
				break;
			}
		}
	}
}

static void
enuma_att_dump(void)
{
	printf("enuma-att: begin entry=%llu entry_bb=%llu mac_rej=%llu mac_rej_bb=%llu early_rej=%llu early_rej_bb=%llu\n",
	    (unsigned long long)__c11_atomic_load(&att_entry, __ATOMIC_RELAXED),
	    (unsigned long long)__c11_atomic_load(&att_entry_bb, __ATOMIC_RELAXED),
	    (unsigned long long)__c11_atomic_load(&att_mac, __ATOMIC_RELAXED),
	    (unsigned long long)__c11_atomic_load(&att_mac_bb, __ATOMIC_RELAXED),
	    (unsigned long long)__c11_atomic_load(&att_early, __ATOMIC_RELAXED),
	    (unsigned long long)__c11_atomic_load(&att_early_bb, __ATOMIC_RELAXED));
	for (unsigned int i = 0; i < 6; i++) {
		enuma_fb_comm_t name = __c11_atomic_load(&att_names[i].name, __ATOMIC_RELAXED);
		if (name) {
			char comm[17] = {0};
			__builtin_memcpy(comm, &name, sizeof(name));
			printf("enuma-att: [com] %s=%llu\n", comm,
			    (unsigned long long)__c11_atomic_load(&att_names[i].count, __ATOMIC_RELAXED));
		}
	}
	printf("enuma-att: end\n");
}
