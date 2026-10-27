// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "EnumaRootRead.h"
#include <stddef.h>
using IOReturn = uint32_t;
constexpr IOReturn kIOReturnSuccess=ENUMA_ROOT_OK, kIOReturnBadArgument=ENUMA_ROOT_ARGUMENT,
    kIOReturnIOError=ENUMA_ROOT_IO;
constexpr uint64_t kDataMax=131072;
// Fixed external NativeUfs production algorithm; build recipe checks its pin.
#include "RootWindowRead.h"
struct EnumaWindowOps {
    const enuma_ufs_geometry &geometry;
    uint64_t first, blocks;
    const enuma_root_ops &ops;
    void lock() { ops.lock(ops.context); }
    void unlock() { ops.unlock(ops.context); }
    IOReturn read(uint64_t lba, uint32_t count, void *destination) {
        enuma_ufs_read request;
        if (lba<first || !enuma_ufs_prepare_read(&geometry,first,blocks,lba-first,count,kDataMax,&request))
            return ENUMA_ROOT_ARGUMENT;
        return ops.read(ops.context,&request,destination);
    }
    IOReturn verify(uint64_t block,const void *data,size_t bytes) {
        return ops.verify(ops.context,block,data,bytes);
    }
    uint64_t copy(uint64_t offset,const void *data,uint64_t bytes) {
        return ops.copy(ops.context,offset,data,bytes);
    }
};
extern "C" enuma_root_result enuma_root_read(const enuma_ufs_geometry *g,
    uint64_t first,uint64_t blocks,uint64_t sector,uint64_t count,
    void *bounce,uint32_t bounce_bytes,const enuma_root_ops *ops) {
    enuma_ufs_read probe;
    if (!g || !ops || !ops->lock || !ops->unlock || !ops->read || !ops->verify || !ops->copy ||
        !bounce || bounce_bytes<kDataMax ||
        !enuma_ufs_prepare_read(g,first,blocks,0,1,kDataMax,&probe))
        return {ENUMA_ROOT_ARGUMENT,0};
    EnumaWindowOps port{*g,first,blocks,*ops};
    auto result=ufsReadWindow(port,first*4096,blocks*4096,sector,count,static_cast<uint8_t *>(bounce));
    return {result.status,result.done};
}
