# nuwa dyld cache reference — 2026-11-22

Status: self-checked source/record analysis; no build, device access or volume modification.

1. **Kernel.** `nuwa/UniXNU-nuwa/board.toml:20-24,42-43` selects the device
   defconfig, arch common fragment, device series and
   `DEVELOPMENT_ARM64_BCM2837` kernel. `configs/nuwa_defconfig:1-18` and
   `UniXNU/profiles/arch/arm64/configs/common.config:1-8` do not set an
   `XNU_4K` switch. `patches/xnu/series:46-47` selects native 4K bootstrap and
   user ABI patches. The pinned base's `docs/zh/xnu/four-k-page-tables.md:3-14`
   specifies BCM2837 `ARM_PGSHIFT=12`, 4096-byte pages; the user ABI patch
   (`UniXNU/patches/xnu/native-4k-user-abi.patch:5-14,22-43,53-61,66-82`)
   sets 4K process/shared maps and advertised shift on non-Apple 4K builds.
   This is a configuration/source conclusion, not a new runtime measurement.

2. **Input.** `UniXNU/profiles/os/ios-16.7.16-20H392/profile.toml:12-16,23-28,81-82`
   identifies iPhone X `iPhone10,3`, d22ap, iOS 16.7.16 and
   `Cryptex1,SystemOS` member `087-86593-047.dmg`. The nuwa record
   `docs/root-inputs-20261113.md:29-47` says the official IPSW extractor obtained
   that member, reported as raw SystemOS, and packaged it into userdata.
   `docs/nuwa-userspace-20261119-observation.md:88-97` identifies
   `dyld_shared_cache_arm64` and `.01..18` inside SystemOS and records the
   read-only union mount; this is not an arm64e filename. It does not state
   slide-info or mapping page size. The mount exposes files, not a cache
   conversion.

3. **Layout and provenance.** No cited receipt measures the deployed 20H392
   cache's slide-info page size, maps its actual file extents, or establishes
   native 4K cache generation. `scripts/payload_cache_slide.py:1,6-10` is a
   *read-only* parser requiring slide v2 with `page == 4096`;
   `scripts/audit-payload-cache-slide.py:16-18,26-28,39-41,63-65` applies it
   to a separately qualified SystemOS image and records a report, but the
   specified `reports/desktop-readiness/.../audit.json` input and a result
   binding that audit to deployed 20H392 were not found in this checkout.
   Its successful execution cannot be assumed. Code-signature hash granularity,
   CPU architecture and `arm64` filename alone do not prove cache slide
   granularity. The premise that every iPhone donor necessarily produces a 16K
   cache is not established: the pinned upstream documentation explicitly
   distinguishes Apple 4K and 16K profiles
   (`UniXNU/docs/zh/xnu/four-k-page-tables.md:58-67`).

4. **Pager patches.** Search of tracked nuwa `patches/xnu/*.patch` found no
   `vm_dyld_pager`, `fixup_page` or `mwli_page_size`; its selected arch patches
   (`patches/xnu/series:36-71`) likewise have no dyld pager hunk in the pinned
   base patch tree. Thus no nuwa dyld pager modification was identified in
   those series; this does not cover untracked/generated build trees or prove
   final binary identity. `native-4k-user-abi` changes `vm_shared_region.c`,
   not `vm_dyld_pager`. The local read-only v2 parser is an analysis tool, not
   a runtime pager or cache converter.

5. **Conclusion.** Nuwa's kernel is configured for 4K and its donor SystemOS
   cache is exposed without a documented cache conversion; whether that
   particular cache has 4K slide layout is **undetermined**. Neither
   “naturally 4K” nor “converted to 4K” is established. There is no identified
   nuwa cache-conversion or dyld-pager assembly implementation to reuse for
   enuma. This also does not prove enuma's cache layout, establish its current
   failure mechanism, or prove that a sheng-style kernel assembly route is
   the only possible solution.
