// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "SparseDisk.h"
#include <cstdio>
#include <vector>
int main(int argc,char **argv){
    if(argc!=2)return 2;
    FILE *f=fopen(argv[1],"rb");if(!f)return 2;
    if(fseek(f,0,SEEK_END)){fclose(f);return 2;}
    long n=ftell(f);if(n<0 || n>0x10000000){fclose(f);return 1;}rewind(f);
    std::vector<uint8_t> data(n);bool read=fread(data.data(),1,n,f)==static_cast<size_t>(n);fclose(f);
    uint64_t logical=0;
    if(!read || !ramPackedLayout(data.data(),data.size(),&logical))return 1;
    printf("%llu\n",static_cast<unsigned long long>(logical));return 0;
}
