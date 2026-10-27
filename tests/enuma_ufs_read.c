// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include "EnumaUfsRead.h"
int main(void){
    uint8_t cap[]={0,0,0x0f,0xff,0,0,0x10,0};struct enuma_ufs_geometry g={0};
    assert(enuma_ufs_capacity10(cap,8,0,&g)&&g.blocks==4096);
    struct enuma_ufs_read r={{0},0,0},old;
    assert(enuma_ufs_prepare_read(&g,100,100,99,1,4096,&r));
    assert(r.cdb[0]==0x28&&r.cdb[5]==199&&r.cdb[8]==1&&r.bytes==4096);old=r;
    assert(!enuma_ufs_prepare_read(&g,100,100,99,2,8192,&r)&&!memcmp(&r,&old,sizeof(r)));
    assert(!enuma_ufs_prepare_read(&g,100,100,0,1,4095,&r));
    assert(!enuma_ufs_prepare_read(&g,UINT64_MAX-1,8,0,1,4096,&r));
    assert(!enuma_ufs_prepare_read(&g,0,4097,0,1,4096,&r));
    assert(!enuma_ufs_prepare_read(&g,0,4096,0,0,4096,&r));
    assert(!enuma_ufs_prepare_read(&g,0,4096,0,65536,UINT32_MAX,&r));
    for(unsigned n=0;n<8;n++)assert(!enuma_ufs_capacity10(cap,n,0,&g));
    memset(cap,255,4);assert(!enuma_ufs_capacity10(cap,8,0,&g));
    cap[0]=0;cap[6]=2;assert(!enuma_ufs_capacity10(cap,8,0,&g));
    puts("PASS: real capacity required, root-window boundaries, overflow, DMA extent, READ(10)-only encoding");
}
