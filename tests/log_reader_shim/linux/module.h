/* Host-only API shim. Actual module compilation uses exact device headers. */
#ifndef ENUMA_READER_TEST_MODULE_H
#define ENUMA_READER_TEST_MODULE_H
#include <errno.h>
#define __init
#define __exit
#define module_init(f)
#define module_exit(f)
#define MODULE_LICENSE(s)
#define MODULE_DESCRIPTION(s)
#define READ_ONCE(x) (x)
void enuma_test_print(const char *, int, const unsigned char *);
#define pr_info(...) enuma_test_print(__VA_ARGS__)
#endif
