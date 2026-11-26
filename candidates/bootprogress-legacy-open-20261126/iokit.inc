/* SPDX-License-Identifier: BSD-2-Clause-Patent */
#include "open.h"

static bool
enuma_chain_service(const OSObject *object)
{
	return object && strcmp(object->getMetaClass()->getClassName(), "NativeLegacyDisplay") == 0;
}

static __attribute__((noinline)) void
enuma_chain_dt(const char *path, IORegistryEntry *entry)
{
	/* Typed inband path only. Record the fixed comparison outcome, not the string. */
	if (strcmp(path, "IODeviceTree:/arm-io") == 0)
		enuma_chain_note(ENUMA_DT_PARENT, 0, entry != nullptr, 0);
	else if (strcmp(path, "IODeviceTree:/arm-io/enuma-gop-display") == 0)
		enuma_chain_note(ENUMA_DT_CHILD, 0, entry != nullptr, 0);
}

static __attribute__((noinline)) void
enuma_chain_first_match(const OSSymbol *type, OSDictionary *dict, IOReturn result)
{
	if (type != gIOFirstMatchNotification)
		return;
	const OSString *provider = OSDynamicCast(OSString, dict->getObject(gIOProviderClassKey));
	if (provider && provider->isEqualTo("IOMobileFramebuffer"))
		enuma_chain_note(ENUMA_FIRST_MATCH, result, result == kIOReturnSuccess, 0);
}

static __attribute__((noinline)) void
enuma_legacy_method(IOUserClient *client, uint32_t selector, unsigned kind)
{
	const uint64_t key = enuma_legacy_method_key();
	if (key && key == client->getRegistryEntryID())
		enuma_legacy_method_note(selector, kind);
}
