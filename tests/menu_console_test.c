// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "EnumaMenuConsole.h"
#include <assert.h>
#include <stdio.h>
static EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL Out;
static EFI_SIMPLE_TEXT_OUTPUT_MODE Mode;
static UINTN Columns=80,Rows=25;
static unsigned Queries,Writes;
static EFI_STATUS QueryStatus;
static EFI_STATUS EFIAPI Query(EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *This,UINTN Index,UINTN *C,UINTN *R) {
  assert(This==&Out && Index==0); Queries++; *C=Columns;*R=Rows;return QueryStatus;
}
static EFI_STATUS EFIAPI Write(EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *This,CHAR16 *Text) {
  (void)This;(void)Text;Writes++;return EFI_SUCCESS;
}
static EFI_STATUS EFIAPI Set(EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *This,UINTN Value) {
  (void)This;(void)Value;Writes++;return EFI_SUCCESS;
}
static EFI_STATUS EFIAPI Cursor(EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *This,UINTN X,UINTN Y) {
  (void)This;(void)X;(void)Y;Writes++;return EFI_SUCCESS;
}
static EFI_STATUS EFIAPI Clear(EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *This) {
  (void)This;Writes++;return EFI_SUCCESS;
}
static EFI_STATUS EFIAPI Enable(EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *This,BOOLEAN Value) {
  (void)This;(void)Value;Writes++;return EFI_SUCCESS;
}
static void Init(void) {
  Queries=Writes=0;Mode.MaxMode=1;Mode.Mode=0;Columns=80;Rows=25;QueryStatus=EFI_SUCCESS;
  Out.Mode=&Mode;Out.QueryMode=Query;Out.OutputString=Write;Out.SetAttribute=Set;
  Out.SetCursorPosition=Cursor;Out.ClearScreen=Clear;Out.EnableCursor=Enable;
}
int main(void) {
  Init();assert(EnumaMenuTextConsoleCheck(NULL)==EFI_NOT_FOUND);
  Out.Mode=NULL;assert(EnumaMenuTextConsoleCheck(&Out)==EFI_NOT_READY && !Queries);
  Init();Out.QueryMode=NULL;assert(EnumaMenuTextConsoleCheck(&Out)==EFI_NOT_READY && !Queries);
  Init();Out.OutputString=NULL;assert(EnumaMenuTextConsoleCheck(&Out)==EFI_NOT_READY && !Queries);
  Init();Out.SetAttribute=NULL;assert(EnumaMenuTextConsoleCheck(&Out)==EFI_NOT_READY && !Queries);
  Init();Out.SetCursorPosition=NULL;assert(EnumaMenuTextConsoleCheck(&Out)==EFI_NOT_READY && !Queries);
  Init();Out.ClearScreen=NULL;assert(EnumaMenuTextConsoleCheck(&Out)==EFI_NOT_READY && !Queries);
  Init();Out.EnableCursor=NULL;assert(EnumaMenuTextConsoleCheck(&Out)==EFI_NOT_READY && !Queries);
  Init();Mode.Mode=-1;assert(EnumaMenuTextConsoleCheck(&Out)==EFI_NOT_READY && !Queries);
  Init();Mode.Mode=1;assert(EnumaMenuTextConsoleCheck(&Out)==EFI_NOT_READY && !Queries);
  Init();QueryStatus=EFI_DEVICE_ERROR;assert(EnumaMenuTextConsoleCheck(&Out)==EFI_DEVICE_ERROR && Queries==1);
  Init();QueryStatus=EFI_WARN_UNKNOWN_GLYPH;assert(EnumaMenuTextConsoleCheck(&Out)==EFI_WARN_UNKNOWN_GLYPH && Queries==1);
  Init();Columns=0;assert(EnumaMenuTextConsoleCheck(&Out)==EFI_UNSUPPORTED);
  Init();Columns=1;assert(EnumaMenuTextConsoleCheck(&Out)==EFI_UNSUPPORTED);
  Init();Rows=0;assert(EnumaMenuTextConsoleCheck(&Out)==EFI_UNSUPPORTED);
  Init();Rows=7;assert(EnumaMenuTextConsoleCheck(&Out)==EFI_UNSUPPORTED);
  Init();Columns=2;Rows=8;assert(EnumaMenuTextConsoleCheck(&Out)==EFI_SUCCESS && Queries==1 && !Writes);
  puts("PASS: absent/incomplete ConOut, invalid mode, query errors/warnings and geometry rejected; usable text console accepted without mode/attribute/cursor/clear/output writes");
}
