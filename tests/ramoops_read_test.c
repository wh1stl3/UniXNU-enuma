// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <setjmp.h>
#include <stdio.h>
#include <sys/mman.h>
#include <Base.h>
static jmp_buf reset_target;
static unsigned delay_calls, cold_calls;
void MicroSecondDelay(UINTN value) { assert(value == 2000000); delay_calls++; }
void ResetCold(void) { cold_calls++; longjmp(reset_target, 1); }
void CpuDeadLoop(void) { assert(!"unexpected reset return"); }
#include "../firmware/diagnostics/EnumaRamoopsReadCheckpoint.h"
int main(void) {
  unsigned *ram = mmap((void *)0xb0000000, 4096, PROT_NONE,
                      MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED_NOREPLACE, -1, 0);
  assert(ram == (void *)0xb0000000);
  EnumaStageCheckpoint(9); // no read is allowed at stage9
  assert(!cold_calls && !delay_calls);
  assert(mprotect(ram,4096,PROT_READ|PROT_WRITE)==0);
  ram[0]=0x43474244;ram[1]=7;ram[2]=12;
  assert(mprotect(ram,4096,PROT_READ)==0); // any header store faults
  if (setjmp(reset_target)==0) EnumaStageCheckpoint(10);
  assert(cold_calls==1 && delay_calls==1);
  assert(ram[0]==0x43474244 && ram[1]==7 && ram[2]==12);
  assert(munmap(ram,4096)==0);
  puts("PASS: stage9 touches no protected console; stage10 accepts read-only page and preserves header before cold reset");
}
