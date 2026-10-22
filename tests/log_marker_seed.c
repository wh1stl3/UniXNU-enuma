#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include "../diagnostics/enuma_marker_seed.h"
int main(void) {
    unsigned char *p=malloc(18);assert(p);memset(p,0x5a,18);
    assert(enuma_seed_marker(p+1,0)==0);
    for(int i=0;i<18;i++)assert(p[i]==0x5a);
    assert(enuma_seed_marker(NULL,1)==0);
    assert(enuma_seed_marker(p+1,1)==1);
    assert(p[0]==0x5a && p[17]==0x5a && !memcmp(p+1,"ENUMA-R002-SEED1",16));
    assert(enuma_seed_marker(p+1,1)==1);
    free(p);return 0;
}
