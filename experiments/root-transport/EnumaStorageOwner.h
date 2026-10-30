// SPDX-License-Identifier: BSD-2-Clause-Patent
#pragma once
#include "EnumaLifecycle.h"
#include "EnumaRootTransport.h"
struct EnumaReadRequest {
    uint64_t sector,count;
    void *destination;
    uint64_t (*copy)(void *,uint64_t,const void *,uint64_t);
};
// Immutable setup held alive by the provider. State and snapshot locks must
// be distinct; snapshot precedes native host lock. No callbacks may throw.
struct EnumaStorageConfig {
    enuma_root_transport *transport;
    void *context,*bounce;
    uint32_t bounceBytes;
    void (*stateLock)(void *),(*stateUnlock)(void *);
    void (*snapshotLock)(void *),(*snapshotUnlock)(void *);
    uint32_t (*verify)(void *,uint64_t,const void *,uint64_t);
    bool (*poisoned)(void *),(*quiesce)(void *);
};
class EnumaStoragePort {
    EnumaStorageConfig config;
    struct Call {EnumaStoragePort &port;const EnumaReadRequest &request;};
    static void rootLock(void *p){auto &c=static_cast<Call *>(p)->port.config;c.snapshotLock(c.context);}
    static void rootUnlock(void *p){auto &c=static_cast<Call *>(p)->port.config;c.snapshotUnlock(c.context);}
    static uint32_t rootRead(void *p,const enuma_ufs_read *r,void *out){
        return enuma_root_transport_read(static_cast<Call *>(p)->port.config.transport,r,out);
    }
    static uint32_t rootVerify(void *p,uint64_t block,const void *data,uint64_t bytes){
        auto &c=static_cast<Call *>(p)->port.config;return c.verify(c.context,block,data,bytes);
    }
    static uint64_t rootCopy(void *p,uint64_t at,const void *data,uint64_t bytes){
        auto &r=static_cast<Call *>(p)->request;return r.copy(r.destination,at,data,bytes);
    }
public:
    explicit EnumaStoragePort(const EnumaStorageConfig &c):config(c){}
    bool valid() const {
        if (!(config.transport && config.transport->read4k && config.bounce && config.bounceBytes>=131072 &&
            config.stateLock && config.stateUnlock && config.snapshotLock && config.snapshotUnlock &&
            config.verify && config.poisoned && config.quiesce))return false;
        enuma_ufs_read probe;auto &t=*config.transport;
        return enuma_ufs_prepare_read(&t.geometry,t.first,t.blocks,0,1,config.bounceBytes,&probe)!=0;
    }
    void lock(){config.stateLock(config.context);}void unlock(){config.stateUnlock(config.context);}
    bool poisoned(){return config.poisoned(config.context);}bool quiesce(){return config.quiesce(config.context);}
    enuma_root_result rejected(){return {ENUMA_ROOT_IO,0};}
    enuma_root_result read(const EnumaReadRequest &r){
        if(!r.destination || !r.copy)return {ENUMA_ROOT_ARGUMENT,0};
        Call call{*this,r};enuma_root_ops ops{&call,rootLock,rootUnlock,rootRead,rootVerify,rootCopy};
        auto &t=*config.transport;
        return enuma_root_read(&t.geometry,t.first,t.blocks,r.sector,r.count,config.bounce,config.bounceBytes,&ops);
    }
};
class EnumaStorageOwner {
    EnumaStoragePort port;
    EnumaLifecycle<EnumaStoragePort> life;
    const bool configured;
public:
    explicit EnumaStorageOwner(const EnumaStorageConfig &c):port(c),life(port),configured(port.valid()){}
    EnumaStorageOwner(const EnumaStorageOwner &)=delete;
    EnumaStorageOwner &operator=(const EnumaStorageOwner &)=delete;
    bool activate(bool takeoverReady){return configured && life.activate(takeoverReady);}
    enuma_root_result read(const EnumaReadRequest &r){return configured?life.read(r):enuma_root_result{ENUMA_ROOT_ARGUMENT,0};}
    void requestStop(){if(configured)life.requestStop();}
    bool tryDrain(){return configured && life.tryDrain();}
    bool releasable(){return configured && life.releasable();}
};
// Completion belongs to the IOKit wrapper AFTER read returns. Retain the
// owner/request/callback contexts through completion. No allocation, release,
// provider registration, persistence writes or guessed private ABI here.
