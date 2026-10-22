// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "EnumaNvt.h"
// Exact manufacturer checksum function is extracted to out/ with host logging
// adapters. It is an independent oracle for the packet envelope only.
#define NVT_ERR(...) ((void)0)
#define NVT_LOG(...) ((void)0)
#include NVT_CHECKSUM_SOURCE
static void checksum(uint8_t *p) {
    unsigned sum = 0;
    for (unsigned i = 1; i < 65; ++i) sum += p[i];
    p[65] = (uint8_t)(0u - sum);
    assert(nvt_ts_point_data_checksum(p, 65) == 0);
}
static void contact(uint8_t *p,unsigned slot,unsigned id,unsigned state,unsigned x,unsigned y) {
    unsigned at=1+6*slot;
    p[at]=(uint8_t)(id*8+state); p[at+1]=(uint8_t)(x>>4); p[at+2]=(uint8_t)(y>>4);
    p[at+3]=(uint8_t)((x&15)*16+(y&15)); p[at+4]=0; p[at+5]=0;
}
int main(void) {
    uint8_t p[80]={0},wire[81]={0},canonical[80]={0};
    struct enuma_nvt_frame f={0},sentinel;
    memset(&sentinel,0xa5,sizeof(sentinel));
    for (unsigned id=1;id<=10;++id) contact(p,id-1,11-id,1+(id&1),160*id,256*id);
    p[63]=255; p[64]=1; checksum(p);
    assert(enuma_nvt_decode(p,80,1600,2560,&f)==0 && f.count==10);
    assert(f.contacts[0].id==10 && f.contacts[9].id==1);
    assert(f.contacts[9].x==1600 && f.contacts[9].y==2560);
    assert(f.contacts[0].pressure==1000 && f.contacts[1].pressure==256 && f.contacts[2].pressure==1);
    assert(f.contacts[0].width==1);
    for (unsigned i=0;i<80;++i) { // Every truncation except the complete touch prefix.
        if(i==66)continue;
        f=sentinel; assert(enuma_nvt_decode(p,i,1600,2560,&f)==ENUMA_NVT_ARGUMENT);
        assert(memcmp(&f,&sentinel,sizeof(f))==0);
    }
    for (unsigned at=1;at<66;++at) {
        p[at]^=1; f=sentinel;
        assert(nvt_ts_point_data_checksum(p,65)==-1);
        assert(enuma_nvt_decode(p,66,1600,2560,&f)==ENUMA_NVT_CHECKSUM);
        assert(memcmp(&f,&sentinel,sizeof(f))==0); p[at]^=1;
    }
    memcpy(wire+2,p+1,79);
    assert(enuma_nvt_unwrap(wire,81,canonical,80)==0 && memcmp(p,canonical,80)==0);
    assert(enuma_nvt_unwrap(wire,81,canonical,79)==ENUMA_NVT_ARGUMENT);
    assert(enuma_nvt_unwrap(wire,80,canonical,80)==ENUMA_NVT_ARGUMENT);
    assert(enuma_nvt_unwrap(wire,81,wire,80)==0 && memcmp(p,wire,80)==0);
    contact(p,1,10,1,1,1); checksum(p); f=sentinel;
    assert(enuma_nvt_decode(p,66,1600,2560,&f)==ENUMA_NVT_MALFORMED);
    assert(memcmp(&f,&sentinel,sizeof(f))==0);
    memset(p,0,sizeof(p)); contact(p,0,0,1,1,1); checksum(p);
    assert(enuma_nvt_decode(p,66,1600,2560,&f)==ENUMA_NVT_MALFORMED);
    contact(p,0,11,2,1,1); checksum(p);
    assert(enuma_nvt_decode(p,66,1600,2560,&f)==ENUMA_NVT_MALFORMED);
    contact(p,0,1,1,1601,1); checksum(p);
    assert(enuma_nvt_decode(p,66,1600,2560,&f)==ENUMA_NVT_MALFORMED);
    contact(p,0,1,1,1,2561); checksum(p);
    assert(enuma_nvt_decode(p,66,1600,2560,&f)==ENUMA_NVT_MALFORMED);
    memset(p,0,sizeof(p)); checksum(p);
    assert(enuma_nvt_decode(p,66,1600,2560,&f)==0 && f.count==0);
    for(unsigned kind=0;kind<2;++kind) {
        for(unsigned i=1;i<=6;++i)p[i]=kind?(i&1?0xfd:0xfe):0x77;
        f=sentinel;
        assert(enuma_nvt_decode(p,66,1600,2560,&f)==(kind?ENUMA_NVT_WATCHDOG:ENUMA_NVT_ESD));
        assert(memcmp(&f,&sentinel,sizeof(f))==0);
    }
    uint16_t v=7;
    assert(enuma_nvt_normalize(0,1600,&v)==0 && v==0);
    assert(enuma_nvt_normalize(1600,1600,&v)==0 && v==32767);
    assert(enuma_nvt_normalize(2560,2560,&v)==0 && v==32767);
    assert(enuma_nvt_normalize(2561,2560,&v)==ENUMA_NVT_ARGUMENT && v==32767);
    assert(enuma_nvt_normalize(0,0,&v)==ENUMA_NVT_ARGUMENT);
    assert(enuma_nvt_normalize(0,4096,&v)==ENUMA_NVT_ARGUMENT);
    puts("PASS: NT36523 ten contacts, checksum oracle/65 corruptions, 79 truncations, wire dummy, ranges, recovery, inclusive HID endpoints");
    return 0;
}
