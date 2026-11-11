# enuma guarded original-PMGR host checkpoint (2026-11-10)

**Historical implementation checkpoint; latest host-only packaging and independent
static conclusions supersede its pending items in [23r record](pmgr-23r-package.md).
No device operation or stage acceptance. The later deep necessity ruling permits
only first controlled diagnostic preparation on the frozen23r hash, without
mode1/3/fault dynamic completion as a precondition; see
[diagnostic preparation](pmgr-23r-diagnostic.md). Those dynamics are still unverified.**
Parent relayed deep session `ses_e3a88bcd9ffeZmVaIm30c4njBR` PASS WITH CONDITIONS
for this implementation scope; that is not final-diff approval. Existing observer
work and media were preserved. No claim was read/modified and no base source was
edited. Apple-derived artifacts remain in ignored local output.

## Provenance / dependency contract

- Publisher and builder reference: UniXNU/UniXNU-sheng
  `6bc0ce1e8c3a3733110a80dd80ddfb2a1ca46555`, files
  `package/ShengPlatformPower.cpp`, `scripts/build-sheng-platform-power.py`.
  Source-specific MIT and repository BSD-2-Clause-Patent notices are retained in
  `package/PMGR-NOTICE.md`. No Apple implementation is copied into tracked code.
- Device HEAD: `7772f75fef46bfeeff899db25554f555ee27670c`, uncommitted working tree.
- Base (Windows and ext4): `693f5d9cae8a408dd18b39f3f9fdc4228c934241`.
  Its tracked `scripts/audit-amfi-pmgr-contract.py` has no workspace diff and SHA256
  `19a0429a75341947b6908da69a26c2b9e686602e3b0f8795968009475fe5df08`.
  The earlier device-repository 404 was a mistaken dependency location, **not** a
  missing base audit. Reference builder line 28 resolves from its ROOT; assembled
  trees contain the base scripts and overlay device scripts. The audit supports
  `--candidate`, requires sibling `.json`, and derives donor/output from __file__.
  Our runner copies the pinned script unchanged into a private ignored view and
  explicitly links the supplied donor/candidate/manifest; its fallback cannot run
  because input existence/hash checks precede execution. No reference machine path
  or newest-file fallback is used.
- XnuPrelink pin: `f1d80d37528a33e24643583787123c652b70a268`. Existing ext4 checkout
  shows dirty files; for `native_prelink.py` and `emit_prelink.py`, actual bytes
  normalized only CRLF -> LF equal `git show HEAD:<file>` exactly. They were not
  rewritten. Evidence: ignored `.cache/pmgr-contract/dependency-eol.json`.
  `native_prelink.py` raw SHA256
  `a2da7ea8a4431f6c26418ecab9be718c0fbd2f0aa2334ba8d32c2270d2ac81dc`,
  normalized SHA256
  `5bd80b8c63deec29b747c28253e02308a56d5f8cdb37c9d315e7c8af7012d017`.
  Runner enforces helper revision and normalized hash.
- Read-only upstream HEAD check: base `3fd05b9f3ea0e31f415551a8868ef7df6db5ce3a`,
  uefi-sheng `66421cb7bb5694843aec8de1ca3d1de4c20cca38`; no active pins changed.

## Actual inputs and build

ext4 base `/root/enuma-step10/UniXNU`, work
`out/enuma/ipados-17.7.11-21H461/enuma/`, assembled tree `tree/`.

- Donor `out/ipsw/21H461/kernelcache.decompressed`, SHA256
  `f18b4df865405f2a287b84977d7aca745e056d656d9fc9df1662970ce2969de7`.
- Explicit reference frozen before replacing target prelink:
  `out/enuma/pmgr-selfcheck/reference-22r.macho`, SHA256
  `48da518122894ba21344c016f09cbc62238848d83dd0ac32f97246c76795cb4d`;
  corresponding `reference-22r.json`, SHA256
  `de2dfc7da3ebb7d7f1f82304d8ded0b5360c4063baad1baf2e2a490f378b0253`.
- Linux compiler argv comes from actual
  `tree/build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/iokit/DEVELOPMENT/IOPlatformExpert.cpo.json`.
  Keep original header warning suppressions after added Wall/Wextra/Werror;
  do not inherit Weverything. No xcrun or SDK from another machine.
- `build/sheng-platform-power/inputs.json` is a required explicit local input,
  not checked in; board archive recipe fails closed without it. Build runner
  supplies every path and SHA256, including frozen reference and manifest.
- First compile exposed the reference filtering of Linux header suppressions
  (`vm_kern.h:629`, missing-designated-field initializer); repaired builder argv,
  not XNU headers. Linux llvm-objcopy lacks Mach-O globalize-symbol: remove only
  this object's initializer section, then change only its named initializer
  symbol's N_EXT bit. Object code equality and final actual linkage are checked.

Host commands, cwd `D:/Code/PortingiOS/enuma` (no device tools):

```powershell
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/.cache/build-pmgr.py
# exit 0; normal tree/patch preparation, archive recipe, native build, prelink;
# 5202 unchanged source mtimes restored, build/prelink 41.11 s.
# Final dependency-pin rerun: exit 0, 5206 mtimes restored, 29.35 s;
# target-build-final.log and build.json supersede initial artifact hashes.
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/.cache/pmgr-contract/final-checks.py
# exit 0: final base byte-contract 0, seven unittest methods 0,
# final prelink audit 0, missing-package rejection 1 as expected.
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/.cache/pmgr-contract/audit-observer.py
# exit 2, manual-review-required, not PASS.
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/.cache/pmgr-contract/disassemble.py
# exit 0; llvm-objdump exit 0, original executable bytes unchanged.
```

Full expanded commands/exits: ignored `.cache/pmgr-contract/final-checks.json`,
`prelink-command.json`, `build-command.json`, `target-build.log`,
`target-build-final.log`; ext4
`out/enuma/pmgr-selfcheck/build.json`, `observer-command.json`, `observer-build.json`.
Archive report in `tree/build/sheng-platform-power/build-report.json` binds source,
compile record/argv, archive, all imports and 340 slots.

## New target artifacts / static results

- Native `tree/build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped.noctf`:
  SHA256 `5b8fd1811e39d6415550786578c1fb96346df32a0ba2a35efbd3ff50a251a74f`.
- Prelink `kernel/kernel.macho`:
  SHA256 `bf9f7e12bb05dc3a09f1a732fbcdb83d7729f6378f65ea7fbe77646514edc072`.
- Metadata `kernel/kernel.json`:
  SHA256 `d5224f1075dce7a5053d8a338d4454562999c4cb86031afd742feb5d311b7dc9`.
- Archive `tree/build/sheng-platform-power/libShengPlatformPower.a`:
  SHA256 `613ecb34657a3cdfd97b8de59516079d6d607d0e42544c4780d46e3136cd40af`.
- Final audit `.cache/pmgr-contract/final-prelink-audit.json`: 340 actual linked
  vtable pointers and 205 import symbols checked for existence only (not complete
  binding proof); original AMFI/ApplePMGR executable
  preserved, no AppleT8011PMGR included. arm64 subtype 0/iOS17 deployment checked
  on original/late relocatable provider objects. Base contract rerun on new final
  prelink also exited 0, not merely on the old reference.
- Actual unique startup BL `0xfffffff0076f6cac` immediately follows the actual
  `bsd_bufferinit` BL; target `_sheng_pmgr_run=0xfffffff0079e4ee4`.
  Manual initializer BL `0xfffffff0079e50ac` -> `0xfffffff0079e5798`;
  no automatic initializer pointer remains. Metaclass `0xfffffff007ae3fb8` in
  writable `__DATA`, initializer/run in resident executable `__text`.
  All values above are from the final dependency-pin build; final original-byte,
  vtable/import/hook audits and observer mechanical audit reran against these
  hashes, not the first-pass `4b0218ec...` / `9aa678ca...` images. Archive and
  inspected addresses were unchanged in the final pass.
- Observer relocated: begin `0xfffffff0073f00a8`, svc `0xfffffff0073f0398`,
  exit `0xfffffff0073f0410`, observer `0xfffffff0073f0204`, write
  `0xfffffff0073f5188`. Existing full mechanical audit reran on new artifacts,
  source-object/patch/input-stamp bindings; automatic JSON still lists its five
  manual gates in `out/enuma/pmgr-selfcheck/observer-audit/audit.json`, unchanged.
  The later independently closed five manual gates are recorded separately in
  pmgr-23r-package.md; they are no longer pending independent review. Old addresses and old
  deep/verifier approval are not reused as new-layout approval.
- Board parameter is exactly one `pmgr=2`. Negative tests cover missing, duplicate,
  wrong value, alternate spelling and sheng-pmgr aliases. Package-capable audit
  reads actual contained `unixnu.toml` and kernel bytes via mtype, then runs the
  archive/final-hook audit; no package exists this round, so that path is **not
  tested**. `--require-package` without actual payload rejects, exit 1.

## Ownership evidence and remaining finite review gates

Ignored `.cache/pmgr-contract/original-pmgr-disassembly.txt` is actual unmodified
ApplePMGR executable extent SHA256
`2c433279d004803b7ef02948e550ad6b77aa3f84b02a06a357e00fa738310a99`
in a code-only diagnostic Mach-O for existing llvm-objdump; not simulation.
`disassembly.json` binds the source bytes; `ownership-imports.json` resolves actual
ADRP/LDR/BR import thunks and low vtables against the frozen reference.

Observed static edges (not a completed ownership proof):

- Provider C2 `0xfffffff0049f003c` calls IOPMGR C2 through `0xfffffff004a32464`,
  copies constants via memcpy/memmove thunk `0xfffffff004a325cc`. D2
  `0xfffffff0049f019c` tail-branches through `0xfffffff004a32470` to native IOPMGR D2.
- Nub create `0xfffffff004a22568` requests `0x740` via typed original allocator
  thunk `0xfffffff004a3220c`, constructs through native IOService C2 thunk
  `0xfffffff004a324dc`, records construction via `0xfffffff004a324f4`, calls
  init helper `0xfffffff004a225f4`; false result releases via vtable byte 40
  at `0xfffffff004a225cc` before returning NULL.
- Init stores safeMetaCast(provider) to nub+0x88 at `0xfffffff004a22660`;
  its subsequent resource-property paths and native init/free dependencies need
  closure review for empty description. No provider retain/description-retain
  conclusion is promoted merely from this store.
- Both original provider/nub vtable slot14 resolve to native IOService::free;
  slot5 to OSObject::release. Exact targets are in ownership-imports.json.
- Actual XNU `IOService.h:949–955` says waitForMatchingService does not consume
  the dictionary and returns an extra reference. Our dictionary and matching
  result releases follow that contract; successful initial nub/provider references
  remain permanent. Source behavior still requires independent review.

**Initial pending items (later independent static conclusions and remaining runtime
limits are recorded in pmgr-23r-package.md; automatic JSON is unchanged):**

1. Deep confirm finite constructor/destructor/native init/free closure, zeroed
   allocation, empty-description property branches, provider/description retention,
   partial-init failure cleanup. In particular original create does not visibly
   check allocation NULL before its constructor call; qualify allocator failure
   semantics rather than claiming our returned-NULL check covers an internal fault.
2. Deep final diff: late nlist globalization and resident RW metaclass after
   lockdown, single caller / preModLoad-static-postModLoad adjacency, failure-stage
   coverage and fail-stop, publication/matching retention, 340 slot exactness.
3. Modes1/2/3 runtime/harness and runtime failure injection have **not run**.
   Unit input gates are not lifecycle/ABI runtime proof. No new board mock created.
4. New observer layout's manual gates; verifier must rerun final build/tests/audits
   after final changes. Final packaging additionally needs actual contained-args
   negative/positive checks and deep/verifier acceptance. No boot/payload/new entry
   was made. Unchanged FAT/trust/ADT baselines were not re-audited.

Package/observer gates have since independently passed as parent relayed; no
repeat is needed. Current verifier action is only the new offline entry/diff
checks in pmgr-23r-diagnostic.md. Do not rebuild the frozen reviewed images or
repeat completed gates. The ext4
`out/enuma/pmgr-selfcheck/target-build-final.log` does not exist and must not be
cited as independent build-exit evidence; retained command/build.json and actual
hashes/artifacts are the build evidence.
