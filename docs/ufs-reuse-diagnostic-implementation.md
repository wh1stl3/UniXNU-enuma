# Default-off XNU reuse-shape diagnostic: fix2 self-checked (2026-11-11)

## Latest: scheme D complete at archive/host scope; self-checked only

Main approved the narrow unused-helper conditional after the initial blocked
delivery. Pre-edit grep found `hostStoreOpen` called only by the store export in
production (plus the existing default-mode `tests/RootCommandsBridge.cpp:60`).
`gStoreRegionFirst/Blocks` are referenced only by store exports. The SAME
`NATIVE_UFS_EXTERNAL_STORE_PROVIDER` conditional now excludes that helper and
private region state too. Function bodies, shared store/log transport state,
geometry/log state, warning policy, class/layout/vtable/personality, probe/start/
stop and diagnostic terminal semantics were not changed. No other helper needed
exclusion. `NATIVE_UFS_EXTERNAL_STORE_PROVIDER` defaults0 independently from
`NATIVE_UFS_REUSE_DIAGNOSTIC`; external=1 omits all six store definitions even
when diagnostic=0. No weak/renaming/stubs/archive surgery.

### Final cumulative patch and measured identities

Complete9-file patch (including untracked source):
`.cache/ufs-reuse-diagnostic-fix2/final-source-20261111/ShengUfs-reuse-diagnostic-fix2-final.patch`
SHA256 `91500f6ceb448c3b4717457aa7828c4315f26b51359e9c14ad79c11f84cdee4d`.
Final source review restored the original trailing blank line in RootCommands.h,
so its diff now consists of ONLY the two conditional directives. The complete
four-build/identity/host matrix was rerun on that exact final source, exit0, in
`/root/enuma-step10/UniXNU-enuma/.cache/sheng-ufs-store-fix2-final-source-20261111`;
no archive reuse was used for this authoritative final run. The prior
final-20261111 patch5b4be2cb... and its outputs are historical and retained.
Old incomplete patch, archives and logs remain at their original paths. Source
snapshot and SHA256SUMS/selfcheck-final.json bind the delivery; it is not yet
independently verified or integrated. Canonical component ID is ShengUfs, checkout
branch enuma/resource-guard, baseline `e2b32cc429e8cf1501161c1d8c517f8994ceb9b2`.

| external | diagnostic | libShengUfs.a SHA256 | NativeUfs.o SHA256 | store definitions / full globals |
|---|---|---|---|---|
| default0 |0| `1feb0c6ea0148cd152734a5a30bac7ddef0a9c92303894c79ee2553fde82b44f` | `d38fcf28362844ac5f45f4c7848f285a09cc7bec73a57cded87e6283155c52a2` |6 /87|
| default0 |1| `41ff8643c531b1fecb65a32a4a8cd4289d9fe99739152e462a0fe4968cc8b4f0` | `11975093723cb0399b316111bb708c3b0cbd5bc8921f64d6e1f0c7dd34db89fb` |6 /87|
|1|0| `f52cc0097011924c2ff4c1811ae0702cfb5c776d788d4c06084a14727ad9fc03` | `a8ce266941722e4bd5e3d1479d37f1f5b99bd89a3c80b35893a121cd6e93d777` |0 /81|
|1|1| `eeaf5a0043fa2333d419be10ded90429cc15b9142560203563a8d95c679703e8` | `32ddd66661a12990533127348d7862f6c35f4aac33714f0f926ff56a7f1176a3` |0 /81|

All four actual official target builds exit0 with existing -Werror/unused policy.
Default global-defined symbol sets equal the corresponding fix1 sets; external
sets are exactly those sets minus the six store names. Full strong-definition
scan of each external archive plus the actual prepared RamBlock archive finds
**zero duplicate strong symbols of any name**, and all six stores exclusively
in EnumaRamBlockStore.o. Default+RamBlock negative controls find precisely the
six known duplicates. RamBlock archive before/after SHA256 remains
`d180b1a41dbc0d998e79ac672bbe08a3a7d24a4239052c1277bdf2f2837f05f0`.
These are archive-level checks, not a native/prelink link claim.

### Default object difference explained, not mislabeled as ar mtime

`scripts/audit-enuma-ufs-object-identity.py:explain_default` passed for both
diagnostic settings before the external builds proceeded. Compile arguments
are identical after substituting isolated-tree paths. Complete preprocessed
default code differs ONLY in source-line constants added by XNU's `panic` macro
(`NativeUfs.cpp` line numbers shift when #if/#endif lines are inserted). Both
objects have exactly45 changed instructions, each the corresponding line-number
MOV immediate; every other instruction and every byte outside those MOVs is
unchanged. Other non-DWARF section payloads, sizes, flags, alignment and
relocations are identical. This is not a change to mode/default logic.

DWARF differences are expected from source coordinates/line tables, isolated-tree
paths and derived string/index offsets. Debug strings compare equal after path
substitution AND lambda source-line substitution; each substituted lambda line
is checked against equal actual source-line text and unchanged column. No
timestamp macro or changed compiler option was needed to explain the difference.
Whole NativeUfs.o bytes are **not** equal; therefore the fix2-vs-fix1 archives are
**not ar-mtime-only differences** and must retain new measured identities.
Machine-checkable proof is in each default cell's `identity.json`; exact
preprocessor/disassembly commands and logs are retained in the target build root.

Separately, actual historical Windows fix1 backups c9884f64.../36abde21... still
have NativeUfs.o bytes equal to the authoritative WSL fix1 objects
`a88c2e9fa0c3a90ce1125d9fc2786145276cebd70bc63bdef7fe8ae156c03ded` /
`0e73514808de6c42630a27a47d984b06506c7e714e1b00357c10c1b8d6dd6eea`.
Their actual ar member mtimes differ (full header/member evidence in
`selfcheck-final.json`). This historical comparison is distinct from fix2.

### Host matrix and exact execution history

Expanded production-header/entry test compiles real unchanged
`package/EnumaRamBlockStore.cpp` as a separate TU and extracts the real
NativeRamBlock.cpp `attachStore` mode assignment plus complete short-circuit
eligibility predicate. Its ineligible body is a counted trap, not a replacement
overlay implementation. For64 combinations per diagnostic setting (observe
absent/0/1/invalid2 × persist absent/0/1/2 × root/probe absent or present=0), real
provider mode remains0, no persist parse occurs and eligibility body entries=0:
GPT/open/overlay are never reached through this real guard. This is bounded
guard evidence, not a full RamBlock start or XNU argument-text-parser test.
Diagnostic refusal, observe-only terminal and conflict semantics are unchanged.
ASan/UBSan nonPIE runs pass633+64 off and639+64 on, actual compile/run exits0.
Guard54/624 is reused from unchanged fix1 source; old transport bodies are
unchanged, so no transport regression was repeated merely for conditional guards.

All commands use Ubuntu-22.04 `-u root` and absolute
`/home/wh1stl3/.local/bin/python3.11`, from Windows enuma cwd:

```powershell
# Authoritative exact-final-source run: all four builds + identity + host, exit0.
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/build-enuma-ufs-store-matrix.py --source /mnt/c/Users/Administrator/AppData/Local/Temp/opencode/ShengUfs-enuma-resource-guard-20261111 --output /root/enuma-step10/UniXNU-enuma/.cache/sheng-ufs-store-fix2-final-source-20261111
# Earlier execution history follows; these do not replace final-source identity.
# Four actual builds, default identity audits and archive/nm checks all pass;
# initial host launch below fails because cross-toolchain PATH selects Darwin clang.
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/build-enuma-ufs-store-matrix.py --source /mnt/c/Users/Administrator/AppData/Local/Temp/opencode/ShengUfs-enuma-resource-guard-20261111 --output /root/enuma-step10/UniXNU-enuma/.cache/sheng-ufs-store-fix2-final2-20261111
# Final runner exit0: verifies production source identity, copies completed cells,
# rescans symbols and runs host test with isolated host PATH and /usr/bin/clang++.
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/build-enuma-ufs-store-matrix.py --source /mnt/c/Users/Administrator/AppData/Local/Temp/opencode/ShengUfs-enuma-resource-guard-20261111 --archives-from /root/enuma-step10/UniXNU-enuma/.cache/sheng-ufs-store-fix2-final2-20261111 --output /root/enuma-step10/UniXNU-enuma/.cache/sheng-ufs-store-fix2-complete-20261111
```

The first runner's overall exit1 was ONLY the host compiler-wrapper selection
(`-no-pie` unused); no target warnings were disabled. Final host compiler is
explicit native `/usr/bin/clang++`; sanitizer/Werror flags remain, including the
unchanged pre-existing extraction-harness unused-function flag (not applied to
any target build). Final `commands.json`, `host/result.json`, four cells and
`history/` retain actual argv/cwd/exits; the earlier reused-archive-commands.json
stays in the historical final-20261111 delivery rather than being relabeled as
a final-source rebuild.
The earlier final attempt also preserved its conservative identity refusal:
DWARF lambda display names contain line coordinates, now explicitly verified.
Old outputs were never overwritten; archive output was saved per cell before
the internal build tree was reused. Prepared ABI/toolchain reuse is not a fresh
toolchain build or reproducibility claim.

Independent verifier must run the first command with a NEW output path, **omit
--archives-from** so it reruns all final builds/tests, then cumulative patch apply/
source comparison, record/diff checks. Deep incremental review must cover the
actual new conditional guards and evidence; acceptance/integration stays with
main. Candidate final native/prelink/map uniqueness command is below and is NOT
executed here. `candidate-selection-final.json` records both defines=1 and the
supported `--local-module driver:ShengUfs=<checkout>` selection; actual candidate
compile wiring, ADT/personality/link/package checks remain future work. No active
board/defconfig/DTS/pin/base/RamBlock/device/MMIO/push changes or24r kernel build.

## Historical initial fix2 blocker (resolved above; partial delivery preserved)

Deep's scheme D supersedes the historical provider question below: retain
EnumaRamBlockStore.cpp and the reviewed RamBlock archive unchanged. In the
temporary ShengUfs checkout, `NATIVE_UFS_EXTERNAL_STORE_PROVIDER` defaults to0;
nonzero excludes the six store definitions plus their private `storeMode`.
It is independent of `NATIVE_UFS_REUSE_DIAGNOSTIC`; geometry/log state and
class/probe/start/stop/terminal logic are not edited.

Actual matrix run (WSL root, Windows enuma cwd) stopped at its first compiler
blocker, exit1: `RootCommands.h:282: hostStoreOpen` is now unused under external=1,
and the official target uses `-Werror,-Wunused-function`. This brief explicitly
allowed the private storeMode conditional only; no transport-header change or
global warning suppression was attempted. The compiler's complete output is
retained, not converted into a successful four-cell result. Main must obtain
narrow permission for the newly exposed private-helper warning before resuming.

| external | diagnostic | measured archive SHA256 | result |
|---|---|---|---|
| default0 |0| `c5bec70584d524bcfbe17d5c9d72119cefbfb38e4ceabbcd5e043043b432a0ab` | build0; unchanged full global-defined set, six stores; all-symbol duplicate scan vs RamBlock finds precisely six stores |
| default0 |1| `63641dff14542fd3d4b2e9a7ac7d6077c90ac6882ee66b395eafb0db242a317f` | same checks0 |
|1|0| none | compile1, no external archive admitted |
|1|1| none | not run after blocker |

Exact runner: `scripts/build-enuma-ufs-store-matrix.py --source
/mnt/c/Users/Administrator/AppData/Local/Temp/opencode/ShengUfs-enuma-resource-guard-20261111
--output /root/enuma-step10/UniXNU-enuma/.cache/sheng-ufs-store-fix2-20261111`,
using `/home/wh1stl3/.local/bin/python3.11` on Ubuntu-22.04 `-u root`.
`commands.json` records actual cwd/argv/CCC flags/exits. The output is NEW;
`fix1-before-{0,1}` copies were made before builds. The internal build tree is
reused across cells but each completed cell is saved separately. Do not reuse
this output path on resume; the runner rejects it. Neither a fresh ABI/toolchain
build nor reproducibility is claimed. New archive identities are not old labels;
any ar-mtime-only comparison must be established from actual member bytes, not
assumed from prior fix1 behavior.

Delivery selfcheck measured both archives' member headers/payloads: mtimes
changed AND NativeUfs.o payload hashes changed in both default cells; symbol-index
payloads are equal. Thus this fix2 rebuild is **not** an ar-mtime-only difference.
Object-content difference cause has not been audited; unchanged export sets do
not prove code/ABI byte identity. Full comparison is in `selfcheck.json`.

Expanded `tests/reuse_admission_test.py` is written but **not run**: it links the
real unchanged empty provider TU and extracts the exact real RamBlock
`attachStore` mode/eligibility predicate. The ineligible body is a counted trap,
not an overlay reimplementation; it cannot establish a complete RamBlock start.
The intended64 combinations cover observe absent/0/1/invalid2, persist absent/
0/1/2 and root/probe absent or present=0, under each diagnostic build. Mock boot
argument values test entry semantics, not XNU parser text conversion. Guard54/624
and old633/639 remain prior independent fix1 evidence only; fix2 host pending.

### Candidate-stage commands (written, not executed)

Canonical ID remains ShengUfs. Candidate selection must independently record
`NATIVE_UFS_EXTERNAL_STORE_PROVIDER=1` and `NATIVE_UFS_REUSE_DIAGNOSTIC=1`, consume
the fork via `--local-module driver:ShengUfs=<checkout>`, and retain RamBlock's
existing member. No active board/defconfig/DTS or source pin was edited here.
The isolated candidate selection is recorded in ignored fix2 delivery; it is
not an assembled/accepted24r configuration. Final integration must route both
defines into the actual ShengUfs compile command (global Linux env is rebuilt by
the base, so merely exporting an outer CCC variable is NOT a proven selector).

After a separate candidate build, run (substitute actual paths; repeat
`--archive` for EVERY final force-loaded archive):

```sh
/home/wh1stl3/.local/bin/python3.11 scripts/check-enuma-ufs-store-symbols.py \
  --archive <candidate-libRamBlock.a> --archive <external1-ShengUfs.a> \
  --archive <each-other-final-archive> --native <actual-native.macho> \
  --prelink <actual-kernel-prelinked.macho> --link-map <actual-native-link.map> \
  --output <new-candidate-symbols.json>
```

The checker rejects ALL duplicate strong global definitions, not just stores;
requires the six archive definitions solely from EnumaRamBlockStore.o, one
definition each in final native/prelink, and actual native link-map provider
indices pointing to that member. Apple-style link-map parsing is written, not
yet exercised against a24r final map. Candidate ADT/personality/link/package
audits, independent verifier and deep incremental review remain pending.

Delivery: `.cache/ufs-reuse-diagnostic-fix2/` contains the full cumulative source
patch including untracked source, SHA256, partial build evidence, selection and
handoff. This patch is incomplete/unverified and must not replace fix1's accepted
identity. No device, real MMIO, candidate build, archive surgery or push.

Incomplete patch SHA256:
`881230f6c7f080308acb35a6a2cbdc9168db4d47eadf7d1e68fafced4d4ac6d1`.
Quick self-check: component/device `git diff --check`0, three Python AST parses0,
porting-record check0 (14 areas), cumulative patch reverse-apply check0 (WSL
executable-bit warnings retained). These are not the pending host/build matrix.

## Historical fix1 checkpoint (provider proposal below superseded by scheme D)

**Fix1 component independently PASS (reported by main); candidate not built or
admitted.** The earlier diagnostic c89aec23 actual diff was CHANGES REQUIRED;
the fixed patch `d7e5af986eb999e8d8f504b887cdb3b888f80dbf5bfea18601769d375aa7e5e4`
now has independent clean-baseline apply/8-file byte equality,633/639 cases,
guard54/624 and record/diff PASS. Independent entry instruction audit reports
only4 mapped32-bit loads, no mapped store or takeover path. Limited deep
re-review PASS adjudicates first-read risk as controllable for a first controlled
diagnostic; this is not takeover/ownership/runtime acceptance. Do not reopen an
unbounded access research prerequisite. Candidate preparation was authorized,
but the concrete RAM-root/UFS symbol-provider issue below needs a deep decision
before configuration/build. No device/real MMIO/kernel/prelink/candidate or
active base/pin/feed/lock change occurred; Android remains in user use, no QR.

## Independent identity and candidate preflight checkpoint

Current authoritative WSL root:
`/root/enuma-step10/UniXNU-enuma/.cache/sheng-ufs-reuse-diagnostic-fix1-20261111/`.
This round's read-only sha256sum confirmed:

| File | SHA256 |
|---|---|
| archive-0/libShengUfs.a (off) | `481b41d26172868ac5f4daa3c91b631c0226a17cd9fb194cb44e2b32083a3546` |
| archive-1/libShengUfs.a (on) | `44182f7fdfc202806b8d223c06338a387e6fd6df3f6c69176aae70a8a929a7e0` |
| archive-1/NativeUfs.o | `0e73514808de6c42630a27a47d984b06506c7e714e1b00357c10c1b8d6dd6eea` |

Main reports an earlier relayed hash transcription error; the values above,
confirmed from actual WSL files, are authoritative. Do not propagate a mistyped
relay or rewrite backups to make hashes agree. Delivery backups under
`.cache/ufs-reuse-diagnostic-fix1/archive-{0,1}/` retain their actual earlier
hashes c9884f64…/36abde21… listed below. Reviewer confirms archive differences
are only ar mtime, with member contents unchanged. This genuine backup-versus-
current-header difference is distinct from a relay typo. The verifier reused a
build directory; this is not fresh/clean rebuild reproducibility. Historical
selfcheck JSON and rejected patch/artifacts remain untouched.

Intended separate candidate: `24r-ufs-reuse-observe`, inheriting23r RAM-root,
pmgr=2,192MiB payload, FD/DTB/trust. Any new native/prelink/payload/boot must get
its own measured hash;23r prelink
`bf9f7e12bb05dc3a09f1a732fbcdb83d7729f6378f65ea7fbe77646514edc072`
must not be relabeled as the new kernel. No24r candidate or one-shot entry has
been created, no old candidate or claim accessed/overwritten.

**First concrete integration issue (new binding decision, no attempted link):**
device board.toml:40 appends EnumaRamBlockStore.o to the RAM-root archive via
scripts/build-enuma-ram-block-store.py:16–17. Its
package/EnumaRamBlockStore.cpp:5–13 strongly defines the same six
`native_ufs_store_{mode,open,read,write,sync,gpt_check}` C symbols as the reviewed
ShengUfs archive (NativeUfs.cpp:1080–1143/1226). Read-only llvm-nm on both actual
archives confirmed all six as T definitions. Base build-xnu-4k-baseline.sh:
638–642 and718–745 force-load both archives for the current RAM-root/no-Virtio
configuration, so simply adding ShengUfs leaves duplicate strong definitions.
No linker failure is claimed to have been executed; this is actual symbol-table
evidence plus the selected link rule. Boot-argument mode0 cannot fix a link conflict.

Deep question: may the diagnostic-only candidate omit the explicit enuma empty
store-backend member and bind RAM-root's six store imports to the already reviewed
ShengUfs mode0/cold interfaces, while preserving RAM-root behavior? This changes
the existing symbol provider, so the implementer has **not** done it. Do not use
weak/duplicate-symbol suppression, remove archive members, alter reviewed UFS
exports or change the base to force a build. If approved, add a narrowly scoped
cold-store/RAM-root binding audit before native/prelink/package work.

Source resolution itself does not require feeds/pin changes: the official
`--local-module driver:ShengUfs=<fixed-patched-checkout>` override is supported
by scripts/unixnu/feeds.py:145–158/components.py:98–127. Board components/archive
entries must use canonical ShengUfs. ADT root enuma.dts:12 already has
qcom,sm8250; shared ufshc is disabled (sm8250.dtsi:55–60), so a diagnostic-only
board enable/unique HC check will be necessary after the binding decision, not
PHY enablement. Board/defconfig/DTS/feed/lock are unchanged in this round.
After this issue is resolved, candidate source/packaging and its independent
verification remain to be done before requesting new device authority.

## Four fixes

1. **SM8250 GCC first, on both snapshots.** Base100000 relative offsets77004
   (GDSCR PWR_ON[31]),77010 (AXI),77018 (AHB),770cc (aggregate AXI). All three
   CBCRs need ENABLE[0]=1 and CLK_OFF[31]=0. HWCG[1] never excuses CLK_OFF.
   No polling/enabling/repair. Native code maps only the177000/1000 page and
   uses these SM8250 offsets, never legacy SM8550 GccUfs.h definitions.
   GCC rejection/read failure leaves HC/SMMU unread; sample2 gates again before
   resampling HC/SMMU. Structural helper is `validateProfileShape`, not a claim
   of established physical access eligibility.
2. **Architecturally consistent stream matching.** Require IDR0 S1TS[30] and
   SMS[27], bounded NUMSMRG[7:0] and sufficient SID width. Unrelated S2TS/NTS/
   CTTW/interrupt capabilities need not be zero. EXIDS[8] is a capability;
   sCR0.EXIDENABLE[3] is mode. Legacy mode uses SMR.VALID[31]; extended mode is
   unsupported and refuses before SMR/S2CR. IDR1 page64K, page-count/bank-count/
   S2-only-bank ranges and IDR2 PTFS4K/IAS/OAS/UBS are checked individually,
   not using unexplained large masks. Extra16K/64K/VMID16 capabilities can pass.
   Counts>128 refuse (never truncate); only matched, in-range contexts are read.
   The old SMS=0 sample0x40000080 is now a negative, not the successful fixture.
3. **Narrow SMMU whitelist.** sCR0/IDR0/1/2 only, then complete supported
   SMR/S2CR and matched candidates' CBAR/CBA2R/SCTLR. No GFSR+48, fault/TLB/
   vendor register access. HC IS is read only. Maximum is now568 reads:
   2*(4 GCC+14 HC+4 SMMU ID/control+256 table+6 context). No PHY/UIC/unmatched
   context, old descriptor or queue-pointer memory reads, writes or write callback.
4. **Truthful progress/output.** Per-word read masks, parsed-slot/bank/reference
   flags and software completion steps prevent early-zero-fill being reported
   as observations. NOT_READ means uncollected/unparsed in the selected sample;
   software completed_step is NOT DMA completion. Unparsed slot never prints
   valid slot0. Each domain's first map/read attempt is preceded by BEFORE_GCC,
   BEFORE_HC or BEFORE_SMMU. Markers only mean reaching a print point, not display
   delivery or precise asynchronous-SError attribution. New UfsReuseReport.h
   bounds summary to14 short lines (<128 chars each), buffer1536 bytes, plus
   at most96 marker bytes. Every snprintf result is checked; failure/truncation
   clears partial output and terminates with a fixed INCOMPLETE message.

Fixed references supplied by deep: Linux v6.1
`830b3c68c1fb1e9176028d02ef86f3cf76aa2476`, gcc-sm8250.c3257–3262/
2856–2873/2841–2853/1090–1107; gdsc.c20/62–89; clk-branch.c16–25/42–77.
The fixed arm-smmu.h was also read for IDR0/1/2/sCR0 field definitions.
Earlier alioth comparison remains criteria-only at
FFT-infra/NativeUfs-alioth@`d6bd207347cb9c870452ff7d2e6ae488b9b13feb`, not a port.

## Unchanged constraints and delivery

Disabled/ObserveReuse/Takeover, compile `NATIVE_UFS_REUSE_DIAGNOSTIC=1` plus
independent `native-ufs-observe-reuse=1` double opt-in, and any root/probe argument
presence conflict before reads/maps remain. No CLI address/SID override.
SM8250-AC takeover is always false. The new branch never enters legacy inspect/
adopt/root/hostBringUp/hostStopQueue/configureUfsSmmu or publishes DMA/commands/
block devices/Data-log-export. After bounded observation it parks the current
CPU with WFE, without a software reboot request or normal start continuation.
That is not stopping firmware/other CPUs/DMA; watchdog reset remains possible.
OBSERVED_REUSE_SHAPE is not ownership/drain/PA=IOVA/real-DMA-width/coherence/LUN
proof, and visible unique references do not exclude secure/other-domain owners.

Same checkout `C:/Users/Administrator/AppData/Local/Temp/opencode/ShengUfs-enuma-resource-guard-20261111`,
branch `enuma/resource-guard`, HEAD `e2b32cc429e8cf1501161c1d8c517f8994ceb9b2`;
uncommitted/unpublished/unintegrated. Full8-source-file patch (including untracked):
`.cache/ufs-reuse-diagnostic-fix1/ShengUfs-reuse-diagnostic-fix1.patch`, SHA256
`d7e5af986eb999e8d8f504b887cdb3b888f80dbf5bfea18601769d375aa7e5e4`.
NativeUfs.cpp, README, UfsPlatformResources.h, UfsPlatformEntry.h,
UfsReuseAdmission.h, **new UfsReuseReport.h**, platform_guard_test.py and
reuse_admission_test.py are bound in ignored selfcheck.json. Generated bytecode
is excluded. Old guard-only and rejected diagnostic patches/artifacts/logs remain.
No old transport/SMMU write policy, queue timeout, ABI/vtable or registration change.

## Implementer command history (subsequently independently verified)

Windows cwd `D:/Code/PortingiOS/enuma`; existing Ubuntu22.04 root/Python3.11:

```powershell
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/c/Users/Administrator/AppData/Local/Temp/opencode/ShengUfs-enuma-resource-guard-20261111/tests/reuse_admission_test.py --output /root/enuma-step10/UniXNU-enuma/.cache/sheng-ufs-reuse-diagnostic-fix1-20261111/reuse-host-release
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/c/Users/Administrator/AppData/Local/Temp/opencode/ShengUfs-enuma-resource-guard-20261111/tests/platform_guard_test.py --output /root/enuma-step10/UniXNU-enuma/.cache/sheng-ufs-reuse-diagnostic-fix1-20261111/platform-host
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/c/Users/Administrator/AppData/Local/Temp/opencode/build-enuma-ufs-reuse-20261111.py --output /root/enuma-step10/UniXNU-enuma/.cache/sheng-ufs-reuse-diagnostic-fix1-20261111
```

Final commands exit0. ASan/UBSan non-PIE:633 off/639 on cases, including every
one of568 potential read-failure positions, all GCC power/enable/CLK_OFF/HWCG
refusals with subsequent-domain zero reads, second-sample gating, SMS0 before
tables, SMS1/additional legal capability acceptance, extended-ID refusal, full
table sharing/multiple/masked/bounds/change/busy/fatal failures. Every partial
snapshot output is checked against masks/parsed flags; every insufficient buffer
capacity and every snprintf-failure position is checked, including canaries.
Mock trace forbids SMMU+48/fault/TLB/vendor reads. Real production headers/
probe/start/diagnostic execute with mock map/read/terminal; source forbidden-call
checks and saved target disassembly are bounded evidence, not whole-platform proof.
Guard54/624 passed; its extracted logic was unchanged by the final formatter-only
compiler fixes. Unchanged TransferPoll/SmmuTakeover/RootCommands passes are reused.

Both off/on real build-arm-driver.py ShengUfs builds, object audit/ar/nm checks
exit0. Off494744B SHA `c9884f64c0d4fdeebb83a2e99f1015ae40d903eeadb6b7b6ab42fd390897bad9`;
on558416B SHA `36abde217c2bd6e1407a75c06b0891f68899c3afb34f8f9ee17d7dd787241a26`.
Exports equal off/on and prior guard. First two default-build failures are retained:
formatter:23 zero-argument -Wformat-security, then formatter:28 unused static
function; fixed via explicit %s and static inline, not target-warning suppression.
Build uses unchanged base tools, official linux_env, reused prepared headers/
recipe/ABI with isolated ROOT/output; no kernel build/prelink/fresh-build claim.
Exact commands/cwd/exits and all attempts in `.cache/ufs-reuse-diagnostic-fix1/`:
`build-commands.json`, `reuse-host-release/result.json`, `platform-host/result.json`,
`archive-0/`, `archive-1/`, `selfcheck.json`. These retain implementer history;
main has now relayed independent fix1 PASS and limited deep re-review PASS.
No component test/build was repeated merely to update this documentation.

**Before packaging (not performed here):** first resolve the symbol-provider
decision above; then verify NativeUfs component/archive and
class inclusion, root personality/KernelConfigTables binding, and full ADT root
compatible plus unique HC/cells/ranges. No personality/ADT/candidate was changed
or assembled by this task. Fix1 component review/verification and first-read-risk
adjudication are complete, not pending. Candidate source/link/ADT/argument and
actual-package checks, independent candidate verification and fresh device
authority are not complete; **currently no device release**. Main retains final
integration and deep routing of the new symbol-provider decision.
