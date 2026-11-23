/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* kern/processor.h declares this behind MACH_KERNEL_PRIVATE. */
extern uint32_t processor_avail_count;

/* Existing ArmCpu C-linkage diagnostics; slot 1 is the logical secondary. */
extern volatile uint32_t armcpu_smp_seen_mpidr[8], armcpu_smp_step[8];
extern volatile uint32_t armcpu_smp_fail[8], armcpu_smp_mpidr[8];

static __attribute__((noinline)) void
enuma_bp_cpu_report(void)
{
	unsigned int step = armcpu_smp_step[1];
	unsigned int online = os_atomic_load(&processor_avail_count, relaxed);
	printf("enuma-cpu: online=%u seen1=0x%llx step1=%u fail1=%u\n",
	    online, (unsigned long long)armcpu_smp_seen_mpidr[1], step,
	    armcpu_smp_fail[1]);
	printf("enuma-cpu: mpidr1=0x%llx\n",
	    (unsigned long long)armcpu_smp_mpidr[1]);
}
