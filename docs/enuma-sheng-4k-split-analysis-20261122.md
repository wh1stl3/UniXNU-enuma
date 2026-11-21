# Sheng 4K / 16K fixup comparison

Static review only; sheng is UniXNU/UniXNU-sheng@c8f92b208068eeaa4cd2b0f592671f04ee70076e. Its worktree contains only .git, so source citations are Git blob line numbers. No device access or build.

## Wait patch

`patches/xnu-12377/vmwait-dyld-pager-source-release.patch:21-65` modifies `osfmk/vm/vm_dyld_pager.c`, `dyld_pager_data_request()` (target hunk offsets 1330 and 1362). Hunk 1 (:23-55) releases the busy source page, its paging reference, and the top-object placeholder immediately after copying the current 4K part, before peeking the others. Hunk 2 (:56-65) skips the normal end-of-loop release when the source was already released. It fixes waiting/deadlock during assembly, not splitting itself: its comments (:3-18) describe an APFS integrity-block UPL waiting on the held source page and copy mappings waiting on the paging reference. The patch states `Not run on hardware` (:20).

The patch adds no macro. It requires `zzzz-sheng-ipados27-bringup.patch` and its local variables, assembly branch and `dyld_pager_peek` (series :6-7). It also mentions a separate shared-region wait fix `native-4k-shared-region-slide.patch`; that file is absent from the local UniXNU patch directory and architecture series, so its contents are not established here.

## Actual assembly and split

Sheng `patches/xnu-12377/zzzz-sheng-ipados27-bringup.patch:1825-1837` allocates an aligned scratch buffer when `mwli_page_size > PAGE_SIZE`; `:1864-1890` copies the faulted part, loops `i < mwli_page_size / PAGE_SIZE`, reads the remaining parts with `dyld_pager_peek`, calls `fixup_page`, then copies the requested `PAGE_SIZE` part to `dst_vaddr`. With 16K metadata and a 4K kernel this is four parts. This is dyld pager data-request/fault handling, not signature hash caching. `:1723-1801` implements the peek with `vm_fault_page`, validation and page release. `:1590-1615,1639-1650,1671-1681,1704-1710` change chain boundaries and indexing to metadata page size. The same patch changes the mapping-with-linking `mwli_page_size` admission check to allow four kernel pages (search that expression in the blob).

Signature handling is separate: local `UniXNU/patches/xnu/native-4k-signature-hash-cache.patch:31-44,94-121,170-195,241-249` uses `XNU_NATIVE_CS_HASH_CACHE` to accept 16K signed code-directory blocks on a 4K kernel, verify whole blocks and cache per-4K hashes; it is not the dyld splitter. Sheng bringup `:1904-1922` shows a distinct shared-region slide-size branch under `!APPLE_ARM64_ARCH_FAMILY && !__ARM_16K_PG__`, but its hunk only adds logging; its implementation/provenance is not established from that device repository. No `vm_fourk_pager` evidence was found in the sheng device patch search.

## Minimum conditional components / enuma

For this specific signed 16K chained-fixup case: (1) 4K kernel and appropriate 4K user ABI/configuration; (2) admission of 16K mapping-with-linking metadata; (3) dyld pager scratch assembly, metadata-sized chain walking and 4K copyout; (4) release-before-peek wait fix and a shared-region equivalent if that path is used; (5) verification support for 16K code-directory hashes, such as the guarded hash cache. Shared-region sliding is a separate conditional path. This list is not proof of sufficiency for every cache format or a complete boot.

Enuma `board.toml:19-24` selects `enuma_defconfig`, architecture/SoC/OS fragments and arch/SoC/OS/device series. `patches/xnu/series:1-4` lists only PID1 and PMGR patches, not the Sheng implementation or wait patch. The selected `UniXNU/profiles/arch/arm64/patches/xnu/series:14-16` lists native-4k bootstrap capacity, signature-hash-cache and user-ABI patches; series membership does not prove their guarded code is enabled. That architecture series does not name Sheng's dyld predecessor, wait fix or shared-region slide patch. The SoC and OS series were not exhaustively traced for equivalent implementations; no named patch is not proof no equivalent code exists. `configs/enuma_defconfig` has no explicit 4K/CS_HASH setting; effective fragment/build values are unverified.

The wait hunk cannot be copied standalone: it depends on the XNU-12377 predecessor and its VM lifecycle. Enuma targets iPadOS 17.7.11 (`board.toml:161-162`), so adaptation is required. BCM2837 is an XNU platform configuration name, not the sheng SoC: Sheng `feeds.toml:1-5` specifies sm8550, and the bringup patch near its BCM2837.h hunk describes sheng A510/A715/X3 cores.

Layer: dyld pager data-request scratch assembly/fixup/4K copyout; shared-region pager is separate.

Enuma missing: Sheng dyld assembly/admission and wait patches are absent from the inspected device and architecture series; effective macros and SoC/OS equivalents remain unverified.

Portability: requires adaptation because the wait patch depends on Sheng XNU-12377 predecessor code and VM page lifecycle.
