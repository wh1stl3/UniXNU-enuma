const volatile unsigned char *enuma_test_va(unsigned long);
#define __va(address) enuma_test_va(address)
