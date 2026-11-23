# r61 dual-core host repack — 2026-11-24

Status: self-checked; no device operation or independent verification. The r58 kernel still contains diagnostic code; removing its arguments disables the selected entry points, not the code itself. Default board configuration is unchanged.

## Sources and scope

`UniXNU/docs/zh/devices/alioth.md:151,155,159` describes kona PSCI, `sheng-smp=1 armcpu-spi-ipi=1 armcpu-self-ipi=1 armcpu-diagnostics=1`, and the two SoC patches. The r58 build tree `.cache/xnu-work/osfmk/arm64/machine_routines.c:1002-1015,1030-1060,1252-1262` selects a maximum total with `cpus=`, preserving the boot CPU, and returns -1 for excluded CPUs. `drivers/ArmCpu/ArmCpu.cpp:210-227,482-495,530-535` rejects excluded CPU nubs and starts registered secondary CPUs. `cpus=2` therefore selects boot CPU plus one secondary in this source; no claim of successful startup.

The r58 `native-link.map:316,321,1024,48836,52146` includes `start.o`, `machine_routines.o`, `libArmCpu.a(ArmCpu.o)`, the cluster patch's `_thread_group_set_default_preferred_clusters`, and `_ml_parse_cpu_topology`. The corresponding build tree `board_config.h:136-138,163-168` includes the secondary patch's eight CPUs and cluster patch override to two clusters. Link map identifies objects/symbols, not patch provenance by itself; no fresh object rebuild was done. r58 ADT has cpu0 through cpu7 and no cluster-type string. No ADT change was made.

## Arguments

Removed: `enuma-fx-diag=1 enuma-bp=1 enuma-fb-fill=1 enuma-th=1 enuma-txpeer=1`.

Added: `sheng-smp=1 armcpu-spi-ipi=1 armcpu-self-ipi=1 cpus=2 armcpu-diagnostics=1`.

Read back from the payload embedded in `boot.img`:

```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1 dk=0 sheng-smp=1 armcpu-spi-ipi=1 armcpu-self-ipi=1 cpus=2 armcpu-diagnostics=1
```

The script asserts exact string transformation, including unchanged order and bytes for all remaining arguments.

## Mechanical evidence

Built with WSL `/home/wh1stl3/.local/bin/python3 scripts/build-enuma-r61-smp2.py --r61`. `boot.img` 169951232 bytes, SHA-256 `6f13c3b5ca3139309019ff966214a1f13acaa819bb8b928a42998452ffde015b`; size delta vs r58 0. r58 `boot.img` remains `e65ad679a1f13adb22012cb825e85deacb741be7cddd8cdc46737e7d838ea285`; all five input artifact hashes checked before and after.

Payload member SHA-256 before → after:

| Member | r58 | r61 |
|---|---|---|
| `unixnu.toml` | `81b7a7019eb0b3579fe3d1364e55461e9dc37fa73dc8b5838a4924c6ae3c3613` | `6eb38a56d0f98dd23898d39bdd39539afe95c2eca9cde4d3fb0da0767c9359ab` |
| `Payloads/kernel.macho.adt` | `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457` | same |
| `Payloads/kernel.macho` | `efe29d1405477dab01b98c5f1a3012f823760fbdcd395f661cdefe55eba71dd5` | same |
| `Payloads/kernel.macho.trustcache` | `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7` | same |
| `Payloads/scratch-data.img` | `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470` | same |

ADT byte comparison matches; native and prelinked Mach-O `llvm-nm -u` and symbol-table checks find zero undefined including weak. The payload tree is unchanged, the embedded payload hash matches, and `unixnu.toml` differs only in the boot-args replacement. Manifest in the output contains all input/output hashes and sizes.

## Interpretation, risk, rollback

| Screen observation | Interpretation |
|---|---|
| A separately established per-CPU online/running count of 2 or explicit secondary-running evidence | Supports the secondary having started; identify the source and CPU before claiming it. |
| Panic, freeze, reset, or no progress | Failure of this attempt, not by itself proof of the failing component or secondary CPU state. |
| Normal progress with no CPU-specific evidence | Does not prove the secondary started. |

This r58 ArmCpu `ArmCpu.cpp:404-406,619,784` uses `armcpu-diagnostics=1` for diagnostic panic conditions; it does not establish a positive screen line reporting that the secondary ran.

Secondary startup can hang or panic; GIC redistributor and IPI delivery have not been verified on enuma. Moving from one to two CPUs changes scheduling and concurrency assumptions. Deep review of the inherited startup and concurrency paths remains pending.

Rollback is the unchanged r58 artifact (`out/ufs-sm8250-rxpid-20261123-r58/boot.img`); restoring a flashed slot requires a separate explicit device-write authorization. No device boot, flash, claim access, runtime CPU count, positive IPI evidence, independent verifier run, or stage promotion occurred.
