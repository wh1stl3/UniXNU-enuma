// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "EnumaRootRead.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>
struct Fixture {
    std::vector<unsigned char> disk,output,bounce;
    unsigned reads=0,checks=0,copies=0,failRead=0,failCheck=0;
    uint64_t shortCopy=UINT64_MAX;
    bool held=false;
    Fixture():disk(80*4096),output(70*4096,0xa5),bounce(131072) {
        for(size_t i=0;i<disk.size();++i)disk[i]=static_cast<unsigned char>(i*13+i/4096);
    }
    static Fixture &self(void *p){return *static_cast<Fixture *>(p);}
    static void lock(void *p){auto &f=self(p);assert(!f.held);f.held=true;}
    static void unlock(void *p){auto &f=self(p);assert(f.held);f.held=false;}
    static uint32_t read(void *p,const enuma_ufs_read *r,void *out){
        auto &f=self(p);assert(f.held);++f.reads;
        assert(r->lun==2 && r->cdb[0]==0x28 && r->bytes<=131072);
        if(f.reads==f.failRead)return ENUMA_ROOT_IO;
        uint32_t lba=0;for(unsigned i=2;i<6;++i)lba=lba*256+r->cdb[i];
        assert(lba>=3 && uint64_t(lba)*4096+r->bytes<=73*4096);
        memcpy(out,f.disk.data()+lba*4096,r->bytes);return 0;
    }
    static uint32_t verify(void *p,uint64_t block,const void *data,uint64_t bytes){
        auto &f=self(p);assert(f.held);++f.checks;
        if(f.checks==f.failCheck)return ENUMA_ROOT_INTEGRITY;
        assert(bytes==4096 && !memcmp(data,f.disk.data()+(block+3)*4096,bytes));return 0;
    }
    static uint64_t copy(void *p,uint64_t at,const void *data,uint64_t bytes){
        auto &f=self(p);assert(f.held);++f.copies;
        uint64_t n=bytes<f.shortCopy?bytes:f.shortCopy;
        assert(at+n<=f.output.size());memcpy(f.output.data()+at,data,n);return n;
    }
    enuma_root_result run(uint64_t sector=0,uint64_t count=513){
        enuma_ufs_geometry g{80,4096,2};enuma_root_ops o{this,lock,unlock,read,verify,copy};
        return enuma_root_read(&g,3,70,sector,count,bounce.data(),bounce.size(),&o);
    }
};
int main(){
    for(unsigned skip=0;skip<8;++skip){Fixture f;auto r=f.run(skip);assert(!r.status && r.done==513*512 && !f.held);
        assert(!memcmp(f.output.data(),f.disk.data()+3*4096+skip*512,r.done));}
    for(unsigned i=1;i<=3;++i){Fixture f;f.failRead=i;auto r=f.run();assert(r.status==ENUMA_ROOT_IO && r.done==(i-1)*131072 && !f.held && f.reads==i);}
    for(unsigned i=1;i<=65;++i){Fixture f;f.failCheck=i;auto r=f.run();assert(r.status==ENUMA_ROOT_INTEGRITY && r.done==((i-1)/32)*131072 && !f.held && f.output[r.done]==0xa5);}
    {Fixture f;f.shortCopy=511;auto r=f.run();assert(r.status==ENUMA_ROOT_IO && r.done==511 && !f.held);}
    {Fixture f;auto r=f.run(559,1);assert(!r.status && r.done==512);}
    for(auto count:{uint64_t(0),UINT64_MAX}){Fixture f;auto r=f.run(0,count);assert(r.status==ENUMA_ROOT_ARGUMENT && !r.done && !f.reads);}
    {Fixture f;auto r=f.run(560,1);assert(r.status==ENUMA_ROOT_ARGUMENT && !f.reads);}
    {Fixture f;enuma_ufs_geometry g{72,4096,2};enuma_root_ops o{&f,Fixture::lock,Fixture::unlock,Fixture::read,Fixture::verify,Fixture::copy};
     auto r=enuma_root_read(&g,3,70,0,1,f.bounce.data(),131072,&o);assert(r.status==ENUMA_ROOT_ARGUMENT);
     g.blocks=80;o.verify=nullptr;r=enuma_root_read(&g,3,70,0,1,f.bounce.data(),131072,&o);assert(r.status==ENUMA_ROOT_ARGUMENT && !f.reads);}
    puts("PASS: 8 alignments, 3 transport failures, 65 integrity failures, short copy, geometry and missing policy");
}
