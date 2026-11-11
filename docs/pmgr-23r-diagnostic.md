# 23r first controlled PMGR diagnosis: preparation and observation record

2026-11-10. The first23r authorization has now been used once, entry/boot returned0,
claim consumed/retained. No replay permission. Latest supplied-photo/user report
below does not establish stage23 or PMGR runtime acceptance. Entry preparation
results and the initial decision below remain their historical scopes.

## Latest media supplement (self-checked organization; not runtime PASS)

User-authorized single-photo move, same basename, into ignored
`.cache/media/stage7-pmgr-23r-20261110/微信图片_20261110232546_369_25.jpg`;
6082128 B SHA256 `065a6fec43aa856e71ab201cb7eeb3811cd842c5981306a8ed336b28a490145d`.
Original `.cache/media/微信图片_20261110232546_369_25.jpg` is absent; old22r media
untouched. `media-record.json` supplies origin/hash and the existing
`.cache/cp23r-user-authorized-01-result.json` one-boot0 binding. That execution
JSON and consumed marker were not changed/accessed respectively by this task.

Terra's parent-relayed visual reading: launchd `Early boot complete` / `Continuing
system boot`, restored_external/xpcproxy pid3/running/Successfully spawned;
NVRAM unavailable, boot-stage registry missing, mount_tmpfs /mnt5, No MRM cache /
Unable load cache, bootstrap-path ENOENT and logd/notification_center/logger lookup
ESRCH. These are visible logs, not complete exec/syscall or lifecycle proof.

Top is cropped; no stage3/stage23/fail-stop/panic/AMFI No PMGR text was visible
in the available frame. **Stage23 text is not directly observed**; lack of
visible panic is not proof of its absence. The separate reviewer inference below
is not an inference from absence of panic. User said
**“一直停在这里”**, the same launchd/restored_external screen; no subsequent
panic/reset was reported and no exact duration given. Static screen is not proof
of kernel hang or stable execution; no stable minute count is claimed. Video and
further offline control-flow analysis are pending. No runtime/area upgrade or
device action; do not reboot for evidence. Full media boundary also recorded in
`docs/runtime-summary-gate.md`.

### Reviewer conclusion: publisher completion inferred, not directly seen

**“mode2 publisher检查完成并返回——控制流推导；stage23文本未直接观察。”**
This parent-relayed reviewer conclusion is conditional on the fixed23r package /
single-boot binding and the supplied later launchd/restored_external[3] logs.
It does not use PID3 alone or absence of a visible panic as an AMFI proof.

Exact source references, no implementation edits:

- `patches/xnu/enuma-pmgr-publisher.patch:5–11`; actual assembled source
  `/root/enuma-step10/UniXNU/out/enuma/ipados-17.7.11-21H461/enuma/tree/.cache/xnu-work/bsd/kern/bsd_init.c:775–779`
  calls the publisher synchronously after bsd_bufferinit; only later comes
  `bsd_utaskbootstrap()` at1202 and `load_init_program(p)` at1282.
- `package/ShengPlatformPower.cpp:82–98`: parse pmgr; the fixed contained unique
  pmgr2 cannot take the missing/zero-argument return. Lines135–148 restrict the
  unpublished cleanup return to mode1; mode3 refuses rather than returning.
- `:38–42,100–134,150–166`: explicit mode2 failures panic, including metaclass,
  pre/post registration, original nub/type/binding/AON, attach/start and actual
  matching. `:156–172` registers, verifies matching/type/binding, then calls
  checkpoint23; only after that does mode2 return at173.

Thus downstream launchd execution under this bound image supports completion of
the mode2 publisher checks and return. It is **control-flow evidence**, not an
observed stage23 screen line, all AMFI paths, sustained activity or complete
PMGR runtime acceptance. Old22r also displayed PID3 before panic, so PID3 cannot
by itself establish all AMFI success this round. Existing RAM-root is the restore
ramdisk, **not a complete GUI OS**; the static screen is not itself anomalous
proof of kernel hang. No established UART/USB log channel exists; do not
automatically query adb/restore tools. No reboot for evidence.

The current23r directory was listed once: only this photo and media-record.json,
no full/early video supplied. Await user video if available, without requesting a
reboot. Next authorized host action is reviewer **read-only native-UFS resource /
interface preparation**; no implementation/driver enabling, userdata write or
Android removal. Storage/whole-stage levels remain unchanged.

## Exact reviewed scope / current decision

Parent relays PMGR deep's necessity ruling for frozen prelink
**`bf9f7e12bb05dc3a09f1a732fbcdb83d7729f6378f65ea7fbe77646514edc072`**:
static lifecycle/fail-stop/340-slot necessary-thunk evidence, independent complete
23r packaging PASS, and observer's five manual gates are sufficient to prepare
the **first bounded controlled diagnostic**. Host tool gate is PASS. This is not
runtime acceptance or permission to execute now. Modes1/3 and boundary faults
remain unverified, but their dynamic completion is **not a prerequisite** for
that first diagnostic under this ruling. No new code/ABI/signing change is made.

Mode2 actual stage23 publication/matching and AMFI progression beyond the22r
failure are the diagnostic's **targets**, not prior results. Stage23 only means
the publisher's own final checks have passed; it does not independently prove
AMFI's later wait/use, stable userspace, display or whole-stage acceptance.

Independent host gates do not rewrite historical `release_allowed=false` or
`device_authorized=false` in the frozen manifest, nor convert any automatic
observer `exit2/manual-review-required` JSON to PASS. Keep those artifacts intact.

## Frozen candidate

Directory `D:/Code/PortingiOS/UniXNU/out/enuma/stage6-ramblock-probe/23r-pmgr-publisher`:

| File | Bytes | SHA256 |
|---|---:|---|
| boot.img | 203505664 | `1f4574a1dcdcc9a7a551a07ac79565b2a5a0274546952ddd3f3fe24ae4e47207` |
| payload.img | 201326592 | `1b4a12f49135937e965bc4413df67a7c87d069c3e1b9fbfec9b5b8fa21336f76` |
| manifest.json | see frozen file | `ad0c3bc7b55c9b228c22c55465844060b4a9c22c435b7786e9217d009fd08690` |

These are the already independently verified package bindings, not a rebuild or
new packaging run. Native hash remains
`5b8fd1811e39d6415550786578c1fb96346df32a0ba2a35efbd3ff50a251a74f`.
Device HEAD `7772f75fef46bfeeff899db25554f555ee27670c`, uncommitted work retained;
active base `693f5d9cae8a408dd18b39f3f9fdc4228c934241`. No pin/image change.

## Preserve unresolved evidence; do not resume the rejected fixture task

Original QEMU mode1 ran the real kernel and stopped before PMGR in original
AppleImage4 at `0xfffffff004a92828`, savedx0/FAR0; PMGR entry absent and16 actual
fields all0. This is **not** successful mode1 create/free/count evidence. Modes2/3
and faults were not run. The host fixture follow-up received **two platform
refusals without a usable execution result**, as relayed by parent; do not infer
a successful fixture change, resumed guest or fixed panic from those attempts.
Do not reproduce or work around that refused task in this preparation task.
Original raw logs remain in the paths recorded by pmgr-qemu-environment.md.

## New single-use entry (offline preparation only)

Ignored `.cache/run-cp23r-once.ps1`, SHA256
`19080c3dae65a2803a11784d0aa8a59d13e259e898ed7e181552fd595b0a8733`.
Derived from unchanged reviewed `.cache/run-cp22r-once.ps1`, SHA256
`53689fadeafc9aa89a8bd2d714805a40e2746d02c96494621c51e3308d06e5ab`.
After newline normalization, exact diff is **only five literal replacements**:

1. fixed candidate directory22r ->23r;
2. boot SHA256 -> the fixed23r hash above;
3. independent marker `cp22r-device-attempt.claimed` -> `cp23r-device-attempt.claimed`;
4. image error label22r ->23r;
5. offline-success label22r ->23r.

Boot size is unchanged203505664. AuthorizationRound remains the same required,
validated generic parameter; no default authorization or round is supplied.
A later execution must use a fresh non-identifying23r label, not a22r label.
The actual boot/identity/claim logic is unchanged: authorization before discovery;
exactly one enuma; every device query/boot is targeted; final identity confirmation
before atomic CreateNew, immediately adjacent to the sole boot call; existing
claim refuses even with another label. No adb/reboot/flash/continue/retry fallback.
Neither old claims nor the real new marker was read/written by this preparation.

Selfchecks actually run, using true child Process.ExitCode:

| Check | Result |
|---|---|
| ParseFile | 0 syntax errors |
| normalized exact literal-only source diff | pass, no logic change |
| `pwsh -NoProfile -File .cache/run-cp23r-once.ps1 -OfflineCheck` | exit0, actual fixed image hash/size match |
| `pwsh -NoProfile -File .cache/run-cp23r-once.ps1` | exit1, unauthorized rejection before client access |
| git ignore for entry/evidence | exit0 |

Exact argv/stdout/stderr/child exits and transformations are in ignored
`.cache/cp23r-preparation-selfcheck.json`. No device client was invoked and no real
claim was created. No extra stub matrix or repeated packaging audit was run.

Parent/independent verifier should rerun only ParseFile, the exact five-literal
diff, OfflineCheck and no-authorization rejection, plus record/diff. Expected
nonzero1 for no authorization is **rejection**, not a failed device boot.

## Historical invocation reference: used once, not replay permission

The preparation-time command below was subsequently executed once under parent
confirmation and user round `cp23r-user-authorized-01`. It is retained as an exact
execution reference, **not** a new authorization or instruction to retry:

```powershell
# HISTORICAL: already used once; do not replay this entry or consumed claim.
pwsh -NoProfile -File .cache/run-cp23r-once.ps1 -AuthorizeDeviceThisRound -AuthorizationRound cp23r-user-authorized-01
```

Recording was requested before that invocation; retain supplied photos/video of
the visible state. This diagnosis may **panic, stall
or reset**; not a promise of desktop/AMFI completion. If any check fails or the
outcome is unclear, **stop**: no automatic retry, altered parameters, continue,
Android recovery or userdata write. Retain the consumed marker if any boot was
attempted, even if the client returns nonzero. A new label cannot renew the right.
No serial/ECID is included in persistent host records. No userdata flash is part
of this diagnostic authorization or entry.

### Short visual identification (source, not predicted visibility)

Publisher source `package/ShengPlatformPower.cpp:26–41` prints exactly:

```
enuma-pmgr stage=%u code=0x%x checks: parent=0x%llx own=0x%llx bound=%u read=0x%llx/0x%llx attach=%llu registered=%llu mode=%llu
enuma-pmgr fail-stop stage=%u code=0x%x
```

Ask only for these short recognizable prefixes; small text need not be fully
transcribed—photos/video are sufficient:

- **`enuma-pmgr stage=3`**: progress before ApplePMGR load (source:93–94), **not
  success**, even with code0. It is not stage23.
- **`enuma-pmgr stage=23 code=0x0`**: final publisher selfcheck (source:150–172)
  after attach/start, registration, actual matching identity and binding checks.
  Relevant fields should report mode2, bound1, attach1, nonzero registered,
  parent/own sizes0x4b8a8 and read0xffffffff/0xffffffff. Do not invent a numeric
  registered mask or require the user to copy every digit.
- **`enuma-pmgr fail-stop stage=`** or any panic: failure evidence, stop/no retry.
- Original failure string **`AMFI: No PMGR?`**: record if present. Its absence
  alone does not prove AMFI progressed; later control-flow/log evidence must be
  judged separately. Stage23 is not an AMFI or userspace acceptance marker.

Actual log visibility remains unverified. Preserve a blank/stalled screen or
reset video as an observation, not proof of success or a reason to boot again.
