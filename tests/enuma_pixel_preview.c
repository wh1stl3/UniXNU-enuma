#include <assert.h>
#include <stdio.h>
#undef NULL
#include "EnumaPixelPreview.h"
static ENUMA_SCANOUT_DESCRIPTOR fixture;
static UINT32 pixels[ENUMA_PIXEL_COUNT], scratch[ENUMA_PIXEL_COUNT];
static unsigned reads,writes,syncs,waits,snapshots,fail_snapshot,change_snapshot,corrupt_verify;
static EFI_STATUS wait_status;
static UINT32 original(unsigned i){return 0x12345678U ^ (i*0x01010101U);}
static unsigned index_at(UINTN a){UINT64 off;unsigned row,col;assert(a>=fixture.Start&&a+4<=fixture.End&&a%4==0);off=a-fixture.Start;row=off/fixture.Pitch;col=(off%fixture.Pitch)/4;assert(row<8&&col<128&&off%4==0);return row*128+col;}
static EFI_STATUS snapshot(ENUMA_SCANOUT_DESCRIPTOR *d){snapshots++;if(snapshots==fail_snapshot)return EFI_DEVICE_ERROR;*d=fixture;if(snapshots==2&&change_snapshot)d->Source+=0x2000;return EFI_SUCCESS;}
static UINT32 read_pixel(UINTN a){unsigned i=index_at(a);UINT32 v=pixels[i];reads++;if(corrupt_verify&&reads>1024&&i==0)v^=1;return v;}
static VOID write_pixel(UINTN a,UINT32 v){unsigned i=index_at(a);writes++;assert(writes<=2048);pixels[i]=v;}
static VOID sync_pixel(UINTN a,UINTN n){unsigned i=index_at(a),j;assert(n==512&&i%128==0);syncs++;assert(syncs<=24);for(j=0;j<128;j++)assert(pixels[i+j]==(syncs>8&&syncs<=16?0xffffffffU:original(i+j)));}
static EFI_STATUS wait_pixel(UINTN us){unsigned i;waits++;assert(us==500000&&waits==1&&writes==1024&&syncs==16);for(i=0;i<1024;i++)assert(pixels[i]==0xffffffffU);return wait_status;}
static void reset(void){unsigned i;assert(EnumaScanoutDecodeDescriptor(0x9c000000,(2560U<<16)|1600,6400,0,0x63f,0,&fixture)==EFI_SUCCESS);fixture.Source=0xae05000;reads=writes=syncs=waits=snapshots=fail_snapshot=change_snapshot=corrupt_verify=0;wait_status=EFI_SUCCESS;for(i=0;i<1024;i++)pixels[i]=original(i);}
static EFI_STATUS run(void){return EnumaPixelPreview(snapshot,read_pixel,write_pixel,sync_pixel,wait_pixel,scratch,1024);}
static void restored(void){unsigned i;assert(reads==2048&&writes==2048&&syncs==24&&waits==1&&snapshots==2);for(i=0;i<1024;i++)assert(pixels[i]==original(i));}
int main(void){unsigned i;
 reset();assert(run()==EFI_SUCCESS);restored();
 reset();wait_status=EFI_ABORTED;assert(run()==EFI_ABORTED);restored();
 reset();corrupt_verify=1;assert(run()==EFI_DEVICE_ERROR);restored();
 reset();fail_snapshot=1;assert(run()==EFI_DEVICE_ERROR&&reads==0&&writes==0);
 reset();fail_snapshot=2;assert(run()==EFI_DEVICE_ERROR&&reads==1024&&writes==0&&waits==0);
 reset();change_snapshot=1;assert(run()==EFI_MEDIA_CHANGED&&reads==1024&&writes==0&&syncs==8);
 reset();assert(EnumaPixelPreview(NULL,read_pixel,write_pixel,sync_pixel,wait_pixel,scratch,1024)==EFI_INVALID_PARAMETER);
 assert(EnumaPixelPreview(snapshot,NULL,write_pixel,sync_pixel,wait_pixel,scratch,1024)==EFI_INVALID_PARAMETER);
 assert(EnumaPixelPreview(snapshot,read_pixel,NULL,sync_pixel,wait_pixel,scratch,1024)==EFI_INVALID_PARAMETER);
 assert(EnumaPixelPreview(snapshot,read_pixel,write_pixel,NULL,wait_pixel,scratch,1024)==EFI_INVALID_PARAMETER);
 assert(EnumaPixelPreview(snapshot,read_pixel,write_pixel,sync_pixel,NULL,scratch,1024)==EFI_INVALID_PARAMETER);
 assert(EnumaPixelPreview(snapshot,read_pixel,write_pixel,sync_pixel,wait_pixel,NULL,1024)==EFI_INVALID_PARAMETER);
 assert(EnumaPixelPreview(snapshot,read_pixel,write_pixel,sync_pixel,wait_pixel,scratch,1023)==EFI_INVALID_PARAMETER);
 assert(EnumaPixelPreview(snapshot,read_pixel,write_pixel,sync_pixel,wait_pixel,(UINT32 *)(UINTN)0x9c000000,1024)==EFI_INVALID_PARAMETER);
 assert(EnumaPixelPreview(snapshot,read_pixel,write_pixel,sync_pixel,wait_pixel,(UINT32 *)(MAX_UINTN-3),1024)==EFI_INVALID_PARAMETER);assert(snapshots==0&&writes==0);
 for(i=0;i<16;i++){reset();switch(i){case 0:fixture.Base=0x9bffffff;break;case 1:fixture.Base=0x9e300000;break;case 2:fixture.Base++;break;case 3:fixture.Width=127;break;case 4:fixture.Height=7;break;case 5:fixture.Pitch=4;break;case 6:fixture.Pitch++;break;case 7:fixture.Width=65536;break;case 8:fixture.Height=65536;break;case 9:fixture.X=65536;break;case 10:fixture.Y=65536;break;case 11:fixture.Start+=4;break;case 12:fixture.End-=4;break;case 13:fixture.End=0x9e300004ULL;break;case 14:fixture.Base=MAX_UINT64;break;case 15:fixture.Pitch=0xffffffffU;break;}assert(run()==EFI_UNSUPPORTED&&reads==0&&writes==0);}
 reset();assert(EnumaScanoutDecodeDescriptor(0x9e2ff000,(8U<<16)|128,512,0,0x63f,0,&fixture)==EFI_SUCCESS);assert(run()==EFI_SUCCESS);restored();
 reset();assert(EnumaScanoutDecodeDescriptor(0x9c000000,(16U<<16)|128,1024,(8U<<16)|16,0x63f,0,&fixture)==EFI_SUCCESS);assert(run()==EFI_SUCCESS);restored();
 puts("PASS: 33 pixel-preview transaction scenarios; no physical device or framebuffer access");
}
