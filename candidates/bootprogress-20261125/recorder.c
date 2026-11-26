/* Recorder-only diagnostic; no framebuffer access or console interception. */
#include <stdint.h>
#ifdef RECORDER_HOST_TEST
extern int PE_parse_boot_argn(const char *, void *, int);
extern void kprintf(const char *, ...);
#else
#include <pexpert/pexpert.h>
#include <kern/debug.h>
#endif

static unsigned bp_recorder_enabled;

void
enuma_bp_init(void)
{
	unsigned value = 0;
	bp_recorder_enabled = PE_parse_boot_argn("boot-progress", &value,
	    sizeof(value)) && value == 2;
}

void
enuma_bp_stage(const char *stage)
{
	if (bp_recorder_enabled) {
		kprintf("enuma-bp stage: %s\n", stage);
	}
}
