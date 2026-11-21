// SPDX-License-Identifier: MIT
// Derived from UniXNU/UniXNU-sheng@6bc0ce1e8c3a3733110a80dd80ddfb2a1ca46555
// package/ShengPlatformPower.cpp; Copyright (c) 2026 UniXNU contributors.
// Guarded original-PMGR publication, NOT a platform power backend.
#include "OriginalPMGRABI.h"
#include <IOKit/IOLib.h>
#include <IOKit/IOPlatformExpert.h>
#include <libkern/c++/OSSymbol.h>
#include <mach/kmod.h>
#include <pexpert/pexpert.h>

extern "C" {
extern kmod_info_t g_kernel_kmod_info;
kern_return_t OSKextLoadKextWithIdentifier(const char *);
void sheng_pmgr_static_init(void) __asm__("__GLOBAL__sub_I_ShengPlatformPower.cpp");
IOService *sheng_original_pmgr_nub_create(IORegistryEntry *, ApplePMGR *);
uint32_t sheng_original_pmgr_nub_read(IOService *);
void sheng_original_pmgr_nub_write(IOService *, uint64_t);
// stage, code, parent-size, own-size, provider, nub, bound-provider,
// read-before, read-after, own-before/after, nub-before/after, attached,
// registered, mode. Diagnostic storage only; NOT a concurrent-once primitive.
volatile uint64_t sheng_pmgr_observation[16];
__attribute__((noinline)) void sheng_pmgr_checkpoint(void) { __asm__ volatile("" ::: "memory"); }
}

static void checkpoint(unsigned stage, uint32_t code)
{
  sheng_pmgr_observation[0] = stage;
  sheng_pmgr_observation[1] = code;
  sheng_pmgr_checkpoint();
  printf("enuma-pmgr stage=%u code=0x%x checks: parent=0x%llx own=0x%llx bound=%u read=0x%llx/0x%llx attach=%llu registered=%llu mode=%llu\n",
      stage, code, sheng_pmgr_observation[2], sheng_pmgr_observation[3],
      sheng_pmgr_observation[4] != 0 && sheng_pmgr_observation[4] == sheng_pmgr_observation[6],
      sheng_pmgr_observation[7], sheng_pmgr_observation[8], sheng_pmgr_observation[13],
      sheng_pmgr_observation[14], sheng_pmgr_observation[15]);
}

__attribute__((noreturn)) static void fail(unsigned stage, uint32_t code)
{
  checkpoint(stage, code);
  panic("enuma-pmgr fail-stop stage=%u code=0x%x", stage, code);
}

__attribute__((noreturn)) static void unavailable(unsigned slot)
{
  fail(0x100 + slot, static_cast<uint32_t>(kIOReturnUnsupported));
}

class ShengPlatformPower : public ApplePMGR {
  OSDeclareDefaultStructors(ShengPlatformPower)
public:
  void enableCPUCore(unsigned, uint64_t) override { unavailable(168); }
  void enableCPUCore(unsigned) override { unavailable(169); }
  void disableCPUCore(unsigned) override { unavailable(170); }
  void enableCPUCluster(unsigned) override { unavailable(171); }
  void disableCPUCluster(unsigned) override { unavailable(172); }
  void initCPUIdle(ml_processor_info_t *) override { unavailable(173); }
  void enterCPUIdle(UInt64 *) override { unavailable(174); }
  void exitCPUIdle(UInt64 *) override { unavailable(175); }
  void updateCPUIdle(UInt64 *) override { unavailable(176); }
#include "GuardedPMGRSlots.inc"
};
OSDefineMetaClassWithInit(ShengPlatformPower, ApplePMGR, )
OSMetaClassConstructorInit(ShengPlatformPower, ApplePMGR, )
OSDefineBasicStructors(ShengPlatformPower, ApplePMGR)
// Preserve OSObject's zeroed size-aware allocation/deallocation pairing.
void *ShengPlatformPower::operator new(size_t size) { return OSObject::operator new(size); }
void ShengPlatformPower::operator delete(void *memory, size_t size)
{
  OSObject::operator delete(memory, size);
}
static_assert(sizeof(ShengPlatformPower) == 0x4b8a8, "Exact original provider storage");

static const OSMetaClass *lookup(const char *text)
{
  const OSSymbol *name = OSSymbol::withCString(text);
  const OSMetaClass *meta = name ? OSMetaClass::getMetaClassWithName(name) : nullptr;
  OSSafeReleaseNULL(name);
  return meta;
}

extern "C" void sheng_pmgr_run(void)
{
  unsigned mode = 0;
  if (!PE_parse_boot_argn("pmgr", &mode, sizeof(mode)) || !mode) return;
  // Only the single bsd_init startup thread may call this. This is a misuse
  // detector, not a synchronization mechanism or permission to add callers.
  static bool entered = false;
  if (entered) fail(1, static_cast<uint32_t>(kIOReturnExclusiveAccess));
  entered = true;
  sheng_pmgr_observation[15] = mode;
  if (mode > 3) fail(2, static_cast<uint32_t>(kIOReturnBadArgument));
  checkpoint(3, 0);
  kern_return_t result = OSKextLoadKextWithIdentifier("com.apple.driver.ApplePMGR");
  if (result) fail(4, static_cast<uint32_t>(result));
  const OSMetaClass *parent = lookup("ApplePMGR"), *nubMeta = lookup("ApplePMGRNub");
  if (!parent || parent != &ApplePMGR::gMetaClass || parent->getClassSize() != 0x4b8a8 ||
      !nubMeta || nubMeta->getClassSize() != 0x740) fail(5, static_cast<uint32_t>(kIOReturnBadArgument));
  sheng_pmgr_observation[2] = parent->getClassSize();
  // No loads/publication/waits between these three operations. NULL handle
  // and failed postModLoad can leave private state: panic, no unlock/retry.
  void *handle = OSMetaClass::preModLoad(g_kernel_kmod_info.name);
  if (!handle) fail(6, static_cast<uint32_t>(kIOReturnNoMemory));
  sheng_pmgr_static_init();
  result = OSMetaClass::postModLoad(handle);
  if (result) fail(7, static_cast<uint32_t>(result));
  sheng_pmgr_observation[9] = ShengPlatformPower::gMetaClass.getInstanceCount();
  sheng_pmgr_observation[11] = nubMeta->getInstanceCount();
  ShengPlatformPower *provider = new ShengPlatformPower;
  if (!provider) fail(8, static_cast<uint32_t>(kIOReturnNoMemory));
  if (!provider->init()) fail(9, static_cast<uint32_t>(kIOReturnError));
  IORegistryEntry *description = new IORegistryEntry;
  if (!description) fail(10, static_cast<uint32_t>(kIOReturnNoMemory));
  if (!description->init()) fail(11, static_cast<uint32_t>(kIOReturnError));
  sheng_pmgr_observation[3] = provider->getMetaClass()->getClassSize();
  sheng_pmgr_observation[4] = reinterpret_cast<uintptr_t>(provider);
  // Empty description: no hardware resources or invented device capability.
  description->setName("enuma-platform-power");
  IOService *nub = sheng_original_pmgr_nub_create(description, provider);
  sheng_pmgr_observation[5] = reinterpret_cast<uintptr_t>(nub);
  if (!nub || nub->getMetaClass() != nubMeta || !provider->metaCast("ApplePMGR"))
    fail(12, static_cast<uint32_t>(kIOReturnBadArgument));
  uintptr_t bound = 0;
  memcpy(&bound, reinterpret_cast<const char *>(nub) + 0x88, sizeof(bound));
  sheng_pmgr_observation[6] = bound;
  if (bound != reinterpret_cast<uintptr_t>(provider)) fail(13, static_cast<uint32_t>(kIOReturnBadArgument));
  uint32_t value = sheng_original_pmgr_nub_read(nub);
  sheng_pmgr_observation[7] = value;
  sheng_original_pmgr_nub_write(nub, uint64_t(value | 4));
  sheng_pmgr_observation[8] = sheng_original_pmgr_nub_read(nub);
  if (value != 0xffffffff || sheng_pmgr_observation[8] != 0xffffffff ||
      nub->getProvider() || provider->getProvider() ||
      ((nub->getState() | provider->getState()) & kIOServiceRegisteredState))
    fail(14, static_cast<uint32_t>(kIOReturnError));
  if (mode == 3) provider->disableCPUCore(1);
  if (mode == 1) {
    // Diagnostic-only unpublished cleanup; donor ownership closure must be
    // independently reviewed before this is qualified at runtime.
    nub->release();
    description->release();
    provider->release();
    sheng_pmgr_observation[10] = ShengPlatformPower::gMetaClass.getInstanceCount();
    sheng_pmgr_observation[12] = nubMeta->getInstanceCount();
    if (sheng_pmgr_observation[9] != sheng_pmgr_observation[10] ||
        sheng_pmgr_observation[11] != sheng_pmgr_observation[12])
      fail(15, static_cast<uint32_t>(kIOReturnError));
    checkpoint(16, 0);
    return;
  }
  IOService *platform = IOService::getPlatform();
  if (!platform || !provider->attach(platform)) fail(17, static_cast<uint32_t>(kIOReturnError));
  if (!provider->start(platform)) fail(18, static_cast<uint32_t>(kIOReturnError));
  if (!nub->attach(provider)) fail(19, static_cast<uint32_t>(kIOReturnError));
  if (!nub->start(provider)) fail(20, static_cast<uint32_t>(kIOReturnError));
  // From publication onwards there may be consumers: never roll back.
  provider->registerService(kIOServiceSynchronous);
  nub->registerService(kIOServiceSynchronous);
  sheng_pmgr_observation[13] = nub->getProvider() == provider && provider->getProvider() == platform;
  sheng_pmgr_observation[14] = (nub->getState() & provider->getState()) & kIOServiceRegisteredState;
  auto matching = IOService::serviceMatching("ApplePMGRNub");
  if (!matching) fail(21, static_cast<uint32_t>(kIOReturnNoMemory));
  IOService *matched = IOService::waitForMatchingService(matching, 1000000);
  matching->release();
  if (matched != nub || matched->getMetaClass() != nubMeta ||
      !sheng_pmgr_observation[13] || !sheng_pmgr_observation[14])
    fail(22, static_cast<uint32_t>(kIOReturnNotFound));
  matched->release(); // Extra matching reference, not the initial nub reference.
  description->release();
  // No unload: permanently retain both successful initial references.
  sheng_pmgr_observation[10] = ShengPlatformPower::gMetaClass.getInstanceCount();
  sheng_pmgr_observation[12] = nubMeta->getInstanceCount();
  checkpoint(23, 0); // Success only after actual matching and attachment checks.
}
