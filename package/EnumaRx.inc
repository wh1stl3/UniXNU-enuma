/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Counts mach_msg2_trap invocations, not sleeping receivers. */
static _Atomic(uint64_t) enuma_rx_in[2], enuma_rx_out[2];

unsigned int
enuma_rx_enter(void)
{
	proc_t p = current_proc();
	unsigned int slot = 2;
	if (p != PROC_NULL) {
		if (p->p_pid == 5)
			slot = 0;
		else if (p->p_pid == 34)
			slot = 1;
	}
	if (slot < 2)
		__c11_atomic_fetch_add(&enuma_rx_in[slot], 1, __ATOMIC_RELAXED);
	return slot;
}

void
enuma_rx_exit(unsigned int slot)
{
	if (slot < 2)
		__c11_atomic_fetch_add(&enuma_rx_out[slot], 1, __ATOMIC_RELAXED);
}

static void
enuma_rx_dump(void)
{
	printf("enuma-rx: sb5 in=%llu out=%llu\n",
	    (unsigned long long)__c11_atomic_load(&enuma_rx_in[0], __ATOMIC_RELAXED),
	    (unsigned long long)__c11_atomic_load(&enuma_rx_out[0], __ATOMIC_RELAXED));
	printf("enuma-rx: bb34 in=%llu out=%llu\n",
	    (unsigned long long)__c11_atomic_load(&enuma_rx_in[1], __ATOMIC_RELAXED),
	    (unsigned long long)__c11_atomic_load(&enuma_rx_out[1], __ATOMIC_RELAXED));
}
