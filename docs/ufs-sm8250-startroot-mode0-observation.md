# SM8250 mode 0 startRoot diagnostic — device result

## Latest: one `native-ufs-root=1` (store mode 0) boot; warm bring-up hit, manifest gate rejected as expected (self-checked record)

2026-11-18. One boot of the `ufs-sm8250-startroot-mode0-20261118-r1` candidate was
authorized and issued once; it returned 0. Everything in this document is
parent-relayed — execution, timeline, claim state and the final screen are a
single parent transcription with **no `vision` re-read, no video and no stills**,
and **neither the candidate nor this observation was independently reviewed or
re-verified**: that channel was unavailable this round. No host tooling here
re-read any image.

### Execution and timeline

Serial is deliberately withheld; the device was identified by model. nuwa did not
appear in any device list this round and received no command.

1. The enuma candidate was booted once from its frozen output directory, with no
   flash, no `continue`, no retry:

```
fastboot -s <enuma> boot out/ufs-sm8250-startroot-mode0-20261118-r1/boot.img
```

| Time (+08:00) | Event |
| --- | --- |
| 19:44:03.7 (approx.) | claim marker atomically created, 5.3 s before the boot |
| 19:44:09 | single `fastboot boot` returned, exit 0 |

No `STOP:` line, no client timeout, no second boot, no partition write, no
`fastboot continue`.

Boot arguments carried in the payload: `-v serial=3 rd=md0-ramblock pmgr=2
native-ufs-root=1 sheng-pmgr=2`. No `sheng-data-persist` (store mode 0), no
`native-ufs-probe`, no initrd (per the candidate `CHECKPOINT.md`). This is the
first run of this series that actually enters `startRoot`; the 2026-11-17 probe
stopped inside `native-ufs-probe=10` and never reached it.

### Candidate identity

All values below are from the candidate directory as reported to this
repository; nothing was rebuilt or re-sealed for this record.

| Item | Value |
| --- | --- |
| boot image | `out/ufs-sm8250-startroot-mode0-20261118-r1/boot.img`, 169,951,232 B, SHA-256 `28746ac9110573558200ec41ea7458ab45265a9988088f13e143fdab62654bf4` |
| payload | `payload.img`, 167,772,160 B, SHA-256 `86c32003…bd3f98` |
| candidate manifest | `candidate-manifest.json`, 10,169 B, SHA-256 `2cc9487a…2c2f20` |
| checkpoint | `CHECKPOINT.md`, 6,816 B, SHA-256 `c536632a…e8855d` |
| RamBlock patch | `ramblock-mode1.patch`, 11,641 B, SHA-256 `8fc7f36e…223952` |
| prelink (kernel) | `prelink.macho`, 124,596,224 B, SHA-256 `21f32613…4a73f` |
| native | `native.macho`, 91,752,608 B, SHA-256 `09992a4a…ca5e1` |
| base pin | `693f5d9cae8a408dd18b39f3f9fdc4228c934241` |

`boot.img` is 31,375,360 B under the `boot_a`/`boot_b` capacity of 201,326,592 B.
That headroom was not exercised: this was `fastboot boot`, which does not write a
slot.

### Claim state

`.cache/ufs-sm8250-startroot-mode0-probe-device-attempt.claimed` was atomically
created 5.3 s before the boot and is **consumed**. It is retained and must not be
opened, deleted or replayed. Any further device observation needs a new round
name and a new per-round authorization.

### Final screen (verbatim)

Transcribed by the parent from the last screen. The first block is cut off in the
transcription where the line wrapped (`t></dict>` is the transcription cut of
`…88300F2</string></dict></dict>`, not literal output).

```
Waiting on <dict ID="0"><key>IOProviderClass</key><string ID="1">IOMedia</string><key>IOPropertyMatch</key><dict ID="2"><key>UUID</key><string ID="3">9071148B-B025-402D-AD7A-4846
t></dict>
NativeUfs: warm bring-up ready (dma=0xc8a10000 len=0x22000 contig=0x22000 owned=0xc007c000+0x20000000 usable=0xc8700000 check=PASS old_utrl=0x99ff3000 old_utmrl=0x99ff4000 excl=4 …
NativeUfs: no valid root manifest in userdata (first=0x290000 last=0x3b037fa status 1, magic 2d3bcf96 0b0631bb)
Still waiting for root device
```

The `…` at the end of the warm line is the transcription's ellipsis; the source
statement (`source/NativeUfs.cpp:2882-2892`) prints the nine fields shown and
nothing after `excl`.

### Field interpretation

- `NativeUfs: warm bring-up ready (…)` is the success terminal of the warm
  takeover, printed at `source/NativeUfs.cpp:2882` after `startRoot` set
  `native_ufs_root_step = 2` (`:2893`): TR/TM stop → read-only dual-stream check →
  own contiguous DMA → NOP → QUERY/SSU → TUR → `gHost.ready`. Unlike the
  2026-11-17 probe this line is **not** followed by a designed panic; the run
  continues into the root-layout path.
- `dma=0xc8a10000 len=0x22000 contig=0x22000`: the retained DMA buffer is at
  `0xc8a10000`, 139,264 B, fully contiguous, ending at `0xc8a32000`.
  **The address differs from the 2026-11-17 probe (`0xc8e10000`) because the
  candidate does not fix a base address**; it allocates and then checks. The
  invariants are unchanged: `usable=0xc8700000 ≤ dma=0xc8a10000`, and
  `dma_end=0xc8a32000 ≤ owned_end=0xe007c000`.
- `owned=0xc007c000+0x20000000`: the kernel-owned window `[0xc007c000,
  0xe007c000)`, i.e. `gPhysBase`/`gPhysSize`, unchanged from the 2026-11-09
  stage-4 on-device record and the 2026-11-17 probe.
- `check=PASS`: every mandatory condition held before the first DMA write — inside
  `owned`, inside `usable`, inside one physical DRAM bank, zero overlap with the
  static reservation/hole ranges, zero overlap with the predecessor queue tables,
  zero overlap with the runtime excluded ranges.
- `old_utrl=0x99ff3000 old_utmrl=0x99ff4000 excl=4`: the predecessor queue bases
  sampled read-only, and four runtime exclusion ranges registered (memory-map
  entries present in this payload, the framebuffer range, the predecessor `UTRL`
  page and the predecessor `UTMRL` page). Values match the 2026-11-17 probe.
- `no valid root manifest in userdata (first=0x290000 last=0x3b037fa status 1,
  magic 2d3bcf96 0b0631bb)`: this is the `layout->manifestStatus != 0` branch at
  `source/NativeUfs.cpp:2903-2910`. `first`/`last` (0-based 4 KiB LBAs
  `[2686976, 61880314]`, 242,455,916,544 B) are the `userdata` partition taken from
  the primary LUN 0 GPT and agree with the 2026-11-17 probe and the recorded
  Android geometry. `magic` are the first two little-endian 32-bit words of the
  partition's first block (`96 cf 3b 2d bb 31 06 0b`) — not `SHNGROOT`
  (`0x474e4853`/`0x544f4f52`), so `manifestStatus` 1 ("no manifest magic",
  `RootLayout.h:156-219`) is the **expected input for a partition that never
  carried a manifest**, not a defect. The gate then logs, calls
  `rootDiagnosticFailure` and returns false: no window preparation, no
  `IOService::start`, no publication (`:2920-2927`).
- `Still waiting for root device`: with `startRoot` having returned false, no root
  media exists to match, so the rootwait is the expected terminal. It is the same
  terminal the GOP r5 run reached for an unrelated reason (no render/root media).
- `Waiting on … UUID 9071148B-B025-402D-AD7A-48464D8B5FFF`: the root-match UUID the
  boot is waiting on. It is the value recorded in the working-tree
  `board.toml:97` `root_match_volume_uuid` and in ADT `root-matching` — the
  **restore ramdisk** APFS UUID. See correction 2.

### Criteria and verdict

Judged against the criteria fixed before the boot (warm-takeover success line
present, manifest gate reached and rejected with a non-`SHNGROOT` first block,
terminal rootwait, and none of: `bring-up failed:`, an SError, an unintended
panic).

| Criterion | Observed | Verdict |
| --- | --- | --- |
| `NativeUfs: warm bring-up ready (…)` success line | printed | hit |
| DMA window inside `owned`/`usable` | `dma=0xc8a10000`, `owned=0xc007c000+0x20000000`, `usable=0xc8700000`, `check=PASS` | hit |
| predecessor queues reported, `excl=4` | `old_utrl=0x99ff3000 old_utmrl=0x99ff4000`, `excl=4` | hit |
| `userdata` geometry from the primary GPT | `first=0x290000 last=0x3b037fa` | hit |
| first block read, no `SHNGROOT` magic | `magic 2d3bcf96 0b0631bb`, `status 1` | hit (expected rejection) |
| no window/publication path entered | no window, no volume, no mount line | hit (rejection ran first) |
| terminal `Still waiting for root device` | printed | hit |
| failure line `bring-up failed:` | absent | not hit (as required) |
| SError | absent | not hit (as required) |
| unintended panic | absent | not hit (as required) |

### Two corrections

1. **A mode 2 store does not write the root manifest.** The mode 2 store window is
   located at the **tail** of `userdata`; the root manifest lives in the
   **first** block. The sentence "writing `SHNGROOT` needs mode 2" is therefore
   wrong: such a store cannot place a manifest at block 0 at all. The next step is
   **not** opening mode 2 — it is producing a first diagnostic root image with a
   legal manifest plus matching owner policies, and only after that the Data store
   owner-authenticated placement binding.
2. **This run's `9071148B-…` rootwait does not show that a UFS OS root matched.**
   `9071148B-B025-402D-AD7A-48464D8B5FFF` is the restore ramdisk APFS UUID in the
   working-tree `board.toml:97` and in the ADT `root-matching` property; the
   recorded OS window UUID is `04769D26-2CA0-4825-B443-E2E5F88300F2`
   (`scripts/enuma-production-recipe.py:17`; observed once as a rootwait target in
   `docs/enuma-gop-r5-device-observation.md:70`). Because `startRoot` rejected
   before publishing anything, the rootwait only shows the boot waiting on the
   configured UUID. A future run must make the root-match UUID and the signed OS
   UUID agree before any root-match conclusion is drawn.

### Established

- The warm takeover sequence reached its success terminal on this board **with
  `native-ufs-root=1` in effect**, i.e. from `startRoot` internals rather than a
  probe.
- The DMA buffer satisfied every ownership condition the candidate enforces
  (`owned`/`usable`/DRAM/reservation/predecessor-queue/exclusion checks), with the
  allocation address differing from the previous run as expected.
- The primary LUN 0 GPT was parsed, the `userdata` partition's first 4 KiB block
  was read through the DMA path, and the manifest gate then fired **in order** and
  rejected with the documented non-zero status.

### Not established

- `SystemOS`/`OS` window publication, volume ready, root mount, persistent root,
  Data volume, any persistent store, and any write capability. The run rejected at
  the manifest gate by design; nothing was mounted.
- That the **backup** GPT is valid — only the primary table's values were
  consumed.
- Long-term DMA ownership across `ExitBootServices` and into user space, and
  completeness of the `UfsDxe` hardware retirement (2026-11-14 accepted residual
  risk unchanged).
- Any UFS OS root match (correction 2).
- That a repeat boot would behave the same; no retry and no second boot was made.
- Any formal bring-up stage promotion; the stage record is unchanged.
- Default NoAccessPolicy / NoContract: unchanged. mode 1 and mode 2 remain
  unreleased.

### Evidence limits

- **Not independently reviewed**: the candidate (mode 0 build, `ramblock-mode1.patch`
  and the packaging) and this observation record have no independent reviewer or
  verifier rerun; the review channel was unavailable. Treat the `self-checked`
  label as the implementer's own.
- **One transcription, not checked by a second source**: the final screen was read
  by the parent only. There was no `vision` re-read, no video and no still; when a
  criterion is "a line is absent" a transcription is weaker than a video, and none
  of the absence criteria here can be strengthened by a still afterwards.
- No image, still or video from this run exists in Git or anywhere else; this
  document carries the transcription and artifact hashes only.

### Reproduction conditions

- Host side: the candidate directory can be re-checked with the commands in
  `out/ufs-sm8250-startroot-mode0-20261118-r1/RATIONALE.md` §"复跑" (full
  `run_self_check.py --rerun-wip-suites` plus a standalone replay of
  `ramblock-mode1.patch` into a fresh temporary tree), without touching `r1`/`r2`/
  `r3`/`r5`. `run_packaging.py --seal` rewrites `payload.img`/`boot.img` and the
  manifest, and the ADT carries a 256 B `random-seed`, so **the hashes above are
  not reproducible** — only the current directory's bytes match them.
- Device side: one enuma identified by model before booting, a new per-round user
  authorization for the single `fastboot boot`, and a new round name. The current
  claim is consumed, so this round cannot be replayed.
- Without a new authorization there is no reproduction path; this document does
  not grant one.
