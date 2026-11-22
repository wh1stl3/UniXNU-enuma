/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Included after the r45 report helpers in the isolated kern_exec.c build. */
static __attribute__((noinline)) void
enuma_bp_print(void)
{
	int enabled = 0;
	if (!PE_parse_boot_argn("enuma-bp", &enabled, sizeof(enabled)) || enabled != 1) {
		return;
	}
	for (unsigned int i = 0; i < 40; ++i) {
		printf("\n");
	}
	uint64_t ns;
	absolutetime_to_nanoseconds(mach_absolute_time(), &ns);
	printf("enuma bp r46 t=%lu\n", (unsigned long)(ns / NSEC_PER_SEC));
	enuma_matchcnt_dump();
	enuma_fixup_report();
	enuma_ps_dump();
	enuma_ex_dump();
}
