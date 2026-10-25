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
  for(unsigned target=1;target<=4;target++) {
    for(unsigned reason=1;reason<=13;reason++) {
      unsigned refresh=reason==4||reason==5||reason==6||reason==7||reason==9||reason==10||reason==11||reason==13;
      unsigned status=reason==12?0:refresh?10:reason==3?1:reason==2?7:reason==8?13:11;
      unsigned match=target==1?reason==5:target==2?(reason==6||reason==9||reason==10||reason==11||reason==13):target==3?reason==4:refresh;
      unsigned a=EnumaVideoReasonResult(status,req,reason,target,1),b=EnumaVideoReasonResult(status,req,reason,target,2);
      assert(a==(match?1u:5u)&&b==(match?5u:1u));n+=2;
    }
  }
  assert(EnumaVideoReasonResult(0,req,5,1,1)==0);
  assert(EnumaVideoReasonResult(13,req,5,1,1)==0);
  assert(EnumaVideoReasonResult(10,req,0,1,1)==0);
  assert(EnumaVideoReasonResult(10,req,5,0,1)==0);
  assert(EnumaVideoReasonResult(10,req,5,1,0)==0);n+=5;
  printf("PASS: %u diagnostic result cases; complementary status predicates, invalid-state rejection, old-mode regression\n",n);
  return 0;
}
