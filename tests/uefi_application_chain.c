// SPDX-License-Identifier: BSD-2-Clause-Patent
// VM-only: real separately linked application, real disk TOML, LoadImage/StartImage.
#include "Internal.h"
#include "InheritedGopPublish.h"
#include "EnumaMenuApplication.h"
#include <Protocol/DevicePathUtilities.h>
EFI_GUID gEfiGraphicsOutputProtocolGuid=EFI_GRAPHICS_OUTPUT_PROTOCOL_GUID;
EFI_GUID gEfiDevicePathProtocolGuid=EFI_DEVICE_PATH_PROTOCOL_GUID;
EFI_GUID gEfiLoadedImageProtocolGuid=EFI_LOADED_IMAGE_PROTOCOL_GUID;
EFI_GUID gEfiSimpleFileSystemProtocolGuid=EFI_SIMPLE_FILE_SYSTEM_PROTOCOL_GUID;
STATIC EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *Output;
VOID EFIAPI UniXNULog(CONST CHAR8 *Format,...) {
  CHAR8 A[384];CHAR16 T[400];UINTN I;VA_LIST Args;
  VA_START(Args,Format);AsciiVSPrint(A,sizeof A,Format,Args);VA_END(Args);
  for(I=0;I<383&&A[I];I++){T[I]=(UINT8)A[I];}T[I++]=13;T[I++]=10;T[I]=0;Output->OutputString(Output,T);
}
STATIC EFI_STATUS EFIAPI Validate(VOID *Context,CONST ENUMA_INHERITED_FRAME *F) {
 return F->Base==(UINTN)Context&&!F->Requirements?EFI_SUCCESS:EFI_NOT_READY;
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

#define CHECK(E) do {if(!(E)){UniXNULog("APPLICATION FAIL line=%u",__LINE__);Ok=FALSE;goto Done;}}while(0)
EFI_STATUS EFIAPI EnumaGopSelfTest(EFI_HANDLE Image,EFI_SYSTEM_TABLE *SystemTable) {
 ENUMA_INHERITED_FRAME F={0};ENUMA_GOP_PUBLICATION *Pub=NULL;
 EFI_LOADED_IMAGE_PROTOCOL *Self;EFI_DEVICE_PATH_PROTOCOL *Path=NULL,*DevicePath;
 EFI_DEVICE_PATH_UTILITIES_PROTOCOL *Utilities;EFI_GUID UtilitiesGuid=EFI_DEVICE_PATH_UTILITIES_PROTOCOL_GUID;
 struct {EFI_DEVICE_PATH_PROTOCOL Header;CHAR16 Name[23];} FileNode;
 EFI_STATUS S;UINT8 *Memory=NULL;UINTN I,Y,Pass;UINT32 Crc;BOOLEAN Ok=TRUE;
 ENUMA_MENU_APPLICATION_CONTEXT Context={0};
 Output=SystemTable->ConOut;gBS->SetWatchdogTimer(0,0,0,NULL);
 F.Width=800;F.Height=600;F.Stride=3232;F.Bytes=F.Stride*F.Height;
 Memory=AllocatePool((UINTN)F.Bytes+64);CHECK(Memory);SetMem(Memory,(UINTN)F.Bytes+64,0xa5);F.Base=(UINTN)(Memory+32);
 F.RedMask=0xff0000;F.GreenMask=0xff00;F.BlueMask=255;F.ReservedMask=0xff000000;F.PipeMask=3;F.CtlMask=1;F.IntfMask=6;
 F.Requirements=22;CHECK(EnumaGopPublish(&F,Validate,Memory+32,&Pub)==EFI_NOT_READY&&!Pub);
 F.Requirements=0; // Synthetic VM RAM only; board requirements never modified.
 CHECK(EnumaGopPublish(&F,Validate,Memory+32,&Pub)==EFI_SUCCESS);
 CHECK(gBS->HandleProtocol(Image,&gEfiLoadedImageProtocolGuid,(VOID **)&Self)==EFI_SUCCESS);
 CHECK(gBS->HandleProtocol(Self->DeviceHandle,&gEfiDevicePathProtocolGuid,(VOID **)&DevicePath)==EFI_SUCCESS);
 CHECK(gBS->LocateProtocol(&UtilitiesGuid,NULL,(VOID **)&Utilities)==EFI_SUCCESS);
 ZeroMem(&FileNode,sizeof FileNode);FileNode.Header.Type=MEDIA_DEVICE_PATH;FileNode.Header.SubType=MEDIA_FILEPATH_DP;
 FileNode.Header.Length[0]=sizeof FileNode;CopyMem(FileNode.Name,L"\\EFI\\UniXNU\\UniXNU.efi",sizeof(L"\\EFI\\UniXNU\\UniXNU.efi"));
 Path=Utilities->AppendDeviceNode(DevicePath,&FileNode.Header);CHECK(Path);
 for(Pass=0;Pass<2;Pass++) {
   S=EnumaMenuApplicationStart(&Context,Image,Path,EnumaGopPublicationHandle(Pub),Pass!=0);
   UniXNULog("APPLICATION real child host=%u status=%r",(UINT32)Pass,S);
   CHECK(S==(Pass?EFI_ABORTED:EFI_SUCCESS));CHECK(!Context.Active);
   CHECK(gST==SystemTable&&gST->ConOut==Output);
   CHECK(gBS->CalculateCrc32(Memory+32,(UINTN)F.Bytes,&Crc)==EFI_SUCCESS&&Crc);
   CHECK(SaveFrame(Image,Pass?L"\\menu-firmware.bgra":L"\\menu-application.bgra",Memory+32,(UINTN)F.Bytes)==EFI_SUCCESS);
   UniXNULog("APPLICATION frame host=%u crc=%08x",(UINT32)Pass,Crc);
 }
 for(I=0;I<32;I++){CHECK(Memory[I]==0xa5&&Memory[32+(UINTN)F.Bytes+I]==0xa5);}
 for(Y=0;Y<F.Height;Y++){for(I=F.Width*4;I<F.Stride;I++){CHECK(Memory[32+Y*F.Stride+I]==0xa5);}}
Done:
 if(Path){FreePool(Path);}
 if(Pub){S=EnumaGopUnpublish(&Pub);if(EFI_ERROR(S)){Ok=FALSE;}}
 if(Memory&&!Pub&&!Context.Active){FreePool(Memory);}
 UniXNULog(Ok?"ENUMA_APPLICATION_CHAIN PASS QEMU RAM ONLY":"ENUMA_APPLICATION_CHAIN FAIL QEMU RAM ONLY");
 gRT->ResetSystem(EfiResetShutdown,Ok?EFI_SUCCESS:EFI_DEVICE_ERROR,0,NULL);return Ok?EFI_SUCCESS:EFI_DEVICE_ERROR;
}
