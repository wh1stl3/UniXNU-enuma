# Official 4K patch audit — 2026-11-22

Status: self-checked static audit; no device access, build, volume modification or independent verifier. Official tree: `693f5d9cae8a408dd18b39f3f9fdc4228c934241`.

## Patch entities

`UniXNU/profiles/arch/arm64/patches/xnu/series:14-16` selects:

* `UniXNU/patches/xnu/native-4k-bootstrap-capacity.patch:1-58`: hunks in `osfmk/arm/pmap/pmap.h`, `osfmk/arm64/start.s` and `genassym.c` enlarge, clear and bound the bootstrap page-table pool. No dyld pager hunk.
* `UniXNU/patches/xnu/native-4k-signature-hash-cache.patch:1-14,17-49,79-200,234-280`: hunks in `bsd/sys/ubc_internal.h` and `bsd/kern/ubc_subr.c` optionally accept a 16K CodeDirectory hash, authenticate original blocks and derive 4K signature hashes. This is code-signature validation, not dyld slide metadata conversion or pager assembly. No dyld pager hunk.
* `UniXNU/patches/xnu/native-4k-user-abi.patch:1-82`: hunks in `bsd/kern/mach_loader.c`, `osfmk/arm/arm_init.c`, `osfmk/arm/commpage/commpage.c` and `osfmk/vm/vm_shared_region.c` select 4K process/shared submaps and page shifts for non-Apple 4K builds. No dyld pager hunk.

None touches `osfmk/vm/vm_dyld_pager.c`, `mwli_page_size`, fixup-page indexing, or 16K metadata to 4K page assembly. The changes also cover bootstrap capacity and loader/arm initialization, not only shared submaps, commpage and signature derivation.

## enuma r14

Paths below are relative to `out/ufs-sm8250-launchd-keystore-20261122-r14/self-check/build-final/`. `logs/patch.log:1` records only the r14 incremental `kern_exec.c` patch, not application of these baseline patches. `link.filelist:210,293,305,324,646,661` names inherited objects, not their source revisions.

* Bootstrap capacity: **not established**. The final filelist includes `start.o` at line 305 but no baseline application receipt or corresponding source/object disassembly was established.
* Signature hash cache: **yes, linked**, not an application-log claim. `source/bsd/kern/ubc_subr.c:113,4879,5776` contains the patch and `native-link.map:1786,61088` shows its version and prepare symbols in the final native link. Runtime execution is not established.
* User ABI: **partial source evidence, final application not established**. `source/bsd/kern/mach_loader.c:515` contains the loader hunk and `link.filelist:661` includes an inherited `mach_loader.o`; their identity and the other three compilation units were not established.

The copied `kernel-build-result.json:2,6-18` identifies an inherited r6/r10 record, not a clean r14 baseline-build receipt.

## nuwa and interpretation

`nuwa/UniXNU-nuwa/board.toml:22-24,41-43` replaces the arch patch series with the device series and selects BCM2837. `nuwa/UniXNU-nuwa/patches/xnu/series:46-47` selects bootstrap capacity and user ABI, but not signature hash cache. This is selection evidence, not proof that a particular deployed binary incorporates them. Historical cumulative application is described in `nuwa/.cache/ci-porting-134fd4e/tools/docs/zh/devices/nuwa.md:66`; that set is not a final-binary receipt.

The iPhone10,3 SystemOS file names and recorded union mount are described in `docs/nuwa-4k-cache-reference-20261122.md:16-25`; slide granularity and deployed file identity are not measured (`:27-40`). Userspace progress alone does not establish that the shared cache was used or fixups executed. Direct 4K consumption and a path not needing the disputed fixups are hypotheses, not an exhaustive proven dichotomy: another path or undocumented generated change is also possible. No conversion was identified in the inspected selected series (`:42-49`).

Nuwa images exist under `nuwa/UniXNU-nuwa/out/`, but this audit did not establish the exact deployed image and did not disassemble its `fixup_page`. Machine-code indexing remains undetermined.
