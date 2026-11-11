# 24r UFS reuse observation — partial host preparation

## Latest: observation-only variant implemented; deep review evidence-only (self-checked)

2026-11-11. Parent-relayed deep static review `ses_e35de8053ffel32m1bGoaREoKE`
returned **CHANGES REQUIRED on evidence/wording only**; it judged the source
completion contract correct and required no source change. This section
supersedes the "execution unknown" handoff below for the observation-only
increment.

Implementation location: temp ShengUfs worktree only
(`ShengUfs-enuma-resource-guard-20261111`, fixed HEAD
`e2b32cc429e8cf1501161c1d8c517f8994ceb9b2`, working tree) plus ignored device
evidence `.cache/ufs-observation-only-20261111/`. **Nothing entered this device
repo's source or any remote.**

Variant: default-0 `NATIVE_UFS_OBSERVATION_ONLY`;1 requires both
`NATIVE_UFS_REUSE_DIAGNOSTIC=1` and `NATIVE_UFS_EXTERNAL_STORE_PROVIDER=1`
(illegal values/combinations `#error`). Entry only `native-ufs-observe-reuse=1`
with `native-ufs-root` and `native-ufs-probe` absent. The o=1 `-Werror` unused
blockers were fixed inside the existing conditional blocks (`NativeUfs.cpp`
hostBringUp/be32w/timerTicks/publish block; `RootCommands.h`
hostNop/hostScsi/hostQueryRead/hostRead4k; `RootQueue.h` whole block, guard
placed after the header comment so default `-E -P` text is unchanged).

Official matrix NEW `.../.cache/ufs-observation-only-final3-20261111` exit0:
4 default cells, 4 explicit o=0 cells, o=1 legal cell (archive `82811fc3...`,
215 undefined, old seven missing symbols zero references), 3 combination
rejections, 2 illegal-value rejections; component guard 54/624 and host 633/639.
Delivery `.cache/ufs-observation-only-20261111/`: source-snapshot,
`increment.patch` SHA256 `51c851e1...05321a`, `evidence.json`, `SHA256SUMS`.
The patch applies on the fix2 clean baseline and reproduces the snapshot
byte-for-byte. All self-checked; no independent verification.

Deep narrowing (now reflected in `evidence.json` and `SHA256SUMS`):

1. identity/`explain_default` runs only in the two external=0 cells
   (`scripts/build-enuma-ufs-store-matrix.py:114-126` else branch); external=1
   and observation cells check symbol sets only
   (`scripts/build-enuma-ufs-observation-matrix.py:68-73`). Four-cell
   function-body equivalence is not claimed.
2. After o=1 admission `ufsReuseDiagnostic` (`NativeUfs.cpp:194-225`) is
   noreturn: invalid profile, summary-format failure and normal summary all end
   in `ufsReuseFinish` (`:188-192`, IOLog plus permanent `wfe`); no panic,
   reboot or normal-XNU continuation; `:1848-1849` is unreachable. The
   diagnostic still maps/allocates GCC/HC/SMMU via `mapPhys` and three
   OSSharedPtr maps (`:207/213/218`). The write path is compile-time unreachable,
   not absent write code. Parking one CPU does not stop other CPUs, firmware or
   DMA; a watchdog may still reset (`:185-187`).
3. Host tests run default macros; o=1 is not dynamically exercised.

Source/patch snapshot hashes unchanged: NativeUfs
`3fe914c0bb62d953e3d4a9e4131b0a7ab5f9189f8246f19446258d5295e4839a`,
RootCommands `96fe7124912fa748c8aad410cfb02938b937578b288ebe45026f44a762492cdc`,
RootQueue `84d9049b636515c84c955e4ba6d7258d41489acc98e115ea4ca55b7df380dff9`,
patch `51c851e14f9cd0f8408d406db3d0e2d19603efaec333a6f1139e62da8c05321a`.

Not done: no native/prelink/link-map, no payload/boot, no final ABI gate, no
personality/PMGR-observer rebinding, no24r candidate/entry, no device/claim/MMIO,
no grade promotion. No24r device authorization.

Next: independent verifier reruns
`scripts/build-enuma-ufs-observation-matrix.py --source <temp ShengUfs>
--output <NEW ext4>` (no `--archives-from`), component
`tests/platform_guard_test.py`, patch apply/reproduction on a clean baseline,
record check and `git diff --check`; reviewer judges the external=1 equivalence
gap and final native/prelink/ABI gates before resuming24r native/prelink.

## Previous resumed result: real native link blocked (self-checked)

The parent-relayed reviewer cleared the two earlier implementation blockers:
the successful23r record locates its resolved `.config` beside `tree/` in work;
VirtioMmioBlock/VerifiedRoot are the canonical ShengUfs dependency closure, not
grounds to exclude components or enable their runtime features. Storage now
records both dependencies, with status still planned; record check exits0
(`14 structured areas checked`). Earlier failure records below remain historical.

Isolated build root (original failure directory also retained):
`/root/enuma-step10/UniXNU/out/enuma-24r-ufs-observe-build-resume1`.
Official defconfig resolution succeeds; `config-delta.json` establishes the ONLY
resolved difference from23r is `XNU_NATIVE_UFS: false -> true`. Native Virtio block
and owner-root probe/audit/trust remain disabled/absent. `status.json`,
`resolved-modules.json` and `archive-plan.json` record the actual local-module
ShengUfs selection and implicit dependency recipes. No feeds/pin/base edit.

All archive recipes reached the final build script, including successful actual
ShengUfs and PMGR builds. `build/sheng-ufs/effective-compile-argv.json` proves
`NATIVE_UFS_REUSE_DIAGNOSTIC=1` AND `NATIVE_UFS_EXTERNAL_STORE_PROVIDER=1` in the
effective cc1 command, alongside the official builder's forced
`NATIVE_VERIFIED_BLOCK=1`/`NATIVE_VERIFIED_BLOCK_MULTI_POLICY=1`.
Wrapper's first evidence parser incorrectly expected concatenated -D spelling;
that ordinary parser defect was fixed without changing compilation semantics.
Its failed logs are saved in `history-before-wrapper-parse-fix/`.

**First real build blocker:** final native link fails at assembled
`tree/.cache/xnu-work/makedefs/MakeInc.kernel:238`, make exit2 / outer Python1.
`logs/kernel.log:1435284–1435302` records:

| Missing symbol | Actual referring compiled source |
|---|---|
| `_boot_progress_poll` | NativeUfs.cpp1538, normal read-window poll (declared weak at64) |
| `_verified_root_key` | NativeUfs.cpp1416, configureVerification |
| `_verified_root_policies` | NativeUfs.cpp1379, configureVerification |
| `_verified_root_policy_count` | NativeUfs.cpp1369/1374/1378, configureVerification |
| `_vr_open` | NativeUfs.cpp1423, configureVerification |
| `_vr_verify_block` | NativeUfs.cpp1529, normal verified read |
| `_vr_xnu_crypto` | NativeUfs.cpp1424/1529, normal verification/read |

Those bodies remain in the force-loaded diagnostic object even though the
reviewed observe-only entry terminates before normal takeover/root operation.
The entry-mode condition does not satisfy static link imports. No library,
policy/key/stub, Virtio runtime or owner-root enablement was added to conceal this.

### Bound input evidence

`link-blocker-evidence-final3/result.json` is the final successful evidence
collection (exit0). Earlier collection failures are retained: wrong absolute nm
location; relative direct-object cwd; missing tool PATH; force-load option-token
classification. These are evidence-runner defects, not additional native-link
attempts. The final run covers1010 actual object inputs and ALL11 archives
(8 force-load + direct libcc_kext/namespace-corecrypto + resolved firehose library).
All7 names are absent from their definitions. Full archive strong-definition
duplicates are zero; all6 stores are uniquely `libRamBlock.a:EnumaRamBlockStore.o`.
Actual RamBlock provider source is unchanged; its newly built archive identity is
not relabeled as the old archive. Final image/map ownership is NOT checked because
the link did not produce a native executable or map, and prelink never ran.

Actual ShengUfs archive:546448 B, SHA256
`512592e15eec29378dbad4a1d50c0e9aa12914b156335f0bb6afbf60b56631ae`.
Actual new RamBlock archive:310480 B, SHA256
`127b13234013257a1c5b6fa7c780840e78a07d404577ba18d7cbd8798ba6e7b1`.
All11 input copies/hashes, `link.filelist`, effective compile argv, nm outputs and
commands are saved there. The original failed execution did not log full linker
argv. `link-command-recovered.json` explicitly records recovery by a successful
same-input `MAKEFLAGS=-n` dry-run, NOT an original exec trace or second real link.
Virtio archive is absent from the recovered link selection; no virtio ADT node
was introduced (A's existing property evidence reused). Frozen23r native/prelink/
metadata hashes were rechecked unchanged.23r/22r candidate images/claims untouched.

### Previous handoff: reviewer changes required; implementation execution unknown (superseded above)

Parent-relayed static reviewer `ses_e3603a005ffebvXk4lJEssmdjT` returned
**CHANGES REQUIRED**. Real official authentication requires a trusted key,
multi-policy bundle and metadata; BootProgress also has runtime dependencies.
These are not appropriate additions merely to obtain read-only observation.
Simply disabling verified macros would let ordinary authentication/reads succeed
and is not an acceptable fix.

The recommendation, **not an implemented or verified result**, is a default0
`NATIVE_UFS_OBSERVATION_ONLY` variant. When1 it must require both diagnostic and
external-provider macros1. Only the explicit ObserveReuse entry remains available;
ordinary configure/startRoot/start/read/auth methods must fail before allocation
or publication. Preserve class/vtable/free, authentication's three states and the
external RamBlock empty backend; ordinary builds retain their existing behavior.
The regular reviewer judged this not a deep-review case; escalate if the actual
change affects ABI, completion or ownership. Do not add fake key/policy/crypto/poll
providers, enable owner-root, link Virtio as a shortcut or edit the base builder.

The subsequent coder delegation `ses_e3645c8dbffejyxMO4b6nBkdtL` returned a
`cyber_policy` platform block without execution results. **That round's execution
and working-tree changes are unknown**: the next session must read-only inspect
actual git diff and artifacts before confirming what, if anything, was changed.
This handoff task only edits documentation and does not resume that implementation.

First next action: read this handoff and current governance, perform that read-only
reconciliation, then confirm the runtime environment/platform restrictions before
addressing the pending implementation. After implementation, check the variant
matrix, default behavior, rejection paths and symbol closure, obtain independent
review/verification, then resume native/prelink/package work. Do not enter device
authorization now; the last confirmed device state is Android.

The parent's earlier claim that project rules stop all retries was corrected:
orchestration line114 addresses quota/region errors, not every safety block.
Do not conflate this result with the earlier QEMU fixture, cite removed fixture
wording as a current prohibition, or suggest agent/prompt changes to bypass it.
The user's current request is handoff only. Claims21r/22r/23r are consumed and
must not be accessed, deleted or replayed. No new device authorization, level
promotion, commit or push.

No new native/prelink/map/payload/boot or24r execution entry exists. Final-image
RamBlock mode call targets, personality diff, PMGR/observer layout rebinding,
package/parameter negative tests and entry stubs remain pending. Old observer
manual approval is not transferred to a nonexistent24r image. A's host evidence
is retained, not runtime acceptance. No24r device authorization.

### Independent verifier handoff for this blocked checkpoint

Do not run a device client or repeat the failed link merely to rediscover it.
Read `resume-result.json`, `logs/kernel.log`, final3 `result.json` and
`nm-commands.json`. Rerun the stored nm argv with its recorded cwd and the11
stored archive copies (write a NEW verifier output), then the archive-only checker:
`python3.11 scripts/check-enuma-ufs-store-symbols.py --archive <each-of-all11> --output <NEW.json>`.
Recheck config-delta/effective cc1 macros and frozen23r hashes. Rerun
`/home/wh1stl3/.local/bin/python3.11 -B /mnt/d/Code/PortingiOS/UniXNU/scripts/porting-record.py check --device /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma`
and `git diff --check`. Final build/test independent verification remains pending
until a separately reviewed resolution produces an actual candidate. No level rise.

## Earlier partial checkpoint (superseded by actual link failure above)

2026-11-11: **self-checked only; no candidate, no device authorization**.
Storage remains planned. Board/defconfig changes are unfinished integration,
not a release configuration. No24r native/prelink/payload/boot hashes exist.

## Actual checkpoint and first blocker

The A property gate used the fixed base devicetree.generate, the23r resolved
Context and data/trust switches, and identity read into memory from its contained
ADT. `mtype` extracted13840 bytes, SHA256
`42cd05283c02f7e1e64e387de8832b02e7ee059c9bb5444da35da39601810757`.
Device DTS only adds `&ufs { status = "okay"; };`; PHY remains disabled.
The new14012-byte ADT differs only in random-seed, arm-io ranges, intc reg and
the new ufshc properties. All other properties, including CPU affinity/timebase
and original interrupt/phandle properties, are byte-identical. All old arm-io
MMIO tuples retain physical address/size. GICD/GICR remain
0x17a00000/0x10000 and0x17a60000/0x100000. New ufshc is
offset0xd84000/size0x3000 under base0x1000000: physical0x1d84000.

Actual assembled tree root:
`/root/enuma-step10/UniXNU/out/enuma/ipados-17.7.11-21H461/enuma/tree`.
`drivers/ArmCpu/ArmCpu.cpp:230–273` maps `/arm-io/intc` using
`bus[1]+regions[index]-bus[0]`, not the old fixed base. Existing compiler JSON
for pe_identify_machine/pe_fiq/pe_serial was replayed with preprocessing only:
BCM2837/PI3_UART active, HAS_GIC_V3 undefined, pe_fiq.c81–114 mapping excluded.
pe_identify_machine.c170–209 reads ranges then adds reg; serial.c831–839
does the same for gpio/aux (neither node exists in either ADT). Full assembled
XNU source search for gSocPhys/pe_arm_get_soc_base_phys and the old physical
base/GIC literals found no fixed-old-base consumer; hwtrace's mappings also add
the DT reg. These are static/preprocessor checks, not runtime validation or
independent review. Evidence: ignored `.cache/ufs-adt-equivalence-24r-20261111/`
(`result.json`, commands, ADTs, three preprocessed files).

The B attempt stopped **before any kernel build/prelink invocation**:
`.cache/build-ufs-observe-24r.py:41`, AssertionError
`Missing actual resolved configuration`. Its assumed baseline path
`/root/enuma-step10/UniXNU-enuma/.config` does not exist. It created only the
isolated preparation root
`/root/enuma-step10/UniXNU/out/enuma-24r-ufs-observe-build` and device copy.
Do not reuse that output path blindly or delete it automatically. The intended
Windows24r candidate path was confirmed absent and was not created.

The new wrapper selects both NATIVE_UFS_REUSE_DIAGNOSTIC=1 and
NATIVE_UFS_EXTERNAL_STORE_PROVIDER=1 for the official ShengUfs builder; it has
**not run**. Final compile commands/macros, personality, GCC window/guard contract,
all archive/native/prelink/map symbol ownership and RamBlock call-target checks,
new PMGR/observer hash-bound audits, package checker and entry/stub tests remain
unperformed. Fix2 independent/deep acceptance is not asserted here.

Final mechanical self-check: four helper AST parses0; `git diff --check`0.
The porting-record checker exits1, **not PASS**: canonical ShengUfs resolves
VirtioMmioBlock and VerifiedRoot dependencies (`base/components.toml:135`), which
have no enuma area record. This was exposed by the new selection, not fixed by
inventing hardware evidence or changing the base catalog. Parent must review the
actual dependency/link selection before resuming; correcting the runner's config
path alone is not sufficient. No dependency/record workaround was attempted.

Firmware DTB is distinct from the generated hardware.dtb/ADT. The existing23r
packager explicitly passes `/root/enuma-step10/inputs/enuma.dtb` to bootimg;
this device DTS edit does not rewrite that input. Its final hash/FD/trust/UUID/
DRAM/window reuse must still be checked in the eventual24r package; no automatic
rebind or successful packaging is claimed. Do not modify frozen23r/22r images
or old claims. Canonical component ID is ShengUfs; feeds/base/pins are unchanged.

## Future diagnosis: interpretation fixed before device execution

Before requesting a new device authorization, confirm Android has been restored,
confirm the target serial in memory, finish independent reviewer/verifier gates
and require recording from before the single boot. No actual device entry exists
yet for24r; the23r consumed entry must not be reused for this purpose.

- Capture BEFORE_GCC, BEFORE_HC, BEFORE_SMMU and the final short summary.
- OBSERVED_REUSE_SHAPE means only that this invocation observed a supported
  shape; it is not takeover authority, DMA-drain, ownership or LUN proof.
- REFUSED/INCOMPLETE must retain the first reason. NOT_READ is not zero.
- Missing final summary, exception or reset means incomplete: stop without
  retry, parameter change or continue. An abort/SError may precede any visible
  marker or occur at any stage; no output does not mean no reads occurred.
- Abort: return to the diagnostic-disabled23r configuration for **offline
  analysis only**, not another boot. HC/queue busy: record not-takeover-eligible
  and pursue a firmware-quiescence design, not repair/reset via this diagnostic.
- Returning to Android is a separate authorized device action. After that new
  authorization, identify the intended serial/product and use only explicitly
  directed `fastboot -s <target> reboot` if in fastboot; reconfirm Android product
  and readiness with explicitly directed read-only adb commands. Do not issue
  these commands now, flash userdata, auto-continue or replay old claims.

## Rerun handoff

Resolve the actual existing Context/config location read-only before revising the
build runner; do not infer it from a filename. Parent retains integration and
acceptance. Verifier should rerun the ADT script with a NEW evidence output
directory (the script currently refuses existing output), the three preprocessor
commands, then final build/tests once the blocker and unfinished integration are
resolved. Current self-check commands: Python AST parsing of the four new helper
scripts, base `scripts/porting-record.py check --device <device>` and device
`git diff --check`. Never execute a real adb/fastboot client for these checks.
