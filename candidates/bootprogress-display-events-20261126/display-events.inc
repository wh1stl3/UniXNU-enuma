// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "display-events.h"

// Sticky observations only. No order or relationship between different fields.
static unsigned enuma_display_seen[ENUMA_DISPLAY_EVENT_COUNT];
static_assert(sizeof(unsigned) == 4 && alignof(unsigned) == 4 &&
    __atomic_always_lock_free(sizeof(unsigned), enuma_display_seen));

extern "C" __attribute__((noinline)) void
enuma_bp_display_mark(enum enuma_bp_display_event event)
{
	__atomic_store_n(&enuma_display_seen[event], 1, __ATOMIC_RELAXED);
}

extern "C" void
enuma_bp_display_sample(struct enuma_bp_display_sample *sample)
{
	for (unsigned i = 0; i < ENUMA_DISPLAY_EVENT_COUNT; ++i)
		sample->seen[i] = __atomic_load_n(&enuma_display_seen[i], __ATOMIC_RELAXED);
}
