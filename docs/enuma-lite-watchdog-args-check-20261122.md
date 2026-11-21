# r17 lite/watchdog boot-arg check — 2026-11-22

Status: self-checked, read-only host inspection; no boot or runtime validation.
UniXNU checkout HEAD `693f5d9cae8a408dd18b39f3f9fdc4228c934241`.

## Source

Search of UniXNU `kits/`, `drivers/`, `patches/` for the requested terms
found no `sheng-lite`, `lite=`, `disable-watchdogd` or `data-persist`
parser there. `drivers/ArmCpu/ArmCpu.cpp:222-224` parses `sheng-smp`
and declines secondary CPU nubs unless enabled; `:439-442` parses it
again along with `sheng-smp-gic` for CPU startup. A watchdog label in
`drivers/QcomBaseband/platform/coachz/patches/coachz-prelink-baseband.patch:163`
is not a sheng boot-argument parser.

The source-storage builder `UniXNU/scripts/build-sheng-source-storage.py:185,204`
selects a device-provided `BootWatchdogPolicy.c`; it is not supplied by the
three UniXNU source directories searched. Thus enabling that mechanism requires
an appropriate device policy implementation, link inclusion and a reachable
post-Data-mount call site, not merely a boot argument. Its exact compatible
implementation, build switches and call site for enuma have not been established.
The donor description mentions disabled launchd jobs, but the service list for
the relevant donor revision is not established from UniXNU source; no list is
asserted for r17.

For comparison only, the older enuma isolated source
`out/owner-data-query-20261113-r3/source-ufs/NativeUfs.cpp:1444-1447,1486`
describes `sheng-data-persist` modes 0/1/2 and parses values up to 2; it
is not proven to be r17's exact compiled source. Mode 1 is read-only window
qualification, mode 2 opens writes (UniXNU `docs/zh/xnu/boot-arguments.md:73`).
Neither mode is authorized by this analysis.

## r17 final images

`strings` and `llvm-nm` on
`out/ufs-sm8250-launchd-keystore-20261122-r17/self-check/build-final/`
show:

| Exact string / relevant symbol | native.macho | prelink.macho |
|---|---|---|
| `sheng-lite` | absent | absent |
| `sheng-disable-watchdogd` | absent | absent |
| `watchdogd` | absent | present (`watchdogd`, `defang_watchdogd`, `/usr/libexec/watchdogd`) |
| `sheng-data-persist` | present | present |
| `sheng-smp`, `sheng-smp-gic` | present | present |
| `lite=`, `smp=` | absent | absent |
| `ArmCpu::probe` | present | present |
| `NativeUfs::startRoot` | present | present |
| symbol containing `BootWatchdogPolicy` | absent | absent |

Command: `strings FILE | grep -Ei 'sheng-lite|disable-watchdogd|watchdogd|data-persist|sheng-smp|lite='`;
`llvm-nm FILE | grep -Ei 'BootWatchdogPolicy|watchdogd|ArmCpu.*probe|NativeUfs.*(start|Store)'`.
Additionally checked `strings FILE | grep -F 'smp='`. Generic watchdog
strings and IOWatchDogTimer symbols do not establish either requested parser.
String/symbol presence alone is not runtime evidence; missing symbols alone
cannot rule out optimized or differently named code. The exact parser strings
are absent in both images.

## Actual payload readback

`mtype -i out/ufs-sm8250-launchd-keystore-20261122-r17/payload.img
::/EFI/UniXNU/unixnu.toml` reads the xnu entry, whose tokens are:

`-v` `serial=3` `rd=md0-ramblock` `pmgr=2` `native-ufs-root=1`
`sheng-pmgr=2` `offline-mobile-graphics-load=1` `offline-legacy-register=1`
`offline-legacy-phase=4` `offline-legacy-gop=1` `offline-legacy-pm=1`
`offline-legacy-validate=1` `offline-legacy-transfer=1`
`offline-legacy-cpu-present=1` `sheng-vsync=60` `sheng-aks=1`.

Missing: `sheng-lite`, `sheng-disable-watchdogd`, `sheng-data-persist`,
`sheng-smp`. The xnu entry points at `Payloads/kernel.macho` and
`Payloads/scratch-data.img`.

## Decision

r17 does not show the lite/watchdog parser strings; adding only those two
arguments is not established to do anything. A suitable policy component
and connected call path must first be established and compiled/linked.
`sheng-lite`'s exact service effect is unknown for the requested donor version;
even with a policy component, launchd policy consumption and Data prerequisites
need separate validation. No SMP or persistence change is proposed.
