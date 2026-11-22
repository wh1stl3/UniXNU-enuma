/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Request and successful-return counters; independently sampled. */
static _Atomic(uint64_t) match_all[2], match_bb[2], match_sb[2];

void
enuma_match_record(unsigned int done)
{
	proc_t p = current_proc();
	__c11_atomic_fetch_add(&match_all[done], 1, __ATOMIC_RELAXED);
	if (p == PROC_NULL)
		return;
	if (p->p_comm[0] == 'b' && strcmp(p->p_comm, "backboardd") == 0)
		__c11_atomic_fetch_add(&match_bb[done], 1, __ATOMIC_RELAXED);
	else if (p->p_comm[0] == 'S' && strcmp(p->p_comm, "SpringBoard") == 0)
		__c11_atomic_fetch_add(&match_sb[done], 1, __ATOMIC_RELAXED);
}

static void
enuma_match_dump(void)
{
	printf("enuma-match: begin all=%llu bb=%llu sb=%llu ok=%llu/%llu/%llu\n",
	    (unsigned long long)__c11_atomic_load(&match_all[0], __ATOMIC_RELAXED),
	    (unsigned long long)__c11_atomic_load(&match_bb[0], __ATOMIC_RELAXED),
	    (unsigned long long)__c11_atomic_load(&match_sb[0], __ATOMIC_RELAXED),
	    (unsigned long long)__c11_atomic_load(&match_all[1], __ATOMIC_RELAXED),
	    (unsigned long long)__c11_atomic_load(&match_bb[1], __ATOMIC_RELAXED),
	    (unsigned long long)__c11_atomic_load(&match_sb[1], __ATOMIC_RELAXED));
	printf("enuma-match: end\n");
}
