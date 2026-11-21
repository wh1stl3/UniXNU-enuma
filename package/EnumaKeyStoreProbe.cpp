// SPDX-License-Identifier: BSD-2-Clause-Patent
// Copyright (c) 2026, UniXNU contributors. All rights reserved.
// Copyright (c) 2026, rootstockos contributors. All rights reserved.
// Adapted from rootstockos/UniXNU-asteroids@6370e66c package/KeyStoreProbe.cpp.
#include <IOKit/IOLib.h>
#include <IOKit/IOService.h>
#include <libkern/OSReturn.h>
#include <libkern/c++/OSSymbol.h>
#include <mach/kmod.h>
#include <pexpert/pexpert.h>

extern kmod_info_t g_kernel_kmod_info;
extern "C" OSReturn OSKextRegisterBoardClasses(const char *, void (*)(void));
extern "C" void native_keyevents_static_init(void) __asm__("__GLOBAL__sub_I_NativeKeyStoreEvents.cpp");
extern "C" IOService *native_keyevents_allocate(void);

extern "C" bool native_aks_state_enabled(void)
{
    unsigned standIn = 0, original = 0;
    PE_parse_boot_argn("sheng-aks", &standIn, sizeof(standIn));
    PE_parse_boot_argn("offline-keystore", &original, sizeof(original));
    return standIn == 1 && original != 1;
}

extern "C" uint32_t native_aks_lock_state(void) { return 0; }
extern "C" void native_keyevents_open_refused(void) {}
extern "C" void native_aks_opened(void) {}
extern "C" void native_aks_call(uint32_t, int32_t) {}

// No board identity was provisioned for the scratch state fixture. Return
// the unavailable sentinel, not a shared synthetic key derivation input.
extern "C" size_t native_aks_device_id(uint8_t *, size_t) { return 0; }

extern "C" void enuma_keystore_probe(void)
{
    if (!native_aks_state_enabled()) return;

    const OSSymbol *name = OSSymbol::withCString("AppleKeyStore");
    IOService *provider = IOService::getResourceService();
    OSReturn status = kIOReturnNoMemory;
    if (name) {
        if (!provider) status = kIOReturnNoDevice;
        else if (OSMetaClass::getMetaClassWithName(name)) status = kIOReturnExclusiveAccess;
        else status = OSKextRegisterBoardClasses(g_kernel_kmod_info.name, native_keyevents_static_init);
        name->release();
    }
    printf("enuma-aks: reg %#x\n", static_cast<unsigned>(status));

    IOService *service = status == kOSReturnSuccess ? native_keyevents_allocate() : nullptr;
    bool attached = service && service->init() && service->attach(provider);
    bool published = attached && service->start(provider);
    if (!published) {
        if (attached) service->detach(provider);
        OSSafeReleaseNULL(service);
    }
    printf("enuma-aks: pub %d\n", published);

    OSDictionary *matching = published ? IOService::serviceMatching("AppleKeyStore") : nullptr;
    IOService *matched = matching ? IOService::waitForMatchingService(matching, 1000000000ULL) : nullptr;
    printf("enuma-aks: match %d %.52s\n", matched && matched == service,
        matched ? matched->getMetaClass()->getClassName() : "-");
    OSSafeReleaseNULL(matched);
    OSSafeReleaseNULL(matching);

    uint8_t id[32];
    size_t size = native_aks_device_id(id, sizeof(id));
    char prefix[17];
    constexpr char digits[] = "0123456789abcdef";
    const size_t count = size < 8 ? size : 8;
    for (size_t i = 0; i < count; ++i) {
        prefix[2 * i] = digits[id[i] >> 4];
        prefix[2 * i + 1] = digits[id[i] & 15];
    }
    prefix[2 * count] = '\0';
    printf("enuma-aks: aksid %zu %s\n", size, count ? prefix : "-");
}
