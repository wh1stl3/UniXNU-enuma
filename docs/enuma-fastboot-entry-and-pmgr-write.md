# Why a long power-key press lands in fastboot, and the one PMGR write in the boot path

Scope: answers one user question — *pressing and holding the power key on the launchd log
screen drops the tablet into fastboot; is that something we made happen?* — and records, next
to it, the single PMGR register write that exists in our boot path and the one place where our
own decision ledger contradicts the device record. Statements carry file + line. No build, no
device action, no `out/` change: `self-checked`.

Companion record: [`launchd-vmm-present-20261119-observation.md`](launchd-vmm-present-20261119-observation.md)
(the boot this question came from). This file is the authoritative detail for the fastboot-entry
mechanism; the observation file carries a short section that points here.

---

## 0. Answer

The fastboot landing is **our own firmware's PON configuration**. From SEC's first line, our
firmware programmes the PMIC PON so that the power key's long press (and power + volume down)
is a **warm reset with the reboot reason `bootloader`**, and it does so on every run. A reset
taken while our UEFI/XNU image is running therefore comes back into fastboot, not into Android.
It is not an XNU bug, not a written boot slot, and not a written `misc` partition.

It is also **not caused by any change of this round**: the round that produced the observed log
changed one ADT property (`/defaults:vmm-present`) with the kernel, trust cache and boot
arguments byte-identical, and the PON programming lives in the firmware FD, which this round did
not touch.

---

## 1. Cause: firmware PON configuration, set on every run

### 1.1 The code path

| # | Location | What it does |
| --- | --- | --- |
| 1 | `uefi-enuma/Silicon/Silicium/SiliciumPkg/Sec/Sec.c:136` | `SecMain` calls `RamLogReset ()` before `PlatformInitialize ()`, unconditionally on every boot |
| 2 | `uefi-enuma/Platforms/Xiaomi/enumaPkg/Library/RamoopsLogLib/RamoopsLogLib.c:404-413` | `RamLogReset` resets the ramoops header, then calls `PrepareWarmFastboot ()` — comment at `:408`: "From the first line on, every reset that ends this run keeps the log and comes back in fastboot" |
| 3 | `RamoopsLogLib.c:324` | `PON_SOFT_RB_SPARE` ← `PON_REASON_BOOTLOADER` (the reboot reason the bootloader reads) |
| 4 | `RamoopsLogLib.c:329` | `PON_PS_HOLD_RST_CTL/CTL2` type ← warm (a software reset) |
| 5 | `RamoopsLogLib.c:334-337` | `PON_KPDPWR_S2_CTL/CTL2` type ← warm (**the power key's long press**) |
| 6 | `RamoopsLogLib.c:339-342` | `PON_COMBO_S2_CTL/CTL2` type ← warm (**power + volume down**) |
| 7 | `RamoopsLogLib.c:230-258` | `SetWarmReset`: reset source off → ≥10 sleep-clock wait → type ← warm → re-enable if it was enabled |
| 8 | `RamoopsLogLib.c:4-5` (file header) | States the design intent: from SEC's first line on, the PON makes the power key's long press (and power with volume down) "a warm reset with the bootloader reason, so a hang that the user ends with the keys keeps its log" |
| 9 | `RamoopsLogLib.c:427-429`, `:347-359` | An `ASSERT` line in the log also triggers `RestartIntoFastboot ()`, which runs the same `PrepareWarmFastboot ()` first |

So there are two reset routes and both end in fastboot: an `ASSERT` restart inside our firmware,
and any reset the SoC takes while our image is in charge — including a key-driven reset, because
the key's S2 reset type was set to warm and the reason word was set to `bootloader`.

### 1.2 Observed behaviour that matches

`docs/entry-probe-bisect.md:21`: the stage-5 bisect images issue PSCI `SYSTEM_RESET`
(`smc #0`, `w0=0x84000009`) from inside `_arm_init`/`_kernel_bootstrap`, and that reset returned
**into fastboot** — "the PSCI reset returns to fastboot (verified in the stage-5 run,
bootreason=bootloader)". That is the same mechanism as the key long press, only started by
software instead of the key.

### 1.3 Why it persists into XNU and into launchd

Nothing rewrites the PON configuration after our firmware. `RamoopsLogLib.c:260-264` records the
boundary: "Linux sets its own types from the device tree when it starts." On a host `fastboot boot`
of our payload, Android never starts, so the PON configuration written by our SEC is the one in
effect when XNU is printing `launchd[1]` — a long press there is a warm reset with reason
`bootloader`, i.e. fastboot.

### 1.4 Not caused by this round's change

The observed round changed exactly one ADT property (`/defaults:vmm-present`), with the packaged
kernel, the trust cache and the boot arguments byte-identical to the previous round (see the
companion observation file, "What changed relative to the previous round"). PON programming is
firmware (FD) code; this round re-ran the payload/ADT and boot-image steps and reused the
pre-existing `SILICIUM_UEFI.fd` (`e524988b8a05f15847ffc991170de8a5e0ead607400421e0835084497a71bf1e`,
recorded at `out/ufs-sm8250-launchd-cache-20261119-r3/CHECKPOINT.md:51`), the same firmware every
recent round used, rather than building a new one. An ADT property cannot reach the PMIC. The
behaviour is older than the observation and would be identical on every earlier image of this
series that ran this firmware.

---

## 2. What it is not (exclusions)

| Exclusion | How it was checked | Result |
| --- | --- | --- |
| `misc` / BCB / `bootcmd` written by us | No `misc`, `BCB`, `bootcmd` or `set_active` reference in `UniXNU-enuma/package/**` or `uefi-enuma/Platforms/Xiaomi/enumaPkg/**`; no `fastboot flash` / `fastboot set_active` anywhere under `UniXNU-enuma/scripts/**` | Zero hits; nothing in either tree writes the bootloader-command block |
| AOSP fastboot `boot` protocol writing `misc` | Protocol behaviour, not repository content | `fastboot boot` transfers the image into memory and starts it; it carries no misc/BCB write |
| A boot slot was written | `fastboot flash boot…` appears only as a **hypothetical** in `docs/persistent-boot-slot-plan.md:376`, `docs/payload-shrink-plan.md:150,223`, `docs/SESSION-HANDOFF-20261118.md:30`; every device record states `fastboot boot` with no flash | No `fastboot flash boot_a|boot_b` was ever executed in this project's records |
| Slot retry/success counters (`slot-retry-count`, `slot-successful`) | Not present in any repository file | No record exists, so no counter-based fallback contributed |
| XNU resetting itself | Parent-verified; **not re-run here** (the XNU sources live in the local build tree, not in the three tracked repos) | No code assigns the XNU reset hook `PE_halt_restart`; XNU alone cannot produce this reset |

The XNU-side item is the only one in this table I did not re-derive myself in this session; it is
recorded as an inherited check, not as a verification.

---

## 3. Disclosure: the one PMGR write in our boot path

`UniXNU-enuma/package/ShengPlatformPower.cpp` contains a PMGR register write that runs in the
observed boot. It is stated here because a reader asking "what does our image write?" should not
have to find it by accident. **It has nothing to do with the fastboot entry** (section 1 is
firmware/PMIC; this is XNU/PMGR), and it is not evidence of working platform power.

| Item | Fact |
| --- | --- |
| Gate | `:85` — `PE_parse_boot_argn ("pmgr", &mode, sizeof (mode))`; the whole path returns immediately unless the boot argument `pmgr` is non-zero. Also single-entry: `:88-90` misuse detector, `:92` mode > 3 fails |
| The write | `:127-131` — `read (nub)` → `write (nub, value \| 4)` → `read (nub)`, i.e. a read-modify-write of bit 2 through the original `ApplePMGR` methods (`sheng_original_pmgr_nub_read/_write`, declared `:17-18`) |
| Asserted invariant | `:131-134` — both reads must return `0xffffffff`, the nub and provider must have no provider, and neither may be in `kIOServiceRegisteredState`; otherwise `fail (14, …)` (kernel panic `enuma-pmgr fail-stop stage=14`) |
| Object it targets | `:112-119` — the nub is created from an **empty** `IORegistryEntry` named `enuma-platform-power`; no resource, range or property is attached, so **the real target address is not derivable from the source** |
| What the boot did | Boot arguments of the observed round contain `pmgr=2 sheng-pmgr=2` (companion observation file), and no `enuma-pmgr fail-stop` panic appeared, so statically the write executed |
| What is not established | The actual register touched, whether bit 2 has any effect on this SoC, and whether that effect is benign. Not verified; no PMGR runtime claim follows from this record |

The write is bounded by the assertions around it (`0xffffffff` before and after, no provider, not
registered), which is why the fail-stop path did not trigger, but "the assertions held" is not the
same as "the write is understood".

---

## 4. Record conflict and its resolution

Two documents say different things about what a reset of this tablet does:

| Location | Text | Standing |
| --- | --- | --- |
| `docs/decisions.md:15` (D2, 2026-11-07) | "载荷来源（2026-11-07）：继续用 `fastboot boot`，不刷 `boot` 分区；**设备自行重启会回 Android**。" | The second clause is **superseded** for a warm/PSCI reset by the 2026-11-09 device observation; the original text is kept with an annotation |
| `docs/persistent-boot-slot-plan.md:213` (table row "断电重启后") | quotes `decisions.md:15` for the `fastboot boot` column | Same quote; annotated in place |
| `docs/entry-probe-bisect.md:21` | "the PSCI reset returns to fastboot (verified in the stage-5 run, `bootreason=bootloader`)" | **Device observation**, and the basis of the correction |

The correction is narrow on purpose:

- **Established**: a reset taken while our image runs (warm reset, PSCI `SYSTEM_RESET`, or a key
  long press) returns to fastboot with `bootreason=bootloader`, because our firmware says so
  (§1).
- **Still unmeasured**: what a **cold** start does after the tablet has been fully powered off.
  No record of a cold start exists in this project; whether the PON `SOFT_RB_SPARE` reason word
  survives a full power removal on this PMIC was not taken either. The original D2 sentence may
  well hold for that case — it is simply not what the device record shows for the case that was
  actually measured.

`decisions.md:15` now carries this as an annotation under the original sentence rather than a
rewrite, so the 2026-11-07 decision stays readable while the measured behaviour wins.

---

## 5. Evidence table

| Claim | Source | Verified in this session |
| --- | --- | --- |
| PON long press / power+vol-down are warm resets with `bootloader` reason | `uefi-enuma/…/RamoopsLogLib.c:4-5` (header comment) | read |
| Reason word written on every run | `RamoopsLogLib.c:324`, `:409`; `Sec.c:136` | read |
| Key and combo S2 reset types set to warm | `RamoopsLogLib.c:334-342`, `:230-258` | read |
| `ASSERT` also restarts into fastboot through the same preparation | `RamoopsLogLib.c:427-429`, `:347-359` | read |
| A reset from inside the kernel returns to fastboot with `bootreason=bootloader` | `docs/entry-probe-bisect.md:21` | read (device record, not re-run) |
| Linux would rewrite the PON types when it starts | `RamoopsLogLib.c:260-264` | read |
| Nothing of ours writes `misc`/BCB/`bootcmd`/`set_active` | `UniXNU-enuma/package/**`, `uefi-enuma/Platforms/Xiaomi/enumaPkg/**`, `UniXNU-enuma/scripts/**` | searched (zero hits) |
| No `fastboot flash boot*` was ever executed | `docs/persistent-boot-slot-plan.md:376`; `docs/payload-shrink-plan.md:150,223`; `docs/SESSION-HANDOFF-20261118.md:30` (all hypothetical) | read |
| PMGR write exists, gated on `pmgr`, target not derivable | `UniXNU-enuma/package/ShengPlatformPower.cpp:85`, `:112-119`, `:127-131` | read |
| `pmgr=2` was in the observed boot arguments | `docs/launchd-vmm-present-20261119-observation.md` (boot arguments block) | read |
| D2 sentence conflicts with the device record | `docs/decisions.md:15`; `docs/persistent-boot-slot-plan.md:213` | read |

---

## 6. What this establishes, and what it does not

Established (static, from tracked sources plus one existing device record):

- The fastboot landing is produced by our firmware's PON programming, not by a written slot, a
  written `misc`, or an XNU-initiated reset.
- The mechanism applies to any reset taken while our image is in charge, including the power-key
  long press on a launchd log screen.
- The round that produced the log did not change this behaviour.

Not established here:

- What a cold start does after a full power-off (no record).
- The identity or effect of the PMGR register the `pmgr=2` path writes.
- Any conclusion about a fix. If key resets into fastboot later become a problem for a
  persistence test, the change would be in the firmware's PON preparation, not in XNU — and it
  is not proposed here.

Status: `self-checked`, record only. No build, no device action, no `out/` change, no stage or
policy change.
