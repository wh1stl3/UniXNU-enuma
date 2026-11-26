/* SPDX-License-Identifier: BSD-2-Clause-Patent */
#include "open.h"

static const char *
panel_chain_dt(const struct enuma_chain_point *p)
{
	return !p->seen ? "unknown" : p->positive ? "returned" : "empty";
}

static const char *
panel_chain_object(const struct enuma_chain_point *iter, const struct enuma_chain_point *open)
{
	return !iter->key || !open->key ? "?" : iter->key == open->key ? "same" : "different";
}

static void
panel_legacy_chain(struct panel_page *page, const struct enuma_chain_snapshot *s)
{
	const struct enuma_chain_point *p = s->point;
	char text[PANEL_COLS], match[24];
	snprintf(text, sizeof(text), "DT inline gen=%u: /arm-io=%s enuma-gop-display=%s | %s",
	    s->generation, panel_chain_dt(&p[ENUMA_DT_PARENT]), panel_chain_dt(&p[ENUMA_DT_CHILD]),
	    s->available ? "direct path only" : "snapshot busy");
	panel_line(&page->main[6], text, PANEL_CYAN, 0);

	const struct enuma_chain_point *reg = &p[ENUMA_FIRST_MATCH], *iter = &p[ENUMA_ITER_SERVICE];
	if (reg->seen && !reg->positive)
		snprintf(match, sizeof(match), "0x%08x", (unsigned)reg->value);
	else
		snprintf(match, sizeof(match), "%s", reg->seen ? "registered" : "unknown");
	snprintf(text, sizeof(text), "IOMobileFramebuffer first-match=%s | board iterator return=%s | pairing unknown",
	    match, iter->positive ? "observed" : "unknown");
	panel_line(&page->main[7], text, PANEL_CYAN, 0);

	const struct enuma_chain_point *reject = &p[ENUMA_OPEN_REJECT];
	const unsigned open_mask = (1u << ENUMA_OPEN_REJECT) | (1u << ENUMA_OPEN_SERVICE);
	snprintf(text, sizeof(text), "Open early=%s | iter object early/call=%s/%s | open lock loss (unowned)=%s",
	    !reject->seen ? "unknown" : reject->value == ENUMA_REJECT_MAC ? "MAC" : "properties",
	    panel_chain_object(iter, reject), panel_chain_object(iter, &p[ENUMA_OPEN_SERVICE]),
	    (s->unsampled & open_mask) ? "seen" : "none seen");
	panel_line(&page->main[8], text, PANEL_CYAN, 0);
}

static void
panel_legacy_open(struct panel_page *page, const struct enuma_open_snapshot *v,
    const struct enuma_bp_event *exec)
{
	char text[PANEL_COLS];
	panel_legacy_chain(page, &v->chain);
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
