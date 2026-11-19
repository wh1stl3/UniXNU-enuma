# `vmm-present = 1` in the ADT — one device boot, device result

## Latest: one `fastboot boot` of the r3 candidate; `launchd[1]` kept logging past 2.5 minutes with no panic (`self-checked`, record only)

2026-11-19. One device action was authorized and issued: a single
`fastboot boot` of `out/ufs-sm8250-launchd-cache-20261119-r3/boot.img` at
18:09:55–18:10:00, exit 0. Nothing was flashed, no `fastboot continue`, no retry,
no second boot.

Everything about the device below is **parent-relayed oral report**: the run, its
duration, the claim state and what was on the screen. No still frame and no video
of this run exist anywhere — not in Git, not on the host. The screen has **not**
been read by `vision` and **has not been judged yet**; in particular it is still
undetermined whether the log stream shows progress or the same set of services
respawning in a loop. The user flagged that `Read-only file system` lines may
appear and that a loop is possible. This record therefore states what was said and
what it does and does not establish, and draws no "stable"/"running userland"
conclusion.

This record was built without building, packaging, touching the device or
modifying `out/`. The only host-side work was read-only re-hashing of the frozen
r3 candidate (section "What is verified here").

### Execution and timeline

Serial is deliberately withheld; the device was identified by model. A second
device (nuwa) did not appear in any list this round and received no command.

| Time (+08:00) | Event |
| --- | --- |
| (boot − 3.1 s) | claim marker `.cache/ufs-launchd-cache-r3-20261119.claimed` created atomically (`CreateNew`) |
| 18:09:55 → 18:10:00 | one `fastboot boot out/ufs-sm8250-launchd-cache-20261119-r3/boot.img`, exit 0 |
| after boot | console keeps printing `launchd[1]` lines; past 2.5 minutes no panic seen |

No `STOP:` line, no client timeout, no flash and no `continue`. The interval is
host wall-clock, not device-side timing. The claim was consumed by that boot and
is retained: it must not be opened, deleted or replayed.

Boot arguments carried in the payload (`self-check/extracted/unixnu.toml:12`):

```
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2
```

Same argument set as the previous two rounds: store mode 0, no
`sheng-data-persist`, no `native-ufs-probe`, no initrd.

### What changed relative to the previous round (r2)

One property, nothing else.

| Item | r2 | r3 |
| --- | --- | --- |
| ADT `/defaults` | `kern.maxvnodes` = 66560 | `kern.maxvnodes` = 66560 **plus `vmm-present`** (u32 `1`, 4 bytes `01000000` LE) |
| `prelink.macho` / packaged `kernel.macho` | `01fa54373eb7c70b4cf587f116c6e265a08f97cef9a9e95939f946e484f65a7c` | byte-identical, not rebuilt |
| trust cache | 61,356 B `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7` | byte-identical |
| boot-args | as quoted above | byte-identical |
| `kernel.macho.adt` | `7c516d0e…` | 13,956 B `1306d665e9d266ccba5ea6ca7d720bb58279e1ad590791887fce27ffb3c4105f` |
| `payload.img` | `8a2f154b793fe783f3028915fb89fcbec28fa2e783d0e9b370e8f6a0ea0a8adf` | 167,772,160 B `f9ef4fab69f6078bc60d19740b33a636f780323ceeb6ffeb17a471f8196c92c4` |
| `boot.img` | `938951b10f0aaee936fb5395ed47b6276e895997d7888cffbbd04f6ad513a8fe` | 169,951,232 B `83987131573d0537cbcb0c38c5a098e116ef67474a8b89a60ad8b390f0fbe58d` |

The ADT difference set, read back from the sealed payload by the build round
(`out/ufs-sm8250-launchd-cache-20261119-r3/CHECKPOINT.md` §3), is exactly one
added property and zero deletions/changes outside the per-build 256 B
`/chosen:random-seed`:

```
/device-tree/defaults:vmm-present = 01000000
```

The override lives only in the candidate's own board copy,
`out/ufs-sm8250-launchd-cache-20261119-r3/self-check/packaging/device/board.toml:155-159`
(`[adt.defaults.u32] vmm-present = 1`, with `unixnu/scripts/unixnu/devicetree.py:378-380`
rendering that table into `/defaults`). The tracked `board.toml` still has no
`[adt]` table, so the default recipe is unchanged by this round.

Previous round for comparison (parent-supplied, **not** re-observed here): r2
carried the same kernel and boot arguments but no `vmm-present`. On that boot
`watchdogd` exited with `OS_REASON_SIGNAL(2)`/`SIGTRAP(5)` after roughly 10 s and
the kernel panicked. That r2 device result is not recorded in any earlier document;
it is repeated here only as the contrast case that motivated r3.

### Observation

r3 (this round, oral only):

- `launchd[1]` log lines keep appearing after the boot, for more than two and a
  half minutes, with no panic within that window.
- The screen was described as "all launchd".
- Possible `Read-only file system` lines and a possible service loop were flagged
  by the user but not confirmed.

No still frame, no video, no screenshot, no serial transcript. The log lines were
not timestamped on the host, the number of distinct services was not counted, and
whether any process pid changes over the window is unknown. **"Kept printing for
2.5 minutes" is the whole claim**; it is not evidence of a completed boot.

### Mechanism basis (static, unchanged this round)

`watchdogd` opens `IOWatchdog`; when the service is missing it consults the
`kern.hv_vmm_present` sysctl, and the two paths diverge:

| case (script `check-watchdogd-branches.py` case table, line 22) | service | `hv_vmm_present` | asserted outcome |
| --- | --- | --- | --- |
| `physical_missing` | absent | 0 | `brk #1` at pc `0x10000ab0c` (line 82) |
| `virtual_missing` | absent | 1 | `exit 0` (line 83) |

`UniXNU/scripts/check-watchdogd-branches.py:20` asserts that the word at
`0x10000ab0c` really is `0xd4200020` (`brk #0x1`); the `0x10000bb5c` hook stub at
`:54-56` substitutes the `kern.hv_vmm_present` read. With the job's
`_PanicOnCrash`/`PanicOnConsecutiveCrash = true` and `KeepAlive`/`SuccessfulExit =
false` (as reported from the OS launchd plist; **no copy of that plist exists on
this host and it was not re-read this round**), three consecutive non-zero exits
become a kernel panic.

Our board's ADT originally declared no `vmm-present`, so `kern.hv_vmm_present` read
0 and `watchdogd` took the `brk` path — the r2 behaviour. Adding the property
moves the same binary onto the `exit 0` path.

Supported by the official device notes: `UniXNU/docs/devices/evb10.md:52` ("without
it watchdogd traps with SIGTRAP three times and the kernel panics") and
`orangepi5.md:41`.

### Side effects (recorded, not silently accepted)

1. **The official native-root gate stops firing.** `unixnu/scripts/unixnu/payload.py:56-73`
   `check_native_root()` returns immediately when the board declares
   `vmm-present`, so the build no longer asserts `sheng-pmgr=2` in the kernel
   arguments nor `_sheng_pmgr_run` in the linked kernel for a
   `native-ufs-root=1` payload. The consequence is that a mis-argumented or
   mis-linked candidate can now pass that gate. r3's packaging script re-asserted
   both conditions itself and recorded that in
   `candidate-manifest.json` (`preflight_gate_carried_by_this_script`).
2. **The OS now believes it runs in a VM.** MobileGestalt answers are cached on the
   Data volume: values such as `mac-address-wifi0` are read from `/chosen` and then
   cached, so a first boot without the property keeps answering false until the
   cache file is deleted or the volume rebuilt (`UniXNU/docs/devices/evb10.md:454`).
   Any later "Wi-Fi missing" symptom has to be read against this.

### Review trail

- The `vmm-present = 1` approach came from `reviewer`, on the basis of
  `UniXNU/docs/devices/evb10.md:52` and `orangepi5.md:41`.
- `deep_reviewer` confirmed the `check-watchdogd-branches.py` branch semantics and
  the side-effect surface listed above.
- **This round's change is an ADT configuration item only and did not go through
  deep review of the final candidate diff.** The frozen diff is one
  `[adt.defaults.u32]` entry in a candidate board copy; the kernel, trust cache and
  boot arguments are reused byte-for-byte.

### What is verified here, and what is not

Verified on the host this round (read-only re-hash of the frozen candidate):

- `boot.img` = 169,951,232 B `83987131573d0537cbcb0c38c5a098e116ef67474a8b89a60ad8b390f0fbe58d`
- `payload.img` = 167,772,160 B `f9ef4fab69f6078bc60d19740b33a636f780323ceeb6ffeb17a471f8196c92c4`
- `self-check/extracted/kernel.macho` = 124,600,320 B `01fa54373eb7c70b4cf587f116c6e265a08f97cef9a9e95939f946e484f65a7c`,
  byte-identical to the r2 extracted kernel and to `self-check/prelink.macho`
- `self-check/extracted/kernel.macho.adt` = 13,956 B `1306d665e9d266ccba5ea6ca7d720bb58279e1ad590791887fce27ffb3c4105f`
- `self-check/extracted/kernel.macho.trustcache` = 61,356 B `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7`
- `self-check/extracted/unixnu.toml:12` boot arguments as quoted above

Not re-run here: the payload/ADT read-back itself (the build round's
`CHECKPOINT.md` §3), and any build or packaging step.

Device behaviour, from the oral report only:

- **Can** state that one `fastboot boot` of this exact image returned exit 0, once.
- **Cannot** prove that `launchd` completed initialization, that any userland
  process reached a steady state, or that a shell/desktop exists.
- **Cannot** distinguish "the boot keeps making progress" from "the same set of
  services respawns repeatedly"; a 2.5-minute log window with no panic is
  consistent with both. The user-reported possibility of `Read-only file system`
  lines and of a loop is exactly this ambiguity and remains unresolved.
- **Cannot** prove the Data volume is usable, or that it is not the missing piece
  behind read-only writes or repeated respawns.
- **Cannot** prove any display output: console text is not pixel output, and the
  GOP/legacy display line stays frozen (no render server, no swap).
- **Cannot** prove persistence of any kind: this is still a host `fastboot boot`,
  nothing was written to a boot slot, no cold start was attempted, and `userdata`'
  own contents were not re-read.
- **Cannot** prove that the `watchdogd` panic is gone for good — only that it did
  not appear in the observed window of this single run. The static mechanism makes
  it plausible; it does not make it observed-absent.

Stage 6 stays **not passed**; the default `NoAccessPolicy`/`NoContract`, mode 1/2
being unauthorized, and the formal stage record (1–2) are unchanged.

### Why a long press of the power key lands in fastboot

Asked after this run (the user held the power key on the `launchd` log screen and got
fastboot): the cause is our own firmware's PON configuration, not anything this round
changed.

1. **The firmware programmes the PMIC PON on every run.** `SecMain` calls `RamLogReset ()`
   unconditionally (`uefi-enuma/Silicon/Silicium/SiliciumPkg/Sec/Sec.c:136`), which calls
   `PrepareWarmFastboot ()` (`uefi-enuma/Platforms/Xiaomi/enumaPkg/Library/RamoopsLogLib/RamoopsLogLib.c:404-413`).
   That sets the reboot reason to `bootloader` (`:324`, `PON_SOFT_RB_SPARE`), and sets the
   power key's and the power+volume-down combo's S2 reset **type** to warm (`:334-342`,
   `PON_KPDPWR_S2_CTL/CTL2` and `PON_COMBO_S2_CTL/CTL2`), next to `PS_HOLD` (`:329`). The file's
   header states the intent verbatim (`:4-5`): from SEC's first line on, the power key's long
   press is "a warm reset with the bootloader reason".
2. **Nothing rewrites it while our image runs.** The same file records the boundary: "Linux sets
   its own types from the device tree when it starts" (`:260-264`). On a host `fastboot boot`,
   Android never starts, so the configuration written by our SEC is the one in effect under XNU.
   The same mechanism was already observed from the software side: the stage-5 PSCI
   `SYSTEM_RESET` returned to fastboot, `bootreason=bootloader`
   (`docs/entry-probe-bisect.md:21`).
3. **The exclusions hold.** Nothing in `UniXNU-enuma/package/**` or
   `uefi-enuma/Platforms/Xiaomi/enumaPkg/**` mentions `misc`/`BCB`/`bootcmd`/`set_active`, no
   `fastboot flash` appears under `UniXNU-enuma/scripts/**`, and every `fastboot flash boot…`
   mention in `docs/` is hypothetical; no `slot-retry-count`/`slot-successful` record exists. The
   boot slot was never written, and `misc` was never written.
4. **Not caused by this round's change.** r3 differs from r2 only by the ADT property
   `vmm-present`; kernel, trust cache and boot arguments are byte-identical, and PON programming
   is firmware code this round did not rebuild — the packaged firmware is the pre-existing
   `SILICIUM_UEFI.fd` `e524988b…`. An ADT property cannot reach the PMIC.

Full evidence table, the PMGR read-modify-write disclosure
(`UniXNU-enuma/package/ShengPlatformPower.cpp:127-131`, gated on the `pmgr` boot argument at
`:85`, target not derivable from source, unrelated to the fastboot entry), and the
`docs/decisions.md:15` conflict are in
[`enuma-fastboot-entry-and-pmgr-write.md`](enuma-fastboot-entry-and-pmgr-write.md), which is the
authoritative detail for this mechanism.

### Claim and marker state

| marker | state |
| --- | --- |
| `.cache/ufs-launchd-cache-r3-20261119.claimed` | created 3.1 s before the boot by `CreateNew`, **consumed**; retained, must not be accessed, deleted or replayed |
| `.cache/ufs-userdata-sparse-flash-20261118.claimed` and the earlier polluted markers | untouched this round; still consumed/retained with the same prohibition |
| r1, r2 candidates (`out/ufs-sm8250-launchd-cache-20261119-r{1,2}/`) | not rebuilt, not re-booted, bytes unchanged |

### Reproduction conditions

Rerunning this observation requires a new authorization round and a new claim; the
r3 claim is spent. What a rerun would have to capture to settle the open question:

1. a timestamped capture (video or serial) long enough to show whether process
   pids and service names repeat, so "progress" and "respawn loop" can be told
   apart;
2. the `Read-only file system` lines, if they occur, with the failing path and
   errno — that names the volume, not just a symptom;
3. confirmation that the ADT in the booted image still carries
   `/defaults:vmm-present = 01000000` (the r3 read-back is the standing evidence
   until a new image is built).

Status: `self-checked`, record only. Single-run observation, no independent
`vision` read, no media retained, no stage promotion.
