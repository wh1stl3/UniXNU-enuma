/* SPDX-License-Identifier: BSD-2-Clause-Patent */
#ifndef ENUMA_BP_PROC_EVENTS_H
#define ENUMA_BP_PROC_EVENTS_H

enum enuma_bp_proc_slot {
	ENUMA_BP_NOT_TRACKED, ENUMA_BP_LAUNCHD, ENUMA_BP_BACKBOARDD, ENUMA_BP_SPRINGBOARD
};
enum { ENUMA_BP_PROC_SLOTS = 3 };

struct enuma_bp_identity {
	uint64_t uniqueid;
	int pid, idversion;
};

struct enuma_bp_event {
	struct enuma_bp_identity latest;
	uint32_t count;
};

struct enuma_bp_proc_events {
	struct {
		struct enuma_bp_event exec, exit;
		int raw_rv;
	} slot[ENUMA_BP_PROC_SLOTS];
};

void enuma_bp_record_exec(enum enuma_bp_proc_slot, struct enuma_bp_identity);
void enuma_bp_record_exit(enum enuma_bp_proc_slot, struct enuma_bp_identity, int);
bool enuma_bp_proc_snapshot(struct enuma_bp_proc_events *);

static inline enum enuma_bp_proc_slot
enuma_bp_classify(const char *comm)
{
	if (strcmp(comm, "launchd") == 0)
		return ENUMA_BP_LAUNCHD;
	if (strcmp(comm, "backboardd") == 0)
		return ENUMA_BP_BACKBOARDD;
	if (strcmp(comm, "SpringBoard") == 0)
		return ENUMA_BP_SPRINGBOARD;
	return ENUMA_BP_NOT_TRACKED;
}

static inline bool
enuma_bp_exec_observed(bool reached, bool failed, int error, bool done, bool notified)
{
	return reached && !failed && !error && done && notified;
}
#endif
