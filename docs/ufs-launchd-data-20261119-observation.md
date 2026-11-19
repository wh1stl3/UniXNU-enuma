# `XNU_OWNER_DATA_MOUNT=1` + scratch Data seed — one device boot (r4), device result

## Latest: one `fastboot boot` of the r4 candidate (2026-11-19 22:09:26); early boot completed and launchd's bootstrap/ondemand domains came up with no panic (`self-checked`, record only)

2026-11-19. One device action was authorized and issued: a single
`fastboot boot out/ufs-sm8250-launchd-data-20261119-r1/boot.img` at 22:09:26, exit 0.
Nothing was flashed, no `fastboot continue`, no retry, no second boot.

Everything below about the device is **parent transcription of the user's video/photos**.
No still frame and no video of this run were handed to this round, `vision` did not read
the screen, and nothing was written into Git. The screen text is quoted as transcribed;
it has not been independently re-read.

This record was built without building, packaging, touching the device or modifying
`out/`. Host-side work was read-only re-hashing of the frozen r4 candidate and of the
seed file (section "What is verified here").

### Execution and timeline

Serial is deliberately withheld; the device was identified by model. Only one `fastboot`
command was issued, and only against that model.

| Time (+08:00) | Event |
| --- | --- |
| 22:09:23 | claim marker `.cache/ufs-launchd-data-r4-20261119.claimed` created atomically, 3 s before the boot |
| 22:09:26 | one `fastboot boot out/ufs-sm8250-launchd-data-20261119-r1/boot.img`, exit 0 |
| after boot | console kept printing launchd/userland lines for at least several minutes, no panic |

No `STOP:` line, no client timeout, no flash and no `continue`. The boot duration was not
recorded. The claim was consumed by that boot and is retained: it must not be opened,
deleted or replayed.

Boot arguments carried in the payload (`self-check/extracted/unixnu.toml`):

```
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2
```

Identical to r3: store mode 0, no `sheng-data-persist`, no `native-ufs-probe`, no
`sheng-smp`, no `armcpu-spi-ipi`. The seed travels as the payload's initrd, not as a
boot argument.

### Candidate identity (r4)

`out/ufs-sm8250-launchd-data-20261119-r1/` (not sealed, not deployed). Relative to r3:

| Item | r3 | r4 |
| --- | --- | --- |
| `XNU_OWNER_DATA_MOUNT` | 0 (Data block not compiled) | **1** (proved by `-dM`) |
| `XNU_OWNER_DATA_VOLUME_UUID` | undefined | **`62F1BC9E-4868-4CFF-BF7E-59AFCD474B4F`** (= seed APSB volume UUID) |
| payload Data initrd | none | `initrd = "Payloads/scratch-data.img"`, 1,142,976 B `c89592f8…0470` |
| cache/root/union/manifest macros | 1 | 1 (unchanged) |
| trust cache | 61,356 B `7416ca4f…7323a7` | byte-identical |
| boot-args | as quoted above | byte-identical |
| ADT `/defaults:vmm-present` | `01000000` | `01000000` (unchanged) |
| ADT delta vs r3 (excluding 256 B `random-seed`) | — | 2 added / 0 deleted / 0 changed: `/device-tree/chosen/memory-map:PackedRAMDisk`, `/device-tree/chosen:ephemeral-storage` |

Artifacts (SHA-256 from the frozen candidate, re-hashed this round):

| Artifact | Bytes | SHA-256 |
| --- | --- | --- |
| `boot.img` | 169,951,232 | `202597ce78623d3fb2917418b7d41d8d93db8567a568ad1394279f8e9a1e6900` |
| `payload.img` | 167,772,160 | `810950bd61936d397ca77fbdf703de48f4128d97fca5407d75246749cbcc8760` |
| `self-check/prelink.macho` | 124,624,896 | `3ba758425282ff99777b66baf6f283f811c6b0a9d327bdefe5aacc27d9179746` |
| `self-check/native.macho` | 91,781,080 | `933f4204f7f3126dd267310336d2768ba6b00f6b739dca332e37ca226d1ab1d9` |
| `self-check/extracted/kernel.macho.adt` | 14,048 | `91c0815d8a0bfb6ac03f4dbd6270f244407f2c2ff15aea48af99135f071afdf6` |
| `self-check/extracted/kernel.macho.trustcache` | 61,356 | `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7` |

Inputs: firmware FD `e524988b8a05f15847ffc991170de8a5e0ead607400421e0835084497a71bf1e`,
board DTB `42d36a005024e1a7c55cb5da077a13bb17e9fb9a79dc9dfac8a61cf1e182f698`, UniXNU
baseline `693f5d9cae8a408dd18b39f3f9fdc4228c934241`. `/chosen:root-matching` still names
the signed OS window `04769D26-2CA0-4825-B443-E2E5F88300F2`.

Two recorded side effects of `DATA_MOUNT=1` that are compiled in but not exercised:
the same patch region also carries the GPU addon / staged apps / cryptex view code
(30 new symbols, all gate off at runtime by boot arguments this payload does not pass),
and `unixnu/devicetree.py:328-329` adds `/chosen:ephemeral-storage = 1` when a seed is
present and `persistent_data` is not declared.

### Seed identity

`out/data-seed-macos-20261119/data.dbr`, 1,142,976 B
`c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470`; `DBRDISK1` logical
size 2,146,996,224 B (524,169 × 4096), 10 packed extents covering 279 non-zero pages,
container UUID `1BB8501A-9FA7-4616-B1B6-F64C245E8224`, volume UUID
`62F1BC9E-4868-4CFF-BF7E-59AFCD474B4F` (three APSB pages agree). Header, block count and
both UUIDs were re-read from the file this round; the 279-page count is the build round's
read-back. Generation route and limits:
[`data-seed-20261119-generation.md`](data-seed-20261119-generation.md).

The seed is **ephemeral**: it is a RAM-backed scratch volume attached from the initrd,
declared `ephemeral-storage = 1`, and has no store window behind it. Nothing written into
it can survive a reboot (see "What this is not" in the generation record).

### What the screen showed (parent transcription, not independently read)

- no `offline scratch Data mount failed` line at any point;
- `(boot) <Notice>: Early boot complete. Continuing system boot.`
- `(user/501) <Notice>: entering ondemand mode` / `created` / `entering bootstrap mode`;
- services attached one after another, each `SOURCE_ATTACH, code = 0`, pid 31 → 61
  (watchdogd / backboardd / sharingd / containermanagerd / bluetoothd / CommCenter …);
- `(pid/5 [SpringBoard]) uncorking exec source upfront` / `created` / `SOURCE_ATTACH`;
- `(system) <Notice>: exiting bootstrap mode`, `exiting ondemand mode`;
- `system`-domain services keep spawning: `notifyd[67]`, `ptpd[48]`,
  `iomfb_fdr_loader[64]` … `Successfully spawned` / `state: running`;
- no `panic` in the observed window (at least a few minutes of screen).

Also on screen, undetermined:

- `kpersona_find_by_type() failed … ESRCH` and `Unable to find persona with type 6`,
  in both the `user/501` and `system` domains, while the services still spawn;
- `decmprs.c:1894/1922: cluster_copy_upl_data err 14`;
- `Failed to bootstrap path: /System/Library/NanoLaunchDaemons`,
  `…/com.apple.tombf.bits_daemon.plist`, `/usr/AppleInternal/LaunchDaemons` (ENOENT).

### Criteria

| # | Criterion fixed before the round | Result | Basis |
| --- | --- | --- | --- |
| 1 | no panic in the observed window | **hit** | transcript: no `panic`; several minutes of continuous output |
| 2 | Data (scratch) volume mounted | **strong inference, not directly observed** | the r4 kernel panics on mount failure by design (`offline scratch Data mount failed: %d`); the boot reached `Early boot complete` — launchd itself running — with no such panic. No positive "mounted" line, no I/O against the volume, no volume-list line was captured |
| 3 | launchd early boot (bootstrap/ondemand domains) | **established** | `Early boot complete`, `entering bootstrap mode`, `SOURCE_ATTACH` for user and system domains, `exiting bootstrap mode`/`exiting ondemand mode` |
| 4 | service bodies stable | **not established** | `SOURCE_ATTACH, code = 0` only says launchd handed off; pid 31 → 61 says spawning continued, not that earlier services stayed up |
| 5 | launchd initialization complete | **not established** | no launchd completion milestone in the transcript; the window ends with services still spawning |
| 6 | display / pixel output | **no** | the console is still printing; GOP/legacy display is not in this payload and no render server or swap exists |
| 7 | persistence | **no** | host `fastboot boot`, nothing written to a boot slot, no cold start |
| 8 | formal stage 6 / stage 7 | **not passed** | `Early boot complete` is not "launchd initialized"; stage record stays 1–2 |

The single substantive difference from the 2026-11-18 root-mount boot (which panicked in
`Launchd(1) … Library not loaded: /usr/lib/libSystem.B.dylib`) is that launchd now runs
and reaches `Early boot complete`. Three changes separate the two images — r3's ADT
`vmm-present = 1`, and r4's `DATA_MOUNT=1` + seed initrd + `ephemeral-storage` — and
**this round does not attribute the change to any of them**. The absence of that panic
here is one observation, not a root-cause closure.

### The three undetermined phenomena

1. **persona type 6 (`kpersona_find_by_type` → ESRCH).** Appears in both domains and
   repeats, yet the services still get `SOURCE_ATTACH, code = 0`. Neither blocking nor
   harmless has been shown. Type 6's meaning in this OS build was not looked up this round.
2. **`Failed to bootstrap path: …` (ENOENT) for `NanoLaunchDaemons`,
   `com.apple.tombf.bits_daemon.plist`, `/usr/AppleInternal/LaunchDaemons`.** These may be
   paths that legitimately do not exist on this OS/device class, or missing volume
   content. Not determined this round; no attempt was made to create them.
3. **`decmprs.c:1894/1922: cluster_copy_upl_data err 14`.** Printed during the run. If
   `14` is a BSD errno it would be `EFAULT`, but that was not established for this call
   site, and the failing decompression stream was not identified. Repeated failures of a
   kext-side decompress could matter for graphics/input, but nothing was measured.

**Do not** hand-populate any of these paths or pre-seed the missing plists; that would
hide whether the volume content or the device tree is the actual input.

### Clock advancing slower than wall time

The user reports that screen timestamps advance noticeably slower than real time. A
measurement is in progress and there is no ratio yet. If the ratio turns out to be
significant, the first thing to check is the timebase (`timebase-frequency` in the ADT
`/cpus` node, `devicetree.py:354`, taken from the hardware DTS `cpus` node), and only
after that scheduler/physical-CPU throughput — i.e. distinguish "the clock runs slow" from
"one CPU is busy keeping up". Nothing in this round establishes either.

### What is verified here, and what is not

Verified on the host this round (read-only re-hash of the frozen candidate and the seed):

- `boot.img` = 169,951,232 B `202597ce78623d3fb2917418b7d41d8d93db8567a568ad1394279f8e9a1e6900`
- `payload.img` = 167,772,160 B `810950bd61936d397ca77fbdf703de48f4128d97fca5407d75246749cbcc8760`
- `prelink.macho` = 124,624,896 B `3ba758425282ff99777b66baf6f283f811c6b0a9d327bdefe5aacc27d9179746`
- `native.macho` = 91,781,080 B `933f4204f7f3126dd267310336d2768ba6b00f6b739dca332e37ca226d1ab1d9`
- `kernel.macho.adt` = 14,048 B `91c0815d8a0bfb6ac03f4dbd6270f244407f2c2ff15aea48af99135f071afdf6`
- `kernel.macho.trustcache` = 61,356 B `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7`
- `data.dbr` = 1,142,976 B `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470`,
  `DBRDISK1` v1 / page 4096 / logical 2,146,996,224 B / 10 extents, block 0 `NXSB`
  `block_size` 4096, `block_count` 524,169, container UUID
  `1BB8501A-9FA7-4616-B1B6-F64C245E8224`, three APSB pages carrying volume UUID
  `62F1BC9E-4868-4CFF-BF7E-59AFCD474B4F`

Not re-run here: the ADT read-back, the seed re-inspection and the packaging steps (they
are the r4 build round's `CHECKPOINT.md` §3–§5), and any build.

Device behaviour, from the transcription only:

- **Can** state that one `fastboot boot` of this exact image returned exit 0, once, and
  that the console showed launchd's early boot through the bootstrap/ondemand transition
  with no panic in the observed window.
- **Cannot** prove the Data volume mounted: the inference rests on "failure panics" plus
  "no panic", and no positive mount line or I/O was observed.
- **Cannot** prove any service is stable, that launchd finished initializing, that a
  shell/desktop exists, or that SpringBoard is running (pid 5 only *logged* about its
  exec source).
- **Cannot** prove the `libSystem`/preboot failure is gone for good, nor which of the
  three image changes (if any) moved the boot past it.
- **Cannot** prove persistence of any kind, nor that `ephemeral-storage` had any effect.
- **Cannot** read the three undetermined phenomena (persona 6, bootstrap-path ENOENT,
  `decmprs` err 14) as either harmless or blocking.
- **Cannot** make any timing claim about device speed; the clock observation is
  user-reported and unquantified.

Stage 6 stays **not passed**; mode 1/2 stay unauthorized; the default
`NoAccessPolicy`/`NoContract` and the formal stage record (1–2) are unchanged.

### Review trail

- The r4 candidate was built by the parent round and **has not been independently
  reviewed** (no reviewer/verifier run on this candidate diff). It changes one kernel
  macro, one generated UUID, one payload input and the resulting ADT delta, with the
  kernel body rebuilt only in the affected translation unit (`kern_exec.o`).
- This observation is a parent transcription with no `vision` re-read; it therefore has
  no independent second source, unlike the 2026-11-16 warm-capacity record.

### Claim and marker state

| marker | state |
| --- | --- |
| `.cache/ufs-launchd-data-r4-20261119.claimed` | created 22:09:23, **consumed**; retained, must not be accessed, deleted or replayed |
| `.cache/ufs-launchd-cache-mode0-20261119.claimed`, `…-r2-20261119.claimed`, `…-r3-20261119.claimed` | earlier rounds, consumed; same prohibition |
| `.cache/ufs-userdata-sparse-flash-20261118.claimed`, `ufs-userdata-root-write-20261118*` | untouched this round; consumed/retained with the same prohibition |
| r1/r2/r3 candidates under `out/ufs-sm8250-launchd-{cache,data}-20261119-*/` | not rebuilt, not re-booted |

### Reproduction conditions

Rerunning this observation requires a new authorization round and a new claim; the r4
claim is spent. What a rerun would have to capture to settle the open points:

1. a timestamped capture (video or serial) long enough to show whether pids/service names
   repeat and whether earlier services stay up, so "progress" and "respawn loop" can be
   told apart — plus the clock ratio against host time;
2. a positive Data-side line if one exists (volume list / mount / first write), otherwise
   an explicit statement that the driver prints none on success;
3. the `Failed to bootstrap path` set repeated verbatim with errno, so it can be compared
   against the OS's own expectations rather than guessed;
4. the ADT `/cpus` `timebase-frequency` actually consumed by this image.

Status: `self-checked`, record only. Single-run observation, no independent `vision`
read, no media retained, no stage promotion.
