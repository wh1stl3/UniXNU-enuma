# SM8250 warm UFS policy r2 read-only probe — device result

## Latest: one `native-ufs-probe=10` boot; every judged criterion hit (self-checked record)

2026-11-17. The user authorized one boot of the SM8250 warm-policy r2 candidate.
Exactly one `fastboot boot` was issued and it returned 0. The facts in this
document are parent-relayed (execution, timeline, claim state) plus an
independent `vision` read of two cropped photos, as described under "Evidence
sources". They are **not** an independent device re-run by this repository, and
no host tooling here re-read the image.

### Execution and timeline

Serial is deliberately withheld; the device was identified by model, not by
connection order. A second device (nuwa) appeared in `fastboot devices` and
received no command.

1. The enuma candidate was booted once from the frozen output directory, with no
   flash, no `continue`, no retry:

```
fastboot -s <enuma> boot out/ufs-sm8250-policy-20261117-r2/boot.img
```

| Time (+08:00) | Event |
| --- | --- |
| 23:15:28.531 | claim marker atomically created (`CreateNew`) |
| 23:15:33 | single `fastboot boot` returned, exit 0 |

No `STOP:` line, no client timeout, no second boot, no partition write, no
`fastboot continue`. The claim was created 4.5 s before the boot.

Boot arguments carried in the payload: `-v serial=3 rd=md0-ramblock pmgr=2
native-ufs-probe=10`. The package audit reports `contains_native_ufs_root=false`,
`contains_sheng_data_persist=false`, no initrd, fixed vendor FD
`e524988b…a71bf1e`.

### Candidate identity

All values below are from `candidate-manifest.json` and its artifact table;
nothing was rebuilt or re-sealed for this record.

| Item | Value |
| --- | --- |
| boot image | `out/ufs-sm8250-policy-20261117-r2/boot.img`, 203505664 B, SHA-256 `c756ef8202bc69ecf7e91ce9d603944d46671eb2006418fd666029b2f220a595` |
| candidate manifest | `candidate-manifest.json`, 3733 B, SHA-256 `c8b31dfa…79e5` |
| checkpoint | `CHECKPOINT.md`, 12653 B, SHA-256 `e93091c1…bb79` (39-item table corrected) |
| policy patch | `sm8250-policy.patch`, 111676 B, SHA-256 `40bcb76f…bee90` |
| source pin | `sourcepin.json`, 23646 B, SHA-256 `a851c62c…db53d` |
| component archive | `self-check/libShengUfs.a`, 511928 B, SHA-256 `372b2d59…58ef` |
| native | `self-check/native.macho`, 91751400 B, SHA-256 `62a2c185…bb2fc` |
| prelink | `self-check/prelink.macho`, 124596224 B, SHA-256 `340997d8…ae75a` |
| payload | `payload.img`, 201326592 B, SHA-256 `2e094735…0eb29` |
| base pin | `693f5d9cae8a408dd18b39f3f9fdc4228c934241` |

### Claim state

`.cache/ufs-sm8250-policy-r2-probe-device-attempt.claimed` was atomically
created at 23:15:28.531 (+08:00) and is **consumed**. It is retained and must not
be opened, deleted or replayed. Any further device observation needs a new round
name and a new per-round authorization.

### Final screen (verbatim)

The IOLog block and the panic block print the same six lines; the panic adds the
`panic(cpu …)` header, the `@NativeUfs.cpp:2597` tail and `MACH Reboot`.

```
NATIVE_UFS root check
dma=0xc8e10000 len=0x22000 contig=0x22000 owned=0xc007c000+0x20000000 usable=0xc8700000 check=PASS
old_utrl=0x99ff3000 old_utmrl=0x99ff4000 excl=4
userdata first=290000 last=3b037fa
block0 magic 2d3bcf96 0b0631bb ext4magic=4b26 ext4blocks=3772222880
manifest status=1 windows=0
panic(cpu 0 caller 0xfffffff00bfc1484): NATIVE_UFS root check
dma=0xc8e10000 len=0x22000 contig=0x22000 owned=0xc007c000+0x20000000 usable=0xc8700000 check=PASS
old_utrl=0x99ff3000 old_utmrl=0x99ff4000 excl=4
userdata first=290000 last=3b037fa
block0 magic 2d3bcf96 0b0631bb ext4magic=4b26 ext4blocks=3772222880
manifest status=1 windows=0 @NativeUfs.cpp:2597
MACH Reboot
```

### Field interpretation

Decoded against the reviewed candidate source in
`out/ufs-sm8250-policy-20261117-r2/` (`source/NativeUfs.cpp`,
`self-check/merged-source/RootLayout.h`, `self-check/merged-source/RootWarmAdopt.h`,
`self-check/merged-source/RootWarmTarget.h`) and the reviewer's reading of the
lines:

- `NATIVE_UFS root check` is the `probe == 10` success-path header
  (`NativeUfs.cpp:2562`). The panic below it is the same statement's terminal
  form (`NativeUfs.cpp:2580-2597`): the probe is designed to stop the machine
  after printing, so a panic here is the intended end of the run, not an
  unintended abort. Its five data lines are diagnostic only; nothing is mounted
  or written.
- `dma=0xc8e10000 len=0x22000 contig=0x22000`: the retained DMA buffer lives at
  `0xc8e10000`, 139264 B (`0x22000`), reported fully contiguous, so its end is
  `0xc8e32000`.
- `owned=0xc007c000+0x20000000`: the kernel-owned window, `[0xc007c000,
  0xe007c000)`. This is `gPhysBase` / `gPhysSize`, cross-checked in-source
  against `PE_state.bootArgs` and the ADT `/chosen:darwinboot-memory-size`
  value, and it matches the 2026-11-09 stage-4 on-device record
  (`DARWINBOOT … pa 0xC007C000`, `window 0x20000000 bytes`) exactly.
  `dma + len = 0xc8e32000 <= 0xe007c000`.
- `usable=0xc8700000`: the dynamic area after the kernel's static payload,
  `roundUp4k(topOfKernelData)`. The check requires `usable <= dma`, and
  `0xc8700000 <= 0xc8e10000` holds.
- `check=PASS`: all six mandatory conditions held before the first `bzero` /
  `cacheCivac` / doorbell: inside `owned`, inside `usable`, inside one physical
  DRAM bank, zero overlap with the 39 static reservation/hole ranges, zero
  overlap with the predecessor queue tables, zero overlap with the runtime
  excluded ranges.
- `old_utrl=0x99ff3000 old_utmrl=0x99ff4000`: the queue bases the predecessor
  UFS driver left in HC `UTRLBA`/`UTRLBAU` and `UTMRLBA`/`UTMRLBAU`, sampled
  read-only before the queues were stopped. Both sit in the low DRAM bank, far
  below `owned`'s base, so they cannot overlap the new window.
- `excl=4`: four runtime exclusion ranges were registered, in source order:
  the entries actually present under ADT `/chosen/memory-map` (this payload
  carries only `TrustCache`), the framebuffer range from `PE_state.video`, the
  predecessor `UTRL` page (1024 B span) and the predecessor `UTMRL` page
  (256 B span). `/reserved-memory` children, if enumerated on this path, would
  each add one more; the observed count of 4 matches the four above, and whether
  that node was present was not separately observed.
- `userdata first=290000 last=3b037fa`: the `userdata` partition's first and last
  0-based 4096-byte LBAs on LUN 0, taken from the LUN 0 GPT —
  `[2686976, 61880314]`. That is 59193339 blocks = 242455916544 B, which matches
  the independently recorded Android geometry (`userdata [2686976, 61880315)`,
  242455916544 B); `last` is inclusive, hence the one-count offset. This is the
  partition's location, not an identity check.
- `block0 magic 2d3bcf96 0b0631bb`: `magic0`/`magic1` are the first two
  little-endian 32-bit words of the partition's first block
  (`RootLayout.h:20`, read at `:152-153` as `le32 (gScratch)` and
  `le32 (gScratch + 4)`), i.e. raw bytes `96 cf 3b 2d bb 31 06 0b`.
  They are not `SHNGROOT` (`0x474e4853` / `0x544f4f52`, compared at `:157`), so
  no root image manifest is present. The 4 KiB read itself succeeded, which is
  the point of the field.
- `ext4magic=4b26`: the 16 bits at byte 1080 of the partition — i.e. the ext
  superblock magic field at 1024 + 0x38, which reads `0xef53` on a real Linux
  ext4 superblock (`RootLayout.h:21`, read at `:154`). `0x4b26` is therefore
  **not** a file system identity. `ext4blocks=3772222880`: `le32` at byte 1028,
  the ext `s_blocks_count_lo` offset (`RootLayout.h:22`, read at `:155`;
  `= 0xE0D78DA0`). Both fields exist only to let a future run distinguish a
  flashed manifest from a foreign first block. The partition holds an
  FBE-encrypted F2FS superblock, so these two ext4-offset reads decode ciphertext
  and carry **no file system meaning**; their values are expected, not a failure.
- `manifest status=1 windows=0`: `manifestStatus` 1 means "no manifest magic"
  (`RootLayout.h:19`), 2-7 being the specific validation failures. Since no root
  image was flashed, 1 is the expected value; `windows=0` follows because the
  window table is only parsed from a valid manifest.
- `panic(cpu 0 caller 0xfffffff00bfc1484)` … `@NativeUfs.cpp:2597` + `MACH
  Reboot`: the panic site is the probe's own success-path `panic`, whose
  statement spans `NativeUfs.cpp:2580-2597`; `MACH Reboot` is what the panic
  handler prints. This is designed terminal forensics, not a reboot that
  bypassed the check.

### Criteria and verdict

Judged against the criteria fixed before the boot in the 2026-11-17 handoff
(`docs/SESSION-HANDOFF-20261117.md`, whose pre-boot next-step text named
`NATIVE_UFS root check`, `userdata first=290000 last=3b037fa`, `block0 magic …`
and `manifest status=…` as hit conditions, and `bring-up failed:`, a bare
`root check:` failure, an SError or a reboot without the designed panic as
failure conditions).

| Criterion | Observed | Verdict |
| --- | --- | --- |
| terminal `NATIVE_UFS root check` header | printed (IOLog and panic copy) | hit |
| `userdata first=290000 last=3b037fa` | exact match | hit |
| `block0 magic …` present with values | `2d3bcf96 0b0631bb` | hit |
| `manifest status=…` present | `status=1 windows=0` | hit |
| DMA window inside owned/usable | `dma=0xc8e10000`, `owned=0xc007c000+0x20000000`, `usable=0xc8700000`, `check=PASS` | hit |
| designed terminal panic at `NativeUfs.cpp:2597` | present | hit |
| failure line `bring-up failed:` | absent | not hit (as required) |
| SError | absent | not hit (as required) |
| reboot without the designed panic | `MACH Reboot` follows the panic | not hit (as required) |

### Evidence sources

Two sources agree character for character on the twelve lines: one parent
transcription and one independent `vision` sub-session read of two crops (1:1
and 2×). The parent's first transcription had two errors — the `ext4blocks`
value and the last two hex digits of the panic caller — both corrected against
the `vision` read; the corrected text is what this document carries. Nothing in
this repository re-read the image itself.

- No video was recorded for this run. When a claim is that some line is absent,
  a still is weaker evidence than a video; here every judged criterion is a
  present line, so the stills suffice for the pass.
- Photo original: 231648 B SHA-256
  `9ff98d3ae97a70c4d2636c846a00ea990849fdec72b83f37c5141a227f29c7e3`,
  1440×1080.
- 1:1 crop: 129849 B SHA-256
  `5b8c75d42f5bb17b506bf45c0be7861c59c6c0031bd260db96b79f358dcb96a8`,
  1440×350, JPEG.
- 2× crop: 283584 B SHA-256
  `f0fa04f481de5c3f8e966248f22a21caed338bb2650ebf6cc8fac314531d7efc`,
  2880×700, JPEG.
- All three images exist only in a host temporary directory; they are not in Git
  and are not uploaded anywhere. This document carries hashes and conclusions
  only.

### Established

- The SM8250 warm takeover sequence reached its success terminal on this board:
  TR/TM stop → read-only dual-stream SMMU check → own contiguous DMA → NOP →
  QUERY/SSU → TUR → `gHost.ready`.
- The DMA buffer satisfied every ownership condition the candidate enforces, and
  the three `owned`/`usable` sources agree with the 2026-11-09 record.
- The LUN 0 GPT was parsed and the `userdata` partition's first 4 KiB block was
  read through the new DMA path with no controller or protocol error reported
  before the probe stopped.

### Not established

- Persistent root volume, Data volume or any persistent store; `SHNGROOT`
  window semantics. `manifestStatus=1` means no root image was examined at all.
- The `startRoot` path: `native-ufs-probe=10` stops inside the probe and never
  calls `startRoot`, `gStoreGeometry` or `IOFindBSDRoot`.
- Long-term DMA ownership across `ExitBootServices` and into user space, and
  completeness of the `UfsDxe` hardware retirement. The 2026-11-14 accepted
  residual risk — a vendor page freed back to `EfiConventionalMemory` before
  `AllocateWindow` without proven retirement — remains undetectable here.
- That the partition's first block is the expected encrypted F2FS superblock:
  only that a 4 KiB read succeeded and that its bytes are not an ext4 superblock
  or a `SHNGROOT` manifest.
- Anything about commands other than NOP/QUERY/SSU/TUR, or any write path.
- That a repeat boot would behave the same; no retry and no second boot was made.
- Any formal bring-up stage promotion; the stage record is unchanged.
- Default NoAccessPolicy / NoContract: unchanged.

### Reproduction conditions

- Host side: the frozen candidate directory can be re-checked with WSL root plus
  Python 3.11 using the commands in
  `out/ufs-sm8250-policy-20261117-r2/CHECKPOINT.md` §4 (patch replay into a
  fresh temporary tree, then `self-check/run_self_check.py --work-dir <fresh>`),
  without touching `r1` or the candidate itself. The base pin stays
  `693f5d9cae8a408dd18b39f3f9fdc4228c934241`.
- Device side: one enuma, identified by model before booting, a new per-round
  user authorization for the single `fastboot boot`, and a new authorization
  round name. The current claim is consumed, so the existing round cannot be
  replayed.
- Without a new authorization there is no reproduction path; this document does
  not grant one.
