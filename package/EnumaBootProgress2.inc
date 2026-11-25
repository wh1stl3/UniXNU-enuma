/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Isolated r49 replacement, included after the report helpers. */
enum { ENUMA_BP_INTERVAL = 60, ENUMA_BP_REPRINTS = 10 };
static unsigned int enuma_bp_index;

static __attribute__((noinline)) void
enuma_bp_print(unsigned int idx)
{
	for (unsigned int i = 0; i < 40; ++i) {
		printf("\n");
	}
	uint64_t ns;
	absolutetime_to_nanoseconds(mach_absolute_time(), &ns);
	printf("enuma bp r49 i=%u t=%lu\n", idx,
	    (unsigned long)(ns / NSEC_PER_SEC));
	if (idx >= 1 && idx <= 2) {
		printf("enuma-ipc2: t=%lu l(1)=%llu/%llu bb(34)=%llu/%llu sb(5)=%llu/%llu\n",
		    (unsigned long)(ns / NSEC_PER_SEC),
		    (unsigned long long)__atomic_load_n(&enuma_ipc_s[0], __ATOMIC_RELAXED),
		    (unsigned long long)__atomic_load_n(&enuma_ipc_r[0], __ATOMIC_RELAXED),
		    (unsigned long long)__atomic_load_n(&enuma_ipc_s[2], __ATOMIC_RELAXED),
		    (unsigned long long)__atomic_load_n(&enuma_ipc_r[2], __ATOMIC_RELAXED),
		    (unsigned long long)__atomic_load_n(&enuma_ipc_s[1], __ATOMIC_RELAXED),
		    (unsigned long long)__atomic_load_n(&enuma_ipc_r[1], __ATOMIC_RELAXED));
	}
	enuma_matchcnt_dump();
	enuma_fixup_report();
	enuma_ps_dump();
	enuma_ex_dump();
}

static void
enuma_bp_repeat(__unused thread_call_param_t arg, thread_call_param_t self)
{
	unsigned int idx = ++enuma_bp_index;
	enuma_bp_print(idx);
	if (idx < ENUMA_BP_REPRINTS) {
		uint64_t deadline;
		clock_interval_to_deadline(ENUMA_BP_INTERVAL, NSEC_PER_SEC, &deadline);
		thread_call_enter1_delayed(self, self, deadline);
	} else {
		thread_call_free(self);
	}
}

static __attribute__((noinline)) void
enuma_bp_start(void)
{
	int enabled = 0;
	if (!PE_parse_boot_argn("enuma-bp", &enabled, sizeof(enabled)) || enabled != 1) {
		return;
	}
	enuma_bp_print(0);
	thread_call_t call = thread_call_allocate_with_options(enuma_bp_repeat,
	    NULL, THREAD_CALL_PRIORITY_KERNEL, THREAD_CALL_OPTIONS_ONCE);
	if (call != NULL) {
		uint64_t deadline;
		clock_interval_to_deadline(ENUMA_BP_INTERVAL, NSEC_PER_SEC, &deadline);
		thread_call_enter1_delayed(call, call, deadline);
	}
}
