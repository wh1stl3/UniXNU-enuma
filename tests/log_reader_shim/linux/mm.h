#ifndef ENUMA_READER_TEST_MM_H
#define ENUMA_READER_TEST_MM_H
#define PAGE_SHIFT 12
struct page { int reserved; };
struct page *enuma_test_page(unsigned long);
int enuma_test_reserved(struct page *);
#define pfn_to_page(pfn) enuma_test_page(pfn)
#define PageReserved(page) enuma_test_reserved(page)
#endif
