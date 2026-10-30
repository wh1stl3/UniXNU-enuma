// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "EnumaRootTransport.h"
uint32_t enuma_root_transport_read(void *context, const struct enuma_ufs_read *r, void *out)
{
    struct enuma_root_transport *t=context;
    struct enuma_ufs_read canonical;
    uint32_t lba=0, blocks;
    if (!t || !r || !out || !t->read4k) return ENUMA_ROOT_ARGUMENT;
    for (unsigned i=2;i<6;i++) lba=(lba<<8)|r->cdb[i];
    blocks=((uint32_t)r->cdb[7]<<8)|r->cdb[8];
    if (lba<t->first || !enuma_ufs_prepare_read(&t->geometry,t->first,t->blocks,
            lba-t->first,blocks,131072,&canonical)) return ENUMA_ROOT_ARGUMENT;
    if (r->lun!=canonical.lun || r->bytes!=canonical.bytes) return ENUMA_ROOT_ARGUMENT;
    for (unsigned i=0;i<10;i++) if (r->cdb[i]!=canonical.cdb[i]) return ENUMA_ROOT_ARGUMENT;
    t->native_status=t->read4k(t->host,r->lun,lba,blocks,out);
    // Preserve detailed native diagnostics separately. No retries or reset;
    // the native host retains any allocation with uncertain DMA ownership.
    return t->native_status ? ENUMA_ROOT_IO : ENUMA_ROOT_OK;
}
