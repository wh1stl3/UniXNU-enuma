// SPDX-License-Identifier: BSD-2-Clause-Patent
#include "display-events.h"

static void
panel_display_events(struct panel_page *page, const struct enuma_bp_display_sample *sample)
{
	char text[PANEL_COLS];
	const unsigned *seen = sample->seen;
	snprintf(text, sizeof(text), "DISPLAY Legacy service sticky: registered=%u | independent samples; 0=not observed",
	    seen[ENUMA_DISPLAY_REGISTERED]);
	panel_line(&page->main[31], text, PANEL_YELLOW, 0);
	snprintf(text, sizeof(text), "VALIDATE enter=%u accept=%u reject=%u | Legacy validator only; accept includes blank",
	    seen[ENUMA_DISPLAY_VALIDATE_ENTER], seen[ENUMA_DISPLAY_VALIDATE_ACCEPT],
	    seen[ENUMA_DISPLAY_VALIDATE_REJECT]);
	panel_line(&page->main[32], text, PANEL_YELLOW, 0);
	snprintf(text, sizeof(text), "PREPARE enter=%u false=%u | includes no display object; final frame may be stale",
	    seen[ENUMA_DISPLAY_PREPARE_ENTER], seen[ENUMA_DISPLAY_PREPARE_FALSE]);
	panel_line(&page->main[33], text, PANEL_YELLOW, 0);
	snprintf(text, sizeof(text), "CLIENT caller/BB unknown | legacy4.enter=%u parent.ok=%u parent.err=%u | not IOServiceOpen result",
	    seen[ENUMA_DISPLAY_LEGACY4_ENTER], seen[ENUMA_DISPLAY_PARENT_OK],
	    seen[ENUMA_DISPLAY_PARENT_ERR]);
	panel_line(&page->main[34], text, PANEL_GREY, 0);
}
