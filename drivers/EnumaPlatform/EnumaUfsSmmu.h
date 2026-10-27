// SPDX-License-Identifier: BSD-2-Clause-Patent
// Derived from UniXNU-umi UmiSmmuTakeover.h at 3eb7257; see ufs-sources.json.
// Offline-qualified component only; not connected to XNU or physical MMIO.
#ifndef ENUMA_UFS_SMMU_H
#define ENUMA_UFS_SMMU_H
#include <stdint.h>
enum enuma_smmu_error { ENUMA_SMMU_OK, ENUMA_SMMU_ARGUMENT, ENUMA_SMMU_IO,
    ENUMA_SMMU_FORMAT, ENUMA_SMMU_DMA, ENUMA_SMMU_CONFLICT, ENUMA_SMMU_BUSY,
    ENUMA_SMMU_NO_SLOT, ENUMA_SMMU_CHANGED, ENUMA_SMMU_WRITE };
typedef int (*enuma_smmu_read)(void *,uint32_t,uint32_t *);
// Implementations must order writes and return failure on refused writes.
typedef int (*enuma_smmu_write)(void *,uint32_t,uint32_t);
typedef int (*enuma_smmu_exclusive_idle)(void *);
struct enuma_smmu_request {
    uint64_t dma,bytes,owned_base,owned_size;
    uint32_t mapped_bytes;
    uint16_t streams[2]; // caller supplies separately established board identity
};
struct enuma_smmu_plan {
    struct enuma_smmu_request request;
    uint32_t id[3],smr[128],s2cr[128],sctlr,cbar,cba2r;
    unsigned count,pages,bank,slot[2],reuse[2];
};
struct enuma_smmu_attempt { unsigned consumed,writes,dma_allowed; };
// Failed planning leaves output untouched. No write callback exists here.
int enuma_smmu_plan(const struct enuma_smmu_request *,enuma_smmu_read,void *,struct enuma_smmu_plan *);
// Caller owns serialization AND has stopped both HC queues. Revalidates the
// entire route table before writing. Any failure leaves dma_allowed false;
// never free DMA descriptors or attempt rollback/retry on this attempt.
int enuma_smmu_apply(const struct enuma_smmu_plan *,enuma_smmu_read,enuma_smmu_write,
                     enuma_smmu_exclusive_idle,void *,struct enuma_smmu_attempt *);
#endif
