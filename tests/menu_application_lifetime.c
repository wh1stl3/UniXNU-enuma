// SPDX-License-Identifier: BSD-2-Clause-Patent
// Cross-image lifetime/failure tests; no device I/O.
#include "EnumaMenuApplication.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
EFI_GUID gEfiGraphicsOutputProtocolGuid=EFI_GRAPHICS_OUTPUT_PROTOCOL_GUID;
EFI_GUID gEfiLoadedImageProtocolGuid=EFI_LOADED_IMAGE_PROTOCOL_GUID;
EFI_BOOT_SERVICES Services;EFI_BOOT_SERVICES *gBS=&Services;
EFI_SYSTEM_TABLE Original;EFI_SYSTEM_TABLE *gST=&Original;
static EFI_LOADED_IMAGE_PROTOCOL Loaded;
static EFI_GRAPHICS_OUTPUT_MODE_INFORMATION Info;
static EFI_GRAPHICS_OUTPUT_PROTOCOL_MODE Mode;
static EFI_GRAPHICS_OUTPUT_PROTOCOL Gop;
static int Scenario,Present,Started,Unloaded;
static EFI_SYSTEM_TABLE *Observed;
VOID *EFIAPI CopyMem(VOID *D,CONST VOID *S,UINTN N){return memcpy(D,S,N);}
static EFI_STATUS EFIAPI Blt(EFI_GRAPHICS_OUTPUT_PROTOCOL *T,EFI_GRAPHICS_OUTPUT_BLT_PIXEL *B,EFI_GRAPHICS_OUTPUT_BLT_OPERATION O,UINTN A,UINTN C,UINTN D,UINTN E,UINTN F,UINTN G,UINTN H){(void)T;(void)B;(void)O;(void)A;(void)C;(void)D;(void)E;(void)F;(void)G;(void)H;return 0;}
static EFI_STATUS EFIAPI Handle(EFI_HANDLE H,EFI_GUID *G,VOID **P){
 (void)G;if(H==(VOID *)1){if(Scenario==1)return EFI_NOT_FOUND;*P=&Gop;return 0;}
 if(!Present||Scenario==4)return EFI_NOT_FOUND;*P=&Loaded;return 0;
}
static EFI_STATUS EFIAPI Load(BOOLEAN B,EFI_HANDLE H,EFI_DEVICE_PATH_PROTOCOL *P,VOID *S,UINTN N,EFI_HANDLE *C){
 (void)B;(void)H;(void)P;(void)S;(void)N;if(Scenario==2)return EFI_NOT_FOUND;
 *C=(VOID *)2;Present=1;return Scenario==3?EFI_SECURITY_VIOLATION:0;
}
static EFI_STATUS EFIAPI Crc(VOID *P,UINTN N,UINT32 *C){(void)P;(void)N;if(Scenario==5)return EFI_DEVICE_ERROR;*C=123;return 0;}
static EFI_STATUS EFIAPI Start(EFI_HANDLE H,UINTN *N,CHAR16 **D){
 (void)H;(void)N;(void)D;Started++;Observed=Loaded.SystemTable;
 assert(Observed!=gST&&Observed->ConsoleOutHandle==(VOID *)1&&!Observed->ConOut&&!Observed->ConIn&&Observed->Hdr.CRC32==123);
 if(Scenario!=6&&Scenario!=7)Present=0;return EFI_ABORTED;
}
static EFI_STATUS EFIAPI Unload(EFI_HANDLE H){(void)H;Unloaded++;if(Scenario==7)return EFI_ACCESS_DENIED;Present=0;return 0;}
int main(void){
 Services.HandleProtocol=Handle;Services.LoadImage=Load;Services.StartImage=Start;Services.UnloadImage=Unload;Services.CalculateCrc32=Crc;
 Original.Hdr.HeaderSize=sizeof Original;Original.ConOut=(VOID *)99;Gop.Blt=Blt;Gop.Mode=&Mode;Mode.Info=&Info;
 for(Scenario=0;Scenario<9;Scenario++){
  ENUMA_MENU_APPLICATION_CONTEXT C={0};EFI_DEVICE_PATH_PROTOCOL Path={0};EFI_STATUS S;
  Present=Started=Unloaded=0;memset(&Loaded,0,sizeof Loaded);Loaded.ImageCodeType=Scenario==8?EfiBootServicesCode:EfiLoaderCode;
  S=EnumaMenuApplicationStart(&C,(VOID *)3,&Path,(VOID *)1,TRUE);
  assert(gST==&Original&&Original.ConOut==(VOID *)99);
  if(Scenario==0||Scenario==6||Scenario==7){assert(Started==1);assert(Loaded.LoadOptionsSize==sizeof(L"unixnu:firmware"));}
  else assert(!Started);
  if(Scenario==7){assert(S==EFI_ACCESS_DENIED&&C.Active&&Present);assert(EnumaMenuApplicationStart(&C,(VOID *)3,&Path,(VOID *)1,TRUE)==EFI_INVALID_PARAMETER);}
  else assert(!C.Active);
  if(Scenario==3)assert(S==EFI_SECURITY_VIOLATION&&Unloaded==1&&!Present);
  if(Scenario==5)assert(S==EFI_DEVICE_ERROR&&Unloaded==1);
  if(Scenario==8)assert(S==EFI_UNSUPPORTED&&Unloaded==1);
 }
 puts("menu application lifetime: 9 scenarios passed");return 0;
}
