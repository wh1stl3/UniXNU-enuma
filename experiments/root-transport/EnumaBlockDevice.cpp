// SPDX-License-Identifier: BSD-2-Clause-Patent
// Offline integration candidate. No static initializer or hardware activation.
#include <IOKit/IOLib.h>
#include <IOKit/storage/IOBlockStorageDevice.h>
#include "EnumaBlockRequest.h"
extern "C" IOService *enuma_storage_publish_readonly(IOService *,
    const EnumaStorageConfig *, bool, bool);

class EnumaBlockDevice : public IOBlockStorageDevice {
    OSDeclareDefaultStructors(EnumaBlockDevice)
    EnumaStorageOwner *owner = nullptr;
    IOService *resourceOwner = nullptr;
    UInt64 sectors = 0;
    bool online = false;
public:
    bool configure(IOService *anchor, const EnumaStorageConfig &config) {
        if (!anchor || owner || !EnumaStoragePort(config).valid() || !config.transport->blocks ||
            config.transport->blocks > UINT64_MAX/8) return false;
        // anchor owns the immutable config, callbacks, bounce/DMA and locks.
        anchor->retain(); resourceOwner=anchor;
        owner=new EnumaStorageOwner(config);
        if (!owner || !owner->activate(true)) return false;
        sectors=config.transport->blocks*8;
        return true;
    }
    bool start(IOService *provider) override {
        if (!owner || provider!=resourceOwner || !IOBlockStorageDevice::start(provider)) return false;
        __atomic_store_n(&online,true,__ATOMIC_RELEASE);
        registerService(); return true;
    }
    void stop(IOService *provider) override {
        __atomic_store_n(&online,false,__ATOMIC_RELEASE);
        if(owner) owner->requestStop();
        IOBlockStorageDevice::stop(provider);
    }
    void free() override {
        bool safe=true;
        if(owner) { owner->requestStop(); safe=owner->tryDrain(); delete owner; owner=nullptr; }
        // An uncertain DMA stop intentionally retains the resource owner.
        // No buffer release follows a failed quiesce; recovery owns quarantine.
        if(resourceOwner && safe) resourceOwner->release();
        resourceOwner=nullptr;
        IOBlockStorageDevice::free();
    }
    IOReturn doAsyncReadWrite(IOMemoryDescriptor *buffer, UInt64 block, UInt64 count,
        IOStorageAttributes *, IOStorageCompletion *completion) override {
        if(!buffer || !completion || !completion->action) return kIOReturnBadArgument;
        if(!__atomic_load_n(&online,__ATOMIC_ACQUIRE)) return kIOReturnNotReady;
        IOStorageCompletion saved=*completion;
        retain(); buffer->retain();
        EnumaReadRequest request{block,count,buffer,
            [](void *p,uint64_t offset,const void *data,uint64_t size)->uint64_t {
                return static_cast<IOMemoryDescriptor *>(p)->writeBytes(offset,data,size);
            }};
        auto submitted=enumaBlockSubmit(*owner,sectors,buffer->getLength(),
            buffer->getDirection()==kIODirectionIn,request,&saved,
            [](void *p,enuma_root_result result) {
                auto c=static_cast<IOStorageCompletion *>(p);
                IOReturn status=result.status==ENUMA_ROOT_OK?kIOReturnSuccess:
                    result.status==ENUMA_ROOT_ARGUMENT?kIOReturnBadArgument:
                    result.status==ENUMA_ROOT_INTEGRITY?kIOReturnNotPrivileged:kIOReturnIOError;
                c->action(c->target,c->parameter,status,result.done);
            });
        buffer->release(); release();
        return submitted==EnumaSubmission::Accepted?kIOReturnSuccess:
            submitted==EnumaSubmission::NotWritable?kIOReturnNotWritable:kIOReturnBadArgument;
    }
    IOReturn doEjectMedia() override {return kIOReturnUnsupported;}
    IOReturn doFormatMedia(UInt64) override {return kIOReturnNotWritable;}
    UInt32 doGetFormatCapacities(UInt64 *,UInt32) const override {return 0;}
    char *getVendorString() override {return const_cast<char *>("Enuma");}
    char *getProductString() override {return const_cast<char *>("Reviewed root window");}
    char *getRevisionString() override {return const_cast<char *>("1");}
    char *getAdditionalDeviceInfoString() override {return const_cast<char *>("Read-only bounded window");}
    IOReturn reportBlockSize(UInt64 *v) override {*v=512;return kIOReturnSuccess;}
    IOReturn reportMaxValidBlock(UInt64 *v) override {*v=sectors-1;return kIOReturnSuccess;}
    IOReturn reportMediaState(bool *p,bool *c) override {*p=__atomic_load_n(&online,__ATOMIC_ACQUIRE);if(c)*c=false;return kIOReturnSuccess;}
    IOReturn reportEjectability(bool *v) override {*v=false;return kIOReturnSuccess;}
    IOReturn reportRemovability(bool *v) override {*v=false;return kIOReturnSuccess;}
    IOReturn reportWriteProtection(bool *v) override {*v=true;return kIOReturnSuccess;}
};
OSDefineMetaClassAndStructors(EnumaBlockDevice,IOBlockStorageDevice)

// Caller must already have qualified takeover AND known-block comparison.
// Returns a retained service; caller must terminate/detach/release it normally.
// This symbol has no automatic caller in current Enuma kernel configuration.
extern "C" IOService *enuma_storage_publish_readonly(IOService *anchor,
    const EnumaStorageConfig *config, bool takeoverReady, bool knownBlocksCompared) {
    if(!anchor || !config || !takeoverReady || !knownBlocksCompared) return nullptr;
    auto device=new EnumaBlockDevice;
    if(!device) return nullptr;
    bool attached=false;
    if(device->init(nullptr) && device->configure(anchor,*config)) {
        attached=device->attach(anchor);
        if(attached && device->start(anchor)) return device;
    }
    if(attached) device->detach(anchor);
    device->release(); return nullptr;
}
