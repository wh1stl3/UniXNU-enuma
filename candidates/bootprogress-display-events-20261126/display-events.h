// SPDX-License-Identifier: BSD-2-Clause-Patent
#ifndef ENUMA_BP_DISPLAY_EVENTS_H
#define ENUMA_BP_DISPLAY_EVENTS_H

enum enuma_bp_display_event {
	ENUMA_DISPLAY_REGISTERED,
	ENUMA_DISPLAY_LEGACY4_ENTER,
	ENUMA_DISPLAY_PARENT_OK,
	ENUMA_DISPLAY_PARENT_ERR,
	ENUMA_DISPLAY_VALIDATE_ENTER,
	ENUMA_DISPLAY_VALIDATE_ACCEPT,
	ENUMA_DISPLAY_VALIDATE_REJECT,
	ENUMA_DISPLAY_PREPARE_ENTER,
	ENUMA_DISPLAY_PREPARE_FALSE,
	ENUMA_DISPLAY_EVENT_COUNT
};

struct enuma_bp_display_sample {
	unsigned seen[ENUMA_DISPLAY_EVENT_COUNT];
};

#ifdef __cplusplus
extern "C" {
#endif
void enuma_bp_display_mark(enum enuma_bp_display_event);
void enuma_bp_display_sample(struct enuma_bp_display_sample *);
#ifdef __cplusplus
}
#endif
#endif
