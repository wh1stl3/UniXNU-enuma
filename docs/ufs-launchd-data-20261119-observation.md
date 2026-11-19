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
| 2 | Data (scratch) volume mounted | **design implication + observation, no positive log and no I/O** (recorded as "strong inference" on 11-19; upgraded by binary-level reading, see the 2026-11-20 section) | the r4 kernel panics on mount failure by design (`offline scratch Data mount failed: %d`, one of 5 `_panic` branches in `_load_init_program`); the boot reached `Early boot complete` — launchd itself running — with no such panic. Still no positive "mounted" line, no I/O against the volume, no volume-list line was captured |
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
   **追加（2026-11-20 二轮离线核验）**：type 6 = `PERSONA_SYSTEM_PROXY`（`bsd/sys/persona.h:45`，
   枚举 `:35-51`）。ESRCH 只说明内核里没有该类型的 persona；**阻塞还是无害仍未定性**。
2. **`Failed to bootstrap path: …` (ENOENT) for `NanoLaunchDaemons`,
   `com.apple.tombf.bits_daemon.plist`, `/usr/AppleInternal/LaunchDaemons`.** These may be
   paths that legitimately do not exist on this OS/device class, or missing volume
   content. Not determined this round; no attempt was made to create them.
   **追加（2026-11-20 二轮离线核验）**：两卷卷内都查过，三条路径都不存在，卷内也没有任何 plist
   引用它们——按「donor 本就缺失的预期噪声」处理，见文末「二进制级判读升级」第 5 条。
3. **`decmprs.c:1894/1922: cluster_copy_upl_data err 14`.** Printed during the run. If
   `14` is a BSD errno it would be `EFAULT`, but that was not established for this call
   site, and the failing decompression stream was not identified. Repeated failures of a
   kext-side decompress could matter for graphics/input, but nothing was measured.

**Do not** hand-populate any of these paths or pre-seed the missing plists; that would
hide whether the volume content or the device tree is the actual input.

### Clock advancing slower than wall time

The user reports that screen timestamps advance noticeably slower than real time. Measured
afterwards from the same recording (no new device run): over 157.3 s of wall time the
**on-screen displayed timestamps** advanced 0.646 s, i.e. a **display-timestamp advance
ratio ≈ 0.0041 (about 1/243)**. That is a statement about the displayed timestamps only —
**not** "the XNU clock runs 243× slow". The per-segment ratio fluctuated between `0.00005`
and `0.026`, one segment went backwards (−7.45 ms), and one `Flushed 52 logs` line carried
a display time about 60 s ahead of its neighbours, **source and timebase undetermined**
(the evidence does not show that user-space and kernel log lines come from different
timebases). A second observation group — 31 µs of log time spanning about 5 s, ≈ 1/161,000
— is three orders of magnitude off the overall ratio, so the two groups did not measure the
same layer and must not be combined.

The ADT **input** value is correct: `cpu0` is `state=running` with
`timebase-frequency=19200000` (`0x0124F800`), the other seven CPUs are `waiting`, and
`pe_identify_machine.c:57-82` consumes it in place of the 24 MHz default. That only rules
out "the ADT carries the wrong frequency". The runtime callback value, `rtclock_sec_divisor`
and the output-layer conversion were never read back, so **a timebase/conversion error is
not excluded**, and neither is a slow scheduler/one busy CPU. Nothing in this round
establishes which layer is wrong.

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
  "no panic", and no positive mount line or I/O was observed. (2026-11-20: the binary shows
  that these two `_mount` calls have only panic exit paths, which makes the implication
  sound for both the SystemOS union mount and the scratch Data mount — still no I/O and no
  positive log; see the section at the end of this file.)
- **Cannot** prove any service is stable, that launchd finished initializing, that a
  shell/desktop exists, or that SpringBoard is running (pid 5 only *logged* about its
  exec source).
- **Cannot** prove the `libSystem`/preboot failure is gone for good, nor which of the
  three image changes (if any) moved the boot past it.
- **Cannot** prove persistence of any kind, nor that `ephemeral-storage` had any effect.
- **Cannot** read the three undetermined phenomena (persona 6, bootstrap-path ENOENT,
  `decmprs` err 14) as either harmless or blocking.
- **Cannot** make any timing claim about device speed: the only number is the on-screen
  timestamp advance ratio measured off the recording (≈ 1/243, see above), which says
  nothing about how much work per second actually executed.

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
4. the ADT `/cpus` `timebase-frequency` this image consumes **and what is derived from it
   at runtime** (`rtclock_sec_divisor`, the output-layer conversion) — the ADT input alone
   does not settle the layer.

Status: `self-checked`, record only. Single-run observation, no independent `vision`
read, no media retained, no stage promotion.

## 二进制级判读升级（2026-11-20，二轮离线核验）

这一节是 2026-11-20 二轮离线核验的**追加判读**，不改上面 11-19 的原始转录与初判；只有两处按本节
修正了措辞（判据表第 2 行、`Cannot` 里的 Data 一条），已在原处标注。本轮无构建、无设备动作、
无 claim、未写 `out/`，所有核对都是主机只读。

### 1. `_load_init_program` 的内联顺序（r4 内核，`0xfffffff00bd09b4c`）

主控侧 reviewer 的二进制级核读（本节只记录它的结论，不重新论证）给出的顺序：

```
_native_verified_block_root_authorized
_native_verified_block_volume_device
_native_owner_publish_boot_manifest
_commpage_update_dyld_flags
_mount SystemOS 8846FE78-2910-4297-AF97-D59BB6F8FC16 -> "/"  (MNT_RDONLY|MNT_UNION)
_mount scratch Data 62F1BC9E-4868-4CFF-BF7E-59AFCD474B4F -> "/private/var"
_memorystatus_init_at_boot_snapshot
exec
```

两个 `_mount` 之后没有「失败但继续」的返回路径：失败串
`"offline owner SystemOS mount failed: %d"`（内核映像 offset 74104813）与
`"offline scratch Data mount failed: %d"`（offset 74104860）都在，`_load_init_program`
内共 5 处 `_panic` 分支。

**因此**：r4 屏上出现 launchd 输出 ⇒ 这两次 `_mount` 都返回 0 ⇒ SystemOS 以
`MNT_RDONLY|MNT_UNION` 挂在 `/`、scratch Data 挂在 `/private/var`。

这是**设计蕴含 + 观测**，不是正向日志：仍然没有任何 "mounted"/volume-list 行，也没有任何 I/O。
判据表第 2 行因此从「强推断」改为「设计蕴含 + 观测支持，无正向日志、无 I/O」——提升的是
「失败必 panic」这一支的确定性，**不是** I/O 证据。

### 2. 11-18 的 `Library not loaded: /usr/lib/libSystem.B.dylib` 闭环

11-18 那颗内核里没有 owner 挂载代码：`_native_owner_*`（含 `_native_owner_publish_boot_manifest`）
符号 idx 全为 -1。没有 owner 挂载就没有 SystemOS 的 union 视图，dyld 拿不到 cryptex 共享缓存，
于是 `/usr/lib/libSystem.B.dylib` 解析失败并 panic。r4 起这段代码在、视图在，该 panic 不再出现。

### 3. 这是绕开，不是修好

SystemOS 卷的 sealed-roothash 语义在 owner 链下**没有执行**：我们只做挂载与 union，没有走 Apple 的
sealed volume 验证路径。本节的卷内核对也顺带看到 OS 卷 fs 树里存在 `libSystem.B.dylib`（父目录 oid
`854`）与 `libexec`（父目录 oid `834`）两个目录项，所以 11-18 的失败更可能是「视图/路径解析缺失」，
而不是「这颗库在卷里没有」——但父目录 oid 到完整路径的映射本轮没有解出，这一句只到目录项一级。

### 4. 阶段不提升

阶段 6 **仍不通过**。成立的是 launchd 早期启动；launchd 初始化完成、服务稳定、显示、像素输出、
持久化均未成立；mode 1/2 未放行，默认 `NoAccessPolicy`/`NoContract` 与正式阶段记录（1–2）不变。

### 5. 三条 `Failed to bootstrap path` 与 persona type 6（同轮卷内只读核对）

卷字节仍在主机上，未重新下载、未重新解包：

| 窗口 | 文件 | 字节 | APFS 卷 | 卷 UUID |
| --- | --- | --- | --- | --- |
| OS | `out/userdata-clean-20261112/OS.raw`（UDIF `044-76040-038.dmg` 展开） | 6,077,580,800 | `DawnUpdate21H461.J120J121J207J208OS` | `04769D26-2CA0-4825-B443-E2E5F88300F2` |
| SystemOS | `out/userdata-clean-20261112/044-76034-038.dmg`（本身即 raw） | 3,303,014,400 | `DawnUpdate21H461.J120J121J207J208SystemCryptex` | `8846FE78-2910-4297-AF97-D59BB6F8FC16` |

容器/卷/omap 布局沿用同目录 `apfs-check.py` 的既有解读结果（容器基址 OS `+17408` / SystemOS `0`，
块 4096，卷 xid 418 / 14）。路径存在性用目录记录键（dir-record key）的**结构判据**在卷字节
上直接扫：同一个偏移上必须同时成立

1. `j_key` 8 字节，高半字节 = 9（`APFS_TYPE_DIR_REC`）；
2. 紧随其后的 4 字节 `name_len_and_hash`，低 10 位 = 名字长度（允许 ±1，含 NUL 写法）；
3. 名字字节逐个可打印 ASCII，且与目标串逐字节相等；
4. 名字之后是 NUL。

四条同时成立才计一次命中，因此文件内容里出现的同一字符串（plist 路径、二进制里的常量）不会被算成
目录项。判据用控制组证明有效：`private-dir` 在 SystemOS 卷命中 7 处；`Applications`、`LaunchDaemons`、
`LaunchAgents`、`libexec`、`libSystem.B.dylib` 在 OS 卷均命中（`LaunchDaemons` 的父目录 oid `18`，
`libSystem.B.dylib` 的父目录 oid `854`）。

| 路径 | OS 卷 | SystemOS 卷 | 判定 |
| --- | --- | --- | --- |
| `/System/Library/NanoLaunchDaemons` | 无目录项 | 无目录项 | donor 里不存在 |
| `com.apple.tombf.bits_daemon.plist`（同时查 `com.apple.tomb.bits_daemon.plist`） | 无目录项 | 无目录项 | donor 里不存在 |
| `/usr/AppleInternal/LaunchDaemons` | 无目录项，且 `/usr/AppleInternal` 全卷 0 次 | 无目录项，`/usr/AppleInternal` 0 次 | donor 里不存在 |

引用者：卷内**没有**任何 plist（或其它文件）作为这三条路径的引用者。`/System/Library/NanoLaunchDaemons`
作为文本只出现在 OS 卷一段长度前缀 ASCII 路径表里（offset `0x146b42d54`、`0x146b43808`、`0x146b48c27`，
≈5.48 GB 处），而且拼写是 `NanoLaunchDaemonsAltAccount`；`/usr/AppleInternal`、`tombf`、`tomb.bits`、
`bits_daemon` 在两卷的出现次数为 0（SystemOS 唯一一处 `tombf` 混在一段带非 ASCII 字节的数据里，
上下文 `…ATXPrasononorC~…AutombfRide…`，不是路径或 plist 引用）。承载那段路径表的文件本轮没有解析
（fs-tree 遍历未完成），这不影响「donor 里没有这三条路径」这一判定。

判读：三条 `Failed to bootstrap path` 是 **donor 本来就缺失的预期噪声**，不是卷内容缺失、也不是 union
视图缺陷；可以从「未定性」清单里剔除。措辞边界：屏上路径是主控转录，`tombf`/`tomb` 两种拼写都查过。

persona：`kpersona_find_by_type` 的 **type 6 = `PERSONA_SYSTEM_PROXY`**
（`bsd/sys/persona.h:45`，枚举 `:35-51`，`PERSONA_INVALID 0` … `PERSONA_ENTERPRISE 8`；副本在
`out/root-match-assertion-20261118/source-xnu/`）。ESRCH 只说明内核里没有这一类型的 persona；
**阻塞还是无害仍未定性**，本节不判读。

### 本节不证明

- 不证明 launchd 在推进（还是同一批服务 respawn）：仍缺一次带时间戳的捕获。
- 不证明服务稳定、launchd 初始化完成、显示/像素输出、持久化。
- 卷内核对证明的是 **donor 卷内容**（也就是写进 `userdata` 的那批字节），不证明设备侧实际 union 视图
  的每一次查找；但三条路径在两卷都不存在，union 两侧都无从提供。
- 反汇编与 offset 归属来自主控侧 reviewer 的核读，本轮未复跑反汇编。
