// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "simplefb_test_uefi.h"
UINT32 FixturePcd[3]={1600,2560,32};
int DisplayDevicePath,gEfiDevicePathProtocolGuid,gEfiGraphicsOutputProtocolGuid;
static unsigned alloc_calls,live,fail_alloc,lookup_calls,configure_calls,blt_calls;
static EFI_STATUS first_lookup,second_lookup,install_status,first_configure,second_configure;
static UINT64 fixture_address=0x10000000,fixture_length=0x2400000;
static EFI_STATUS mock_alloc(unsigned type,UINTN size,VOID **p) {
 (void)type;alloc_calls++;*p=NULL;
 if(fail_alloc==alloc_calls)return EFI_OUT_OF_RESOURCES;
 *p=calloc(1,size);assert(*p);live++;return EFI_SUCCESS;
}
static EFI_STATUS mock_free(VOID *p){assert(p && live);free(p);live--;return EFI_SUCCESS;}
VOID *AllocatePool(UINTN n){VOID *p=NULL;mock_alloc(4,n,&p);return p;}
VOID FreePool(VOID *p){mock_free(p);}
static EFI_TPL raise_tpl(EFI_TPL t){(void)t;return 4;}
static VOID restore_tpl(EFI_TPL t){(void)t;}
static EFI_STATUS install(EFI_HANDLE *h,...){(void)h;return install_status;}
static BOOT_SERVICES services={mock_alloc,mock_free,raise_tpl,restore_tpl,install};
BOOT_SERVICES *gBS=&services;
EFI_STATUS LocateMemoryRegionByName(const char *name,EFI_MEMORY_REGION_DESCRIPTOR *p){
 lookup_calls++;assert(strcmp(name,lookup_calls==1?"Display Reserved":"Display_Reserved")==0);
 EFI_STATUS status=lookup_calls==1?first_lookup:second_lookup;
 if(!EFI_ERROR(status)){p->Address=fixture_address;p->Length=fixture_length;}return status;
}
EFI_STATUS FrameBufferBltConfigure(VOID *base,EFI_GRAPHICS_OUTPUT_MODE_INFORMATION *info,FRAME_BUFFER_CONFIGURE *config,UINTN *size){
 (void)base;(void)info;configure_calls++;
 if(!config){*size=128;return first_configure;}assert(*size==128);return second_configure;
}
EFI_STATUS FrameBufferBlt(FRAME_BUFFER_CONFIGURE *c,EFI_GRAPHICS_OUTPUT_BLT_PIXEL *p,EFI_GRAPHICS_OUTPUT_BLT_OPERATION op,UINTN a,UINTN b,UINTN d,UINTN e,UINTN f,UINTN g,UINTN h){
 (void)c;(void)p;(void)op;(void)a;(void)b;(void)d;(void)e;(void)f;(void)g;(void)h;blt_calls++;return EFI_SUCCESS;
}
#include SIMPLEFB_SOURCE
static void reset_fixture(void){
 FreeMemoryBuffers();assert(live==0);alloc_calls=fail_alloc=lookup_calls=configure_calls=blt_calls=0;
 first_lookup=second_lookup=install_status=second_configure=EFI_SUCCESS;first_configure=EFI_BUFFER_TOO_SMALL;
 fixture_address=0x10000000;fixture_length=0x2400000;FixturePcd[0]=1600;FixturePcd[1]=2560;FixturePcd[2]=32;
}
int main(void){
 EFI_PHYSICAL_ADDRESS base;UINT32 w,h,d;UINTN size;EFI_GRAPHICS_OUTPUT_MODE_INFORMATION *info;
 reset_fixture();assert(GetFrameBufferInfos(NULL,&w,&h,&d)==EFI_INVALID_PARAMETER && lookup_calls==0);
 reset_fixture();assert(GetFrameBufferInfos(&base,&w,&h,&d)==0 && lookup_calls==1 && base==fixture_address);
 reset_fixture();first_lookup=EFI_NOT_FOUND;assert(GetFrameBufferInfos(&base,&w,&h,&d)==0 && lookup_calls==2);
 reset_fixture();first_lookup=EFI_DEVICE_ERROR;assert(GetFrameBufferInfos(&base,&w,&h,&d)==EFI_DEVICE_ERROR && lookup_calls==1 && base==0);
 reset_fixture();first_lookup=second_lookup=EFI_NOT_FOUND;assert(GetFrameBufferInfos(&base,&w,&h,&d)==EFI_NOT_FOUND && base==0);
 reset_fixture();fixture_address=0;assert(GetFrameBufferInfos(&base,&w,&h,&d)==EFI_NOT_FOUND);
 reset_fixture();fixture_length=0;assert(GetFrameBufferInfos(&base,&w,&h,&d)==EFI_NOT_FOUND);
 reset_fixture();FixturePcd[0]=1;assert(GetFrameBufferInfos(&base,&w,&h,&d)==EFI_UNSUPPORTED);
 reset_fixture();FixturePcd[2]=0;assert(GetFrameBufferInfos(&base,&w,&h,&d)==EFI_UNSUPPORTED);
 for(unsigned failure=1;failure<=3;failure++){
  reset_fixture();fail_alloc=failure;assert(RegisterFrameBuffer(NULL,NULL)==EFI_OUT_OF_RESOURCES);assert(live==0 && !mFrameBuffer.Mode && !FrameBufferConfiguration);
 }
 reset_fixture();install_status=EFI_DEVICE_ERROR;assert(RegisterFrameBuffer(NULL,NULL)==EFI_DEVICE_ERROR && live==0);
 reset_fixture();first_configure=EFI_SUCCESS;assert(RegisterFrameBuffer(NULL,NULL)==EFI_DEVICE_ERROR && live==0);
 reset_fixture();second_configure=EFI_DEVICE_ERROR;assert(RegisterFrameBuffer(NULL,NULL)==EFI_DEVICE_ERROR && live==0);
 reset_fixture();assert(RegisterFrameBuffer(NULL,NULL)==0 && live==3);unsigned allocations=alloc_calls;
 assert(RegisterFrameBuffer(NULL,NULL)==EFI_ALREADY_STARTED && alloc_calls==allocations);
 assert(FrameBufferQueryMode(NULL,0,&size,&info)==EFI_INVALID_PARAMETER);
 assert(FrameBufferQueryMode(&mFrameBuffer,1,&size,&info)==EFI_INVALID_PARAMETER && info==NULL && size==0);
 assert(FrameBufferQueryMode(&mFrameBuffer,0,NULL,&info)==EFI_INVALID_PARAMETER);
 mFrameBuffer.Mode->Info->PixelInformation.RedMask=0x1234;
 assert(FrameBufferQueryMode(&mFrameBuffer,0,&size,&info)==0 && info->PixelInformation.RedMask==0x1234);FreePool(info);
 fail_alloc=alloc_calls+1;assert(FrameBufferQueryMode(&mFrameBuffer,0,&size,&info)==EFI_OUT_OF_RESOURCES && info==NULL && size==0);fail_alloc=0;
 assert(FrameBufferSetMode(&mFrameBuffer,0)==0 && FrameBufferSetMode(&mFrameBuffer,1)==EFI_UNSUPPORTED);
 assert(SetFrameBufferModeDetails(0x10000000,1600,2560,32)==0 && mFrameBuffer.Mode->FrameBufferSize==16384000);
 assert(SetFrameBufferModeDetails(0,UINT32_MAX,UINT32_MAX,32)==EFI_BAD_BUFFER_SIZE);
 assert(SetFrameBufferModeDetails(UINT64_MAX-10,640,480,32)==EFI_BAD_BUFFER_SIZE);
 assert(FrameBufferGopBlt(&mFrameBuffer,NULL,0,0,0,0,0,1,1,0)==EFI_UNSUPPORTED && blt_calls==0);
 FreeMemoryBuffers();FreeMemoryBuffers();assert(live==0 && !mFrameBuffer.Mode && !FrameBufferConfiguration);
 assert(FrameBufferQueryMode(&mFrameBuffer,0,&size,&info)==EFI_NOT_STARTED);
 assert(FrameBufferSetMode(&mFrameBuffer,0)==EFI_NOT_STARTED);
 return 0;
}
