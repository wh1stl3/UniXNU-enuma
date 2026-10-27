// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "EnumaRamDisk.h"
#include "SparseDisk.h"
namespace {
struct State { RamSparseDisk disk; uint64_t budget; };
bool valid(const enuma_ram_disk *d){return d && d->ops && d->ops->lock && d->ops->unlock && d->ops->allocate && d->ops->release;}
struct Guard {
    const enuma_ram_ops &o;
    explicit Guard(const enuma_ram_ops &ops):o(ops){o.lock(o.context);}
    ~Guard(){o.unlock(o.context);}
};
void destroy(State *s,const enuma_ram_ops &o){
    if(!s)return;
    if(s->disk.pages){
        for(uint64_t i=0;i<s->disk.bytes/4096;++i)
            if(s->disk.pages[i])o.release(o.context,s->disk.pages[i],4096);
        o.release(o.context,s->disk.pages,s->disk.bytes/4096*sizeof(uint8_t *));
    }
    o.release(o.context,s,sizeof(*s));
}
struct Pages {
    State &s;const enuma_ram_ops &o;
    uint8_t *allocate(){
        if(s.disk.resident>s.budget || 4096>s.budget-s.disk.resident)return nullptr;
        auto *p=static_cast<uint8_t *>(o.allocate(o.context,4096));
        if(p)memset(p,0,4096);
        return p;
    }
};
struct Transfer:Pages {
    void *request;uint64_t (*callback)(void *,uint64_t,void *,uint64_t);
    uint64_t read(uint64_t at,void *p,uint64_t n){return callback(request,at,p,n);}
    uint64_t copy(uint64_t at,const void *p,uint64_t n){return callback(request,at,const_cast<void *>(p),n);}
};
}
extern "C" uint32_t enuma_ram_start(enuma_ram_disk *d,const void *packed,uint64_t bytes,uint64_t budget){
    if(!valid(d))return ENUMA_RAM_ARGUMENT;
    Guard guard(*d->ops);
    if(d->implementation)return ENUMA_RAM_BUSY;
    uint64_t logical=0;
    if(!ramPackedLayout(static_cast<const uint8_t *>(packed),bytes,&logical) || logical>0x80000000ULL ||
        budget>logical || (budget&4095))return ENUMA_RAM_ARGUMENT;
    auto *s=static_cast<State *>(d->ops->allocate(d->ops->context,sizeof(State)));
    if(!s)return ENUMA_RAM_MEMORY;
    memset(s,0,sizeof(*s));s->disk.bytes=logical;s->budget=budget;
    uint64_t table=logical/4096*sizeof(uint8_t *);
    s->disk.pages=static_cast<uint8_t **>(d->ops->allocate(d->ops->context,table));
    if(!s->disk.pages){destroy(s,*d->ops);return ENUMA_RAM_MEMORY;}
    memset(s->disk.pages,0,table);Pages pages{*s,*d->ops};
    if(!ramSparseImport(s->disk,static_cast<const uint8_t *>(packed),bytes,pages)){
        destroy(s,*d->ops);return ENUMA_RAM_MEMORY;
    }
    d->implementation=s;return ENUMA_RAM_OK;
}
extern "C" uint32_t enuma_ram_info(enuma_ram_disk *d,struct enuma_ram_info *out){
    if(!valid(d)||!out)return ENUMA_RAM_ARGUMENT;
    Guard guard(*d->ops);auto *s=static_cast<State *>(d->implementation);
    if(!s)return ENUMA_RAM_OFFLINE;
    *out={s->disk.bytes,s->disk.resident,s->disk.bytes/4096*sizeof(uint8_t *),s->budget};return ENUMA_RAM_OK;
}
extern "C" enuma_ram_result enuma_ram_io(enuma_ram_disk *d,int write,uint64_t sector,uint64_t count,
    uint64_t descriptor,void *request,uint64_t (*callback)(void *,uint64_t,void *,uint64_t)){
    if(!valid(d)||!callback||(write!=0&&write!=1))return {ENUMA_RAM_ARGUMENT,0};
    Guard guard(*d->ops);auto *s=static_cast<State *>(d->implementation);
    if(!s)return {ENUMA_RAM_OFFLINE,0};
    if(!count || sector>=s->disk.bytes/512 || count>s->disk.bytes/512-sector || count>descriptor/512)
        return {ENUMA_RAM_ARGUMENT,0};
    Transfer transfer{{*s,*d->ops},request,callback};bool noMemory=false;
    uint64_t done=ramSparseIO(s->disk,write,sector*512,count*512,transfer,noMemory);
    return {noMemory?ENUMA_RAM_MEMORY:done==count*512?ENUMA_RAM_OK:ENUMA_RAM_IO,done};
}
extern "C" uint32_t enuma_ram_stop(enuma_ram_disk *d){
    if(!valid(d))return ENUMA_RAM_ARGUMENT;
    Guard guard(*d->ops);auto *s=static_cast<State *>(d->implementation);
    d->implementation=nullptr;destroy(s,*d->ops);return ENUMA_RAM_OK;
}
