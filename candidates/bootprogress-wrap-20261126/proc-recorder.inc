/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Reuse the static spin-lock setup from r64 EnumaProcExecReport.inc. */
static LCK_GRP_DECLARE(enuma_bp_proc_group, "enuma-bp-proc");
static LCK_SPIN_DECLARE(enuma_bp_proc_lock, &enuma_bp_proc_group);
static struct enuma_bp_proc_events enuma_bp_events;

static inline void
enuma_bp_note_event(struct enuma_bp_event *event, struct enuma_bp_identity who)
{
	if (event->count != UINT32_MAX)
		++event->count;
	event->latest = who;
}

__attribute__((noinline)) void
enuma_bp_record_exec(enum enuma_bp_proc_slot slot, struct enuma_bp_identity who)
{
	lck_spin_lock(&enuma_bp_proc_lock);
	enuma_bp_note_event(&enuma_bp_events.slot[slot - 1].exec, who);
	lck_spin_unlock(&enuma_bp_proc_lock);
}

__attribute__((noinline)) void
enuma_bp_record_exit(enum enuma_bp_proc_slot slot, struct enuma_bp_identity who, int rv)
{
	lck_spin_lock(&enuma_bp_proc_lock);
	enuma_bp_note_event(&enuma_bp_events.slot[slot - 1].exit, who);
	enuma_bp_events.slot[slot - 1].raw_rv = rv;
	lck_spin_unlock(&enuma_bp_proc_lock);
}

__attribute__((noinline)) bool
enuma_bp_proc_snapshot(struct enuma_bp_proc_events *snapshot)
{
	if (!lck_spin_try_lock(&enuma_bp_proc_lock))
		return false;
	*snapshot = enuma_bp_events;
	lck_spin_unlock(&enuma_bp_proc_lock);
	return true;
}
