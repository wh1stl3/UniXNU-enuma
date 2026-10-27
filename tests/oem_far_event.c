// A real RestoreTPL notification can replace the ring tail before the old observer.
#ifndef ENUMA_OEM_RAM_EVENT
#define ENUMA_OEM_RAM_EVENT 1
#endif
#define main FarRegression
#include "oem_far_chain.c"
#undef main
static unsigned Inject;
#if ENUMA_OEM_RAM_EVENT
static VOID CheckedRecord(ENUMA_SERVICE_TRACE *Trace,CONST ENUMA_SERVICE_EVENT *E){
  assert(Level==TPL_HIGH_LEVEL);
  OemProgressRecord(Trace,E);
}
#endif
static VOID EFIAPI NotifyRestore(EFI_TPL L){
  Restore(L);
  if(Inject&&L==TPL_APPLICATION&&T.Log.NextCall==7){
    Inject=0;
    Level=TPL_CALLBACK; // CoreRestoreTpl dispatches pending notification TPLs first.
    assert(T.Boot.AllocatePool(EfiBootServicesData,8,NULL)==EFI_SUCCESS);
    Level=L;
  }
}
int main(void){
  Setup();Boot.RestoreTPL=NotifyRestore;Inject=1;
#if ENUMA_OEM_RAM_EVENT
  T.Recorded=CheckedRecord;
#endif
  int Stopped=setjmp(Jump);
  if(!Stopped){assert(EnumaTraceLocateProtocolAt(0x4608,&Main,NULL,NULL)==EFI_SUCCESS);}
#if ENUMA_OEM_RAM_EVENT
  assert(!Stopped&&MainCalls==1&&!Inject&&!Phases);
  assert((mOemProgress.FarFlags&0x100c)==0x100c);
  assert(!T.BeforeForward&&!T.AfterForward&&T.Recorded);
  for(unsigned I=0;I<200;I++){assert(T.Boot.AllocatePool(EfiBootServicesData,8,NULL)==0);}
  assert(T.Log.Dropped>0&&(mOemProgress.FarFlags&0x100c)==0x100c&&!Phases);
  OemProgressReturned(EFI_ABORTED);OemProgressFarFinish(FALSE,FALSE,FALSE);
  assert(Phases==1);
  assert(FarRegression()==0);
  puts("PASS: nested RestoreTPL notification does not replace the observed event or abort original forwarding");
#else
  assert(Stopped==1&&MainCalls==0&&!Inject&&!Phases);
  puts("REPRODUCED: v7 aborts before forwarding when RestoreTPL runs a nested traced notification");
#endif
  return 0;
}
