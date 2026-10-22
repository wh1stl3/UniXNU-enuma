// SPDX-License-Identifier: GPL-2.0
/* R-002: ABI probe by default; explicit separate build reads 16 marker bytes.
 * No MMIO, writes, arbitrary addresses, force loading or writable parameters.
 * Host must first verify the active FDT reserve tuple and all eight pages.
 */
#include <linux/module.h>
#include <linux/mm.h>
#include <asm/memory.h>

static int __init enuma_reader_init(void)
{
#ifdef ENUMA_READ_MARKER
    unsigned long pfn;
    unsigned char marker[16];
    const volatile unsigned char *source;
    for(pfn=0x9fff7000UL>>PAGE_SHIFT;pfn<0x9ffff000UL>>PAGE_SHIFT;pfn++)
        if(!PageReserved(pfn_to_page(pfn))) return -EPERM;
    source=__va(0x9fff7000UL);
    for(pfn=0;pfn<sizeof(marker);pfn++) marker[pfn]=READ_ONCE(source[pfn]);
    pr_info("ENUMA_R002 MARKER=%*phN\n",(int)sizeof(marker),marker);
#else
    pr_info("ENUMA_R002 ABI_OK no_physical_access\n");
#endif
    return 0;
}
static void __exit enuma_reader_exit(void) { }
module_init(enuma_reader_init);
module_exit(enuma_reader_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Enuma R-002 bounded read-only marker diagnostic");
