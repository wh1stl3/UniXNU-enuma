#include <stdio.h>
#include <stdlib.h>
int enuma_reserve_log(unsigned char *, size_t);
int main(int argc, char **argv) {
    if(argc!=3) return 2;
    FILE *f=fopen(argv[1],"rb"); if(!f) return 2;
    unsigned char *b=malloc(0x200001); if(!b) return 2;
    size_t n=fread(b,1,0x200001,f); fclose(f);
    if(n>0x200000) {free(b); return 2;}
    int result=enuma_reserve_log(b,n);
    f=fopen(argv[2],"wb"); if(!f) {free(b); return 2;}
    if(fwrite(b,1,n,f)!=n) return 2;
    fclose(f); free(b); printf("%d\n",result); return 0;
}
