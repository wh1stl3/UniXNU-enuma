// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <assert.h>
#include <setjmp.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <Base.h>
#include <Library/BaseLib.h>
static jmp_buf reset_target;
static unsigned delay_calls, warm_calls, irq_off, irq_restore;
BOOLEAN SaveAndDisableInterrupts(void) { irq_off++; return 1; }
BOOLEAN SetInterruptState(BOOLEAN value) { assert(value == 1); irq_restore++; return 0; }
void MicroSecondDelay(UINTN value) { assert(value == 2000000); delay_calls++; }
void ResetWarm(void) { warm_calls++; longjmp(reset_target, 1); }
void ResetCold(void) { assert(!"unexpected cold error path"); }
void CpuDeadLoop(void) { assert(!"unexpected reset return"); }
#include "../firmware/diagnostics/EnumaRamoopsStageCheckpoint.h"
int main(void) {
  unsigned char *ram = mmap((void *)0xb0000000, 0x201000,
                            PROT_READ | PROT_WRITE,
                            MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED_NOREPLACE, -1, 0);
  assert(ram == (void *)0xb0000000);
  assert(mprotect(ram + 0x200000, 4096, PROT_NONE) == 0);
  EnumaStageCheckpoint(9);
  assert(*(unsigned *)ram == 0 && delay_calls == 0 && irq_off == 0);
  if (setjmp(reset_target) == 0) EnumaStageCheckpoint(10);
  assert(warm_calls == 1 && delay_calls == 1 && irq_off == 1 && irq_restore == 1);
  ENUMA_RAMOOPS_HEADER *h = (void *)ram;
  assert(h->Signature == 0x43474244 && h->Start == 44 && h->Size == 44);
  assert(memcmp(ram + 12, "ENUMA-R017:0123456789abcdef0123456789abcdef\n", 44) == 0);
  assert(munmap(ram, 0x201000) == 0);
  puts("PASS: exact 44-byte canary, stage9 no-op, stage10 append/delay/warm and IRQ ordering; pmsg guard page");
  return 0;
}
