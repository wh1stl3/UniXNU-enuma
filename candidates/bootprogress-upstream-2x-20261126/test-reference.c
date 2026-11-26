// SPDX-License-Identifier: BSD-2-Clause-Patent
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "framebuffer.h"
#include "../bootprogress-upstream-20261126/page.h"

void original_page(const struct bp_framebuffer *fb, const void *page)
{
	for (unsigned y = 0; y < fb->height; ++y)
		panel_raster(fb, y, page, NULL);
}
