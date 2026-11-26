// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstring>

static unsigned calls, failed_at, released;
static int logged = -1;
static int gIOServicePlane;

struct IORegistryEntry {
    IORegistryEntry *parent;
    unsigned first;

    bool property(const char *key, unsigned long long value, unsigned bits)
    {
        static const char *const keys[] = {
            "Built-In", "DisplayIntegrated", "PrimaryUsagePage", "PrimaryUsage"
        };
        static const unsigned values[] = {1, 1, 0x0d, 4};
        assert(calls >= first && calls - first < 4);
        const unsigned i = calls - first;
        assert(!strcmp(key, keys[i]) && value == values[i] && bits == (i < 2 ? 0 : 32));
        return ++calls != failed_at;
    }
    bool setProperty(const char *key, bool value) { return property(key, value, 0); }
    bool setProperty(const char *key, unsigned long long value, unsigned bits)
    {
        return property(key, value, bits);
    }
    IORegistryEntry *getParentEntry(int) { return parent; }
    void release() { ++released; }
};

struct IOService { IORegistryEntry *driver; };
static IORegistryEntry *findEventDriver(IOService *device, unsigned depth)
{
    assert(depth == 4);
    return device->driver;
}

static void record_log(const char *format, int ok)
{
    assert(!strcmp(format, "enuma HID stand-in: digitizer properties=%d\n"));
    logged = ok;
}

#define printf record_log
#include "checkpoint.inc"
#undef printf

static void check_line(bool seen)
{
    char text[HID_ROW_COLS];
#include "hid-format.inc"
    assert(n > 0 && static_cast<size_t>(n) < sizeof(text));
    assert(!strcmp(text, seen ?
        "TOUCH HID reports=4294967295 | digitizer properties: observed" :
        "TOUCH HID reports=4294967295 | digitizer properties: not observed"));
}

int main(int argc, char **argv)
{
    assert(argc == 2);
    const unsigned scenario = static_cast<unsigned>(atoi(argv[1]));
    assert(scenario <= 9);
    assert(enuma_hid_digitizer_sample() == 0);
    check_line(false);
    IORegistryEntry parent{nullptr, 0}, driver{scenario == 9 ? nullptr : &parent, 4};
    IOService device{nullptr};
    native_hid_live_checkpoint(&device);
    assert(calls == 0 && released == 0 && logged == -1 && enuma_hid_digitizer_sample() == 0);

    device.driver = &driver;
    failed_at = scenario;
    native_hid_live_checkpoint(&device);
    const bool seen = scenario == 0;
    const unsigned expected = seen ? 8 : scenario == 9 ? 0 : scenario;
    assert(calls == expected && released == 1 && logged == seen);
    assert(enuma_hid_digitizer_sample() == seen);
    check_line(seen);

    driver.parent = nullptr;
    native_hid_live_checkpoint(&device);
    assert(calls == expected && released == 1 && logged == seen);
    assert(enuma_hid_digitizer_sample() == seen);
    check_line(seen);
    printf("checkpoint scenario %u passed\n", scenario);
}
