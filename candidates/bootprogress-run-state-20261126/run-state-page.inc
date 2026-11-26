/* SPDX-License-Identifier: BSD-2-Clause-Patent */
#include "run-state-result.h"

enum { RUN_STATE_ROW = 13 };

static void
panel_run_state(struct panel_page *page, const struct enuma_bp_run_report *report)
{
	static const char *const name[] = { "backboardd", "SpringBoard" };
	static const char *const phase[] = { [RUN_PRE] = "pre", [RUN_POST] = "post", [RUN_TARGET] = "target" };
	static const char *const reason[] = {
		[RUN_BUSY] = "recorder-busy",
		[RUN_SATURATED] = "recorder-saturated",
		[RUN_EXIT] = "matching-exit",
		[RUN_INCOMPLETE] = "pair-not-published",
		[RUN_CHANGED] = "record-changed",
		[RUN_INVALID_TID] = "invalid-tid",
		[RUN_INSTANCE_NOT_FOUND] = "instance-not-found",
		[RUN_PROC_UNAVAILABLE] = "proc-unavailable",
		[RUN_TID_NOT_IN_TASK] = "tid-not-in-task",
		[RUN_INFO_REFUSED] = "thread-info-refused",
		[RUN_PROC_OR_TASK_CHANGED] = "proc-or-task-changed",
	};
	for (unsigned i = 0; i < 2; ++i) {
		char text[PANEL_COLS];
		const struct enuma_bp_run_result *result = report ? &report->target[i] : NULL;
		if (!result)
			snprintf(text, sizeof(text), "%s pending", name[i]);
		else if (result->reason == RUN_OK)
			snprintf(text, sizeof(text), "%s run_state=%d", name[i], result->run_state);
		else
			snprintf(text, sizeof(text), "%s no-sample:%s:%s",
			    name[i], phase[result->where], reason[result->reason]);
		panel_line(&page->main[RUN_STATE_ROW + i], text,
		    result && result->reason == RUN_OK ? PANEL_CYAN : PANEL_GREY, 0);
	}
}
