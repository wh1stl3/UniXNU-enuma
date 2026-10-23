// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <assert.h>
#define IN
#define OUT
#define OPTIONAL
#define FALSE 0
#define STATIC static
#define CONST const
#define EFIAPI
#define VOID void
#define DEBUG(x) do { } while (0)
#define ASSERT_EFI_ERROR(x) assert(!EFI_ERROR(x))
#define ASSERT(x) assert(x)
#define MAX_UINT64 UINT64_MAX
#define MAX_UINTN UINTPTR_MAX
#define EFI_ERROR(x) (((uint64_t)(x) >> 63) != 0)
#define ERR(x) (UINT64_C(0x8000000000000000) | (x))
#define EFI_SUCCESS 0
#define EFI_INVALID_PARAMETER ERR(2)
#define EFI_UNSUPPORTED ERR(3)
#define EFI_BAD_BUFFER_SIZE ERR(4)
#define EFI_BUFFER_TOO_SMALL ERR(5)
#define EFI_NOT_STARTED ERR(19)
#define EFI_ALREADY_STARTED ERR(20)
#define EFI_DEVICE_ERROR ERR(7)
#define EFI_OUT_OF_RESOURCES ERR(9)
#define EFI_NOT_FOUND ERR(14)
#define EFI_COMPROMISED_DATA ERR(33)
#define RETURN_INVALID_PARAMETER EFI_INVALID_PARAMETER
#define RETURN_UNSUPPORTED EFI_UNSUPPORTED
#define RETURN_BUFFER_TOO_SMALL EFI_BUFFER_TOO_SMALL
#define RETURN_SUCCESS EFI_SUCCESS
#define EfiBootServicesData 4
#define TPL_NOTIFY 16
#define PixelBlueGreenRedReserved8BitPerColor 1
#define PixelRedGreenBlueReserved8BitPerColor 0
#define PixelBitMask 2
#define PixelBltOnly 3
typedef uint64_t EFI_STATUS;
typedef uint64_t RETURN_STATUS;
typedef uint64_t EFI_PHYSICAL_ADDRESS;
typedef uintptr_t UINTN;
typedef uint64_t UINT64;
typedef uint32_t UINT32;
typedef uint8_t UINT8;
typedef int8_t INT8;
typedef unsigned EFI_GRAPHICS_PIXEL_FORMAT;
typedef unsigned EFI_TPL;
typedef void *EFI_HANDLE;
typedef struct {int unused;} EFI_SYSTEM_TABLE;
typedef struct {UINT32 RedMask,GreenMask,BlueMask,ReservedMask;} MASK;
typedef MASK EFI_PIXEL_BITMASK;
typedef struct {UINT32 Version,HorizontalResolution,VerticalResolution,PixelFormat;MASK PixelInformation;UINT32 PixelsPerScanLine;} EFI_GRAPHICS_OUTPUT_MODE_INFORMATION;
typedef struct {UINT32 MaxMode,Mode;EFI_GRAPHICS_OUTPUT_MODE_INFORMATION *Info;UINTN SizeOfInfo;EFI_PHYSICAL_ADDRESS FrameBufferBase;UINTN FrameBufferSize;} EFI_GRAPHICS_OUTPUT_PROTOCOL_MODE;
typedef struct {unsigned char data[4];} EFI_GRAPHICS_OUTPUT_BLT_PIXEL;
typedef unsigned EFI_GRAPHICS_OUTPUT_BLT_OPERATION;
typedef struct GOP EFI_GRAPHICS_OUTPUT_PROTOCOL;
struct GOP {
 EFI_STATUS (*QueryMode)(EFI_GRAPHICS_OUTPUT_PROTOCOL*,UINT32,UINTN*,EFI_GRAPHICS_OUTPUT_MODE_INFORMATION**);
 EFI_STATUS (*SetMode)(EFI_GRAPHICS_OUTPUT_PROTOCOL*,UINT32);
 EFI_STATUS (*Blt)(EFI_GRAPHICS_OUTPUT_PROTOCOL*,EFI_GRAPHICS_OUTPUT_BLT_PIXEL*,EFI_GRAPHICS_OUTPUT_BLT_OPERATION,UINTN,UINTN,UINTN,UINTN,UINTN,UINTN,UINTN);
 EFI_GRAPHICS_OUTPUT_PROTOCOL_MODE *Mode;
};
#ifdef SIMPLEFB_REAL_CONFIGURE
typedef struct FRAME_BUFFER_CONFIGURE FRAME_BUFFER_CONFIGURE;
static inline int HighBitSet32(UINT32 value) { return value ? 31-__builtin_clz(value) : -1; }
#else
typedef struct {uint64_t opaque;} FRAME_BUFFER_CONFIGURE;
#endif
typedef struct {EFI_PHYSICAL_ADDRESS Address;UINT64 Length;} EFI_MEMORY_REGION_DESCRIPTOR;
typedef struct {EFI_STATUS (*AllocatePool)(unsigned,UINTN,VOID**);EFI_STATUS (*FreePool)(VOID*);EFI_TPL (*RaiseTPL)(EFI_TPL);VOID (*RestoreTPL)(EFI_TPL);EFI_STATUS (*InstallMultipleProtocolInterfaces)(EFI_HANDLE*,...);} BOOT_SERVICES;
extern BOOT_SERVICES *gBS;
extern int DisplayDevicePath,gEfiDevicePathProtocolGuid,gEfiGraphicsOutputProtocolGuid;
enum {PcdFrameBufferWidth,PcdFrameBufferHeight,PcdFrameBufferColorDepth};
extern UINT32 FixturePcd[3];
#define FixedPcdGet32(x) FixturePcd[x]
#define ZeroMem(p,n) memset((p),0,(n))
#define CopyMem(d,s,n) memcpy((d),(s),(n))
VOID *AllocatePool(UINTN);
VOID FreePool(VOID*);
EFI_STATUS LocateMemoryRegionByName(const char*,EFI_MEMORY_REGION_DESCRIPTOR*);
EFI_STATUS FrameBufferBltConfigure(VOID*,EFI_GRAPHICS_OUTPUT_MODE_INFORMATION*,FRAME_BUFFER_CONFIGURE*,UINTN*);
EFI_STATUS FrameBufferBlt(FRAME_BUFFER_CONFIGURE*,EFI_GRAPHICS_OUTPUT_BLT_PIXEL*,EFI_GRAPHICS_OUTPUT_BLT_OPERATION,UINTN,UINTN,UINTN,UINTN,UINTN,UINTN,UINTN);
