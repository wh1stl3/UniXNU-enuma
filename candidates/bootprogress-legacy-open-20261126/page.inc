/* SPDX-License-Identifier: BSD-2-Clause-Patent */
#include "open.h"

static void
panel_legacy_open(struct panel_page *page, const struct enuma_open_snapshot *v,
    const struct enuma_bp_event *exec)
{
	char text[PANEL_COLS];
	if (v->phase >= ENUMA_OPEN_ATTEMPT)
		snprintf(text, sizeof(text), "BB exec for open: pid=%d uid=%llu ver=%d gen=%u",
		    v->attempt.pid, (unsigned long long)v->attempt.uid, v->attempt.version, v->attempt.generation);
	else if (exec && exec->count)
		snprintf(text, sizeof(text), "BB latest exec (not attributed): pid=%d uid=%llu ver=%d gen=%u",
		    exec->latest.pid, (unsigned long long)exec->latest.uniqueid, exec->latest.idversion, exec->count);
	else
		snprintf(text, sizeof(text), "BB exec: %s", exec ? "not observed" : "snapshot busy");
	panel_line(&page->main[3], text, PANEL_CYAN, 0);

	if (v->phase >= ENUMA_OPEN_RAW)
		snprintf(text, sizeof(text), "Legacy open type=%u newUserClient=0x%08x class=%s%s",
		    v->attempt.type, (unsigned)v->raw.result, v->raw.client_class[0] ? v->raw.client_class : "-",
		    v->raw.truncated ? "..." : "");
	else if (v->phase == ENUMA_OPEN_ATTEMPT)
		snprintf(text, sizeof(text), "Legacy open attempt type=%u | newUserClient pending", v->attempt.type);
	else
		snprintf(text, sizeof(text), "Legacy open: not attributed (absence unknown)");
	panel_line(&page->main[4], text, PANEL_CYAN, 0);

	if (v->phase == ENUMA_OPEN_FINAL)
		snprintf(text, sizeof(text), "Legacy server final: err=0x%08x result=0x%08x client=%u (not reply receipt)",
		    (unsigned)v->final.err, (unsigned)v->final.result, (unsigned)v->final.client);
	else
		snprintf(text, sizeof(text), "Legacy server final: %s", v->phase ? "pending" : "unknown");
	panel_line(&page->main[11], text, PANEL_CYAN, 0);

	if (v->method_kind) {
		const char *kind = v->method_kind == ENUMA_METHOD_SYNC ? "sync" :
		    v->method_kind == ENUMA_METHOD_VAR ? "var" : "async";
		snprintf(text, sizeof(text), "First observed dispatch: %s sel=%u | same exec/object; connection unknown",
		    kind, v->selector);
	} else
		snprintf(text, sizeof(text), "Method: %s | connection unknown",
		    v->method_eligible ? "not observed yet" : "not tracked without successful object key");
	panel_line(&page->main[12], text, PANEL_CYAN, 0);
}
