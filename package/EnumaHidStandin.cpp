// SPDX-License-Identifier: BSD-2-Clause-Patent
// Adapted from Orange Pi 5's Evb10HidProbe.cpp and LegacyDisplayProbe.cpp:
// Copyright (c) 2026, UniXNU contributors; see the r23 host record.
#include <IOKit/IOLib.h>
#include <IOKit/IOService.h>
#include <libkern/c++/OSIterator.h>
#include <libkern/c++/OSKext.h>
#include <libkern/c++/OSMetaClass.h>
#include <libkern/c++/OSSymbol.h>
#include <mach/kmod.h>
#include <pexpert/pexpert.h>

extern kmod_info_t g_kernel_kmod_info;
extern "C" kern_return_t OSKextLoadKextWithIdentifier(const char *);
extern "C" void enuma_hid_static_init(void) __asm__("__GLOBAL__sub_I_NativeHidInput.cpp");
extern "C" IOService *native_hid_input_allocate(void);

extern "C" {
volatile uint32_t native_touch_seq, native_touch_count, native_touch_hid_reports;
volatile int native_touch_xs[12], native_touch_ys[12], native_touch_ids[12];
void native_touch_set_sink(void (*)(void *), void *) {}
void native_buttons_set_sink(void (*)(void *, uint32_t), void *) {}
void native_hid_input_observed(unsigned, int) {}
bool native_hid_input_requested(void) { return false; }
}

static IORegistryEntry *findEventDriver(IORegistryEntry *parent, unsigned depth)
{
    if (!depth) return nullptr;
    OSIterator *children = parent->getChildIterator(gIOServicePlane);
    if (!children) return nullptr;
    IORegistryEntry *driver = nullptr;
    while (OSObject *child = children->getNextObject()) {
        IORegistryEntry *entry = OSDynamicCast(IORegistryEntry, child);
        if (!entry) continue;
        if (entry->metaCast("IOHIDEventDriver")) {
            driver = entry;
            driver->retain();
            break;
        }
        driver = findEventDriver(entry, depth - 1);
        if (driver) break;
    }
    children->release();
    return driver;
}

static bool publishDigitizerProperties(IORegistryEntry *entry)
{
    return entry->setProperty("Built-In", true) &&
           entry->setProperty("DisplayIntegrated", true) &&
           entry->setProperty("PrimaryUsagePage", 0x0dULL, 32) &&
           entry->setProperty("PrimaryUsage", 4ULL, 32);
}

extern "C" void native_hid_live_checkpoint(IOService *device)
{
    // The one combined device's timer calls this after normal matching. Its
    // keyboard-first descriptor otherwise makes the event service look like (1,6).
    static bool published;
    if (published) return;
    IORegistryEntry *driver = findEventDriver(device, 4);
    if (!driver) return;
    IORegistryEntry *interface = driver->getParentEntry(gIOServicePlane);
    published = true; // Do not repeatedly notify attached user clients.
    const bool ok = interface && publishDigitizerProperties(interface) &&
                    publishDigitizerProperties(driver);
    printf("enuma HID stand-in: digitizer properties=%d\n", ok);
    driver->release();
}

static void startStandin(IOService *resource)
{
    const OSSymbol *name = OSSymbol::withCString("IOHIDDevice");
    const OSMetaClass *meta = name ? OSMetaClass::getMetaClassWithName(name) : nullptr;
    const unsigned size = meta ? meta->getClassSize() : 0;
    OSSafeReleaseNULL(name);
    if (size != 208) {
        printf("enuma HID stand-in: IOHIDDevice size=%u, expected 208\n", size);
        return;
    }
    void *handle = OSMetaClass::preModLoad(g_kernel_kmod_info.name);
    if (!handle) {
        printf("enuma HID stand-in: preModLoad failed\n");
        return;
    }
    enuma_hid_static_init();
    const auto status = OSMetaClass::postModLoad(handle);
    if (status) {
        printf("enuma HID stand-in: postModLoad=%d\n", status);
        return;
    }
    IOService *device = native_hid_input_allocate();
    const bool valid = device && device->metaCast("IOHIDDevice") && device->init();
    const bool attached = valid && device->attach(resource);
    const bool started = attached && device->start(resource);
    printf("enuma HID stand-in: init=%d attach=%d start=%d\n", valid, attached, started);
    if (!started) {
        if (attached) device->detach(resource);
        OSSafeReleaseNULL(device);
    }
    // On success retain the allocation for this boot, as on Orange Pi 5.
}

// Called once from load_init_program(), after Data and before exec of launchd.
extern "C" void enuma_hid_standin_start(void)
{
    unsigned enabled = 0;
    if (!PE_parse_boot_argn("sheng-touch-hid", &enabled, sizeof(enabled)) || enabled != 1)
        return;
    const int family = OSKextLoadKextWithIdentifier("com.apple.iokit.IOHIDFamily");
    const int driver = family ? -1 : OSKext::loadKextWithIdentifier(
        "com.apple.iokit.IOHIDEventDriver", true, false,
        kOSKextExcludeNone, kOSKextExcludeNone, nullptr);
    printf("enuma HID stand-in: IOHIDFamily=%d IOHIDEventDriver=%d\n", family, driver);
    if (family || driver) return;
    OSDictionary *match = IOService::serviceMatching("IOHIDResource");
    IOService *resource = match ? IOService::waitForMatchingService(match, 5000000000ULL) : nullptr;
    printf("enuma HID stand-in: IOHIDResource=%s\n", resource ? "found" : "missing");
    if (resource) startStandin(resource);
    OSSafeReleaseNULL(resource);
    OSSafeReleaseNULL(match);
}
