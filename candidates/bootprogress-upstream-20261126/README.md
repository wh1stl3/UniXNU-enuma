# enuma · upstream BootProgress page candidate

Host-only r6 derivative; not a release or device authorization. The recipe
replays the reviewed r6 link with just `video_console.o` replaced. All other
objects, the CPU Legacy archive, PE/VC mapping, gate and transitions, validated
GUI first-frame release, and panic escape are r6. There is no imported upstream
worker, independent pixel writer, IRQ hook, GUI overlay, diagnostic resume,
forced halt, boot-log writer or device-side operation.

## Reference and field mapping

Reference: `UniXNU-sheng@c8f92b208068eeaa4cd2b0f592671f04ee70076e`,
`package/BootProgress.c` (`draw` at lines 250–513) and
`package/BootProgressDisplay.h`, both SPDX MIT. Not a nuwa asset. The external
`Font.h` used by the original painter is supplied from the existing enuma
Silicium framebuffer serial font
(`wh1stl3/uefi-enuma@964dffaae931e4eaddc9b4229d509227c02d5969`,
Android Open Source Project copyright and BSD-style terms retained in
`reference/Font.h`, SHA-256 `7749b211129f6f669f53fd9ee16b8e8dc9464aad41ba1bb6f7ce9b45c4eb2f1d`).
The top-left 48-row grid, 119 visible columns, 6×14 cells, original 5×12
glyph encoding, 3× scale threshold, black background, bar/section palette and
eight right-side slot positions follow the pinned page. The previously
observed enuma GOP geometry is **1600×2560**, so the original rule chooses
**1×**, with the diagnostic grid at top left rather than scaled or rotated.
Raster writes keep
r6's zero BGRX X byte; the reference's X byte is not part of visible RGB.

| Pinned page | enuma source and difference |
| --- | --- |
| 0: title, optional tag, deadline | Original live and continuous-deadline strings and blue bar, same `build-tag` input; 30 s idle / 120 s total from first refresh, not early PE. Deadline does not halt the OS. |
| 1: time / idle / IRQ / monitor / lost / root / proc count / free | Actual physical counter and refresh count; stage or UFS change counts as activity, not proof of forward progress. Real owner-root acceptance and VM free pages. Total IRQ, collector drops and process count are `n/a`, not inferred. |
| 2 and 46: UFS transport, verification, publication, timings | Existing r6 `native_ufs_*` counters, root probe/match/step/static failure and read/verification tick sums. No offline VirtIO source in this build. |
| 3: TCR, TTBR0/1, SCTLR; 4, 12–15: IRQ/PC | Real read-only ARM register sample on the refresh CPU; no interrupted-context PC/PSR/SP or sample ring. |
| 5–11: stage and history | Existing r6 kernel/BSD/pre-PID1 checkpoints. Timestamps are first observation on refresh; a stage not observed is not added. No per-process or upstream PE stage hooks. |
| 16–23: latest console / optional process-exit and UI modes | Latest seven XNU `msgbuf` lines, using a bounded 1 KiB copy under its existing nonblocking lock before any pixel lease; no new log hook, short/long lines clipped for the grid. Lock contention is shown as unavailable for that sample. Process exits/UI trace not collected. |
| 24–30, 38–41: process details, GIC, CPU frequency, clocks | No process walker or CPU-frequency collector. GIC fields come from existing `ArmCpu` snapshots; `CLK` is `CNTPCT`/`CNTFRQ` and `gPEClockFrequencyInfo`, not a wall-clock calibration. |
| 31–34, 44: display/PM/client/swap/frame data and GOP | Upstream observer entry points in r6 are not equivalent to live counters; rows say unavailable. Mapping VA, mapped length and initial boot-args PA are the same data that admitted the r6 map. No new interrogation of display hardware. |
| 35–36: memory/RAM disk | Same VM counters and `max_mem`; existing `native_ram_block_*` sparse capacity/residency and VM thresholds. |
| 37–38, 42: IRQ/SMP/timer | Existing ArmCpu IRQ phase/ID, quiesce/halt and SMP counters; timer/IPI values explicitly not total IRQ count. Timer/DAIF registers sampled on the refresh CPU. |
| 42–43, 47: touch, monitor/pulse | Existing HID report count is shown separately (41); no controller trace or pad overlay. XNU msgbuf dropped characters are not upstream collector drops. Bottom row is a refresh count, not an independent pulse. |
| 45: transport CMD/QUEUE cache | Upstream fields unavailable, no fresh controller sample. |
| Right extension slots | Existing Data persistence events/counters/first LBA, not a claim of persistent Data; no upstream key-store/GPU extensions are fabricated. Blank slots remain black. |
| Panic / post-handoff | No sheng panic-buffer sampler, touch painter or crash banner; r6 actually relinquishes the panel and uses stock panic handling. |

All values shown together are asynchronous samples, not an atomic hardware snapshot.

## Reproduce

From the device repository, run in WSL as root for the existing local r6 inputs:

```sh
/home/wh1stl3/.local/bin/python3.11 \
  candidates/bootprogress-upstream-20261126/build.py \
  out/bootprogress-upstream-independent-20261126
```

`commands.json` captures exit status and commands. `reference-blocks.json`
identifies exact upstream `draw()` blocks exercised with synthetic inputs.
`upstream-selected-rows.ppm` renders those blocks with the original upstream
`bp_line_bg` and extension renderer; unexecuted original rows are **not**
represented. `enuma-candidate.ppm` renders the candidate sampler (synthetic
registers and msgbuf contents) and actual raster. The test compares visible
RGB only for shared valid rows, records whole-image differences, and checks
differential vs fresh paint and padded-pitch clipping. `test-screen.log` and
`test-host.log` cover the unchanged r6 display transaction/lease tests.
`final-abi.json` checks final display ABI against r6; `bootprogress-manifest.json`,
`boot.json`, `provenance.json` and `embedded.toml` record what was packed. No
host test asserts that device timing, logs, pixels or GUI operation have been
observed.

## Built candidate — self-checked

Output: `out/bootprogress-upstream-20261126-r5/`.

| Artifact/check | Result |
| --- | --- |
| `boot.img` | 169,951,232 B; SHA-256 `52c7232d4f74c67fc5ac3f102f47589c41482911bab0e6d4b51e871dd44f2e36` |
| Embedded payload | 167,772,160 B; SHA-256 `6c66b376a0ebb1c7c515b9f0678498fd2833ff9318b263a2c6dfc642b235f1b5` |
| Embedded prelink | SHA-256 `60ea4af0094b6e9635ba5e39ec2e35122dfe5d7a98a864e3114017fd4387cb8e`; native/prelink undefined lists empty; final 358 slots requalified |
| Parameters | `embedded.toml` byte-identical to r6 (`boot-progress=2`, no new argument); payload member list, scratch seed and other members unchanged; Android v1 header, kernel address `0x8000`, tags `0x1e00000`, same FD/DTB |
| Offscreen ASan/UBSan | 1600×2560: 189,924 identical RGB samples from shared rows, 14,179 whole-image differences (including the unexecuted original rows); differential output equals fresh paint; narrow 256×128 clipping and pitch padding pass |
| Display ASan/UBSan | Existing r6 gate/lease and generated PE/VC replay tests pass; extracted kernel retains the reviewed call edges, with no upstream writer symbols |

The r6 `boot.img` hash was rechecked unchanged after the build. The PPMs are
offscreen renders, not device captures; original whole-page behavior and
real panel output were not verified.
