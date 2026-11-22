/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Included only by the isolated r44 ubc_subr.c build. */
static uint8_t enuma_fx_bits;
_Static_assert(__atomic_always_lock_free(sizeof(enuma_fx_bits), 0),
    "fixup hit bitmap requires lock-free byte atomics");

void
enuma_fixup_report(void)
{
	/* Observe a published bit before sampling its preceding applied increment. */
	unsigned int bits = os_atomic_load(&enuma_fx_bits, acquire);
	unsigned int applied = os_atomic_load(&cs_text_fixup_applied, relaxed);
	/* Published during EARLY_BOOT, before the user-space report can run. */
	unsigned int parsed = cs_text_fixup_parsed;
	printf("enuma-fx: parsed=%u applied=%u\n", parsed, applied);
	/* The frozen candidate has four ADT records and no per-slot boot args. */
	if (parsed == 4) {
		printf("enuma-fx: bits=0x%02x\n", bits);
	} else {
		printf("enuma-fx: bits=n/a\n");
	}
}
