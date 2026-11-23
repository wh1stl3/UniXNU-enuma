/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Diagnostic-only, included in an isolated build of osfmk/ipc/ipc_kmsg.c. */
#include <kern/startup.h>
#include <mach/vm_param.h>

extern int proc_selfpid(void);
void enuma_tx_dump(void);

static TUNABLE(int, enuma_tx_enabled, "enuma-txpeer", 0);
enum { ENUMA_TX_CAP = 8, ENUMA_TX_PORT_BITS = 44 };
typedef unsigned __int128 enuma_tx_word_t;
#define ENUMA_TX_PORT_MASK ((UINT64_C(1) << ENUMA_TX_PORT_BITS) - 1)
#define ENUMA_TX_PORT_PREFIX ((uint64_t)VM_MIN_KERNEL_ADDRESS & ~ENUMA_TX_PORT_MASK)
#define ENUMA_TX_PID_MAX ((1U << (64 - ENUMA_TX_PORT_BITS)) - 1)
_Static_assert(sizeof(uintptr_t) == 8, "64-bit port token");
_Static_assert(((uint64_t)VM_MAX_KERNEL_ADDRESS & ~ENUMA_TX_PORT_MASK) ==
    ENUMA_TX_PORT_PREFIX, "kernel VA window must fit in the port token");
_Static_assert(__atomic_always_lock_free(sizeof(enuma_tx_word_t), 0),
    "ring requires lock-free 128-bit atomics");

struct enuma_tx_ring {
	_Atomic uint64_t head;
	_Atomic enuma_tx_word_t slot[ENUMA_TX_CAP];
};
static struct enuma_tx_ring enuma_tx_rings[2];

/* Called with the destination's existing ip_mq_lock held. */
static __attribute__((noinline)) void
enuma_tx_record(const mach_msg_header_t *hdr, ipc_port_t port, int sender)
{
	struct enuma_tx_ring *ring = &enuma_tx_rings[sender == 34];
	const uint64_t ticket = __c11_atomic_fetch_add(&ring->head, 1, __ATOMIC_RELAXED) + 1;
	const uintptr_t token = (uintptr_t)port;
	if ((token & ~ENUMA_TX_PORT_MASK) != ENUMA_TX_PORT_PREFIX) {
		return; /* Unrepresentable token: leave a hole, never truncate it. */
	}
	const pid_t receiver = ip_active(port) ?
	    ipc_port_get_receiver_task_locked(port, NULL) : -1;
	/* Zero encodes -1/NA; the pinned tree's PID_MAX (99999) fits. */
	const unsigned int rxcode = receiver > 0 && (unsigned int)receiver <= ENUMA_TX_PID_MAX ?
	    (unsigned int)receiver : 0;
	_Atomic enuma_tx_word_t *slot = &ring->slot[(ticket - 1) % ENUMA_TX_CAP];
	const uint32_t tag = (uint32_t)ticket;
	const enuma_tx_word_t next = ((enuma_tx_word_t)tag << 96) |
	    ((enuma_tx_word_t)(uint32_t)hdr->msgh_id << 64) |
	    ((uint64_t)rxcode << ENUMA_TX_PORT_BITS) | (token & ENUMA_TX_PORT_MASK);
	enuma_tx_word_t old = __c11_atomic_load(slot, __ATOMIC_RELAXED);

	/* Do not retry the publication against a different observed slot value. */
	const uint32_t advance = tag - (uint32_t)(old >> 96);
	if (old == 0 || (advance != 0 && advance < UINT32_C(0x80000000))) {
		(void)__c11_atomic_compare_exchange_weak(slot, &old, next,
		    __ATOMIC_RELAXED, __ATOMIC_RELAXED);
	}
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
				printf("enuma-tx: %d  id=NA port=NA rxpid=NA\n", pid);
				continue;
			}
			const unsigned int id = (uint32_t)(row >> 64);
			const unsigned long long port = ((uint64_t)row & ENUMA_TX_PORT_MASK) |
			    ENUMA_TX_PORT_PREFIX;
			const int receiver = (int)((uint64_t)row >> ENUMA_TX_PORT_BITS);
			if (receiver > 0) {
				printf("enuma-tx: %d  id=0x%x port=0x%llx rxpid=%d\n",
				    pid, id, port, receiver);
			} else {
				printf("enuma-tx: %d  id=0x%x port=0x%llx rxpid=NA\n",
				    pid, id, port);
			}
		}
	}
}
