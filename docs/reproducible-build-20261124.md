# enuma r63 source inventory and full rebuild status — 2026-11-24

`self-checked` source preflight. The incremental r64 exists; a full build
without historical objects has not run.

## r63 `link.filelist`

| Class | Entries | Evidence |
| --- | ---: | --- |
| XNU translation units | 1,006 | 995 in the baseline `ios-obj/DEVELOPMENT_ARM64_BCM2837` and 11 replacements at lines 27, 40, 199, 565, 585, 586, 646, 678, 807, 935, 956; e.g. `osfmk/vm/vm_fault.c`, `bsd/kern/kern_exec.c`, `iokit/Kernel/IOUserClient.cpp`. Includes generated XNU units. |
| enuma translation units | 1 | Line 1007: `package/EnumaThreadSnapshot56.c` → `EnumaThreadSnapshot56.o`. Included board `.inc` files are not separate entries. `EnumaUserStack64.c` is new in r64. |
| External components | 0 | External archives are passed directly in the link command. |
| Confirmed unrecoverable | 0 | None established. Absence at the historical object path is not proof of lost source. |

All 1,007 paths are distinct. Seven historical objects are missing at their
exact paths: `vm_fault.o`, `bsd_init.o`, `kern_exit.o`, `vm_unix.o`,
`OSKext.cpo`, `IOUserClient.cpo` and `IOKitBSDInit.cpo`. The incremental r64
recompiled them; see [r64 host record](enuma-r64-ustack-host-20261124.md).
The 11 replacements are part of the 1,006, not additional entries.

## Direct link inputs and source staging

Twelve source groups were staged in `.cache/enuma-full-inputs-20261124/`
with original paths and per-file SHA-256 in `sources.json`. No old `.a`,
`.o`, Mach-O or boot image was copied into the source staging root. The
upstream exports came from local Git objects; no downloads were required.
UniXNU recipe baseline: `UniXNU/UniXNU@693f5d9cae8a408dd18b39f3f9fdc4228c934241`.

| Link input or tool | Source / revision / licence | Status |
| --- | --- | --- |
| `libArmCpu.a` | `UniXNU/ArmCpu@93a5030c5d983d0ef90f0fca93879d6e36ad1ba8`, BSD-2-Clause-Patent | `ArmCpu/`; checkout diff against pin was line endings only. |
| `libArmDTPlatform.a` | `UniXNU/ArmDTPlatform@417ff95d6a6e8607ddea9309ec45c3bfd4a67c60`, BSD-2-Clause-Patent | `ArmDTPlatform/`. |
| `libSoftwareAES.a` | `UniXNU/SoftwareAES@4a45326da5c2cd6fe6813d79ee43db20805628af`, BSD-2-Clause-Patent | `SoftwareAES/`; generate the original bindings separately. |
| `libShengUfs.a` | `UniXNU/ShengUfs@38c19c2b` + local enuma startroot-WIP r11, BSD-2-Clause-Patent | `ShengUfs-enuma/`; exact r11 `NativeUfs.cpp`, WIP patch, r40 regenerated source and board `.inc`. The r11 archive is not the r40 archive. |
| `libRamBlock.a` | `UniXNU/RamBlock@4be2d7eb05ef5a98126c91e0302c149140c0e3e1` + local `ramblock-mode1.patch`, BSD-2-Clause-Patent | `RamBlock/` and `RamBlock-enuma/`. Incremental r64 reused the available earlier archive; a full build must rebuild it and its bindings. |
| `libVerifiedRootDependencies.a` | `UniXNU/VerifiedRoot@974f043d0c71ba2e60331483a41c6c6d35274ee3`, BSD-2-Clause-Patent; generated enuma policy provider | `VerifiedRoot/`; incremental binary at `out/ufs-sm8250-launchd-display-20261119-r1/self-check/libVerifiedRootDependencies.a` (`53e72ccd…`). Provider generation from pinned inputs is not implemented in the full path. |
| `libEnumaGopLegacy.a` | `UniXNU/GopFramebuffer@e47c1b8de169cd2bd0b885c7d85e433010e3cdf2` and local r5 enuma wrapper/CPU-only patch, BSD-2-Clause-Patent (`NativeGpuTrace.h`: MIT) | `GopFramebuffer/` and `LegacyDisplay-enuma/`; r34 instrumentation and binding generation are separate steps. The r5 archive is not the r34 archive. |
| `libAppleKeyStoreState.a` | `UniXNU/AppleKeyStoreState@8c70daf814aafdf4a3d35e40dde0322655fd0a83`, BSD-2-Clause-Patent; local `package/EnumaKeyStoreProbe.cpp` | `AppleKeyStoreState/`; r39 probe and late initializer recipe survive. |
| `libShengHidInputStandin.a` | `UniXNU/ShengHidInput@71a40e76daeae1bb4127546f96ffa7339c7a06ff`, BSD-2-Clause-Patent; local `package/EnumaHidStandin.cpp` | `ShengHidInput/`; r23 build recipe survives. |
| `libShengPlatformPower.a`, `EnumaUfsOwnerQuery.o`, `libEnumaBootWatchdogPolicy.a` | Device `package/ShengPlatformPower.cpp`, `package/EnumaUfsOwnerQuery.cpp`, `package/BootWatchdogPolicy.c`; original source notices (`package/PMGR-NOTICE.md`, `package/UFS-OWNER-QUERY-LICENSE`) | Project source, not external exports. |
| `libcc_kext.a` | `llvm/llvm-project@58c46bae21181fb4240cf964461bea738d96d50e`, Apache-2.0 with LLVM exceptions; headers from `apple-oss-distributions/Libc@899a3b2d52d95d75e05fb286a5e64975ec3de757`, original per-file notices | UniXNU `scripts/linux/prepare-xnu.py` `libs` recipe. Not restaged. |
| `libfirehose_kernel.a`, `libpthread_kernel.a` | Apple OSS `libdispatch@30fe6a7d945340ce69cef121132f049e810089a5`, `libpthread@c0e60fb5ecfc54cf379c261d3f9572cc22ded891`, original per-file notices | Existing references in baseline `refer/`; `build-firehose.sh`, `build-libpthread-kernel.py`. |
| `libcorecrypto_kernel_noasm-namespaced.a` | `ONLYA/corecrypto-2023@11fba65b12d8830630e248dfa8344caf8b065f26`; Apple source terms | Existing `refer/corecrypto-2023`; `scripts/build-corecrypto-14.py --namespace`. Not redistributed. |
| `libmockfs_fixture.a` | UniXNU baseline `scripts/build-mockfs-fixture.py` and XNU fixtures; original per-file notices | Not separately staged. |
| Prelink | `UniXNU/XnuPrelink@f1d80d37528a33e24643583787123c652b70a268`, BSD-2-Clause-Patent | `XnuPrelink/`. Pinned 21H461 donor is a required binary input, not a historical native intermediate. |

Shared feed `FFT-infra/UniXNU-sm8250-common@166235ec2480ff0992627b7aafa15c65ce6b4efa`
is not a substitute for these component revisions.

The r40 UFS input was recovered, not approximated: the r11
`resume-20261118-r11/merged-source/NativeUfs.cpp` has the expected SHA-256
`6ee5fb866c9bcdc5b1c50268ede8dc86f3eef1526c3784b3e8f0664da27ccb69`.
Replaying just `build-enuma-r40-storegeom.py:89–118` generated
`ShengUfs-enuma/NativeUfs.r40.cpp` with SHA-256
`7ec57752896a57621ba02a14449a8b81fd15a79a8e0b5a92576c8b2548dfab6b`.
The r11 BSD side was separately reconstructed by applying the timebase and
keystore patches to the r13 audit snapshot before the r40 insertion.

## Full rebuild vs. incremental r64

The incremental r64 script uses unaffected historical objects and archives,
and copies pinned content from the existing r63 package. It is not a recipe
that can bootstrap after deleting those inputs. The full path still needs
fresh XNU header/unit generation, the source-stage substitutions, generation
of original bindings and of the signed-policy provider, compilation of all
units, native/prelink verification, and packaging using direct pinned
firmware, DTB, trust-cache and scratch Data inputs. `scripts/build-enuma-full.py`
does not exist; no invocation is claimed.

The incremental r64 image and readback are in the linked host record.
Its digest differs from r63 because the packaged kernel changed despite
the ADT and arguments remaining the same. A full repack may also use a new
ADT random seed and packaging timestamps; equivalence must be checked on
inputs, symbols and unpacked content, not by requiring r63's image hash.
