# BootProgress source-only archive — 2026-11-26

Static provenance audit (`self-checked`), not a rebuild, release, or device
authorization. Candidate recipes are archival and require local inputs not
included here. No generated C, glyph data, donor binaries, or package outputs
are included.

## 2026-11-25 full-screen and preliminary experiments

Compared against enuma history through `b383d8d951191586f46236aad23099f1f535a12f`,
`UniXNU/UniXNU@693f5d9cae8a408dd18b39f3f9fdc4228c934241`,
the fixed XNU commit `d8b80295118ef25ac3a784134bcf95cd8e88109f` and its
actual patched worktree, and retained original build/generation material.
The older `porting.toml` evidence line records the blocked **r69d** archive
provenance check; the README describes a different, later **r65-derived r6**
candidate. The latter does not carry the r69d GUI writer forward.

| `candidates/bootprogress-20261125/` | Provenance and boundary |
| --- | --- |
| `README.md` | Local narrative; r65-derived recipe, r6 boot digest and generated test-input names agree with the r6 manifest/logs. The historical experiments named at the end are not the r6 recipe. |
| `enuma_defconfig` | Same baseline blob `c5f474aac5d4` at `a05d60c` and `b383d8d`; candidate changes only the BootProgress comment and `n` → `y`. Does not replace the board config. |
| `build-archive.py` | Local compile-record adapter. The six staged BootProgress/BootTime files compare byte-for-byte to the named sheng commit; the staged `boot_progress.h` compares byte-for-byte to the excluded output of the pinned UniXNU patch extractor. Neither the extracted code nor the font is stored in the script. |
| `build-enuma-gop-legacy.py` | Local adapter, not the earlier builder: `out/bootprogress-display-source-20261125/scripts/build-enuma-gop-legacy.py` matches its `BUILDER_SHA`. The Enuma C++/ABI inputs are separately hash-bound; `wire_scanout` also adapts the fill-layout preamble of `UniXNU/GopFramebuffer@e47c1b8de169cd2bd0b885c7d85e433010e3cdf2:NativeLegacyRequest.h` (lines 82–102 of the adapter). Retained notice below. The rest of the separately sourced C++ bodies and ABI parser are loaded at runtime. |
| `build-full.py` | Local r65 command/pack replay and enuma insertion bodies. `blit_source`, `vc_source`, `pe_source` use signatures, switch boundaries and small context anchors; `blit_source` reads the dispatch and `pe_source` reads the original scale/release/routing blocks from the caller's source, not embedded function bodies. In the progress refusal splice (92–101), the adjacent deadline/schedule API calls reuse the existing XNU scheduling idiom, and the other matched text is context, declarations, or retained call sites (`gc_hide_cursor`, `vc_needsave`). Comparing the fixed blobs to the actual patched worktree separates stock anchors from enuma context such as `ep_console_can_write` and `ep_first_mapping`. In-memory transform replay against that worktree exactly matches r6 `video_console.c` and `pe_init.c`; debug adds only the panic call, the r64 `bsd_init.c` input adds the two checkpoints, and the r64 `IOUserClient.cpp` input is forwarded unchanged. The generated XNU files retain their Apple headers (APSL 2.0 at the fixed tree's `APPLE_LICENSE`); those files are not archived here. |
| `build-recorder.py` | Local compile-record adapter. The XNU startup/ARM signatures and one PE setup line are selection context, not an embedded source unit; stage-only `startup.c`, `arm_init.c` and the recorded compiler input for `recorder.c` corroborate the split. |
| `framebuffer.h` | Local gate, lease, framebuffer bounds and raster-row helpers; no matched sheng body, fixed XNU body, or font table. The 11-26 refresh consumes this gate. |
| `recorder.c` | Local two-entry checkpoint logger paired with the stage-only compile record. The shared `boot-progress` key is an interface name, not the sheng collector. |
| `renderer.inc` | Local r6 frame/lease and centered 8×16 text renderer; SHA-256 `266388ce5b06…` matches `generated-test-inputs.json`. Compared to sheng's 5×12 layout/raster and fixed XNU console/font: uses the pre-existing `iso_font` symbol without vendoring the table or the sheng pixel routine. |
| `test-framebuffer.c` | Local gate, layout and thread fixtures; the historical `compile-host` command selects this file and the separately generated Legacy include directory. |
| `test-generated.py` | Local function-boundary extractor. It loads r6 PE/VC/renderer inputs and emits four separately hashed excerpts (`screen.inc`, `pe.inc`, `blit.inc`, `bp-init.inc`); all recorded input and output hashes matched. No extracted function is embedded in this tool. |
| `test-recorder.c` | Local synthetic boot-arg/log fixture for the recorder. Only the boot-arg key and recorder interface are shared. |
| `test-screen.c` | Local scheduler/console doubles, screen transaction and blit expectations; the small state-reset/callback overlap is enuma test glue. The actual staged PE/VC implementations and rotation/blit data enter via the four generated includes, which are excluded. |

## 2026-11-26 page variants

`U` = `bootprogress-upstream-20261126`, `2×` = `bootprogress-upstream-2x-20261126`,
`W` = `bootprogress-wrap-20261126`, all under `candidates/`. Compared each
distinct SHA-256 once, using r5, 2× r1 and proc-events r4 staging outputs,
respectively. Those outputs have the same `page.h`, `refresh.inc`, and
`sample.inc` bytes as their respective candidates and hold separate exact
copies of pinned sheng input. None of those outputs is added to Git.

| Files | Provenance and disposition |
| --- | --- |
| `U/README.md`, `2×/README.md`, `W/README.md` | Local field and result documentation, 2× geometry, and wrap/proc changes respectively. Upstream-source descriptions and labels are references, not embedded source; the existing font/license is named but the glyphs are not included. Archive. |
| `U/build.py`, `2×/build.py`, `W/build.py` | Local r6 replay lineage. U/2× stage inputs and reuse r6 link/pack; W adds proc replay, with the exit log and two boot-progress substitutions traceable to enuma `a05d60c6908834fae9f7eb8f2c46b6ecd169a0ad:scripts/build-enuma-r64-ustack.py`. W's short XNU signatures/condition/call anchors select original text read at runtime. None contains the sheng painter or font. Archive. |
| `U/reference.py`, `2×/reference.py`, `W/reference.py` (`320681b2293e…`) | Identical local extractors. `draw`/overlay boundary strings name locations in `BootProgress.c`; `reference-draw.inc`, `reference-side.inc` and `captured-sample.inc` contain the actual excerpts and are not archived. Archive the extractor only. |
| `U/refresh.inc`, `2×/refresh.inc`, `W/refresh.inc` (`86d9f88022ba…`) | Identical derivative of the local r6 `renderer.inc` thread-call/row-lease loop. It calls `panel_sample` and `panel_raster` instead of embedding their implementation. Archive. |
| `U/test-page.c`, `2×/test-page.c`, `W/test-page.c` | Local synthetic input/reference harness, with 2× equivalence and wrap cases added locally. Lines 14–16 repeat the reference palette identifier/value pairs from `BootProgress.c:242–244` for the extracted fixture. The test has comparisons, fixture counters and pixel/PPM checks, not the upstream implementation; the implementation is included from local/pinned separate files. Archive. |
| `2×/test-reference.c`, `W/test-reference.c` (`f58e418d1638…`) | Identical thin local caller of the unscaled candidate `panel_raster`; no copied raster body. Archive. |
| `U/page.h`, `2×/page.h`, `W/page.h` | Adapted raster/layout in all three from `UniXNU/UniXNU-sheng@c8f92b208068eeaa4cd2b0f592671f04ee70076e:package/BootProgress{,Display}.*`, including the cell geometry, glyph selection and painter conventions. Hold all three. |
| `U/sample.inc`, `2×/sample.inc`, `W/sample.inc` | The sampling/declaration glue is enuma, but the page text is not wholly independent: U/2× 105–107 (W 110–112) reproduce both verbatim title strings from `BootProgress.c:263–266`; U/2× 124, 133, 136, 150, 156, 159, 166, 177, 188, 198, 205, 209 (W +5) repeat the selected upstream row formatting. This is copied page expression within the sampler, not merely an inclusion of `page.h`. Hold all three. |

The sheng pinned blobs label the relevant files MIT, but neither those files
nor their ancestor versions through the initial import supply the
copyright/permission notice for them. The pinned repository root `LICENSE`
is BSD-2-Clause-Patent and is not a substitute for the MIT notice. The missing
input for those six files is a rights-holder-supplied notice covering the
copied sheng painter and page text. No author was inferred from Git commit
metadata. The pinned enuma firmware `Font.h` at
`wh1stl3/uefi-enuma@964dffaae931e4eaddc9b4229d509227c02d5969` has its own
complete Android Open Source Project notice; it remains a separate input.

## Retained BSD-2-Clause-Patent notices

The two original `LICENSE` files have identical text after their first line.
Notices below are for the respective pinned sources cited above, not the
withheld sheng MIT material.

```text
Copyright (c) 2026, UniXNU contributors. All rights reserved.
Copyright (c) 2026, ArmVirtPlatform contributors. All rights reserved.

SPDX-License-Identifier: BSD-2-Clause-Patent

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

Subject to the terms and conditions of this license, each copyright holder
and contributor hereby grants to those receiving rights under this license
a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable
(except for failure to satisfy the conditions of this license) patent
license to make, have made, use, offer to sell, sell, import, and otherwise
transfer this software, where such license applies only to those patent
claims, already acquired or hereafter acquired, licensable by such copyright
holder or contributor that are necessarily infringed by:

(a) their Contribution(s) (the licensed copyrights of copyright holders and
    non-copyrightable additions of contributors, in source or binary form)
    alone; or

(b) combination of their Contribution(s) with the work of authorship to
    which such Contribution(s) was added by such copyright holder or
    contributor, if, at the time the Contribution is added, such addition
    causes such combination to be necessarily infringed. The patent license
    shall not apply to any other combinations which include the
    Contribution.

Except as expressly stated above, no rights or licenses from any copyright
holder or contributor is granted under this license, whether expressly, by
implication, estoppel or otherwise.

DISCLAIMER

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
```
