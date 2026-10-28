#include "EnumaOemExceptionView.h"
#include <assert.h>
#include <string.h>
static EFI_SYSTEM_TABLE St;
static EFI_CONFIGURATION_TABLE Ct[2];
static EFI_DEBUG_IMAGE_INFO_TABLE_HEADER H;
static EFI_DEBUG_IMAGE_INFO Entries[2];
static EFI_DEBUG_IMAGE_INFO_NORMAL Normal[2];
static EFI_LOADED_IMAGE_PROTOCOL L[2];
static UINT8 Path[24];
static unsigned Calls,Fail,Change;
static int span(UINTN A,UINTN N,const void *P,UINTN Bytes){return A>=(UINTN)P&&A-(UINTN)P<=Bytes&&N<=Bytes-(A-(UINTN)P);}
static BOOLEAN read_meta(VOID *C,UINTN A,VOID *D,UINTN N){
 (void)C;Calls++;if(Calls==Fail){return FALSE;}
 if(!(span(A,N,&St,sizeof(St))||span(A,N,Ct,sizeof(Ct))||span(A,N,&H,sizeof(H))||span(A,N,Entries,sizeof(Entries))||span(A,N,Normal,sizeof(Normal))||span(A,N,L,sizeof(L))||span(A,N,Path,sizeof(Path)))){return FALSE;}
 memcpy(D,(void *)A,N);if(Change&&A==(UINTN)&H){H.UpdateStatus^=2;}return TRUE;
}
static void setup(void){
 memset(&St,0,sizeof(St));memset(Ct,0,sizeof(Ct));memset(&H,0,sizeof(H));memset(L,0,sizeof(L));
 St.Hdr.Signature=EFI_SYSTEM_TABLE_SIGNATURE;St.Hdr.HeaderSize=sizeof(St);St.NumberOfTableEntries=1;St.ConfigurationTable=Ct;
 Ct[0].VendorGuid=(EFI_GUID)EFI_DEBUG_IMAGE_INFO_TABLE_GUID;Ct[0].VendorTable=&H;
 H.TableSize=1;H.EfiDebugImageInfoTable=Entries;
 for(unsigned i=0;i<2;i++){Entries[i].NormalImage=&Normal[i];Normal[i].ImageInfoType=1;Normal[i].LoadedImageProtocolInstance=&L[i];L[i].ImageBase=(void *)0x100000;L[i].ImageSize=0x10000;L[i].FilePath=(void *)Path;}
 memset(Path,0,sizeof(Path));Path[0]=4;Path[1]=6;Path[2]=20;for(unsigned i=0;i<16;i++){Path[i+4]=(UINT8)i;}Path[20]=0x7f;Path[21]=0xff;Path[22]=4;
 Calls=Fail=Change=0;
}
static ENUMA_EXCEPTION_RECORD record(void){
 EFI_SYSTEM_CONTEXT_AARCH64 C={0};ENUMA_EXCEPTION_RECORD R;
 C.ELR=0x100120;C.ESR=0x96000004;C.FAR=0xfeed000000000abcULL;C.LR=0x100100;C.SPSR=0x3c5;
 assert(ExSnapshot(&R,0,&C,0x1234));assert(R.Pc==C.ELR&&R.Esr==C.ESR&&R.Far==C.FAR&&R.Lr==C.LR&&R.Spsr==C.SPSR&&R.Session==0x1234);
 assert(!ExSnapshot(NULL,0,&C,1)&&!ExSnapshot(&R,0,NULL,1)&&!ExSnapshot(&R,4,&C,1)&&!ExSnapshot(&R,0,&C,0));
 return R;
}
int main(void){
 ENUMA_EXCEPTION_RECORD R;setup();R=record();ExFindOwner(&R,(UINTN)&St,read_meta,NULL);
 assert(R.Owner==1&&R.Base==0x100000&&R.Rva==0x120&&R.Bytes==0x10000&&R.GuidValid);
 assert(!memcmp(&R.Guid,Path+4,16));unsigned complete=Calls;
 for(unsigned i=1;i<=complete;i++){setup();R=record();Fail=i;ExFindOwner(&R,(UINTN)&St,read_meta,NULL);assert(R.Owner!=1||!R.GuidValid);assert(R.Pc==0x100120&&R.Far==0xfeed000000000abcULL);}
 setup();R=record();H.UpdateStatus=1;ExFindOwner(&R,(UINTN)&St,read_meta,NULL);assert(R.Owner==4&&!R.Base);
 setup();R=record();Change=1;ExFindOwner(&R,(UINTN)&St,read_meta,NULL);assert(R.Owner==5&&!R.Base);
 setup();R=record();H.TableSize=129;ExFindOwner(&R,(UINTN)&St,read_meta,NULL);assert(R.Owner==6);
 setup();R=record();St.NumberOfTableEntries=65;ExFindOwner(&R,(UINTN)&St,read_meta,NULL);assert(R.Owner==5);
 setup();R=record();H.TableSize=2;ExFindOwner(&R,(UINTN)&St,read_meta,NULL);assert(R.Owner==3&&!R.Base&&!R.GuidValid);
 setup();R=record();R.Pc=0x110000;ExFindOwner(&R,(UINTN)&St,read_meta,NULL);assert(R.Owner==2);
 setup();R=record();L[0].ImageBase=(void *)(UINTN)(MAX_UINTN-0x100);ExFindOwner(&R,(UINTN)&St,read_meta,NULL);assert(R.Owner==5);
 setup();R=record();Entries[0].NormalImage=NULL;ExFindOwner(&R,(UINTN)&St,read_meta,NULL);assert(R.Owner==2);
 setup();R=record();Path[22]=3;ExFindOwner(&R,(UINTN)&St,read_meta,NULL);assert(R.Owner==1&&!R.GuidValid);
 setup();R=record();Path[0]=0;Path[1]=0;Path[2]=4;ExFindOwner(&R,(UINTN)&St,read_meta,NULL);assert(R.Owner==1&&!R.GuidValid);
 setup();R=record();St.NumberOfTableEntries=2;Ct[1]=Ct[0];ExFindOwner(&R,(UINTN)&St,read_meta,NULL);assert(R.Owner==5);
 setup();R=record();H.EfiDebugImageInfoTable=(void *)(UINTN)(MAX_UINTN-1);ExFindOwner(&R,(UINTN)&St,read_meta,NULL);assert(R.Owner==5);
 return 0;
}
