# PID1 runtime summary observer — host checkpoint (2026-11-10)

**22r host candidate delivery gate complete: independent packaging-binding PASS,
within the scope below. Subsequent authorized 22r boot has now produced a user-reported
kernel panic and the photo observations recorded at the end.**
The final f native/prelink hashes below passed the parent's independent deep
manual and verifier mechanical gates. Automatic audit still says
`manual-review-required`/child exit 2; the hash-bound manual PASS is a separate
supplement, not a rewritten automatic result. Not integrated or accepted as a
completed runtime stage; the later device panic is recorded separately below.
The packaging task did no device operation/kernel rebuild; the later one-shot
device run and this media-only update are separately recorded below. No replay/push.

## Review scope and final implementation

Deep `ses_e3b06b236ffeg4OkLpLYAdysj8` cleared the reduced console design with
conditions. Its actual diff review then requested two Medium audit fixes and a
Low missing thread-start-result fix. Those fixes and the five hash-bound manual
items subsequently passed independent deep review (**PASS WITH CONDITIONS**,
reported by parent). Verifier independently passed host/policy/old-artifact/hash/
record/diff checks and confirmed capture wrapper exit 0, actual audit child exit
2, stderr 0. Native build timing below remains the implementer's build evidence;
no independent rebuild is claimed here. The final packaging-binding gate has now
also passed independently, as reported by parent; no additional test was rerun in
this documentation-only closeout.

Authoritative implementation: `patches/xnu/enuma-pid1-observer.patch` (479 lines),
last in device series; normal assembly remains arch -> soc -> device-local OS ->
device, **61 patches**. No base source/tool edits. Patch SHA256:
`a3c12c0f1d210bb2481ba83fa28023c91fad27ac346f992d7613de7e8ed12109`.

Patch anchors / scope:

| Patch lines | Actual source change |
|---|---|
| 18 | `bsd_init.c`, bsd_utaskbootstrap: PID1/immutable uniqueid + once observer start before original return-wait release |
| 40 | `kern_exit.c`, exit_with_reason: selected exit thread, proc lock held, after p_xstat=rv, parameter p, before proc_transend |
| 47–83 | `sleh.c`: actual BSD accessor forward declarations (surrounding BSD-entrypoint convention, avoiding sys/types clock_t collision); non-platform SVC numeric identity/trap/PC after credential update, before dispatch |
| 128–281 | `video_console.c`: private boot-owned eligibility, reader batches of 16, timed observer, startup result, transition revoke/drain |
| 283–294 | `osfmk/kern/Makefile`: helper in XNU_ONLY_EXPORTS so BSD compilation can find it; not a public SDK interface |
| 295–456 | actual shared helper: permanent BSS, atomic identity/count, immutable first/exit slots, startup-result publication and console gate |
| 475 | `startup.c`: diagnostic-only NULL TextMode before original NULL Acquire, after interrupts enabled |

Permanent numeric state includes one-time PID1+uniqueid release publication,
independent atomic SVC count, one-attempt EMPTY/WRITING/READY first and exit slots.
READY payloads never change; acquire readers never wait on WRITING. Strong CAS
may use backend LLSC retries: **not a strict wait-free or global-first guarantee**.
No proc/name/os_reason pointer escapes; rv is wait status, not errno. Existing
exit/panic/exception-return policies remain unchanged; PID1 panic may precede
any refresh.

Thread startup records SKIPPED/STARTING/RUNNING/FAILED and the kernel return code
in permanent state; no printf/retry or PID1 blocking. Host failure tests assert
the actual state/result and returned thread-reference release. Normal kernel
priority and 1000 ms timed blocking wait; no lock held over sleep.

Console recognizes only its first valid boot-owned self-map. Later non-NULL info
permanently revokes, even if self-mapped. Pre-start NULL TextMode/Acquire preserve
eligibility. Start requires lock initialized, initialized/enabled text and no
transition; any initialize_screen after start revokes/drains under the same
VCPUTC lock before original changes/free. Never resumes. Reader stays inside
video_console.c: gc hide/putchar/show, fixed rows, 96-byte stack formatting,
16-character lock batches, cursor/pending-wrap restore, no vcputc recursion,
pointer caching/export, new mapping, per-refresh clear/enable or scroll. No hot
SVC/exit allocation/formatting/drawing, child/name/tail/full-boot-progress feature.

## Actual final build and revisions

Device HEAD `7772f75fef46bfeeff899db25554f555ee27670c`, **uncommitted work tree**.
Base Windows/ext4 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`; original XNU
`d8b80295118ef25ac3a784134bcf95cd8e88109f` plus selected patches. DarwinBoot
`3c75734014cdab0acd9541e88057b7606ee7ae08`, firmware
`d994be64e57576a35e31f8eb69b6e46c1ec6b3bc`, unchanged. Upstream main checks:
UniXNU `d830d23b0d19c9322d906c21afeca1d6c54aeffe`, uefi-sheng
`66421cb7bb5694843aec8de1ca3d1de4c20cca38`; active pins unchanged.

Final f build **exit 0**, 38.546 s (warm incremental, not clean-build timing).
Native executable: 18284192 B, SHA256
`8c9dadc04f697c5d53e7421535552ff12840dabd1cfc85de2a9e2a1259a4d86e`:
`/root/enuma-step10/UniXNU/out/enuma/ipados-17.7.11-21H461/enuma/tree/build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped.noctf`.

Prelinked kernel: 51126272 B, SHA256
`48da518122894ba21344c016f09cbc62238848d83dd0ac32f97246c76795cb4d`:
`/root/enuma-step10/UniXNU/out/enuma/ipados-17.7.11-21H461/enuma/kernel/kernel.macho`.
Actual metadata `kernel/kernel.json` SHA256
`de2dfc7da3ebb7d7f1f82304d8ded0b5360c4063baad1baf2e2a490f378b0253`.
All Apple-containing outputs remain local ignored out. The native f checkpoint
did not package an image; the subsequent 22r host packaging is recorded below.

Build evidence directory `S=/root/enuma-step10/UniXNU/out/enuma/pid1-observer-selfcheck`:
`build.json` binds patch, prepared-input stamp, native/prelink/metadata hashes and
six actual source/object/compile-record tuples. Logs:
`/root/enuma-step10/logs/pid1-build-{c,d,e,f}.log`; normal kernel/prelink logs are
under `out/enuma/ipados-17.7.11-21H461/enuma/logs/`. e was a successful earlier
proc_pid revision; **f hashes above are authoritative**.

Earlier failures, resolved: initial BSD libkern/Mach clock_t include collision;
then sleh missing accessor declarations; then missing BSD exported helper header.
Public `TrustCache/Types.h` truncation was recovered from existing enuma cache:
11720 B, actual Git blob `f3412f3869c69d1d2e40a0f8883aa9e3f5b3c7ae`, not SHA256.
All 26 restored headers passed Git-blob checks. Local cached manifests now point
to these verified file:// blobs, preserving original manifests; the unmodified
official restore script still verifies every restored object. No network retry,
guessed replacement header, dependency install or base-tool bypass was needed.

## Audit results: automated vs manual

`S/audit/audit.json` is **manual-review-required**, not a PASS. Automated checks:
bound artifact/metadata/patch/source-object hashes; actual native/prelink collector
sites (same owner and instruction offset); relative credential/begin/release/
transend call ordering; RW zero-fill BSS; actual startup preprocessing macros;
no framebuffer driver component. Collector/proc_getpid instruction ranges reject
BL, external B tails, out-of-range conditional branches and unaudited indirect
transfers, while permitting local atomic loops. Actual SVC counter uses 64-bit
LDXR/STXR; slot/identity publication uses LDAR/STLR. No collector out-of-line call.

State is at `0xfffffff007b04e20`, aligned 8, writable `__DATA,__bss`; lock-ready
at `0xfffffff007b04e78`; compiler-split gate fields `...4e7c–...4e8c`. Startup
macro output contains `ENUMA_PID1_DIAGNOSTIC=1`, `XNU_BOOT_PROGRESS=0` and is bound
to actual compile records/objects and output hashes, not used as a binary proof.

Native instruction observations (original manual self-check, subsequently covered
by the parent's hash-bound independent manual PASS; exports remain in audit.json):

- `kernel_bootstrap_thread`: `0xfffffff0072d1950` calls initialize_screen with
  x0=0/w1=2; `...195c` calls with x0=0/w1=4, after ml_set_interrupts_enabled(1).
- `bsd_utaskbootstrap`: begin at `0xfffffff0076f3380`, original return-wait
  release **B tail** at `...3398` (w1=3); numeric accessors precede begin.
- `sleh_synchronous`: platform exclusion before cred call `0xfffffff00741ff58`;
  get_bsdthreadtask_info/getpid/uniqueid then collector `0xfffffff00742006c`,
  followed by signed-trap dispatch. Disassembly, not a handle_svc symbol guess.
- `exit_with_reason`: p_xstat store at `0xfffffff0077252e0`; numeric parameter-p
  accessors/reason loads; collector `...532c`, proc_transend `...5338`.

The audit **does not auto-pass** argument/dominance/lifetime semantics. Explicit
manual_pending includes startup parameters/dominance, SVC argument provenance,
PID1 begin/release, selected-exit p/rv/reason store order and identity-call-chain
review. `proc_uniqueid` and get_bsdthreadtask_info contain existing zone validation
and panic-only edges; they are not falsely classified leaf. Actual chain exports
include zone_require_ro, mach_vm_range_contains, sanitizer/failure edges. Review
normal valid-proc paths and those invariant-failure paths independently; do not
ban the syscall handler's unrelated pre-existing dispatch branches.

## Tests, reproduction and independent handoff

WSL Ubuntu-22.04 (`-u root` for ext4 /root access), absolute interpreter:
`P=/home/wh1stl3/.local/bin/python3.11`; device
`D=/mnt/d/Code/PortingiOS/enuma/UniXNU-enuma` (variables here are shorthand only).

| Actual command | Result |
|---|---|
| `$P $D/scripts/check-enuma-pid1.py --out /root/enuma-step10/logs/pid1-host` | exit 0, actual helper/reader/begin extracted from patch, startup result assertions included |
| `$P $D/scripts/tests/test_enuma_pid1_audit.py` | exit 0, 6 policy unit tests: stale/mismatched file, changed artifact, missing hook, atomic-load/external-tail, indirect tail, legal local retry/RET |
| `$P $D/.cache/build-pid1.py` | final f exit 0; official normal assemble/prepare/build/prelink APIs, no pin update; unchanged-source mtimes restored only on equal content |
| `$P $D/scripts/audit-enuma-pid1.py --record $S/build.json --tree /root/enuma-step10/UniXNU/out/enuma/ipados-17.7.11-21H461/enuma/tree --out $S/audit` | exit 2 by design, automated checks completed; mandatory manual review still pending |

Policy negatives are unit inputs/raw A64 encodings, **not fake Mach-O target
verification**. Host C tests use fake gc/thread backends and manually controlled
gate transitions: they do not prove real mapping lifetime, framebuffer latency,
physical scanout or scheduler timing. Existing valid-proc uniqueid source is
immutable `proc_ro.p_uniqueid`; actual getter/validation chain is exported above.

Additional **real old-artifact negative**, `.cache/negative-pid1-old-artifact.py`:
substituted the existing Windows enuma baseline prelink path into a copy of the
current binding record without changing the expected current digest. Actual audit
rejected it with **exit 1**, `stale/mismatched bound artifact: prelink`; negative
driver exit 0. No synthetic image. Evidence `S/negative-old-artifact.log` and
`S/negative-old-record.json`; the valid final `S/build.json` is unchanged.

Final record check, cwd `/mnt/d/Code/PortingiOS/UniXNU`:
`/home/wh1stl3/.local/bin/python3.11 scripts/porting-record.py check --device /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma`.
Actual **exit 0**, `enuma: 14 structured areas checked`; all three Python files
py_compile exit 0; device `git diff --check` exit 0. Use no `--base`.
The original implementation gates above are now complete in the scopes reported
by parent; do not rerun them just for packaging. Audit exit 2 must not be suppressed
or called automatic PASS. Its manual_pending array remains unchanged; candidate
review-bindings.json records the separate parent-reported manual conclusion.
Parent owns integration and acceptance. Board/defconfig, RAM-root UUID/trust/
memory/arguments and area completion levels remain unchanged; no 21r reset probe,
new boot entry, display driver, UFS/userdata or firmware change.

## 22r-pid1-runtime-summary packaging checkpoint

Both destination directories were absent before this task; no prior candidate or
user asset was overwritten. Existing 21r images were read only for unchanged
input metadata/header geometry; its claim and entry were not accessed/replayed.

- Ext4: `/root/enuma-step10/UniXNU/out/enuma/stage6-ramblock-probe/22r-pid1-runtime-summary/`
- Windows: `D:/Code/PortingiOS/UniXNU/out/enuma/stage6-ramblock-probe/22r-pid1-runtime-summary/`
- WSL Windows path: `/mnt/d/Code/PortingiOS/UniXNU/out/enuma/stage6-ramblock-probe/22r-pid1-runtime-summary/`

| File | Bytes | SHA256 |
|---|---:|---|
| boot.img | 203505664 | `fe9d2bcfa49270d17a20a0e70effbf2e2ad71a599a29f8b751c718dd02afada8` |
| payload.img | 201326592 | `5ddfeab69dc05b1fb9f54283c76195168e0800c5929bda397d3c759f7fec8302` |
| manifest.json | 4663 | `1ee43511cb327ea1d23c4553ac991eda6f29cb8e3d1d01c2a5d00a4ba4a21441` |

`commands.json` preserves full argv/cwd/returncode for the normal `unixnu build
payload --kernel <reviewed prelink> --config <existing local config>
--data-ramdisk <existing restore.dbr> --trust-cache <existing bundle>` and
`unixnu bootimg --fd <existing FD> --dtb <existing enuma.dtb> --ramdisk <22r payload>`.
Both commands **exit 0**; no kernel build or temporary board/probe edits. Canonical
payload scratch outputs were updated normally; historical candidate directories
were not overwritten. Source FD SHA256
`e524988b8a05f15847ffc991170de8a5e0ead607400421e0835084497a71bf1e`, source DTB
`42d36a005024e1a7c55cb5da077a13bb17e9fb9a79dc9dfac8a61cf1e182f698`, BootShim 192 B,
header v1 and firmware+DTB boot-kernel hash match the previous baseline.

Payload-contained kernel SHA256 is **exactly** the approved prelink
`48da518122894ba21344c016f09cbc62238848d83dd0ac32f97246c76795cb4d`; no entry/reset
patch or reseal transformed it. Actual old 21r site `0xfffffff00741ff58` is normal
BL `0x940b7ec5` to credential update, not a reset-cave B. Collector site
`0xfffffff00742006c` is BL `0x97ff30cb` to `0xfffffff0073ec398`.
Resolved probe/panic-screen configuration is off. No automatic reset is injected.

Incremental self-check **exit 0**: boot ramdisk binds to payload; payload contains
the reviewed kernel; actual selected ADT properties retain UUID
`9071148B-B025-402D-AD7A-48464D8B5FFF`, 8 GiB DRAM and 512 MiB owned window;
payload remains 192 MiB, RAM-root arguments/data/trust metadata unchanged. No full
unchanged ADT/FAT/trust audit was repeated. All files copied across environments
were hashed and matched; `copy-validation.json` records the result. The final
Windows read-only checker with externally pinned manifest also **exit 0**.

The first packaging wrapper exited 1 **after both build commands succeeded**:
manifest generation incorrectly expected Context.bootimg. Corrected only the
ignored wrapper to read actual header pagesize; `--finish-existing` validated the
two successful command records and continued checking/copying without rebuilding.
Logs: `/root/enuma-step10/logs/pid1-package-22r.log` and
`pid1-package-22r-finish.log` (continuation exit 0). This was a packaging wrapper
failure, not a kernel or image failure. Both Python packaging scripts py_compile
exit 0; final functional checker exit 0 supersedes that syntax-only check.

Prepack upstream HEAD check: UniXNU
`00f47f6875749dec49bb782718dff1de28006856` (newer than earlier snapshot), uefi-sheng
`66421cb7bb5694843aec8de1ca3d1de4c20cca38`; active base/source pins stayed unchanged.
Candidate `review-bindings.json` records parent-reported deep/verifier conclusions
bound to patch/native/prelink hashes; automatic audit JSON was not edited.

**Independently executed final packaging command** (no rebuild, device action or full audit):

```powershell
wsl -d Ubuntu-22.04 -- /home/wh1stl3/.local/bin/python3.11 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/check-enuma-pid1-package.py --candidate /mnt/d/Code/PortingiOS/UniXNU/out/enuma/stage6-ramblock-probe/22r-pid1-runtime-summary --manifest-sha256 1ee43511cb327ea1d23c4553ac991eda6f29cb8e3d1d01c2a5d00a4ba4a21441; exit $LASTEXITCODE
```

Verifier reported **exit 0**, independently extracting the contained kernel hash
`48da518122894ba21344c016f09cbc62238848d83dd0ac32f97246c76795cb4d`, binding the
boot ramdisk to the payload and confirming both image hashes/sizes and both SVC
site/word/target tuples above. Selected ADT UUID/8 GiB DRAM/512 MiB window and the
RAM-root/trust/arguments/firmware sources match the 21r baseline incrementally.
The checker's printed `self-checked` is a fixed script label; this independent
execution's conclusion is **verified for packaging bindings**, not merely an
implementer self-check. Parent-reported deep/manual PASS WITH CONDITIONS plus
independent mechanical/packaging PASS satisfy host candidate delivery; automatic
audit remains manual-review-required/exit 2, with a separate hash-bound manual
supplement. No automatic JSON, code or candidate was changed for this closeout.

Limit: the checker does **not** explicitly assert manifest `probe_disabled`.
No-reset-injection evidence rests primarily on the entire contained kernel hash being
identical to the deep-reviewed kernel and on the actual SVC instructions, not
merely a flag or absence of reset text. This does not prevent a real runtime panic.
No observer count refresh or exit-summary visibility has been verified; the later
photo contains launchd text, not an identified observer display.

The later 22r single-use entry has been executed and consumed. Never reuse either
22r or 21r entry/claim. The requested close-up has now been supplied and confirmed;
do not request the same photo again or boot again to obtain evidence.

## 22r device panic and media organization (2026-11-10)

This is **self-checked media/record organization**, not implementation analysis or
a new device operation. Source conclusions are the user's panic report and terra's
visual transcription relayed by parent; reviewer is independently locating the
PMGR trigger conditions. Caller and line are now confirmed by the user and terra
as recorded below; no root cause or panic PID is established by this task.

Existing actual execution snapshot (not rerun): ignored
`.cache/cp22r-20261110-fastboot-current-result.json`, round
`cp22r-20261110-fastboot-current`, records entry invoked once/child returncode 0,
boot returncode 0, stderr 0, boot size 203505664 B/SHA256
`fe9d2bcfa49270d17a20a0e70effbf2e2ad71a599a29f8b751c718dd02afada8`,
claim absent -> present, empty marker retained. Prior sanitized commands:

```
pwsh -NoProfile -File UniXNU-enuma/.cache/cp22r-20261110-fastboot-current.ps1 -AuthorizeDeviceThisRound
# sole entry boot, serial redacted; NOT repeated in media task:
fastboot -s <REDACTED> boot D:/Code/PortingiOS/UniXNU/out/enuma/stage6-ramblock-probe/22r-pid1-runtime-summary/boot.img
```

Device revision remains `7772f75fef46bfeeff899db25554f555ee27670c`, uncommitted
working tree. That execution JSON's `user_observation=pending` is its capture-time
snapshot; the later user/photo observation is this separate supplement. Neither
execution JSON nor candidate/claim was edited for the media update.

User explicitly authorized moving **only** the supplied photo, keeping its basename:

- Original: `.cache/media/微信图片_20261110202502_367_25.jpg`.
- New: `.cache/media/stage7-pid1-22r-20261110/微信图片_20261110202502_367_25.jpg`.
- 5857736 B, SHA256 **before and after move**:
  `a534193b5dc75e42de300d8c5a9cc378297c21fb04d0c611cf05a57db9c9fa27`.
- Source existed; destination directory did not exist. New directory created,
  exactly one file moved; source path now absent. Other media untouched.
- Host command: `Move-Item -LiteralPath 'UniXNU-enuma/.cache/media/微信图片_20261110202502_367_25.jpg' -Destination 'UniXNU-enuma/.cache/media/stage7-pid1-22r-20261110/微信图片_20261110202502_367_25.jpg'`.
- Photo and new `media-record.json` both pass `git check-ignore` (exit 0).
  Original media stays local/ignored, not committed or uploaded.

Reported visible observations:

- Panic: `AMFI: No PMGR? @ConfigurationSettings.cpp:235`.
- launchd text includes `xpcproxy spawned pid3`,
  `Successfully spawned restored_external[3] because speculative`, `service running`.
- These are visible logs, **not independent confirmation of complete exec/syscall
  health**, and do not identify panic as belonging to PID3.
- PID1 observer text was not seen in the supplied-photo transcription.
  `Flushed74` belongs to launchd's log, **not** the observer SVC counter.
- Caller **`0xfffffff004ac9420`** and `ConfigurationSettings.cpp:235` are now
  explicitly confirmed by the user; terra actually read the new close-up and
  clearly confirmed the complete `AMFI: No PMGR?` panic. This supersedes the
  earlier uncertain-caller transcription. No further identical close-up needed.
- New photo, already in the target directory and **not moved**:
  `.cache/media/stage7-pid1-22r-20261110/微信图片_20261110203216_368_25.jpg`,
  6883239 B, SHA256
  `887fc1dcc12cc7b3514a7d23272081034eded3be56ba73115fcd86cad6b017d0`.
  Path/hash and confirmation source appended to ignored `media-record.json`.
- The new photo also shows two groups of missing persona type 6 / errno 3,
  and PID3 requests for logd/notification_center/system.logger with lookup error 3.
  Record this visible sequence only; no causal relationship is concluded.

Next: await reviewer's final analysis, not another copy of the same photo.
No device action, code/candidate change, rebuild, claim cleanup/replay,
commit or push in this task. Area levels and whole-stage acceptance do not change.

## 23r supplied photo and stationary-screen report (2026-11-10)

**self-checked media/record organization only**, not implementation analysis.
User authorized moving only `.cache/media/微信图片_20261110232546_369_25.jpg`
into newly created ignored
`.cache/media/stage7-pmgr-23r-20261110/微信图片_20261110232546_369_25.jpg`,
retaining the basename. Destination was absent; source now absent. Size6082128 B,
SHA256 before/after
`065a6fec43aa856e71ab201cb7eeb3811cd842c5981306a8ed336b28a490145d`.
Same-directory `media-record.json` records paths/hash, source of observations,
execution binding and limitations. Both ignored; no22r media/claim was accessed.

Binding is existing `.cache/cp23r-user-authorized-01-result.json`: sole fixed
entry and boot returned0, boot203505664 B SHA256
`1f4574a1dcdcc9a7a551a07ac79565b2a5a0274546952ddd3f3fe24ae4e47207`,
reviewed contained kernel
`bf9f7e12bb05dc3a09f1a732fbcdb83d7729f6378f65ea7fbe77646514edc072`.
Its claim state was consumed/retained; this task only reads the execution JSON,
not the marker. That JSON's pending observation is a capture-time snapshot and
was not rewritten. Device revision remains
`7772f75fef46bfeeff899db25554f555ee27670c`, uncommitted work preserved.

Parent-relayed terra visual reading of the supplied photo:

- launchd `Early boot complete` / `Continuing system boot`;
  restored_external/xpcproxy pid3, status running, `Successfully spawned`.
- `NVRAM unavailable`, boot-stage registry missing, `mount_tmpfs /mnt5`;
  `No MRM cache` / `Unable load cache`; bootstrap path ENOENT;
  logd/notification_center/logger lookup ESRCH. Record visible text, no causal
  interpretation or claimed equivalence with the offline QEMU failure.
- Photo **top is cropped**. No stage3/stage23/fail-stop/panic/AMFI No PMGR text
  was seen in the available frame. Non-observation cannot establish absence of
  panic or success of PMGR/AMFI; **direct stage23 evidence is missing**.

User subsequently said **“一直停在这里”**: remaining at the same
launchd/restored_external log screen. No later panic/reset was reported, but exact
observation duration was not supplied. Do not invent stable minutes. A static
screen proves neither kernel hang nor stable execution. Video remains pending;
reviewer is analyzing actual control flow offline. This task does not declare
complete exec/syscall health, stable userspace, PMGR runtime PASS or stage7
acceptance. No area level changes. Wait for video/reviewer findings without
rebooting for evidence. No device/build/QEMU/code/candidate/claim/commit/push action.

Reviewer supplement: fixed unique pmgr2 and the synchronous bsd_bufferinit-following
hook (assembled bsd_init.c:775–779, before bsd_utaskbootstrap:1202 and
load_init_program:1282), together with publisher's only mode2 successful return
after checkpoint23 (`package/ShengPlatformPower.cpp:82–98,135–173`, fail:38–42),
support **mode2 publisher checks completed and returned — control-flow inference**
from the bound23r image and downstream launchd/restored_external logs. Stage23
text was **not directly observed**. This is not all AMFI paths, sustained liveness
or complete runtime acceptance;22r also showed PID3 before panic. Exact reasoning
and limits are in pmgr-23r-diagnostic.md. RAM-root is restore ramdisk without a
complete GUI; no established UART/USB log channel or automatic adb/restore query.
Current23r directory has no supplied full/early video. Next host action is
reviewer read-only UFS resource/interface preparation, not enabling UFS or writing
userdata; Android retained. No area/stage promotion.
