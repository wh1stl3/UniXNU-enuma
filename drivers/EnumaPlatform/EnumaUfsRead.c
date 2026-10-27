// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "EnumaUfsRead.h"
static uint32_t be32(const uint8_t *p){return (uint32_t)p[0]<<24|(uint32_t)p[1]<<16|(uint32_t)p[2]<<8|p[3];}
int enuma_ufs_capacity10(const uint8_t *p,unsigned bytes,uint8_t lun,struct enuma_ufs_geometry *out){
    if(!p||!out||bytes!=8||lun>7)return 0;
    uint32_t last=be32(p),size=be32(p+4);
    // The pinned root parser consumes 4 KiB LBAs. Other geometry needs a
    // different parser, never silent conversion or another board's capacity.
    if(last==UINT32_MAX||!last||size!=4096)return 0;
    *out=(struct enuma_ufs_geometry){(uint64_t)last+1,size,lun};return 1;
}
int enuma_ufs_prepare_read(const struct enuma_ufs_geometry *g,uint64_t first,uint64_t count,
    uint64_t relative,uint32_t blocks,uint32_t dma_bytes,struct enuma_ufs_read *out){
    struct enuma_ufs_read r={{0},0,0};uint64_t lba;
    if(!g||!out||g->block_bytes!=4096||g->lun>7||!g->blocks||g->blocks>UINT32_MAX||
       !count||first>=g->blocks||count>g->blocks-first||relative>=count||
       !blocks||blocks>65535||blocks>count-relative||blocks>dma_bytes/4096)return 0;
    lba=first+relative;r.cdb[0]=0x28;
    for(unsigned i=0;i<4;i++)r.cdb[2+i]=(uint8_t)(lba>>(24-8*i));
    r.cdb[7]=(uint8_t)(blocks>>8);r.cdb[8]=(uint8_t)blocks;r.lun=g->lun;r.bytes=blocks*4096;
    *out=r;return 1;
}
