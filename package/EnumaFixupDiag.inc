/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Included by the isolated r47 ubc_subr.c translation unit. */
#include <pexpert/pexpert.h>
int enuma_fxd_enabled;
unsigned int enuma_fxd_sv, enuma_fxd_fx, enuma_fxd_taint, enuma_fxd_novalid;
unsigned int enuma_fxd_nx, enuma_fxd_vnode, enuma_fxd_range, enuma_fxd_bytes;
unsigned int enuma_fxd_page;

#define ENUMA_FXD_INC(counter) do { \
	if (enuma_fxd_enabled) { \
		os_atomic_inc(&(counter), relaxed); \
	} \
} while (0)

static void
enuma_fxd_report(void)
{
	if (enuma_fxd_enabled != 1) {
		return;
	}
	printf("enuma-fxd: sv=%u fx=%u taint=%u novalid=%u nx=%u\n",
	    os_atomic_load(&enuma_fxd_sv, relaxed), os_atomic_load(&enuma_fxd_fx, relaxed),
	    os_atomic_load(&enuma_fxd_taint, relaxed), os_atomic_load(&enuma_fxd_novalid, relaxed),
	    os_atomic_load(&enuma_fxd_nx, relaxed));
	printf("enuma-fxd: vnode=%u range=%u bytes=%u page=%u\n",
	    os_atomic_load(&enuma_fxd_vnode, relaxed), os_atomic_load(&enuma_fxd_range, relaxed),
	    os_atomic_load(&enuma_fxd_bytes, relaxed), os_atomic_load(&enuma_fxd_page, relaxed));
}
