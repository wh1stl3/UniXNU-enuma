/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Isolated user Mach message trap observations, not a transactional snapshot. */
static _Atomic(uint64_t) ipc_all[2], ipc_bb[2], ipc_sb[2];

void
enuma_ipc_record(unsigned int receive)
{
	proc_t p = current_proc();
	__c11_atomic_fetch_add(&ipc_all[receive], 1, __ATOMIC_RELAXED);
	if (p == PROC_NULL)
		return;
	if (p->p_comm[0] == 'b' && strcmp(p->p_comm, "backboardd") == 0)
		__c11_atomic_fetch_add(&ipc_bb[receive], 1, __ATOMIC_RELAXED);
	else if (p->p_comm[0] == 'S' && strcmp(p->p_comm, "SpringBoard") == 0)
		__c11_atomic_fetch_add(&ipc_sb[receive], 1, __ATOMIC_RELAXED);
}

static void
enuma_ipc_dump(void)
{
	printf("enuma-ipc: begin send=%llu recv=%llu\n",
	    (unsigned long long)__c11_atomic_load(&ipc_all[0], __ATOMIC_RELAXED),
	    (unsigned long long)__c11_atomic_load(&ipc_all[1], __ATOMIC_RELAXED));
	printf("enuma-ipc: bb send=%llu recv=%llu\n",
	    (unsigned long long)__c11_atomic_load(&ipc_bb[0], __ATOMIC_RELAXED),
	    (unsigned long long)__c11_atomic_load(&ipc_bb[1], __ATOMIC_RELAXED));
	printf("enuma-ipc: sb send=%llu recv=%llu\n",
	    (unsigned long long)__c11_atomic_load(&ipc_sb[0], __ATOMIC_RELAXED),
	    (unsigned long long)__c11_atomic_load(&ipc_sb[1], __ATOMIC_RELAXED));
	printf("enuma-ipc: end\n");
}
