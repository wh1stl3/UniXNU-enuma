// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <Uefi.h>
#include "EnumaMenuConfigFs.h"
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
static int FailAllocation;
VOID *EFIAPI AllocateZeroPool(UINTN N){return FailAllocation?NULL:calloc(1,N);}
VOID EFIAPI FreePool(VOID *P){free(P);}
VOID *EFIAPI CopyMem(VOID *D,CONST VOID *S,UINTN N){return memcpy(D,S,N);}
VOID *EFIAPI ZeroMem(VOID *D,UINTN N){return memset(D,0,N);}
BOOLEAN EFIAPI CompareGuid(CONST GUID *A,CONST GUID *B){return memcmp(A,B,sizeof *A)==0;}
INTN EFIAPI StrCmp(CONST CHAR16 *A,CONST CHAR16 *B){while(*A&&*A==*B){A++;B++;}return *A-*B;}
int main(void){
 ENUMA_MENU_CONFIG_FS Fs;EFI_FILE_PROTOCOL *Root,*File,*Other,*Handles[8];UINTN N,I;UINT64 Position;
 EFI_GUID Guid=EFI_FILE_INFO_ID,Bad={0};UINT8 Buffer[2048];EFI_FILE_INFO *Info=(VOID *)Buffer;
 MenuConfigInit(&Fs);assert(Fs.Protocol.OpenVolume(&Fs.Protocol,&Root)==0&&Fs.OpenCount==1);
 assert(Root->Open(Root,&File,L"\\EFI\\UniXNU\\unixnu.toml",EFI_FILE_MODE_WRITE,0)==EFI_WRITE_PROTECTED);
 assert(Root->Open(Root,&File,L"\\EFI\\BOOT\\BOOTAA64.EFI",EFI_FILE_MODE_READ,0)==EFI_NOT_FOUND);
 assert(Root->Open(Root,&File,L"\\EFI\\UniXNU\\unixnu.toml",EFI_FILE_MODE_READ,0)==0);
 assert(Root->Close(Root)==0&&Fs.OpenCount==1);
 N=0;assert(File->GetInfo(File,&Guid,&N,NULL)==EFI_BUFFER_TOO_SMALL&&N<=sizeof Buffer);
 assert(File->GetInfo(File,&Guid,&N,Buffer)==0&&Info->FileSize==sizeof(mMenuConfig)-1&&Info->Attribute==EFI_FILE_READ_ONLY);
 assert(File->GetInfo(File,&Bad,&N,Buffer)==EFI_UNSUPPORTED);
 N=5;assert(File->Read(File,&N,Buffer)==0&&N==5&&memcmp(Buffer,mMenuConfig,5)==0);
 assert(File->GetPosition(File,&Position)==0&&Position==5);
 N=sizeof Buffer;assert(File->Read(File,&N,Buffer)==0&&N==sizeof(mMenuConfig)-6);
 N=sizeof Buffer;assert(File->Read(File,&N,Buffer)==0&&N==0);
 assert(Fs.ReadBytes==sizeof(mMenuConfig)-1);
 assert(File->SetPosition(File,MAX_UINT64)==0);assert(File->SetPosition(File,sizeof(mMenuConfig))==EFI_INVALID_PARAMETER);
 assert(File->SetPosition(File,0)==0);N=1;assert(File->Read(File,&N,NULL)==EFI_INVALID_PARAMETER);
 assert(File->Write(File,&N,Buffer)==EFI_WRITE_PROTECTED);assert(File->SetInfo(File,&Guid,N,Buffer)==EFI_WRITE_PROTECTED);
 assert(File->Open(File,&Other,L"x",EFI_FILE_MODE_READ,0)==EFI_NOT_FOUND);
 assert(File->Delete(File)==EFI_WARN_DELETE_FAILURE&&Fs.OpenCount==0);
 for(I=0;I<8;I++){assert(Fs.Protocol.OpenVolume(&Fs.Protocol,&Handles[I])==0);}
 assert(Fs.Protocol.OpenVolume(&Fs.Protocol,&Other)==EFI_OUT_OF_RESOURCES);
 for(I=0;I<8;I++){assert(Handles[I]->Close(Handles[I])==0);}
 FailAllocation=1;assert(Fs.Protocol.OpenVolume(&Fs.Protocol,&Other)==EFI_OUT_OF_RESOURCES&&Fs.OpenCount==0);
 puts("menu readonly config FS: path/mode/info/partial-read/EOF/seek/close/limits/allocation passed");return 0;
}
