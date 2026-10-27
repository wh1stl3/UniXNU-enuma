// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "EnumaUfsSmmu.h"
static int owned(const struct enuma_smmu_request *r){
    return r->bytes && r->owned_size && r->owned_size<=UINT64_MAX-r->owned_base &&
        r->dma>=r->owned_base && r->bytes<=r->owned_size &&
        r->dma-r->owned_base<=r->owned_size-r->bytes && !(r->dma&4095);
}
int enuma_smmu_plan(const struct enuma_smmu_request *r,enuma_smmu_read read,void *ctx,struct enuma_smmu_plan *out){
    struct enuma_smmu_plan p={0};unsigned free_slots[128],free_count=0,banks;
    static const unsigned bits[]={32,36,40,42,44,48};
    if(!r||!read||!out||r->streams[0]==r->streams[1]||r->streams[0]>0x7fff||r->streams[1]>0x7fff)return ENUMA_SMMU_ARGUMENT;
    if(!owned(r))return ENUMA_SMMU_DMA;
    if(r->mapped_bytes<0x2000)return ENUMA_SMMU_FORMAT;
    p.request=*r;
    for(unsigned i=0;i<3;i++)if(!read(ctx,0x20+4*i,&p.id[i]))return ENUMA_SMMU_IO;
    p.count=p.id[0]&255;p.pages=1U<<(((p.id[1]>>28)&7)+1);banks=p.id[1]&255;
    if(!(p.id[0]&(1U<<30))||!(p.id[0]&(1U<<27))||!(p.id[2]&(1U<<12))||
       !p.count||p.count>128||(p.id[1]>>31)||p.pages>128||banks<2||banks>128||
       (p.pages+banks)*4096>r->mapped_bytes)return ENUMA_SMMU_FORMAT;
    for(unsigned shift=0;shift<=8;shift+=4){
        unsigned code=(p.id[2]>>shift)&15;
        if(code>=6||r->dma>=(1ULL<<bits[code])||r->bytes>(1ULL<<bits[code])-r->dma)return ENUMA_SMMU_DMA;
    }
    p.bank=banks-1;
    for(unsigned i=0;i<p.count;i++){
        if(!read(ctx,0x800+4*i,&p.smr[i])||!read(ctx,0xc00+4*i,&p.s2cr[i]))return ENUMA_SMMU_IO;
        if(!(p.smr[i]&0x80000000U)){free_slots[free_count++]=i;continue;}
        unsigned mask=(p.smr[i]>>16)&0x7fff,own=((p.s2cr[i]>>16)&3)==0&&(p.s2cr[i]&255)==p.bank,used=0;
        for(unsigned s=0;s<2;s++){
            if(((p.smr[i]^r->streams[s])&0xffff&~mask)!=0)continue;
            if(p.reuse[s]||mask||!own||p.s2cr[i]!=p.bank)return ENUMA_SMMU_CONFLICT;
            p.reuse[s]=1;p.slot[s]=i;used=1;
        }
        if(own&&!used)return ENUMA_SMMU_CONFLICT;
    }
    if(!read(ctx,(p.pages+p.bank)*4096,&p.sctlr)||!read(ctx,0x1000+4*p.bank,&p.cbar)||
       !read(ctx,0x1800+4*p.bank,&p.cba2r))return ENUMA_SMMU_IO;
    if((p.sctlr&1)||((p.reuse[0]||p.reuse[1])&&(p.sctlr||p.cbar!=0x10000||(p.cba2r&~1U))))return ENUMA_SMMU_BUSY;
    for(unsigned s=0;s<2;s++)if(!p.reuse[s]){
        if(!free_count)return ENUMA_SMMU_NO_SLOT;
        p.slot[s]=free_slots[--free_count];
    }
    *out=p;return ENUMA_SMMU_OK;
}
static int same(const struct enuma_smmu_plan *a,const struct enuma_smmu_plan *b){
    if(a->count!=b->count||a->bank!=b->bank||a->pages!=b->pages||a->sctlr!=b->sctlr||a->cbar!=b->cbar||a->cba2r!=b->cba2r)return 0;
    for(unsigned i=0;i<3;i++)if(a->id[i]!=b->id[i])return 0;
    for(unsigned i=0;i<a->count;i++)if(a->smr[i]!=b->smr[i]||a->s2cr[i]!=b->s2cr[i])return 0;
    for(unsigned i=0;i<2;i++)if(a->slot[i]!=b->slot[i]||a->reuse[i]!=b->reuse[i])return 0;
    return 1;
}
static int put(enuma_smmu_read read,enuma_smmu_write write,void *ctx,struct enuma_smmu_attempt *a,uint32_t at,uint32_t value){
    uint32_t got=0;a->writes++;
    return write(ctx,at,value)&&read(ctx,at,&got)&&got==value;
}
int enuma_smmu_apply(const struct enuma_smmu_plan *p,enuma_smmu_read read,enuma_smmu_write write,
                     enuma_smmu_exclusive_idle idle,void *ctx,struct enuma_smmu_attempt *a){
    struct enuma_smmu_plan fresh;int error;uint32_t cb;
    if(a)a->dma_allowed=0;
    if(!p||!read||!write||!idle||!a)return ENUMA_SMMU_ARGUMENT;
    if(a->consumed)return ENUMA_SMMU_BUSY;
    a->consumed=1;a->writes=0;a->dma_allowed=0;
    if(!idle(ctx))return ENUMA_SMMU_BUSY;
    error=enuma_smmu_plan(&p->request,read,ctx,&fresh);
    if(error)return error;
    if(!same(p,&fresh))return ENUMA_SMMU_CHANGED;
    if(!idle(ctx))return ENUMA_SMMU_BUSY;
    cb=(p->pages+p->bank)*4096;
    if(!p->reuse[0]&&!p->reuse[1]){
        if(!put(read,write,ctx,a,cb,0)||!put(read,write,ctx,a,0x1000+4*p->bank,0x10000))return ENUMA_SMMU_WRITE;
    }
    if(!put(read,write,ctx,a,0x1800+4*p->bank,1))return ENUMA_SMMU_WRITE;
    for(unsigned s=0;s<2;s++)if(!p->reuse[s])
        if(!put(read,write,ctx,a,0xc00+4*p->slot[s],p->bank))return ENUMA_SMMU_WRITE;
    for(unsigned s=0;s<2;s++)if(!p->reuse[s])
        if(!put(read,write,ctx,a,0x800+4*p->slot[s],0x80000000U|p->request.streams[s]))return ENUMA_SMMU_WRITE;
    // Complete final replan catches either route changing after its readback.
    error=enuma_smmu_plan(&p->request,read,ctx,&fresh);
    if(error||!fresh.reuse[0]||!fresh.reuse[1]||fresh.bank!=p->bank||
       fresh.slot[0]!=p->slot[0]||fresh.slot[1]!=p->slot[1]||fresh.cba2r!=1||!idle(ctx))return ENUMA_SMMU_CHANGED;
    a->dma_allowed=1;return ENUMA_SMMU_OK;
}
