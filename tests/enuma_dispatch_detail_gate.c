// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <setjmp.h>
#include <stdint.h>
#include <string.h>
static unsigned resets, delays;
static jmp_buf stopped;
void MicroSecondDelay(uint64_t us) { assert(us == ENUMA_DIAG_DELAY_US); ++delays; }
void ResetCold(void) { ++resets; }
void CpuDeadLoop(void) { longjmp(stopped, 1); }
#include DETAIL_HEADER
#include IMAGE_HEADER
int main(void) {
    EFI_GUID actual = { 0x1122334455667788ULL, 0x8877665544332211ULL };
    if (TEST_GUID_CASE == 1) actual.low ^= 1;
    if (TEST_GUID_CASE == 2) actual.high ^= 1;
    const EFI_GUID *guid = TEST_GUID_CASE == 3 ? NULL : &actual;
    unsigned guid_ok = !ENUMA_DIAG_GUID_ENABLED || TEST_GUID_CASE == 0;
    for (unsigned ordinal = 1; ordinal <= 4; ++ordinal) {
        unsigned before = resets;
        if (setjmp(stopped) == 0) EnumaDispatchCheckpoint(12);
        assert(resets - before == (ENUMA_DIAG_STAGE == 12 && ordinal == 3));
        const unsigned points[] = {14, 15, 20, 21, 22, 24, 25, 13};
        for (unsigned i = 0; i < 8; ++i) {
            unsigned point = points[i];
            EFI_STATUS status = point == 15 ? 0 : TEST_STATUS;
            const unsigned hook[] = {13, 14, 15, 13, 13, 14, 14, 20, 21, 22, 23, 24, 25, 26, 27};
            const int required_error[] = {-1, -1, -1, 1, 0, 1, 0, -1, -1, -1, -1, -1, -1, -1, -1};
            unsigned spec = ENUMA_DIAG_DETAIL_POINT - 13;
            unsigned status_ok = required_error[spec] < 0 || required_error[spec] == (int)EFI_ERROR(status);
            before = resets;
            if(point>=20) {
                EnumaStartingImage=(EFI_HANDLE)(uintptr_t)1;
                EnumaStartingFile=guid;
                // A nested StartImage or cleared context cannot impersonate it.
                EnumaImageEntryCheckpoint(point,(EFI_HANDLE)(uintptr_t)2,status);
                EnumaImageEntryCheckpoint(point,NULL,status);
                assert(resets==before);
                EFI_CONFIGURATION_TABLE entries[2] = { { {0,0}, NULL },
                    { {0x40f7080ab898d8dcULL,0x123456789abcdef0ULL}, NULL } };
                if(point==25) entries[1].VendorGuid.low ^= 1;
                EFI_SYSTEM_TABLE table = {2,entries};
                EnumaImageCanaryTableCheckpoint((EFI_HANDLE)(uintptr_t)2,&table);
                EnumaImageCanaryTableCheckpoint(EnumaStartingImage,NULL);
                EFI_SYSTEM_TABLE invalid = {4097,entries};
                EnumaImageCanaryTableCheckpoint(EnumaStartingImage,&invalid);
                invalid.NumberOfTableEntries=2;invalid.ConfigurationTable=NULL;
                EnumaImageCanaryTableCheckpoint(EnumaStartingImage,&invalid);
                assert(resets==before);
                if(setjmp(stopped)==0) {
                    if(point>=24) EnumaImageCanaryTableCheckpoint(EnumaStartingImage,&table);
                    else EnumaImageEntryCheckpoint(point,EnumaStartingImage,status);
                }
                EnumaStartingImage=NULL;
                EnumaImageEntryCheckpoint(point,NULL,status);
                EnumaStartingFile=NULL;
            } else if (setjmp(stopped) == 0) EnumaDispatchDetailCheckpoint(point, guid, status);
            assert(resets - before == (ENUMA_DIAG_STAGE == 13 && (ENUMA_DIAG_GUID_ONLY || ordinal == 3) &&
                   point == hook[spec] && status_ok && guid_ok && (point<20 || guid!=NULL)));
        }
    }
    assert(delays == resets);
    return 0;
}
