// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <strings.h>
#include <assert.h>
typedef char CHAR8;
typedef uint8_t UINT8;
typedef uint32_t UINT32;
typedef uint64_t UINT64;
typedef size_t UINTN;
typedef int EFI_STATUS;
typedef void VOID;
typedef struct { int unused; } EFI_MEMORY_REGION_DESCRIPTOR;
#define IN
#define OUT
#define EFIAPI
#define STATIC static
#define EFI_SUCCESS 0
#define EFI_INVALID_PARAMETER 1
#define EFI_NOT_FOUND 2
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))
#define AsciiStriCmp strcasecmp
#include "ConfigurationMapLib.h"
#include "EFIUefiConfig.h"
#include "ConfigMap.inc"
#include "ConfigHelper.inc"
int main(void) {
  _Static_assert(offsetof(EFI_UEFI_CONFIG_LIBRARY, GetCfgInfoVal) == 0x18, "real DisplayDxe slot");
  _Static_assert(sizeof(EFI_CONFIGURATION_ENTRY_DESCRIPTOR) == 72, "actual configuration layout");
  EFI_UEFI_CONFIG_LIBRARY lib = {0x10002, NULL, NULL, LocateConfigurationEntry32, LocateConfigurationEntry64, NULL};
  UINT32 value = 99;
  assert(lib.GetCfgInfoVal("EnableDisplayThread", &value) == EFI_SUCCESS && value == 0);
  value = 99; assert(lib.GetCfgInfoVal("enabledisplaythread", &value) == EFI_SUCCESS && value == 0);
  assert(lib.GetCfgInfoVal(NULL, &value) == EFI_INVALID_PARAMETER);
  assert(lib.GetCfgInfoVal("EnableDisplayThread", NULL) == EFI_INVALID_PARAMETER);
  value = 99; assert(lib.GetCfgInfoVal("NoSuchEntry", &value) == EFI_NOT_FOUND && value == 99);
  assert(lib.GetCfgInfoVal("EnableMultiThreading", &value) == EFI_SUCCESS && value == 1);
  UINT64 wide = 0;
  assert(lib.GetCfgInfoVal64("NumCpus", &wide) == EFI_SUCCESS && wide == 8);
  puts("PASS: production config map/helper through real ABI slot0x18 returns display-thread=0; missing/null rejected; other thread/CPU policy retained");
  return 0;
}
