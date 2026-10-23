// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#undef NULL
#include "EnumaScreen.h"

static EFI_GRAPHICS_OUTPUT_BLT_PIXEL scratch[ENUMA_SCREEN_SCRATCH_PIXELS + 1];
static EFI_GRAPHICS_OUTPUT_BLT_PIXEL canvas[480 * 336];
static ENUMA_SCREEN screen;
static unsigned calls, reenter, fail_at;
static EFI_STATUS injected;
static EFI_STATUS EFIAPI blt (EFI_GRAPHICS_OUTPUT_PROTOCOL *gop,
 EFI_GRAPHICS_OUTPUT_BLT_PIXEL *buffer,EFI_GRAPHICS_OUTPUT_BLT_OPERATION op,
 UINTN sx,UINTN sy,UINTN dx,UINTN dy,UINTN w,UINTN h,UINTN delta) {
 (void)gop;calls++;
 assert(op==EfiBltBufferToVideo && sx==0 && sy==0 && dx==screen.Region.X);
 assert(w==480 && h==28 && delta==480*sizeof(*buffer) && dy>=screen.Region.Y && dy-screen.Region.Y+h<=336);
 if(reenter)assert(EnumaScreenLine(&screen,0,"REENTER",7)==EFI_ALREADY_STARTED);
 if(fail_at && calls==fail_at)return EFI_DEVICE_ERROR;
 if(EFI_ERROR(injected))return injected;
 memcpy(canvas+(dy-screen.Region.Y)*480,buffer,w*h*sizeof(*buffer));return EFI_SUCCESS;
}
static EFI_GRAPHICS_OUTPUT_MODE_INFORMATION info;
static EFI_GRAPHICS_OUTPUT_PROTOCOL_MODE mode;
static EFI_GRAPHICS_OUTPUT_PROTOCOL gop;
static ENUMA_SCREEN_REGION region={0,0,480,336};
static void reset(void) {
 memset(&info,0,sizeof(info));memset(&mode,0,sizeof(mode));memset(&gop,0,sizeof(gop));
 memset(&screen,0,sizeof(screen));memset(scratch,0,sizeof(scratch));memset(canvas,0,sizeof(canvas));
 info.HorizontalResolution=1600;info.VerticalResolution=2560;info.PixelFormat=PixelBltOnly;
 mode.Info=&info;mode.SizeOfInfo=sizeof(info);mode.MaxMode=1;
 // No physical framebuffer: BltOnly must work without inventing a base/pitch.
 mode.FrameBufferBase=0;mode.FrameBufferSize=0;gop.Mode=&mode;gop.Blt=blt;
 calls=reenter=fail_at=0;injected=EFI_SUCCESS;
 scratch[ENUMA_SCREEN_SCRATCH_PIXELS].Blue=0x5a;
}
static void init(BOOLEAN enabled) {
 assert(EnumaScreenInit(&screen,&gop,scratch,ENUMA_SCREEN_SCRATCH_PIXELS,region,enabled)==EFI_SUCCESS);
}
int main(int argc,char **argv) {
 reset();init(FALSE);assert(EnumaScreenLine(&screen,0,"X",1)==EFI_ACCESS_DENIED && calls==0);
 reset();assert(EnumaScreenLine(&screen,0,"X",1)==EFI_NOT_READY && calls==0);
 reset();assert(EnumaScreenInit(&screen,&gop,scratch,ENUMA_SCREEN_SCRATCH_PIXELS-1,region,TRUE)==EFI_BUFFER_TOO_SMALL);
 reset();mode.Info=NULL;assert(EnumaScreenInit(&screen,&gop,scratch,ENUMA_SCREEN_SCRATCH_PIXELS,region,TRUE)==EFI_NOT_STARTED);
 reset();mode.SizeOfInfo=0;assert(EnumaScreenInit(&screen,&gop,scratch,ENUMA_SCREEN_SCRATCH_PIXELS,region,TRUE)==EFI_COMPROMISED_DATA);
 reset();info.PixelFormat=(EFI_GRAPHICS_PIXEL_FORMAT)MAX_UINT32;
 assert(EnumaScreenInit(&screen,&gop,scratch,ENUMA_SCREEN_SCRATCH_PIXELS,region,TRUE)==EFI_COMPROMISED_DATA);
 reset();ENUMA_SCREEN_REGION bad={MAX_UINT32,0,480,336};assert(EnumaScreenInit(&screen,&gop,scratch,ENUMA_SCREEN_SCRATCH_PIXELS,bad,TRUE)==EFI_BAD_BUFFER_SIZE);
 reset();bad=region;bad.Height=27;assert(EnumaScreenInit(&screen,&gop,scratch,ENUMA_SCREEN_SCRATCH_PIXELS,bad,TRUE)==EFI_BAD_BUFFER_SIZE);
 reset();bad=region;bad.Width=492;assert(EnumaScreenInit(&screen,&gop,scratch,ENUMA_SCREEN_SCRATCH_PIXELS,bad,TRUE)==EFI_BAD_BUFFER_SIZE);
 reset();init(TRUE);assert(EnumaScreenLine(&screen,12,"X",1)==EFI_BAD_BUFFER_SIZE && calls==0);
 assert(EnumaScreenLine(&screen,0,NULL,1)==EFI_INVALID_PARAMETER && calls==0);
 assert(EnumaScreenLine(&screen,0,"X",41)==EFI_BAD_BUFFER_SIZE && calls==0);
 assert(EnumaScreenHex(&screen,0,"X",24,0)==EFI_BAD_BUFFER_SIZE && calls==0);
 reenter=1;assert(EnumaScreenLine(&screen,0,"A",1)==EFI_SUCCESS && calls==1);reenter=0;
 // Independent A bitmap in the font's logical 5x12 grid, scaled twofold.
 const unsigned rows[12]={0,4,10,17,17,17,31,17,17,17,0,0};
 for(unsigned y=0;y<28;y++)for(unsigned x=0;x<480;x++) {
  unsigned on=x<10 && y<24 && (rows[y/2] & (1u<<(x/2)));
  assert(scratch[y*480+x].Blue==(on?255:0));
 }
 EFI_GRAPHICS_OUTPUT_BLT_PIXEL question[ENUMA_SCREEN_SCRATCH_PIXELS];
 assert(EnumaScreenLine(&screen,0,"?",1)==EFI_SUCCESS);memcpy(question,scratch,sizeof(question));
 assert(EnumaScreenLine(&screen,0,"\001",1)==EFI_SUCCESS && memcmp(question,scratch,sizeof(question))==0);
 assert(EnumaScreenHex(&screen,0,"STATUS",6,((UINT64)1<<63)|7)==EFI_SUCCESS);
 memcpy(question,scratch,sizeof(question));
 assert(EnumaScreenLine(&screen,0,"STATUS 8000000000000007",23)==EFI_SUCCESS && memcmp(question,scratch,sizeof(question))==0);
 assert(EnumaScreenLine(&screen,11,NULL,0)==EFI_SUCCESS);
 assert(scratch[ENUMA_SCREEN_SCRATCH_PIXELS].Blue==0x5a);
 reset();init(TRUE);injected=EFI_DEVICE_ERROR;
 assert(EnumaScreenLine(&screen,0,"X",1)==EFI_DEVICE_ERROR && calls==1);
 injected=EFI_SUCCESS;assert(EnumaScreenLine(&screen,0,"X",1)==EFI_DEVICE_ERROR && calls==1);
 reset();init(TRUE);info.HorizontalResolution++;
 assert(EnumaScreenLine(&screen,0,"X",1)==EFI_MEDIA_CHANGED && calls==0);
 reset();init(TRUE);gop.Mode=NULL;
 assert(EnumaScreenLine(&screen,0,"X",1)==EFI_MEDIA_CHANGED && calls==0);
 reset();init(TRUE);gop.Blt=NULL;
 assert(EnumaScreenLine(&screen,0,"X",1)==EFI_MEDIA_CHANGED && calls==0);
 reset();init(TRUE);mode.MaxMode=0;
 assert(EnumaScreenLine(&screen,0,"X",1)==EFI_MEDIA_CHANGED && calls==0);
 reset();ENUMA_SCREEN_REGION edge={1120,2224,480,336};
 assert(EnumaScreenInit(&screen,&gop,scratch,ENUMA_SCREEN_SCRATCH_PIXELS,edge,TRUE)==EFI_SUCCESS);
 assert(EnumaScreenLine(&screen,11,"EDGE",4)==EFI_SUCCESS && calls==1);
 ENUMA_SCREEN_SNAPSHOT snap={"HOST PREVIEW / SYNTHETIC",24,0x20,EFI_DEVICE_ERROR,1600,2560,1600,1,0x10000000,16384000,0,0};
 reset();init(TRUE);fail_at=3;
 assert(EnumaScreenPage(&screen,&snap)==EFI_DEVICE_ERROR && calls==3);
 reset();init(TRUE);
 assert(EnumaScreenPage(&screen,&snap)==EFI_SUCCESS && calls==12);
 if(argc==2) {
  FILE *out=fopen(argv[1],"wb");assert(out);
  assert(fwrite(canvas,sizeof(*canvas),480*336,out)==480*336);assert(fclose(out)==0);
 }
 return 0;
}
