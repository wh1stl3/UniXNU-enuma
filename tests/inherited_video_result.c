// Actual production diagnostic selector, including invalid states and old mode.
#include <assert.h>
#include <stdio.h>
#include "VideoResult.h"
int main(void) {
  unsigned s,q,n=0,req=ENUMA_REQUIRE_ADDRESS|ENUMA_REQUIRE_TOPOLOGY;
  for(s=0;s<=EnumaInheritedTopology;s++) {
    unsigned a=EnumaVideoResult(s,req,1),b=EnumaVideoResult(s,req,2);
    assert(a==(s==EnumaInheritedTopology?1u:5u));
    assert(b==(s==EnumaInheritedTopology?5u:1u));
    assert(a+b==6); assert(EnumaVideoResult(s,req,0)==(s?5u:1u)); n+=3;
  }
  for(q=0;q<3;q++) {
    assert(EnumaVideoResult(0,0,q)==0);
    assert(EnumaVideoResult(0,ENUMA_REQUIRE_ALL,q)==0);
    assert(EnumaVideoResult(14,req,q)==0);
    assert(EnumaVideoResult(~0u,req,q)==0); n+=4;
  }
  assert(EnumaVideoResult(13,req,3)==0); n++;
  printf("PASS: %u diagnostic result cases; complementary status predicates, invalid-state rejection, old-mode regression\n",n);
  return 0;
}
