// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "EnumaRamDisk.h"
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <vector>
struct Fixture {
    std::mutex gate;
    std::mutex observation;
    std::condition_variable attempted;
    unsigned attempts=0;
    std::map<void *,uint64_t> allocations;
    unsigned calls=0,fail=0;
    bool held=false;
    enuma_ram_ops ops{this,lock,unlock,allocate,release};
    enuma_ram_disk disk{&ops,nullptr};
    static Fixture &self(void *p){return *static_cast<Fixture *>(p);}
    static void lock(void *p){auto &f=self(p);{std::lock_guard<std::mutex> lock(f.observation);++f.attempts;f.attempted.notify_all();}
        f.gate.lock();assert(!f.held);f.held=true;}
    static void unlock(void *p){auto &f=self(p);assert(f.held);f.held=false;f.gate.unlock();}
    static void *allocate(void *p,uint64_t n){auto &f=self(p);assert(f.held);if(++f.calls==f.fail)return nullptr;
        void *v=malloc(n);assert(v);memset(v,0xa5,n);f.allocations[v]=n;return v;}
    static void release(void *p,void *v,uint64_t n){auto &f=self(p);assert(f.held && f.allocations.at(v)==n);
        f.allocations.erase(v);free(v);}
    ~Fixture(){assert(!disk.implementation && allocations.empty());}
};
struct Request {
    std::vector<uint8_t> data;
    bool write=false;
    uint64_t limit=UINT64_MAX;
    unsigned calls=0;
    std::mutex control;std::condition_variable changed;bool park=false,entered=false,proceed=false;
    explicit Request(size_t n):data(n,0x5a){}
    static uint64_t transfer(void *p,uint64_t at,void *page,uint64_t n){
        auto &r=*static_cast<Request *>(p);++r.calls;
        if(r.park){std::unique_lock<std::mutex> lock(r.control);r.entered=true;r.changed.notify_all();r.changed.wait(lock,[&]{return r.proceed;});}
        n=n<r.limit?n:r.limit;assert(at+n<=r.data.size());
        if(r.write)memcpy(page,r.data.data()+at,n);else memcpy(r.data.data()+at,page,n);
        return n;
    }
};
static std::vector<uint8_t> load(const char *path){FILE *f=fopen(path,"rb");assert(f);fseek(f,0,SEEK_END);long n=ftell(f);assert(n>0);rewind(f);
    std::vector<uint8_t> b(n);assert(fread(b.data(),1,n,f)==size_t(n));fclose(f);return b;}
int main(int argc,char **argv){
    assert(argc==3);auto seed=load(argv[1]);unsigned allocations;
    {Fixture f;assert(enuma_ram_start(&f.disk,seed.data(),seed.size(),8<<20)==0);allocations=f.calls;
     struct enuma_ram_info info;assert(!enuma_ram_info(&f.disk,&info) && info.logical_bytes==512ULL<<20 && info.resident_bytes<8<<20);
     assert(enuma_ram_start(&f.disk,seed.data(),seed.size(),8<<20)==ENUMA_RAM_BUSY);
     FILE *raw=fopen(argv[2],"rb");assert(raw);Request r(1<<20);std::vector<uint8_t> expected(r.data.size());
     for(uint64_t at=0;at<info.logical_bytes;at+=r.data.size()){
         auto result=enuma_ram_io(&f.disk,0,at/512,r.data.size()/512,r.data.size(),&r,Request::transfer);
         assert(!result.status && result.done==r.data.size());assert(fread(expected.data(),1,expected.size(),raw)==expected.size());assert(r.data==expected);
     }fclose(raw);
     // Volatile writes span pages, short writes report their actual prefix.
     r.write=true;r.limit=511;auto result=enuma_ram_io(&f.disk,1,1001,16,r.data.size(),&r,Request::transfer);
     assert(result.status==ENUMA_RAM_IO && result.done==511);
     r.limit=UINT64_MAX;std::fill(r.data.begin(),r.data.end(),0x3c);result=enuma_ram_io(&f.disk,1,1001,16,r.data.size(),&r,Request::transfer);
     assert(!result.status && result.done==8192);r.write=false;std::fill(r.data.begin(),r.data.end(),0);result=enuma_ram_io(&f.disk,0,1001,16,r.data.size(),&r,Request::transfer);
     assert(!result.status);for(unsigned i=0;i<8192;++i)assert(r.data[i]==0x3c);
     for(auto count:{uint64_t(0),UINT64_MAX})assert(enuma_ram_io(&f.disk,0,0,count,UINT64_MAX,&r,Request::transfer).status==ENUMA_RAM_ARGUMENT);
     assert(enuma_ram_io(&f.disk,0,info.logical_bytes/512,1,512,&r,Request::transfer).status==ENUMA_RAM_ARGUMENT);
     assert(!enuma_ram_stop(&f.disk) && !enuma_ram_stop(&f.disk));assert(enuma_ram_io(&f.disk,0,0,1,512,&r,Request::transfer).status==ENUMA_RAM_OFFLINE);
     assert(!enuma_ram_start(&f.disk,seed.data(),seed.size(),8<<20));assert(!enuma_ram_stop(&f.disk));}
    // Fail every allocation of the actual APFS seed import, not a dummy seed.
    for(unsigned i=1;i<=allocations;++i){Fixture f;f.fail=i;assert(enuma_ram_start(&f.disk,seed.data(),seed.size(),8<<20)==ENUMA_RAM_MEMORY);
        assert(!f.disk.implementation && f.allocations.empty() && !f.held);assert(!enuma_ram_stop(&f.disk));}
    {Fixture f;assert(enuma_ram_start(&f.disk,seed.data(),seed.size(),0)==ENUMA_RAM_MEMORY);assert(f.allocations.empty());}
    {Fixture f;assert(enuma_ram_start(&f.disk,seed.data(),31,8<<20)==ENUMA_RAM_ARGUMENT);assert(!f.calls);}
    {Fixture f;assert(!enuma_ram_start(&f.disk,seed.data(),seed.size(),8<<20));f.fail=f.calls+1;
     Request r(4096);r.write=true;auto result=enuma_ram_io(&f.disk,1,(512ULL<<20)/512-8,8,4096,&r,Request::transfer);
     assert(result.status==ENUMA_RAM_MEMORY && !result.done && !r.calls);
     r.write=false;result=enuma_ram_io(&f.disk,0,(512ULL<<20)/512-8,8,4096,&r,Request::transfer);
     assert(!result.status);for(auto byte:r.data)assert(!byte);assert(!enuma_ram_stop(&f.disk));}
    // Exact resident budget: new zero page cannot be allocated; existing data is readable.
    {Fixture f;assert(!enuma_ram_start(&f.disk,seed.data(),seed.size(),8<<20));struct enuma_ram_info info;assert(!enuma_ram_info(&f.disk,&info));
     assert(!enuma_ram_stop(&f.disk));assert(!enuma_ram_start(&f.disk,seed.data(),seed.size(),info.resident_bytes));
     Request r(4096);r.write=true;auto result=enuma_ram_io(&f.disk,1,(512ULL<<20)/512-8,8,4096,&r,Request::transfer);
     assert(result.status==ENUMA_RAM_MEMORY && !result.done && !r.calls);assert(!enuma_ram_stop(&f.disk));}
    // stop cannot release pages while a descriptor copy is in progress.
    {Fixture f;assert(!enuma_ram_start(&f.disk,seed.data(),seed.size(),8<<20));Request r(512);r.park=true;
     enuma_ram_result result{};std::thread reader([&]{result=enuma_ram_io(&f.disk,0,0,1,512,&r,Request::transfer);});
     {std::unique_lock<std::mutex> lock(r.control);r.changed.wait(lock,[&]{return r.entered;});}
     unsigned before;{std::lock_guard<std::mutex> lock(f.observation);before=f.attempts;}
     std::thread stop([&]{assert(!enuma_ram_stop(&f.disk));});
     {std::unique_lock<std::mutex> lock(f.observation);f.attempted.wait(lock,[&]{return f.attempts>before;});}
     {std::lock_guard<std::mutex> lock(r.control);r.proceed=true;r.changed.notify_all();}
     reader.join();stop.join();assert(!result.status && result.done==512 && f.allocations.empty());}
    printf("PASS: complete 512MiB seed readback, %u import allocation failures, partial writes, budget exhaustion, stop/restart and concurrent stop\n",allocations);
}
