// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "EnumaScreen.h"
// Hash-locked BSD-licensed AOSP font from DarwinBoot, staged under own out/.
#include "DiagFont.h"
STATIC CONST UINT64 mFont[] = GLYPH_FONT;

EFI_STATUS EnumaScreenInit (
  ENUMA_SCREEN *Screen, EFI_GRAPHICS_OUTPUT_PROTOCOL *Gop,
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL *Scratch, UINTN ScratchPixels,
  ENUMA_SCREEN_REGION Region, BOOLEAN WriteEnabled)
{
  EFI_GRAPHICS_OUTPUT_MODE_INFORMATION *Info;
  UINT32 Columns, Rows;
  if (Screen == NULL) { return EFI_INVALID_PARAMETER; }
  *Screen = (ENUMA_SCREEN) {0};
  Screen->Failure = EFI_NOT_READY;
  if (Gop == NULL || Scratch == NULL || Gop->Blt == NULL) { return EFI_INVALID_PARAMETER; }
  if (Gop->Mode == NULL || Gop->Mode->Info == NULL) { return EFI_NOT_STARTED; }
  Info = Gop->Mode->Info;
  if (Gop->Mode->SizeOfInfo < sizeof (*Info) || Gop->Mode->MaxMode == 0 ||
      Gop->Mode->Mode >= Gop->Mode->MaxMode || (UINT32) Info->PixelFormat >= (UINT32) PixelFormatMax) {
    return EFI_COMPROMISED_DATA;
  }
  if (Region.X > Info->HorizontalResolution || Region.Y > Info->VerticalResolution ||
      Region.Width > Info->HorizontalResolution - Region.X ||
      Region.Height > Info->VerticalResolution - Region.Y) { return EFI_BAD_BUFFER_SIZE; }
  Columns = Region.Width / ENUMA_SCREEN_CELL_WIDTH;
  Rows = Region.Height / ENUMA_SCREEN_CELL_HEIGHT;
  if (Columns == 0 || Rows == 0 || Columns > ENUMA_SCREEN_MAX_COLUMNS || Rows > ENUMA_SCREEN_MAX_ROWS) {
    return EFI_BAD_BUFFER_SIZE;
  }
  if (ScratchPixels < (UINTN) Columns * ENUMA_SCREEN_CELL_WIDTH * ENUMA_SCREEN_CELL_HEIGHT) {
    return EFI_BUFFER_TOO_SMALL;
  }
  Screen->Gop = Gop; Screen->Blt = Gop->Blt; Screen->Mode = Gop->Mode; Screen->Info = Info;
  Screen->Scratch = Scratch; Screen->Region = Region;
  Screen->Columns = Columns; Screen->Rows = Rows;
  Screen->ModeNumber = Gop->Mode->Mode;
  Screen->ScreenWidth = Info->HorizontalResolution; Screen->ScreenHeight = Info->VerticalResolution;
  Screen->PixelFormat = Info->PixelFormat;
  Screen->WriteEnabled = WriteEnabled; Screen->Failure = EFI_SUCCESS;
  return EFI_SUCCESS;
}

EFI_STATUS EnumaScreenLine (ENUMA_SCREEN *Screen, UINTN Row, CONST CHAR8 *Text, UINTN Length)
{
  UINTN Width, Count, Index, X, Y, Dx, Dy, Cell, Position;
  UINT64 Glyph, Bits;
  UINT8 Ch;
  EFI_STATUS Status;
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL Black = {0,0,0,0}, White = {255,255,255,0};
  if (Screen == NULL) { return EFI_INVALID_PARAMETER; }
  if (EFI_ERROR (Screen->Failure)) { return Screen->Failure; }
  if (Screen->Gop == NULL || Screen->Scratch == NULL) { return EFI_NOT_READY; }
  if (!Screen->WriteEnabled) { return EFI_ACCESS_DENIED; }
  if (Screen->Busy) { return EFI_ALREADY_STARTED; }
  if (Text == NULL && Length != 0) { return EFI_INVALID_PARAMETER; }
  if (Row >= Screen->Rows || Length > Screen->Columns) { return EFI_BAD_BUFFER_SIZE; }
  if (Screen->Gop->Blt != Screen->Blt || Screen->Gop->Mode != Screen->Mode ||
      Screen->Mode->Info != Screen->Info || Screen->Mode->Mode != Screen->ModeNumber ||
      Screen->Mode->MaxMode == 0 || Screen->Mode->Mode >= Screen->Mode->MaxMode ||
      Screen->Mode->SizeOfInfo < sizeof (*Screen->Info) ||
      Screen->Info->HorizontalResolution != Screen->ScreenWidth ||
      Screen->Info->VerticalResolution != Screen->ScreenHeight ||
      Screen->Info->PixelFormat != Screen->PixelFormat) {
    Screen->Failure = EFI_MEDIA_CHANGED;
    return Screen->Failure;
  }
  Screen->Busy = TRUE;
  Width = (UINTN) Screen->Columns * ENUMA_SCREEN_CELL_WIDTH;
  Count = Width * ENUMA_SCREEN_CELL_HEIGHT;
  for (Index = 0; Index < Count; Index++) { Screen->Scratch[Index] = Black; }
  for (Cell = 0; Cell < Length; Cell++) {
    Ch = (UINT8) Text[Cell];
    if (Ch < 32 || Ch > 126) { Ch = '?'; }
    Glyph = mFont[Ch - 32];
    // Preserve DarwinBoot's two packed 6-row halves, not a flat 80-bit shift.
    for (Y = 0; Y < 12; Y++) {
      Bits = Y < 6 ? ((Glyph >> 32) >> (Y * 5)) : ((Glyph & 0xffffffffULL) >> ((Y - 6) * 5));
      for (X = 0; X < 5; X++) {
        if ((Bits >> X) & 1) {
          for (Dy = 0; Dy < 2; Dy++) {
            for (Dx = 0; Dx < 2; Dx++) {
              Position = (Y * 2 + Dy) * Width + Cell * ENUMA_SCREEN_CELL_WIDTH + X * 2 + Dx;
              Screen->Scratch[Position] = White;
            }
          }
        }
      }
    }
  }
  Status = Screen->Gop->Blt (Screen->Gop, Screen->Scratch, EfiBltBufferToVideo, 0, 0,
    Screen->Region.X, Screen->Region.Y + Row * ENUMA_SCREEN_CELL_HEIGHT,
    Width, ENUMA_SCREEN_CELL_HEIGHT, Width * sizeof (*Screen->Scratch));
  Screen->Busy = FALSE;
  if (EFI_ERROR (Status)) { Screen->Failure = Status; }
  return Status;
}

EFI_STATUS EnumaScreenHex (ENUMA_SCREEN *Screen, UINTN Row, CONST CHAR8 *Label, UINTN Length, UINT64 Value)
{
  CHAR8 Text[ENUMA_SCREEN_MAX_COLUMNS];
  CONST CHAR8 Hex[] = "0123456789ABCDEF";
  UINTN Index;
  if (Screen == NULL || (Label == NULL && Length != 0)) { return EFI_INVALID_PARAMETER; }
  if (Length > ENUMA_SCREEN_MAX_COLUMNS - 17) { return EFI_BAD_BUFFER_SIZE; }
  for (Index = 0; Index < Length; Index++) { Text[Index] = Label[Index]; }
  Text[Length] = ' ';
  for (Index = 0; Index < 16; Index++) { Text[Length + 1 + Index] = Hex[(Value >> ((15 - Index) * 4)) & 15]; }
  return EnumaScreenLine (Screen, Row, Text, Length + 17);
}

EFI_STATUS EnumaScreenPage (ENUMA_SCREEN *Screen, CONST ENUMA_SCREEN_SNAPSHOT *Snapshot)
{
  EFI_STATUS Status;
  UINTN Index;
  CONST CHAR8 *Labels[] = {"STAGE", "EFI STATUS", "GOP WIDTH", "GOP HEIGHT", "GOP STRIDE",
    "GOP FORMAT", "GOP BASE", "GOP BYTES", "GETMAP STATUS", "BEST FREE"};
  CONST UINTN Lengths[] = {5,10,9,10,10,10,8,9,13,9};
  UINT64 Values[10];
  if (Screen == NULL || Snapshot == NULL || Snapshot->Build == NULL) { return EFI_INVALID_PARAMETER; }
  if (Screen->Rows < 12 || Screen->Columns < 30 || Snapshot->BuildLength > Screen->Columns) {
    return EFI_BAD_BUFFER_SIZE;
  }
  Values[0] = Snapshot->Stage; Values[1] = Snapshot->Status;
  Values[2] = Snapshot->Width; Values[3] = Snapshot->Height; Values[4] = Snapshot->Stride;
  Values[5] = Snapshot->Format; Values[6] = Snapshot->Base; Values[7] = Snapshot->Bytes;
  Values[8] = Snapshot->MapStatus; Values[9] = Snapshot->BestFree;
  Status = EnumaScreenLine (Screen, 0, "ENUMA DIAG UEFI / NOT XNU", 25);
  if (EFI_ERROR (Status)) { return Status; }
  Status = EnumaScreenLine (Screen, 1, Snapshot->Build, Snapshot->BuildLength);
  if (EFI_ERROR (Status)) { return Status; }
  for (Index = 0; Index < 10; Index++) {
    Status = EnumaScreenHex (Screen, Index + 2, Labels[Index], Lengths[Index], Values[Index]);
    if (EFI_ERROR (Status)) { return Status; }
  }
  return Status;
}
