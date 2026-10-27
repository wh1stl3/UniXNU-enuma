// SPDX-License-Identifier: BSD-2-Clause-Patent
// QEMU-only physical callback substitution; production menu adapter is unchanged.
#include "Internal.h"
#include "InheritedVideo/MenuWindow.h"
EFI_GUID gEfiGraphicsOutputProtocolGuid=EFI_GRAPHICS_OUTPUT_PROTOCOL_GUID;
EFI_GUID gEfiDevicePathProtocolGuid=EFI_DEVICE_PATH_PROTOCOL_GUID;
EFI_GUID gEfiSimpleTextInProtocolGuid=EFI_SIMPLE_TEXT_INPUT_PROTOCOL_GUID;
EFI_GUID gEfiLoadedImageProtocolGuid=EFI_LOADED_IMAGE_PROTOCOL_GUID;
EFI_GUID gEfiSimpleFileSystemProtocolGuid=EFI_SIMPLE_FILE_SYSTEM_PROTOCOL_GUID;
STATIC EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *Output;
STATIC UINT32 *Memory,Reads,Writes,Bars,Captured;
STATIC EFI_HANDLE Image;
VOID EFIAPI UniXNULog(CONST CHAR8 *Format,...) {
  CHAR8 Ascii[384];CHAR16 Text[400];UINTN I;VA_LIST Args;
  VA_START(Args,Format);AsciiVSPrint(Ascii,sizeof Ascii,Format,Args);VA_END(Args);
  for(I=0;I<383&&Ascii[I];I++){Text[I]=(UINT8)Ascii[I];}Text[I++]=13;Text[I++]=10;Text[I]=0;
  Output->OutputString(Output,Text);
}
STATIC EFI_STATUS Capture(VOID) {
  EFI_LOADED_IMAGE_PROTOCOL *Loaded;EFI_SIMPLE_FILE_SYSTEM_PROTOCOL *Fs;EFI_FILE_PROTOCOL *Root=NULL,*File=NULL;
  EFI_STATUS S;UINTN Size=(800*4+32)*600,Written=Size,Y;UINT8 *Raw=AllocatePool(Size);UINT32 Crc;
  if(!Raw){return EFI_OUT_OF_RESOURCES;}SetMem(Raw,Size,0xa5);
  for(Y=0;Y<600;Y++){CopyMem(Raw+Y*(800*4+32),Memory+(Y+96)*1600+64,800*4);}
  S=gBS->CalculateCrc32(Raw,Size,&Crc);if(EFI_ERROR(S)){goto Done;}
  S=gBS->HandleProtocol(Image,&gEfiLoadedImageProtocolGuid,(VOID **)&Loaded);if(EFI_ERROR(S)){goto Done;}
  S=gBS->HandleProtocol(Loaded->DeviceHandle,&gEfiSimpleFileSystemProtocolGuid,(VOID **)&Fs);if(EFI_ERROR(S)){goto Done;}
  S=Fs->OpenVolume(Fs,&Root);if(EFI_ERROR(S)){goto Done;}
  S=Root->Open(Root,&File,L"\\menu-landscape.bgra",EFI_FILE_MODE_READ|EFI_FILE_MODE_WRITE|EFI_FILE_MODE_CREATE,0);
  if(!EFI_ERROR(S)){S=File->Write(File,&Written,Raw);if(!EFI_ERROR(S)&&Written!=Size){S=EFI_DEVICE_ERROR;}File->Close(File);}
  Root->Close(Root);
  if(!EFI_ERROR(S)){UniXNULog("CHAIN menu rendered 800x600 crc=%08x",Crc);}
Done:FreePool(Raw);return S;
}
STATIC int Address(UINT64 A) {
  UINT64 O;if(A<0x9c000000ULL||A>=0x9cfa0000ULL||(A&3)){return 0;}O=A-0x9c000000ULL;
  return O/6400>=96&&O/6400<696&&O%6400>=256&&O%6400<3456;
}
STATIC int Read(void *C,UINT64 A,UINT32 *V) {
  (VOID)C;if(!V||!Address(A)||Reads>=14*ENUMA_MENU_PIXELS){return 0;}Reads++;*V=Memory[(A-0x9c000000ULL)/4];return 1;
}
STATIC int Write(void *C,UINT64 A,UINT32 V) {
  (VOID)C;if(!Address(A)||Writes>=13*ENUMA_MENU_PIXELS){return 0;}
  if(V==0x71717171&&!Captured){Captured=Capture()==EFI_SUCCESS?1:2;}
  Writes++;Memory[(A-0x9c000000ULL)/4]=V;return 1;
}
STATIC int Barrier(void *C) {(VOID)C;Bars++;return 1;}
STATIC int Validate(void *C,const ENUMA_INHERITED_FRAME *F) {(VOID)C;return F->Requirements==22;}
UINT32 EnumaBoundedMenu(const ENUMA_INHERITED_FRAME *,ENUMA_PIXEL_READ,ENUMA_PIXEL_WRITE,ENUMA_PIXEL_BARRIER,ENUMA_PIXEL_REVALIDATE,VOID *);
EFI_STATUS EFIAPI EnumaGopSelfTest(EFI_HANDLE Handle,EFI_SYSTEM_TABLE *SystemTable) {
  ENUMA_INHERITED_FRAME F={0x9c000000ULL,6400ULL*2560,1600,2560,6400,0xff0000,0xff00,255,0xff000000,16,8,0,3,1,0,6,22};
  UINT32 Result,I;BOOLEAN Ok=TRUE;
  Image=Handle;Output=SystemTable->ConOut;gBS->SetWatchdogTimer(0,0,0,NULL);
  Memory=AllocatePool(6400*2560);if(!Memory){return EFI_OUT_OF_RESOURCES;}SetMem(Memory,6400*2560,0x71);
  Result=EnumaBoundedMenu(&F,Read,Write,Barrier,Validate,NULL);
  for(I=0;I<1600*2560;I++){if(Memory[I]!=0x71717171){Ok=FALSE;break;}}
  Ok=Ok&&Result==5&&Captured==1&&gST==SystemTable&&F.Requirements==22;
  UniXNULog("BOUNDED result=%u captured=%u reads=%u writes=%u barriers=%u restored=%u",Result,Captured,Reads,Writes,Bars,Ok);
  UniXNULog(Ok?"ENUMA_BOUNDED_MENU PASS QEMU RAM ONLY":"ENUMA_BOUNDED_MENU FAIL QEMU RAM ONLY");
  FreePool(Memory);gRT->ResetSystem(EfiResetShutdown,Ok?EFI_SUCCESS:EFI_DEVICE_ERROR,0,NULL);return Ok?EFI_SUCCESS:EFI_DEVICE_ERROR;
}
