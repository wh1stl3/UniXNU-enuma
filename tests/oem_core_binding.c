// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <Uefi.h>
#include <Protocol/LoadedImage.h>
#include <Library/BaseMemoryLib.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
VOID *EFIAPI CopyMem(VOID *D,CONST VOID *S,UINTN N){return memcpy(D,S,N);}
VOID *EFIAPI ZeroMem(VOID *D,UINTN N){return memset(D,0,N);}
INTN EFIAPI CompareMem(CONST VOID *A,CONST VOID *B,UINTN N){return memcmp(A,B,N);}
#include "EnumaOemPrecallCapture.h"
STATIC EFI_HANDLE EnumaStartingImage;
STATIC CONST EFI_GUID *EnumaStartingFile;
STATIC EFI_SYSTEM_TABLE *gDxeCoreST;
EFI_GUID gEfiLoadedImageProtocolGuid;
EFI_GUID gEfiFirmwareVolume2ProtocolGuid;
STATIC EFI_LOADED_IMAGE_PROTOCOL *Protocol;
STATIC unsigned CrcCalls,FailCrc;
STATIC unsigned Stops,OriginalAllocations;
STATIC jmp_buf StopJump;
STATIC EFI_STATUS CoreHandleProtocol(EFI_HANDLE H,EFI_GUID *G,VOID **Out){
  if(G==&gEfiFirmwareVolume2ProtocolGuid){assert(H==(EFI_HANDLE)3);*Out=(VOID *)3;return EFI_SUCCESS;}
  assert(H==EnumaStartingImage);*Out=Protocol;return EFI_SUCCESS;
}
// Host tests the real Core binding/state machine; board MMIO is separately
// compiled into the full FD, not replaced with a host success claim.
#define ENUMA_OEM_BOARD_CAPTURE_H
STATIC EFI_BOOT_SERVICES *mOemOriginalBoot;
STATIC BOOLEAN OemBoardSink(VOID *C,CONST CHAR8 *L,UINTN N){(void)C;(void)L;(void)N;return FALSE;}
STATIC VOID OemCaptureTerminal(VOID *C){(void)C;Stops++;longjmp(StopJump,1);}
STATIC BOOLEAN OemProgressPresent(UINT32 P,CONST ENUMA_SERVICE_EVENT *E,UINT64 S){(void)P;(void)E;(void)S;return FALSE;}
#include "EnumaOemCoreBinding.h"
STATIC EFI_TPL EFIAPI Raise(EFI_TPL T){(void)T;return TPL_APPLICATION;}
STATIC VOID EFIAPI Restore(EFI_TPL T){(void)T;}
STATIC EFI_STATUS EFIAPI Crc(VOID *P,UINTN N,UINT32 *V){(void)P;(void)N;CrcCalls++;*V=0;return CrcCalls==FailCrc?EFI_DEVICE_ERROR:EFI_SUCCESS;}
STATIC EFI_STATUS EFIAPI Locate(EFI_GUID *G,VOID *R,VOID **I){(void)G;(void)R;(void)I;return EFI_NOT_FOUND;}
STATIC EFI_STATUS EFIAPI Handle(EFI_HANDLE H,EFI_GUID *G,VOID **I){(void)H;(void)G;(void)I;return EFI_NOT_FOUND;}
STATIC EFI_STATUS EFIAPI Allocate(EFI_MEMORY_TYPE T,UINTN N,VOID **B){(void)T;(void)N;(void)B;OriginalAllocations++;return EFI_OUT_OF_RESOURCES;}
int main(int argc,char **argv){
  EFI_GUID Display={0x4138022f,0x06c7,0x4f79,{0x9c,0x94,0x7e,0x33,0xb5,0x11,0xa4,0xe7}},Wrong={0};
  EFI_BOOT_SERVICES Boot={0};EFI_SYSTEM_TABLE System={0};EFI_LOADED_IMAGE_PROTOCOL Loaded={0},Other={0};
  UINT8 Path[24]={MEDIA_DEVICE_PATH,MEDIA_PIWG_FW_FILE_DP,20,0};
  UINT8 *Image=malloc(ENUMA_OEM_ID_SIZE);UINTN I,Entry;UINT64 V,Delta;FILE *F;
  assert((argc==2||argc==3)&&Image);F=fopen(argv[1],"rb");assert(F);assert(fread(Image,1,ENUMA_OEM_ID_SIZE,F)==ENUMA_OEM_ID_SIZE);fclose(F);
  Delta=(UINT64)(UINTN)Image-ENUMA_OEM_ID_BASE;
  for(I=0;I<sizeof(EnumaOemTextRelocs)/sizeof(UINT32);I++){
    UINT8 *P=Image+ENUMA_OEM_ID_TEXT_RVA+EnumaOemTextRelocs[I];memcpy(&V,P,8);V+=Delta;memcpy(P,&V,8);
  }
  Loaded.ImageBase=Image;Loaded.ImageSize=ENUMA_OEM_ID_SIZE;Entry=(UINTN)Image+ENUMA_OEM_ID_ENTRY;
  if(argc==3){assert(!EnumaOemLoadedIdentity(&Loaded,Entry));free(Image);puts("PASS: cross-profile identity rejected");return 0;}
  assert(EnumaOemLoadedIdentity(&Loaded,Entry));
  assert(!EnumaOemLoadedIdentity(&Loaded,Entry+4));
  Loaded.ImageSize--;assert(!EnumaOemLoadedIdentity(&Loaded,Entry));Loaded.ImageSize++;
  Image[0x1994]^=1;assert(!EnumaOemLoadedIdentity(&Loaded,Entry));Image[0x1994]^=1;
  Image[ENUMA_OEM_ID_TEXT_RVA+EnumaOemTextRelocs[0]]^=1;assert(!EnumaOemLoadedIdentity(&Loaded,Entry));Image[ENUMA_OEM_ID_TEXT_RVA+EnumaOemTextRelocs[0]]^=1;
  Boot.Hdr.HeaderSize=sizeof(Boot);Boot.RaiseTPL=Raise;Boot.RestoreTPL=Restore;Boot.CalculateCrc32=Crc;
  Boot.LocateProtocol=Locate;Boot.HandleProtocol=Handle;Boot.AllocatePool=Allocate;
  System.Hdr.HeaderSize=sizeof(System);System.BootServices=&Boot;gDxeCoreST=&System;
  Loaded.SystemTable=&System;Loaded.ImageCodeType=EfiBootServicesCode;Protocol=&Loaded;
  memcpy(Path+4,&Display,16);Path[20]=END_DEVICE_PATH_TYPE;Path[21]=END_ENTIRE_DEVICE_PATH_SUBTYPE;Path[22]=4;
  Loaded.FilePath=(EFI_DEVICE_PATH_PROTOCOL *)Path;Loaded.DeviceHandle=(EFI_HANDLE)3;EnumaOemStartingFv=(EFI_HANDLE)3;
  EnumaStartingImage=(EFI_HANDLE)1;EnumaStartingFile=&Wrong;
  assert(EnumaOemCoreBeforeEntry((EFI_HANDLE)2,&Loaded,Entry)==EFI_SUCCESS&&!mOemCoreAttempted);
  EnumaStartingFile=&Display;
  assert(EnumaOemCoreBeforeEntry((EFI_HANDLE)2,&Loaded,Entry)==EFI_SUCCESS&&!mOemCoreAttempted);
  assert(EnumaOemCoreBeforeEntry((EFI_HANDLE)1,&Other,Entry)==EFI_SECURITY_VIOLATION&&!mOemCoreAttempted);
  Path[4]^=1;assert(EnumaOemCoreBeforeEntry((EFI_HANDLE)1,&Loaded,Entry)==EFI_SECURITY_VIOLATION);Path[4]^=1;mOemCoreAttempted=FALSE;
  Loaded.DeviceHandle=(EFI_HANDLE)4;assert(EnumaOemCoreBeforeEntry((EFI_HANDLE)1,&Loaded,Entry)==EFI_SECURITY_VIOLATION);Loaded.DeviceHandle=(EFI_HANDLE)3;mOemCoreAttempted=FALSE;
  assert(EnumaOemCoreBeforeEntry((EFI_HANDLE)1,&Loaded,Entry+4)==EFI_SECURITY_VIOLATION&&!mEnumaServiceTrace);
  assert(EnumaOemCoreBeforeEntry((EFI_HANDLE)1,&Loaded,Entry)==EFI_ALREADY_STARTED);
  mOemCoreAttempted=FALSE;FailCrc=1;
  assert(EnumaOemCoreBeforeEntry((EFI_HANDLE)1,&Loaded,Entry)==EFI_DEVICE_ERROR&&Loaded.SystemTable==&System&&!mEnumaServiceTrace);
  mOemCoreAttempted=FALSE;FailCrc=0;
  assert(EnumaOemCoreBeforeEntry((EFI_HANDLE)1,&Loaded,Entry)==EFI_SUCCESS);
  assert(Loaded.SystemTable==&mOemCoreTrace.System&&System.BootServices==&Boot&&mOemCoreTrace.Published);
  if(ENUMA_OEM_PROGRESS){assert(mOemProgress.Owner==&mOemCoreTrace&&mOemProgressHandle==(EFI_HANDLE)1);}
  else{assert(mOemCoreCapture.State==EnumaCaptureArmed&&mOemCoreCapture.Owner==&mOemCoreTrace&&mOemOriginalBoot==&Boot);}
  assert(EnumaOemCoreBeforeEntry((EFI_HANDLE)1,&Loaded,Entry)==EFI_ALREADY_STARTED);
  if(ENUMA_OEM_RUNTIME){
    for(UINTN I=0;I<ENUMA_PROGRESS_CALL;I++){assert(mOemCoreTrace.Boot.AllocatePool(EfiBootServicesData,256,NULL)==EFI_OUT_OF_RESOURCES);}
    if(setjmp(StopJump)==0){mOemCoreTrace.Boot.AllocatePool(EfiBootServicesData,32,NULL);assert(0);}
    assert(Stops==1&&OriginalAllocations==ENUMA_PROGRESS_CALL&&mOemCoreCapture.State!=EnumaCaptureExported);
  }
  free(Image);puts("PASS: relocation normalization, corrupt code/relocation, entry/size, nested handle, loaded pointer, no retry, CRC failure, private table and armed capture");return 0;
}
