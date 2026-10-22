/* Exercise actual marker-reader source, not a duplicate algorithm.
 * Mock only kernel APIs; use an exact 16-byte ASan allocation as source.
 */
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#define ENUMA_READ_MARKER
#include "../diagnostics/enuma_log_reader.c"

static struct page pages[8];
static unsigned char *source;
static unsigned char captured[16];
static int checked, mapped, printed;

struct page *enuma_test_page(unsigned long pfn) {
    assert(pfn>=(0x9fff7000UL>>12) && pfn<(0x9ffff000UL>>12));
    return &pages[pfn-(0x9fff7000UL>>12)];
}
int enuma_test_reserved(struct page *page) {
    assert(page==&pages[checked]); checked++;
    return page->reserved;
}
const volatile unsigned char *enuma_test_va(unsigned long address) {
    assert(address==0x9fff7000UL && checked==8);
    mapped++;
    return source;
}
void enuma_test_print(const char *format, int bytes, const unsigned char *data) {
    assert(!strcmp(format,"ENUMA_R002 MARKER=%*phN\n"));
    assert(bytes==16 && mapped==1);
    memcpy(captured,data,16); printed++;
}
int main(void) {
    source=malloc(16); assert(source);
    for(int missing=0;missing<8;missing++) {
        for(int i=0;i<8;i++) pages[i].reserved=i!=missing;
        checked=mapped=printed=0;
        memset(source,0xa5,16);
        assert(enuma_reader_init()==-EPERM);
        assert(checked==missing+1 && !mapped && !printed);
        for(int i=0;i<16;i++) assert(source[i]==0xa5);
    }
    for(int i=0;i<8;i++) pages[i].reserved=1;
    for(int i=0;i<16;i++) source[i]=(unsigned char)(i*13+7);
    checked=mapped=printed=0;
    assert(enuma_reader_init()==0 && checked==8 && mapped==1 && printed==1);
    assert(!memcmp(source,captured,16));
    for(int i=0;i<16;i++) assert(source[i]==(unsigned char)(i*13+7));
    enuma_reader_exit(); free(source);
    return 0;
}
