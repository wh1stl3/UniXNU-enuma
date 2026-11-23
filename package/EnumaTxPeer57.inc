/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Diagnostic-only, included in an isolated build of osfmk/ipc/ipc_kmsg.c. */
#include <kern/startup.h>

extern int proc_selfpid(void);
void enuma_tx_dump(void);

static TUNABLE(int, enuma_tx_enabled, "enuma-txpeer", 0);
enum { ENUMA_TX_CAP = 8 };
typedef unsigned __int128 enuma_tx_word_t;
_Static_assert(sizeof(uintptr_t) == 8, "64-bit port token");
_Static_assert(__atomic_always_lock_free(sizeof(enuma_tx_word_t), 0),
    "ring requires lock-free 128-bit atomics");

struct enuma_tx_ring {
	_Atomic uint64_t head;
	_Atomic enuma_tx_word_t slot[ENUMA_TX_CAP];
};
static struct enuma_tx_ring enuma_tx_rings[2];

static __attribute__((noinline)) void
enuma_tx_record(const mach_msg_header_t *hdr, ipc_port_t port)
{
	const int pid = proc_selfpid();
	if (pid != 5 && pid != 34) {
		return;
	}
	struct enuma_tx_ring *ring = &enuma_tx_rings[pid == 34];
	const uint64_t ticket = __c11_atomic_fetch_add(&ring->head, 1, __ATOMIC_RELAXED) + 1;
	_Atomic enuma_tx_word_t *slot = &ring->slot[(ticket - 1) % ENUMA_TX_CAP];
	const uint32_t tag = (uint32_t)ticket;
	const enuma_tx_word_t next = ((enuma_tx_word_t)tag << 96) |
	    ((enuma_tx_word_t)(uint32_t)hdr->msgh_id << 64) | (uintptr_t)port;
	enuma_tx_word_t old = __c11_atomic_load(slot, __ATOMIC_RELAXED);

	/* Publish the tag and both fields together. A delayed older writer
	 * must not overwrite a newer reservation already published here. */
	do {
		const uint32_t advance = tag - (uint32_t)(old >> 96);
		if (old != 0 && (advance == 0 || advance >= UINT32_C(0x80000000))) {
			return;
		}
	} while (!__c11_atomic_compare_exchange_strong(slot, &old, next,
	    __ATOMIC_RELAXED, __ATOMIC_RELAXED));
}

void
enuma_tx_dump(void)
{
	if (enuma_tx_enabled != 1) {
		return;
	}
	for (unsigned int i = 0; i < 2; ++i) {
		const int pid = i == 0 ? 5 : 34;
		struct enuma_tx_ring *ring = &enuma_tx_rings[i];
		const uint64_t head = __c11_atomic_load(&ring->head, __ATOMIC_RELAXED);
		for (uint64_t n = 0; n < ENUMA_TX_CAP && n < head; ++n) {
			const uint64_t ticket = head - n;
			const enuma_tx_word_t row = __c11_atomic_load(
				&ring->slot[(ticket - 1) % ENUMA_TX_CAP], __ATOMIC_RELAXED);
			if (row == 0 || (uint32_t)(row >> 96) != (uint32_t)ticket) {
				printf("enuma-tx: %d  id=NA port=NA owner=NA\n", pid);
				continue;
			}
			printf("enuma-tx: %d  id=0x%x port=0x%llx owner=NA\n",
			    pid, (unsigned int)(uint32_t)(row >> 64), (unsigned long long)row);
		}
	}
}
