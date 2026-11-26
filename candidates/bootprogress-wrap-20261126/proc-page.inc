/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Rows 24–28 only. The console ends at 23; leave other diagnostics intact. */
static void
panel_proc_event(char *text, size_t cap, const struct enuma_bp_event *event)
{
	if (!event->count) {
		snprintf(text, cap, "not observed");
		return;
	}
	const struct enuma_bp_identity *id = &event->latest;
	if (event->count == UINT32_MAX)
		snprintf(text, cap, "%-10s %x:%llx:%x", "SAT",
		    (unsigned)id->pid, (unsigned long long)id->uniqueid, (unsigned)id->idversion);
	else
		snprintf(text, cap, "%u %x:%llx:%x", event->count,
		    (unsigned)id->pid, (unsigned long long)id->uniqueid, (unsigned)id->idversion);
}

static void
panel_proc_events(struct panel_page *page, const struct enuma_bp_proc_events *snap)
{
	static const char *const names[ENUMA_BP_PROC_SLOTS] = {"launchd", "backboardd", "SpringBoard"};
	panel_line(&page->main[24], snap ?
	    "PROC latest only | SAT=at least 4294967295 | pid:uniqueid:idversion hex | no liveness or pairing" :
	    "PROC snapshot busy (retry next refresh)", PANEL_CYAN, 0);
	if (!snap)
		return;

	panel_line(&page->main[25],
	    "            EXEC installed                                  EXIT prepare (raw wait status hex; 0 may be fallback)",
	    PANEL_CYAN, 0);
	for (unsigned i = 0; i < ENUMA_BP_PROC_SLOTS; ++i) {
		char exec[46], exit[46], raw[13], text[PANEL_COLS];
		panel_proc_event(exec, sizeof(exec), &snap->slot[i].exec);
		panel_proc_event(exit, sizeof(exit), &snap->slot[i].exit);
		raw[0] = '\0';
		if (snap->slot[i].exit.count)
			snprintf(raw, sizeof(raw), " rv=%x", (unsigned)snap->slot[i].raw_rv);
		snprintf(text, sizeof(text), "%-11s %-47s %s%s", names[i], exec, exit, raw);
		panel_line(&page->main[26 + i], text, PANEL_WHITE, 0);
	}
}
