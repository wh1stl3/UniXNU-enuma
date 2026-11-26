/* SPDX-License-Identifier: BSD-2-Clause-Patent */
#include "open.h"

static __attribute__((noinline)) void
enuma_legacy_method(IOUserClient *client, uint32_t selector, unsigned kind)
{
	const uint64_t key = enuma_legacy_method_key();
	if (key && key == client->getRegistryEntryID())
		enuma_legacy_method_note(selector, kind);
}
