#include <assert.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static int present;
static unsigned value;
static unsigned messages;
static char last[256];
int PE_parse_boot_argn(const char *name, void *out, int size) {
	assert(!strcmp(name, "boot-progress") && size == sizeof(value));
	*(unsigned *)out = value;
	return present;
}
void kprintf(const char *format, ...) {
	va_list ap;
	va_start(ap, format);
	vsnprintf(last, sizeof(last), format, ap);
	va_end(ap);
	messages++;
}
void enuma_bp_init(void);
void enuma_bp_stage(const char *);
int main(void) {
	enuma_bp_init();
	enuma_bp_stage("off");
	assert(messages == 0);
	present = 1; value = 1; enuma_bp_init();
	enuma_bp_stage("disabled");
	assert(messages == 0);
	value = 2; enuma_bp_init();
	enuma_bp_stage("mounted");
	assert(messages == 1 && strstr(last, "stage: mounted"));
	puts("recorder opt-in and output PASS");
}
