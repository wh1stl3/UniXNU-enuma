/* SPDX-License-Identifier: BSD-2-Clause-Patent */
#include "open.h"

/* Single open writer. Published fields never change; read only published parts. */
static struct enuma_open_snapshot enuma_open_slot;
static unsigned enuma_open_claimed, enuma_method_claimed;
static uint64_t enuma_open_registry;

static bool
enuma_open_current(struct enuma_bp_identity *who)
{
	proc_t p = current_proc();
	if (p == PROC_NULL || proc_task(p) != current_task())
		return false;
	struct proc_ident id = proc_ident(p);
	*who = (struct enuma_bp_identity){id.p_uniqueid, id.p_pid, id.p_idversion};
	return true;
}

/* Caller holds the pre-existing proc spin lock. No reference or name lookups. */
static uint32_t
enuma_open_generation(struct enuma_bp_identity who)
{
	const unsigned i = ENUMA_BP_BACKBOARDD - 1;
	const struct enuma_bp_event *exec = &enuma_bp_events.slot[i].exec;
	return exec->count != UINT32_MAX && !enuma_bp_matching_exit[i] &&
	    enuma_bp_same_identity(who, exec->latest) ? exec->count : 0;
}

__attribute__((noinline)) bool
enuma_legacy_open_claim(uint32_t type)
{
	struct enuma_bp_identity who;
	if (__atomic_load_n(&enuma_open_claimed, __ATOMIC_RELAXED) ||
	    !enuma_open_current(&who) || !lck_spin_try_lock(&enuma_bp_proc_lock))
		return false;
	const uint32_t generation = enuma_open_generation(who);
	unsigned empty = 0;
	const bool claimed = generation && __atomic_compare_exchange_n(&enuma_open_claimed,
	    &empty, 1, false, __ATOMIC_RELAXED, __ATOMIC_RELAXED);
	if (claimed) {
		enuma_open_slot.attempt.uid = who.uniqueid;
		enuma_open_slot.attempt.pid = who.pid;
		enuma_open_slot.attempt.version = who.idversion;
		enuma_open_slot.attempt.generation = generation;
		enuma_open_slot.attempt.type = type;
		__atomic_store_n(&enuma_open_slot.phase, ENUMA_OPEN_ATTEMPT, __ATOMIC_RELEASE);
	}
	lck_spin_unlock(&enuma_bp_proc_lock);
	return claimed;
}

__attribute__((noinline)) void
enuma_legacy_open_raw(int result, const char *name)
{
	enuma_open_slot.raw.result = result;
	if (name) {
		char *dst = enuma_open_slot.raw.client_class;
		unsigned i = 0;
		for (; i + 1 < sizeof(enuma_open_slot.raw.client_class) && name[i]; ++i)
			dst[i] = name[i];
		dst[i] = 0;
		enuma_open_slot.raw.truncated = name[i] != 0;
	}
	__atomic_store_n(&enuma_open_slot.phase, ENUMA_OPEN_RAW, __ATOMIC_RELEASE);
}

__attribute__((noinline)) void
enuma_legacy_open_final(int err, int result, bool client, uint64_t registry)
{
	enuma_open_slot.final.err = err;
	enuma_open_slot.final.result = result;
	enuma_open_slot.final.client = client;
	enuma_open_registry = !err && !result && client ? registry : 0;
	__atomic_store_n(&enuma_open_slot.phase, ENUMA_OPEN_FINAL, __ATOMIC_RELEASE);
}

__attribute__((noinline)) uint64_t
enuma_legacy_method_key(void)
{
	if (__atomic_load_n(&enuma_open_slot.phase, __ATOMIC_ACQUIRE) != ENUMA_OPEN_FINAL ||
	    __atomic_load_n(&enuma_method_claimed, __ATOMIC_RELAXED))
		return 0;
	return enuma_open_registry;
}

__attribute__((noinline)) void
enuma_legacy_method_note(uint32_t selector, unsigned kind)
{
	struct enuma_bp_identity who;
	if (!enuma_legacy_method_key() || !enuma_open_current(&who) ||
	    !lck_spin_try_lock(&enuma_bp_proc_lock))
		return;
	unsigned empty = 0;
	if (who.uniqueid == enuma_open_slot.attempt.uid && who.pid == enuma_open_slot.attempt.pid &&
	    who.idversion == enuma_open_slot.attempt.version &&
	    enuma_open_generation(who) == enuma_open_slot.attempt.generation &&
	    __atomic_compare_exchange_n(&enuma_method_claimed, &empty, 1, false,
	    __ATOMIC_RELAXED, __ATOMIC_RELAXED)) {
		enuma_open_slot.selector = selector;
		__atomic_store_n(&enuma_open_slot.method_kind, kind, __ATOMIC_RELEASE);
	}
	lck_spin_unlock(&enuma_bp_proc_lock);
}

__attribute__((noinline)) void
enuma_legacy_open_read(struct enuma_open_snapshot *out)
{
	out->phase = __atomic_load_n(&enuma_open_slot.phase, __ATOMIC_ACQUIRE);
	if (out->phase >= ENUMA_OPEN_ATTEMPT)
		out->attempt = enuma_open_slot.attempt;
	if (out->phase >= ENUMA_OPEN_RAW)
		out->raw = enuma_open_slot.raw;
	if (out->phase == ENUMA_OPEN_FINAL) {
		out->final = enuma_open_slot.final;
		out->method_eligible = enuma_open_registry != 0;
		out->method_kind = __atomic_load_n(&enuma_open_slot.method_kind, __ATOMIC_ACQUIRE);
		if (out->method_kind)
			out->selector = enuma_open_slot.selector;
	}
}
