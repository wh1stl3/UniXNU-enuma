// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <thread>
#include "framebuffer.h"
#include "page.h"
#include "display-page.inc"
#include "display-events.inc"
#include "NativeLegacyRequest.h"

// Production callback excerpts below; only their dependencies are mocked.
using IOReturn = int;
using UInt32 = uint32_t;
using task_t = void *;
constexpr int kIOReturnSuccess = 0;
struct IOUserClient {} connection;
struct IOMobileFramebufferLegacy {
	int nextStatus = 0, calls = 0;
	task_t lastTask = nullptr;
	void *lastSecurity = nullptr;
	UInt32 lastType = 0;
	virtual IOReturn newUserClient(task_t task, void *security, UInt32 type, IOUserClient **client)
	{
		++calls; lastTask = task; lastSecurity = security; lastType = type;
		if (!nextStatus && client) *client = &connection;
		return nextStatus;
	}
	virtual bool validateSwap(const struct OriginalLegacySwapRequest *) { return false; }
};
struct OSObject { bool metaCast(const char *) { return false; } };
struct IOMemoryDescriptor : OSObject { uint64_t getLength() { return 0; } };
struct OriginalLegacySwapRequest { unsigned char data[2656]; };
// Qualified request offsets from the R6 generated ABI header.
enum { kRequestSurfaces = 2624, kRequestMasks = 792, kRequestRect0 = 17,
	kRequestRect1 = 81, kRequestOptions = 804, kRequestDims = 816 };
static IOMemoryDescriptor *native_legacy_surface_descriptor(OSObject *) { return nullptr; }
static uint64_t native_legacy_surface_width(OSObject *) { return 0; }
static uint64_t native_legacy_surface_height(OSObject *) { return 0; }
static uint64_t native_legacy_surface_stride(OSObject *) { return 0; }
static uint64_t native_legacy_surface_allocation(OSObject *) { return 0; }
static unsigned native_legacy_surface_format(OSObject *) { return 0; }
static unsigned native_legacy_surface_planes(OSObject *) { return 0; }
static bool nativeScanoutFormat(unsigned, unsigned) { return false; }
static void native_legacy_surface_rejected(...) { assert(false); }
static unsigned observedReason;
static int observedStatus;
static IOUserClient *observedClient;
static void native_legacy_swap_validation_observed(bool accepted, unsigned reason,
	const void *, const void *)
{
	assert(accepted == (reason == 5));
	observedReason = reason;
}
static void native_legacy_client_enter(task_t, uint32_t) {}
static void native_legacy_client_observed(IOReturn status, IOUserClient *client)
{
	observedStatus = status; observedClient = client;
}
static void PE_parse_boot_argn(const char *name, unsigned *value, size_t size)
{
	assert(!strcmp(name, "offline-legacy-validate") && size == sizeof(*value));
	*value = 1;
}
static unsigned native_legacy_swapstat[16];
struct TestDisplay : IOMobileFramebufferLegacy {
	bool logicalPM = true, primary = true, bootMapping = true;
	unsigned added = 0, removed = 0;
	void getDisplayDimensions(uint32_t *width, uint32_t *height) { *width = 16; *height = 24; }
	void addValidated(const OriginalLegacySwapRequest *) { ++added; }
	void removeValidated(const OriginalLegacySwapRequest *) { ++removed; }
	unsigned validatedCount() { return added; }
	void stat(unsigned) {}
	void note(int, int, const OriginalLegacySwapRequest *) {}
#include "test-callbacks.inc"
};

struct PE_Video {};
static TestDisplay *displayObject;
static unsigned takeCalls;
static bool takeResult;
extern "C" {
bool enuma_bp_gui_take(const PE_Video *) { ++takeCalls; return takeResult; }
#include "test-prepare.inc"
}

static bp_gate enuma_bp_gate;
static uint32_t pixel;
static bp_framebuffer enuma_bp_map = {(volatile unsigned char *)&pixel, sizeof(pixel), 1, 1, 4};
static int enuma_bp_call;
static constexpr uint64_t NSEC_PER_SEC = 1000000000;
static unsigned samples, rasters, schedules;
static bool interruptEnabled = true;
using boolean_t = bool;
#define FALSE false
#define __unused __attribute__((unused))
static bool ml_set_interrupts_enabled(bool enable)
{
	bool old = interruptEnabled; interruptEnabled = enable;
	return old;
}
static void clock_interval_to_deadline(unsigned n, uint64_t unit, uint64_t *value) { *value = n * unit; }
static void thread_call_enter_delayed(int *, uint64_t deadline)
{
	assert(interruptEnabled && deadline == NSEC_PER_SEC);
	++schedules;
}
static void panel_sample(struct panel_page *page)
{
	assert(interruptEnabled && !(enuma_bp_gate.state & BP_WRITING));
	struct enuma_bp_display_sample snapshot;
	enuma_bp_display_sample(&snapshot);
	panel_display_events(page, &snapshot);
	++samples;
}
static void host_dsb()
{
	assert(!interruptEnabled && (enuma_bp_gate.state & BP_WRITING));
	++rasters;
}
#include "test-refresh.inc"

int main()
{
	struct enuma_bp_display_sample snapshot;
	enuma_bp_display_sample(&snapshot);
	for (auto value : snapshot.seen) assert(!value);
	enuma_bp_gate.state = BP_ACTIVE;
	enuma_bp_refresh(nullptr, nullptr);
	assert(samples == 1 && rasters == 1 && schedules == 1);
	bp_panic(&enuma_bp_gate);
	enuma_bp_refresh(nullptr, nullptr);
	assert(samples == 1 && rasters == 1 && schedules == 1);

	TestDisplay test;
	IOUserClient *client = nullptr;
	assert(test.newUserClient(&test, &pixel, 17, &client) == 0 && test.calls == 1);
	assert(client == &connection && observedClient == client && observedStatus == 0);
	assert(test.lastTask == &test && test.lastSecurity == &pixel && test.lastType == 17);
	test.nextStatus = -317;
	assert(test.newUserClient(&test, nullptr, 18, &client) == -317 && test.calls == 2);
	assert(client == &connection && observedClient == nullptr && observedStatus == -317);

	OriginalLegacySwapRequest request = {};
	auto word = [&](unsigned offset, uint32_t value) { memcpy(request.data + offset, &value, 4); };
	word(kRequestDims, 16); word(kRequestDims + 4, 24);
	word(kRequestMasks, 1); word(kRequestMasks + 4, 1);
	assert(test.validateSwap(&request) && observedReason == 5 && test.added == 1);
	enuma_bp_display_sample(&snapshot);
	assert(snapshot.seen[ENUMA_DISPLAY_VALIDATE_ACCEPT] && !snapshot.seen[ENUMA_DISPLAY_VALIDATE_REJECT]);
	word(kRequestMasks + 4, 0);
	assert(!test.validateSwap(&request) && observedReason == 2 && test.removed == 1);

	PE_Video video;
	assert(!native_legacy_prepare_scanout(&video) && takeCalls == 0);
	enuma_bp_display_sample(&snapshot);
	assert(snapshot.seen[ENUMA_DISPLAY_PREPARE_ENTER] && snapshot.seen[ENUMA_DISPLAY_PREPARE_FALSE]);
	displayObject = &test;
	assert(!native_legacy_prepare_scanout(&video) && takeCalls == 1);
	takeResult = true;
	assert(native_legacy_prepare_scanout(&video) && takeCalls == 2);
	assert(!snapshot.seen[ENUMA_DISPLAY_REGISTERED]);
	struct panel_page page = {}, previous;
	panel_line(&page.main[30], "before", PANEL_WHITE, 0);
	panel_line(&page.main[35], "after", PANEL_WHITE, 0);
	previous = page;
	panel_display_events(&page, &snapshot);
	assert(!memcmp(&page.main[0], &previous.main[0], 31 * sizeof(page.main[0])));
	assert(!memcmp(&page.main[35], &previous.main[35], (PANEL_ROWS - 35) * sizeof(page.main[0])));
	assert(!memcmp(page.extra, previous.extra, sizeof(page.extra)) &&
	       !memcmp(page.side, previous.side, sizeof(page.side)));
	assert(strstr(page.main[31].text, "registered=0"));
	assert(strstr(page.main[32].text, "enter=1 accept=1 reject=1"));
	assert(strstr(page.main[33].text, "enter=1 false=1"));
	assert(strstr(page.main[34].text, "caller/BB unknown | legacy4.enter=1 parent.ok=1 parent.err=1"));
	for (unsigned row = 31; row <= 34; ++row) {
		assert(strlen(page.main[row].text) < PANEL_COLS - 1);
		puts(page.main[row].text);
	}

	// Host-only reset before starting real concurrent writers and reader.
	for (auto &value : enuma_display_seen) __atomic_store_n(&value, 0, __ATOMIC_RELAXED);
	std::thread writers[ENUMA_DISPLAY_EVENT_COUNT];
	for (unsigned i = 0; i < ENUMA_DISPLAY_EVENT_COUNT; ++i)
		writers[i] = std::thread([i] {
			for (unsigned n = 0; n < 20000; ++n)
				enuma_bp_display_mark(static_cast<enuma_bp_display_event>(i));
		});
	enuma_bp_display_sample(&snapshot);
	for (unsigned n = 0; n < 20000; ++n) {
		auto old = snapshot;
		enuma_bp_display_sample(&snapshot);
		for (unsigned i = 0; i < ENUMA_DISPLAY_EVENT_COUNT; ++i)
			assert(snapshot.seen[i] <= 1 && snapshot.seen[i] >= old.seen[i]);
	}
	for (auto &writer : writers) writer.join();
	enuma_bp_display_sample(&snapshot);
	for (auto value : snapshot.seen) assert(value == 1);
	puts("display events: real callback excerpts, independent sticky fields, row bounds and STOP pass");
}
