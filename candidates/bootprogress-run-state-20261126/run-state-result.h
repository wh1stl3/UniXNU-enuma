/* SPDX-License-Identifier: BSD-2-Clause-Patent */
#ifndef ENUMA_BP_RUN_STATE_RESULT_H
#define ENUMA_BP_RUN_STATE_RESULT_H

enum enuma_bp_run_where { RUN_STATE, RUN_PRE, RUN_POST, RUN_TARGET };
enum enuma_bp_run_reason {
	RUN_OK, RUN_BUSY, RUN_SATURATED, RUN_EXIT, RUN_INCOMPLETE, RUN_CHANGED,
	RUN_INVALID_TID, RUN_INSTANCE_NOT_FOUND, RUN_PROC_UNAVAILABLE, RUN_TID_NOT_IN_TASK,
	RUN_INFO_REFUSED, RUN_PROC_OR_TASK_CHANGED
};
struct enuma_bp_run_result {
	enum enuma_bp_run_where where;
	enum enuma_bp_run_reason reason;
	int run_state;
};
struct enuma_bp_run_report {
	struct enuma_bp_run_result target[2];
};

bool enuma_bp_run_read(struct enuma_bp_run_report *);
#endif
