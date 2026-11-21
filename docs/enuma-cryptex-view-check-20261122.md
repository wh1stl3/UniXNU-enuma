# r13 cryptex view and arm64 cache: offline check

Status: self-checked; no build, device access, or volume modification. The
donor architecture is the parent-provided iPad7,1/A10X arm64 assessment. An
arm64e ENOENT alone does not establish absence of an arm64 cache.

## r13 build configuration

`out/ufs-sm8250-launchd-keystore-20261122-r13/self-check/build-final/logs/cc1-includes-r13.log:8`
records the actual `kern_exec.c` compiler command with
`XNU_OWNER_CACHE_MOUNT=1` and `XNU_OWNER_UNION_SYSTEMOS=1`. Its source
`self-check/build-final/source/bsd/kern/kern_exec.c:7016,7056-7062,7093-7095`
gates the cache preparation and requests the native union mount on `/`.
This proves compile-time selection, not a successful runtime mount.
`XNU_OWNER_SYSTEMOS_MOUNT` is not present in that compiler command or these
source guards; an independent setting by that name cannot be established.

The r10 isolated build script
`out/ufs-sm8250-launchd-display-20261121-r10/self-check/build_kernel.py:131-143`
explicitly overrides the `kern_exec.o` macros to 1, including both flags,
and requires `CONFIG_UNION_MOUNTS 1`. r13's recorded compiler command
independently confirms the resulting values; these are not inferred from
board.toml or the packaging defconfig. The production planner
`scripts/enuma-production-recipe.py:40-41` specifies the two config values
as `y`; the separate CI final-link fixture
`scripts/ci/native_final_link.py:119-120` hardcodes both macros to `0`.
r13 is an isolated inherited diagnostic compilation, not that CI fixture.
The difference is their different explicit compilation inputs, not evidence
of a runtime configuration change. Runtime union success remains unverified.

## Offline OID/path evidence

The parent reports four SystemOS records named `dyld_shared_cache_arm64`,
two each under parent OID `0x14` and `0x30`. Those reports alone do not
identify the parents' names, current tree reachability, or paths. This
inspection did not locate a saved directory-record mapping or a readable
parent-chain scan result; therefore **both OID paths remain unresolved**.
Likewise the presence of `dyld_shared_cache_arm64.symbols` in either
directory, and correspondence to either expected path, cannot be established.
The parent report has not been independently reproduced here. A raw record
scan without active tree/snapshot resolution would not by itself prove a
live pathname.

## Proposed r14 lookup list

Probe directory and file separately, recording errno and file type:

* `/System/Cryptexes/OS/System/Library/dyld` and its
  `dyld_shared_cache_arm64`: candidate cryptex view; 0 means lookup exists,
  ENOENT means this pathname or an ancestor is absent, not why.
* `/System/Library/Caches/com.apple.dyld` and its
  `dyld_shared_cache_arm64`: candidate alternate view; same errno meanings.
* For each directory also probe `dyld_shared_cache_arm64.symbols`: 0 shows
  that name is visible; ENOENT is not proof the main cache is absent.
* `/System/Cryptexes/OS/System/Library/dyld/dyld_shared_cache_arm64e`:
  negative architecture control; ENOENT is expected but not proven for that
  exact path. Any other errno reports a different lookup failure.

These are candidate paths, not OID-resolved paths. A successful directory
lookup plus missing file can indicate a wrong basename or incomplete view;
missing directories can indicate an absent view or wrong path. Distinguishing
them requires a resolved active-volume path and mount-status evidence, not
errno alone. No r14 probe was built or run.
