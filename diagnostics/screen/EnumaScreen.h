// SPDX-License-Identifier: BSD-2-Clause-Patent
#ifndef ENUMA_SCREEN_H
#define ENUMA_SCREEN_H
#include <Uefi.h>
#include <Protocol/GraphicsOutput.h>

#define ENUMA_SCREEN_MAX_COLUMNS 40
#define ENUMA_SCREEN_MAX_ROWS 12
#define ENUMA_SCREEN_CELL_WIDTH 12
#define ENUMA_SCREEN_CELL_HEIGHT 28
#define ENUMA_SCREEN_SCRATCH_PIXELS (ENUMA_SCREEN_MAX_COLUMNS * ENUMA_SCREEN_CELL_WIDTH * ENUMA_SCREEN_CELL_HEIGHT)

typedef struct {
  UINT32 X, Y, Width, Height;
} ENUMA_SCREEN_REGION;

typedef struct {
  EFI_GRAPHICS_OUTPUT_PROTOCOL *Gop;
  EFI_GRAPHICS_OUTPUT_PROTOCOL_BLT Blt;
  EFI_GRAPHICS_OUTPUT_PROTOCOL_MODE *Mode;
  EFI_GRAPHICS_OUTPUT_MODE_INFORMATION *Info;
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL *Scratch;
  ENUMA_SCREEN_REGION Region;
  UINT32 Columns, Rows, ModeNumber, ScreenWidth, ScreenHeight;
  EFI_GRAPHICS_PIXEL_FORMAT PixelFormat;
  BOOLEAN WriteEnabled, Busy;
  EFI_STATUS Failure;
} ENUMA_SCREEN;

// Caller owns Scratch and must keep it disjoint from the context and GOP.
// WriteEnabled defaults FALSE in the future caller. TRUE requires actual
// provider/scanout/region evidence; metadata validity is not that evidence.
// Single context at application TPL only: Busy prevents callback reentry,
// not concurrent CPU access. Never call during/after ExitBootServices.
EFI_STATUS EnumaScreenInit (
  ENUMA_SCREEN *Screen, EFI_GRAPHICS_OUTPUT_PROTOCOL *Gop,
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL *Scratch, UINTN ScratchPixels,
  ENUMA_SCREEN_REGION Region, BOOLEAN WriteEnabled);

// Explicit byte count: no unbounded strlen, implicit wrap, scroll or clear.
// One BltBufferToVideo call per line. Any Blt error/mode change latches shut.
EFI_STATUS EnumaScreenLine (ENUMA_SCREEN *Screen, UINTN Row, CONST CHAR8 *Text, UINTN Length);
EFI_STATUS EnumaScreenHex (ENUMA_SCREEN *Screen, UINTN Row, CONST CHAR8 *Label, UINTN Length, UINT64 Value);

// Values must come from the caller's observations; this helper collects no
// MMIO, memory maps or firmware state and cannot certify their provenance.
typedef struct {
  CONST CHAR8 *Build;
  UINTN BuildLength;
  UINT64 Stage, Status, Width, Height, Stride, Format, Base, Bytes, MapStatus, BestFree;
} ENUMA_SCREEN_SNAPSHOT;
EFI_STATUS EnumaScreenPage (ENUMA_SCREEN *Screen, CONST ENUMA_SCREEN_SNAPSHOT *Snapshot);
#endif
