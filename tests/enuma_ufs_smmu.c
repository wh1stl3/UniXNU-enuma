// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "EnumaUfsSmmu.h"
static uint32_t regs[0x100000/4];
static unsigned reads,writes,fail_read,fail_write,drop_write,idle;
static int rd(void *c,uint32_t at,uint32_t *v){(void)c;assert(at<sizeof(regs)&&!(at&3));if(++reads==fail_read)return 0;*v=regs[at/4];return 1;}
static int wr(void *c,uint32_t at,uint32_t v){(void)c;assert(at<sizeof(regs)&&!(at&3));writes++;if(writes==fail_write)return 0;if(writes!=drop_write)regs[at/4]=v;return 1;}
static int quiet(void *c){(void)c;return idle;}
static struct enuma_smmu_request request={0x10000000,0x10000,0x10000000,0x20000,0x100000,{0xe0,0x4e0}};
static void reset(void){memset(regs,0,sizeof(regs));reads=writes=fail_read=fail_write=drop_write=0;idle=1;regs[0x20/4]=(1U<<30)|(1U<<27)|8;regs[0x24/4]=4;regs[0x28/4]=0x1222;}
static struct enuma_smmu_plan plan(void){struct enuma_smmu_plan p;assert(enuma_smmu_plan(&request,rd,0,&p)==0);return p;}
int main(void){
    reset();struct enuma_smmu_plan p=plan(),old=p;unsigned plan_reads=reads;
    struct enuma_smmu_attempt a={0};reads=0;
    assert(enuma_smmu_apply(&p,rd,wr,quiet,0,&a)==0&&a.dma_allowed&&a.writes==7);
    unsigned apply_reads=reads;
    assert(enuma_smmu_apply(&p,rd,wr,quiet,0,&a)==ENUMA_SMMU_BUSY&&writes==7&&!a.dma_allowed);
    struct enuma_smmu_plan reused=plan();struct enuma_smmu_attempt reuse={0};
    assert(reused.reuse[0]&&reused.reuse[1]);assert(enuma_smmu_apply(&reused,rd,wr,quiet,0,&reuse)==0);
    for(unsigned i=1;i<=plan_reads;i++){
        reset();p=old;fail_read=i;assert(enuma_smmu_plan(&request,rd,0,&p)==ENUMA_SMMU_IO);assert(!memcmp(&p,&old,sizeof(p))&&!writes);
    }
    for(unsigned i=1;i<=apply_reads;i++){
        reset();p=plan();reads=0;fail_read=i;a=(struct enuma_smmu_attempt){0};
        assert(enuma_smmu_apply(&p,rd,wr,quiet,0,&a)!=0&&!a.dma_allowed&&a.consumed);
    }
    for(unsigned i=1;i<=7;i++){
        reset();p=plan();fail_write=i;a=(struct enuma_smmu_attempt){0};
        assert(enuma_smmu_apply(&p,rd,wr,quiet,0,&a)==ENUMA_SMMU_WRITE&&!a.dma_allowed&&writes==i);
        reset();p=plan();drop_write=i;a=(struct enuma_smmu_attempt){0};
        // Writing zero to an already-zero SCTLR need not change a register.
        int e=enuma_smmu_apply(&p,rd,wr,quiet,0,&a);assert(i==1?e==0:e!=0);
    }
    reset();p=plan();regs[0x800/4]=0x80000000|0x55;regs[0xc00/4]=p.bank;a=(struct enuma_smmu_attempt){0};
    assert(enuma_smmu_apply(&p,rd,wr,quiet,0,&a)==ENUMA_SMMU_CONFLICT&&!writes);
    reset();p=plan();regs[0xc00/4]=0x10000;a=(struct enuma_smmu_attempt){0};
    assert(enuma_smmu_apply(&p,rd,wr,quiet,0,&a)==ENUMA_SMMU_CHANGED&&!writes);
    reset();p=plan();p.slot[0]=200;a=(struct enuma_smmu_attempt){0};
    assert(enuma_smmu_apply(&p,rd,wr,quiet,0,&a)==ENUMA_SMMU_CHANGED&&!writes);
    reset();p=plan();idle=0;a=(struct enuma_smmu_attempt){0};assert(enuma_smmu_apply(&p,rd,wr,quiet,0,&a)==ENUMA_SMMU_BUSY&&!writes);
    reset();regs[0x800/4]=0x80000000|0x4000000|0xe0;assert(enuma_smmu_plan(&request,rd,0,&p)==ENUMA_SMMU_CONFLICT);
    reset();regs[5*4096/4]=1;assert(enuma_smmu_plan(&request,rd,0,&p)==ENUMA_SMMU_BUSY);
    reset();struct enuma_smmu_request r=request;r.dma=UINT64_MAX-4095;r.owned_base=r.dma;r.owned_size=8192;
    assert(enuma_smmu_plan(&r,rd,0,&p)==ENUMA_SMMU_DMA);
    r=request;r.streams[1]=r.streams[0];assert(enuma_smmu_plan(&r,rd,0,&p)==ENUMA_SMMU_ARGUMENT);
    r=request;r.mapped_bytes=8192;assert(enuma_smmu_plan(&r,rd,0,&p)==ENUMA_SMMU_FORMAT);
    printf("PASS: plan reads=%u, apply reads=%u fault-injected; 7 write refusals, stale/foreign routes, reused routes, DMA bounds and quarantine\n",plan_reads,apply_reads);
}
