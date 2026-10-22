/* R-002: exactly 16 bytes at the approved buffer start, only after reserving
 * the FDT range. No allocator, variable address, log append or extra metadata.
 * Destination is explicit to let host sanitizers check the actual function.
 */
#ifndef ENUMA_MARKER_SEED_H
#define ENUMA_MARKER_SEED_H
static int enuma_seed_marker(volatile unsigned char *destination, int reserved) {
    static const unsigned char marker[16]="ENUMA-R002-SEED1";
    if(!reserved || !destination) return 0;
    for(unsigned int i=0;i<sizeof(marker);i++) destination[i]=marker[i];
    return 1;
}
#endif
