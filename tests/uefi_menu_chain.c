// SPDX-License-Identifier: BSD-2-Clause-Patent
// QEMU-only software chain: allocated RAM GOP -> real GraphicsConsole -> real
// pinned UniXNU Ui/Menu. Scripted keyboard is a fixture, never enuma input proof.
#include "Internal.h"
#include <Protocol/SerialIo.h>
#include <Protocol/DevicePath.h>
#include "InheritedGopPublish.h"
#include "InheritedGopWtArm.h"
#include "EnumaJournalConsole.h"
#include "EnumaMenuConsole.h"
#include "ConsoleGop.h"

EFI_GUID gEfiGraphicsOutputProtocolGuid=EFI_GRAPHICS_OUTPUT_PROTOCOL_GUID;
EFI_GUID gEfiDevicePathProtocolGuid=EFI_DEVICE_PATH_PROTOCOL_GUID;
EFI_GUID gEfiSimpleTextInProtocolGuid=EFI_SIMPLE_TEXT_INPUT_PROTOCOL_GUID;
EFI_GUID gEfiLoadedImageProtocolGuid=EFI_LOADED_IMAGE_PROTOCOL_GUID;
EFI_GUID gEfiSimpleFileSystemProtocolGuid=EFI_SIMPLE_FILE_SYSTEM_PROTOCOL_GUID;
STATIC EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *HostOutput;
STATIC EFI_SIMPLE_TEXT_INPUT_PROTOCOL Input;
STATIC EFI_INPUT_KEY Keys[4];
STATIC UINTN KeyCount,KeyIndex;
STATIC BOOLEAN KeyReady;
STATIC EFI_STATUS Failure;
STATIC UINTN FailureLine;
STATIC EFI_SYSTEM_TABLE LocalTable;

STATIC VOID Log(CONST CHAR16 *Text) { if(HostOutput){HostOutput->OutputString(HostOutput,(CHAR16 *)Text);} }
// Test log receiver: keeps actual UniXNU Menu/Ui logs visible on AAVMF's serial
// ConOut while the menu itself draws on the independent RAM graphics handle.
VOID EFIAPI UniXNULog(CONST CHAR8 *Format,...) {
  CHAR8 Ascii[384];CHAR16 Text[400];UINTN I;VA_LIST Args;
  VA_START(Args,Format);AsciiVSPrint(Ascii,sizeof Ascii,Format,Args);VA_END(Args);
  for(I=0;I<383&&Ascii[I];I++){Text[I]=(UINT8)Ascii[I];}
  Text[I++]=L'\r';Text[I++]=L'\n';Text[I]=0;Log(Text);
}
STATIC EFI_STATUS EFIAPI Validate(VOID *Context,CONST ENUMA_INHERITED_FRAME *F) {
  return F->Base==(UINTN)Context && !F->Requirements?EFI_SUCCESS:EFI_NOT_READY;
}
STATIC VOID EFIAPI KeyNotify(EFI_EVENT Event,VOID *Context) {
  (VOID)Context;
  if(KeyIndex<KeyCount){KeyReady=TRUE;gBS->SignalEvent(Event);}
}
STATIC EFI_STATUS EFIAPI ReadKey(EFI_SIMPLE_TEXT_INPUT_PROTOCOL *This,EFI_INPUT_KEY *Key) {
  (VOID)This;
  if(!KeyReady||KeyIndex>=KeyCount){return EFI_NOT_READY;}
  *Key=Keys[KeyIndex++];KeyReady=FALSE;return EFI_SUCCESS;
}
STATIC VOID Script(UINT16 FirstScan,CHAR16 FirstChar,BOOLEAN EnterAfter) {
  KeyIndex=0;KeyReady=FALSE;KeyCount=EnterAfter?2:1;
  Keys[0].ScanCode=FirstScan;Keys[0].UnicodeChar=FirstChar;
  Keys[1].ScanCode=0;Keys[1].UnicodeChar=L'\r';
}
STATIC EFI_STATUS SaveFrame(EFI_HANDLE Image,CONST CHAR16 *Name,CONST VOID *Bytes,UINTN Size) {
  EFI_LOADED_IMAGE_PROTOCOL *Loaded;EFI_SIMPLE_FILE_SYSTEM_PROTOCOL *Fs;EFI_FILE_PROTOCOL *Root=NULL,*File=NULL;
  EFI_STATUS S;UINTN Written=Size;
  S=gBS->HandleProtocol(Image,&gEfiLoadedImageProtocolGuid,(VOID **)&Loaded);if(EFI_ERROR(S)){return S;}
  S=gBS->HandleProtocol(Loaded->DeviceHandle,&gEfiSimpleFileSystemProtocolGuid,(VOID **)&Fs);if(EFI_ERROR(S)){return S;}
  S=Fs->OpenVolume(Fs,&Root);if(EFI_ERROR(S)){return S;}
  S=Root->Open(Root,&File,(CHAR16 *)Name,EFI_FILE_MODE_READ|EFI_FILE_MODE_WRITE|EFI_FILE_MODE_CREATE,0);
  if(!EFI_ERROR(S)){S=File->Write(File,&Written,(VOID *)Bytes);if(!EFI_ERROR(S)&&Written!=Size){S=EFI_DEVICE_ERROR;}if(!EFI_ERROR(S)){S=File->Flush(File);}File->Close(File);}
  Root->Close(Root);return S;
}
#define REQUIRE(E) do {if(!(E)){Failure=EFI_DEVICE_ERROR;FailureLine=__LINE__;goto Done;}}while(0)
STATIC EFI_STATUS Geometry(EFI_HANDLE Image,BOOLEAN Portrait) {
  ENUMA_INHERITED_FRAME F={0};ENUMA_GOP_PUBLICATION *Publication=NULL;
  EFI_GRAPHICS_OUTPUT_PROTOCOL *Gop=NULL;EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *TextOut=NULL;
  EFI_HANDLE Display=NULL,Keyboard=NULL;EFI_STATUS S;UINT8 *Memory=NULL;
  UINTN I,Y,Index,Choice;UINT32 Crc=0;EFI_SYSTEM_TABLE *OriginalTable=gST;
  UNIXNU_CONFIG Config={0};UNIXNU_UI Ui;UNIXNU_ENTRY Entries[2]={{0}};
  ENUMA_BOOT_LOG Journal={0};UINT32 Cursor=0;
#if defined(ENUMA_MENU_TEST_WT_OPAQUE) && ENUMA_MENU_TEST_WT_OPAQUE
  ENUMA_GOP_WT_WINDOW Window={0};ENUMA_GOP_ACCESS Access;
#define PUBLISH_FRAME() EnumaGopPublishWtOpaque(&F,Validate,Memory+32,&Access,&Publication)
#else
#define PUBLISH_FRAME() EnumaGopPublish(&F,Validate,Memory+32,&Publication)
#endif
  // Separate vendor identity for the fixture keyboard. Display identity comes
  // from the production publication helper and is compared by host tests.
  STATIC struct {VENDOR_DEVICE_PATH Vendor;EFI_DEVICE_PATH_PROTOCOL End;} KeyboardPath={
    {{HARDWARE_DEVICE_PATH,HW_VENDOR_DP,{sizeof(VENDOR_DEVICE_PATH),0}},
      {0x19cd2af8,0x7549,0x4e90,{0xba,0x08,0x68,0x1a,0xa3,0x1d,0x6c,0x07}}},
    {END_DEVICE_PATH_TYPE,END_ENTIRE_DEVICE_PATH_SUBTYPE,{END_DEVICE_PATH_LENGTH,0}}};
  F.Width=Portrait?768:800;F.Height=Portrait?1024:600;F.Stride=F.Width*4+32;F.Bytes=(UINT64)F.Stride*F.Height;
  Memory=AllocatePool((UINTN)F.Bytes+64);REQUIRE(Memory);
  SetMem(Memory,(UINTN)F.Bytes+64,0xa5);F.Base=(UINTN)(Memory+32);
  F.RedMask=0xff0000;F.GreenMask=0xff00;F.BlueMask=255;F.ReservedMask=0xff000000;
  F.PipeMask=3;F.CtlMask=1;F.IntfMask=6;
#if defined(ENUMA_MENU_TEST_WT_OPAQUE) && ENUMA_MENU_TEST_WT_OPAQUE
  Window.Base=F.Base;Window.Bytes=F.Bytes;Access=EnumaWtAccess(&Window);
#endif
  F.Requirements=22;
  REQUIRE(PUBLISH_FRAME()==EFI_NOT_READY&&!Publication);
  F.Requirements=0; // Synthetic allocated-RAM fixture only; not board evidence.
  REQUIRE(PUBLISH_FRAME()==EFI_SUCCESS);
#undef PUBLISH_FRAME
  Display=EnumaGopPublicationHandle(Publication);
  REQUIRE(gBS->HandleProtocol(Display,&gEfiGraphicsOutputProtocolGuid,(VOID **)&Gop)==EFI_SUCCESS);
  {EFI_GRAPHICS_OUTPUT_PROTOCOL *Borrowed=NULL;
    REQUIRE(EnumaLookupConsoleGop(gBS,Display,&Borrowed)==EFI_SUCCESS&&Borrowed==Gop);}
  REQUIRE(EnumaMenuGraphicsConsoleCheck(Gop)==EFI_SUCCESS);
  UniXNULog("CHAIN published RAM GOP %ux%u",F.Width,F.Height);
  S=gBS->ConnectController(Display,NULL,NULL,TRUE);
  REQUIRE(S==EFI_SUCCESS);
  {EFI_GUID Guid=EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL_GUID;
    REQUIRE(gBS->HandleProtocol(Display,&Guid,(VOID **)&TextOut)==EFI_SUCCESS);}
  REQUIRE(EnumaMenuTextConsoleCheck(TextOut)==EFI_SUCCESS);
  REQUIRE(EnumaBootLogAppend(&Journal,15,7,&gEfiGraphicsOutputProtocolGuid,0));
  REQUIRE(EnumaBootLogAppend(&Journal,13,7,&gEfiGraphicsOutputProtocolGuid,EFI_SUCCESS));
  REQUIRE(EnumaJournalConsoleDrain(&Journal,TextOut,&Cursor)==EFI_SUCCESS);
  REQUIRE(Cursor==Journal.Count+1);
  UniXNULog("CHAIN GraphicsConsole and attributed ConOut replay accepted");
  CopyMem(&LocalTable,OriginalTable,sizeof LocalTable);LocalTable.ConsoleOutHandle=Display;LocalTable.ConOut=TextOut;
  LocalTable.ConIn=NULL;gST=&LocalTable;
  Entries[0].Id="return";Entries[0].Title=L"Return without boot";Entries[0].Type=UniXNUEntryAction;
  Entries[1].Id="diagnostic";Entries[1].Title=L"Diagnostics fixture";Entries[1].Type=UniXNUEntryAction;
  Config.Title=L"UniXNU menu chain test";Config.SourceLabel=L"QEMU RAM ONLY - NOT ENUMA DISPLAY";
  Config.Entries=Entries;Config.EntryCount=2;Config.DefaultIndex=0;Config.Timeout=-1;Config.FallbackTimeout=1;
  Config.Console=UniXNUConsoleGraphics;Config.Layout=UniXNULayoutAuto;Config.PortraitBelow=800;Config.Scale=1;
  // Direct graphics entry must work without a text console or journal drain.
  LocalTable.ConOut=NULL;
  UniXNUUiInit(&Config,&Ui);REQUIRE(Ui.Mode==UniXNUUiGraphics&&Ui.Gop==Gop&&Ui.Portrait==Portrait);
  Index=UniXNUMenuRun(&Ui,&Config,TRUE);REQUIRE(Index==0);
  REQUIRE(gBS->CalculateCrc32(Memory+32,(UINTN)F.Bytes,&Crc)==EFI_SUCCESS&&Crc);
  REQUIRE(SaveFrame(Image,Portrait?L"\\menu-portrait.bgra":L"\\menu-landscape.bgra",Memory+32,(UINTN)F.Bytes)==EFI_SUCCESS);
  UniXNULog("CHAIN menu rendered %ux%u crc=%08x no-input fallback selected default",F.Width,F.Height,Crc);
  // Real event services and real Menu logic, synthetic physical input protocol.
  Input.ReadKeyStroke=ReadKey;
  REQUIRE(gBS->CreateEvent(EVT_NOTIFY_WAIT,TPL_CALLBACK,KeyNotify,NULL,&Input.WaitForKey)==EFI_SUCCESS);
  REQUIRE(gBS->InstallMultipleProtocolInterfaces(&Keyboard,&gEfiSimpleTextInProtocolGuid,&Input,
    &gEfiDevicePathProtocolGuid,&KeyboardPath,NULL)==EFI_SUCCESS);
  LocalTable.ConIn=&Input;Config.Timeout=5;
  Script(SCAN_DOWN,0,TRUE);Index=UniXNUMenuRun(&Ui,&Config,TRUE);REQUIRE(Index==1&&KeyIndex==2);
  Entries[1].Confirm=L"Confirm fixture only?";
  Script(SCAN_ESC,0,FALSE);REQUIRE(!UniXNUMenuConfirm(&Ui,&Entries[1],&Choice));
  Script(0,L'\r',FALSE);REQUIRE(UniXNUMenuConfirm(&Ui,&Entries[1],&Choice));
  REQUIRE(LocalTable.ConOut==NULL);
  UniXNULog("CHAIN graphics menu and scripted input accepted with ConOut NULL");
  // Exercise the actual text fallback on the same GraphicsConsole instance.
  LocalTable.ConOut=TextOut;
  Config.Console=UniXNUConsoleText;UniXNUUiInit(&Config,&Ui);REQUIRE(Ui.Mode==UniXNUUiText);
  Script(0,L'1',FALSE);Index=UniXNUMenuRun(&Ui,&Config,TRUE);REQUIRE(Index==0);
  UniXNULog("CHAIN scripted selection/cancel/confirm and text fallback returned");
#if defined(ENUMA_MENU_TEST_WT_OPAQUE) && ENUMA_MENU_TEST_WT_OPAQUE
  {ENUMA_GOP_ACCESS_STATE State;
    EFI_GRAPHICS_OUTPUT_BLT_PIXEL Readback;
    REQUIRE(Gop->Blt(Gop,&Readback,EfiBltVideoToBltBuffer,0,0,0,0,1,1,0)==EFI_SUCCESS&&Readback.Reserved==0);
    REQUIRE(EnumaGopGetAccessState(Gop,&State)==EFI_SUCCESS);
    UniXNULog("CHAIN WT opaque reads=%lx writes=%lx barriers=%lx fault=%r",State.Reads,State.Writes,State.Barriers,State.Fault);
    REQUIRE(!State.Latched&&State.Reads&&State.Writes&&State.Barriers);}
#endif
  for(I=0;I<32;I++){REQUIRE(Memory[I]==0xa5&&Memory[32+(UINTN)F.Bytes+I]==0xa5);}
  for(Y=0;Y<F.Height;Y++){for(I=F.Width*4;I<F.Stride;I++){REQUIRE(Memory[32+Y*F.Stride+I]==0xa5);}}
Done:
  gST=OriginalTable;
  if(Keyboard){
    S=gBS->UninstallMultipleProtocolInterfaces(Keyboard,&gEfiSimpleTextInProtocolGuid,&Input,&gEfiDevicePathProtocolGuid,&KeyboardPath,NULL);
    if(S!=EFI_SUCCESS){Failure=S;FailureLine=__LINE__;}
  }
  if(Input.WaitForKey){gBS->CloseEvent(Input.WaitForKey);Input.WaitForKey=NULL;}
  if(Publication){
    S=gBS->DisconnectController(EnumaGopPublicationHandle(Publication),NULL,NULL);
    if(S!=EFI_SUCCESS&&S!=EFI_NOT_FOUND){Failure=S;FailureLine=__LINE__;}
    S=EnumaGopUnpublish(&Publication);if(S!=EFI_SUCCESS){Failure=S;FailureLine=__LINE__;}
  }
  // Retain frame storage if any interface could still reference it.
  if(Memory&&!Publication){FreePool(Memory);}
  return Failure;
}

// Reuse the fixed constructor/entry object for the previous QEMU RAM self-test;
// the resulting EFI is a new off-device artifact with its own input manifest.
EFI_STATUS EFIAPI EnumaGopSelfTest(EFI_HANDLE Image,EFI_SYSTEM_TABLE *SystemTable) {
  HostOutput=SystemTable->ConOut;gBS->SetWatchdogTimer(0,0,0,NULL);
  Log(L"ENUMA_MENU_CHAIN BEGIN QEMU RAM ONLY\r\n");
  Geometry(Image,FALSE);
  if(Failure==EFI_SUCCESS){Geometry(Image,TRUE);}
  if(Failure!=EFI_SUCCESS){UniXNULog("ENUMA_MENU_CHAIN FAIL line=%u status=%r",(UINT32)FailureLine,Failure);}
  else {Log(L"ENUMA_MENU_CHAIN PASS QEMU RAM ONLY\r\n");}
  gRT->ResetSystem(EfiResetShutdown,Failure,0,NULL);return Failure;
}
