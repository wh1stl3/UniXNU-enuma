# enuma UFS input evidence (2026-11-11)

**self-checked, host-only input validation; not hardware readiness.** No driver
selection/linkage, device/claim operation, userdata/write window, kernel build or
activation-file change. Android retained; storage remains `planned`.
Reviewer static PASS WITH CONDITIONS is separate from mechanical verification.
Final follow-up self-check: real checker and24 tests exit0; record/diff/ignore0.
Independent verifier rerun remains pending.

## Takeover hard stop: insufficient ownership evidence (2026-11-11)

Main reports the reviewer's **one deep-requested public-source check** ended
**INSUFFICIENT EVIDENCE**. Actual takeover is blocked; this is not a request for
another device run or an open-ended offline tooling/research task.

Fixed sources: MiCode/Xiaomi_Kernel_OpenSource `elish-r-oss`, commit
[`52a2f180865f8368828985d6384130acd093fa93`](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/commit/52a2f180865f8368828985d6384130acd093fa93)
(commit body Pad5Pro/5G, `enuma_user_defconfig`,
`LA.UM.9.12.r1-08000-SMxx50.0`); Linux v6.1 commit
[`830b3c68c1fb1e9176028d02ef86f3cf76aa2476`](https://github.com/torvalds/linux/commit/830b3c68c1fb1e9176028d02ef86f3cf76aa2476).
Xiaomi `ufshcd.c:10951–10985` shutdown blocks its own requests and holds PM/clock;
`:1614–1670` checks UTMRLDBR/UTRLDBR zero; `:5885–5900` clears/polls HCE.
Upstream `ufshcd.c:1121–1168/4569–4590` provides a cross-check, **not** a guarantee
that an unknown UEFI owner or inflight interconnect DMA has finished. Under the
current evidence, **HCE=0, doorbell=0 and RSR=0 do not authorize old-page release**.
Xiaomi `ufs-qcom.c:823–890/1552–1590` has PHY/clock/power prerequisites;
upstream `sm8250.dtsi:2120–2164` iommus0xe0/0x4e0 echoes the static records but
does not prove runtime exclusivity or PA=IOVA. JESD223B/C official body returned
403 and was not obtained; search snippets are not substitute clauses. Actual
board HCI version/errata and the complete Xiaomi enuma DT chain remain unverified.

| Hard blocker | Required referencable contract/evidence |
|---|---|
| Unique submission ownership | Who can stop UEFI, asynchronous and other execution-domain TR/TM submissions, acknowledge the stop and transfer sole ownership? |
| Complete DMA termination | For this board's HCI version, which completion definition covers descriptor/data/response and interconnect DMA, with applicable specification/errata and timeout semantics? |
| Retention and failure responsibility | Who retains old pages/mappings/power/clocks, and owns failed-stop recovery and eventual release? |

A citable Qualcomm or firmware-maintainer contract/specification is needed to
close these items before the required deep review can admit actual takeover.
No maintainer has been contacted and no issue/message was sent by this task.
Stop further code/tools/simulation/candidates or public-source expansion here;
the user need not reboot to fill these contractual gaps. The independently
passed guard patch remains deliverable offline, unintegrated and with SM8250-AC
execution rejected. Android remains usable. The unwired identity/QR in-progress
files and prior selfchecks are preserved/paused, not expanded or deleted.

## Component platform admission (2026-11-11)

**Independently verified offline delivery (reported by main); not integrated or
admitted for takeover.** This final documentation-only checkpoint supersedes
earlier pending-verifier notes. Main reports independent static review
**PASS WITH CONDITIONS**, final patch apply--check/apply0 in an isolated tree
from `git archive e2b32cc429e8cf1501161c1d8c517f8994ceb9b2`, and all five patched
files byte-identical to the working tree. Patch SHA256:
`819a4be3f24bd544169039b2dbf428747d18b27d2dca6aed7dda8e0f886f1f66`.
Independent PASS covers54 scenarios/624 extracted-model rejected root starts
with zero MMIO/DMA/queue/SMMU counters, target archive build/exports,
non-PIE SmmuTakeover/RootCommands and record/diff checks. TransferPoll's unchanged
earlier pass was reused. This is not full-archive no-call proof or prelink/runtime
validation. Verifier reused its build directory: **not a fresh/clean rebuild
or reproducibility claim**. No component, patch or artifact was changed/copied
over in this documentation-only round.

Reviewer independently compared the two492600B archives:

| Artifact | SHA256 |
|---|---|
| Earlier archive | `3c02690dbe89921cfbeaa7e502cf582ccc01372629a675320d1dc7aed0fd12f` |
| Verifier archive | `6e7cbe8dabb4f0ca2191ecc10c806bf5c8e5d9b7350538ff1925aa7a8d7976c9` |
| Common NativeUfs.o member | `2e8342b8308b7fafdba60e27913bce1a3c2b8f4d862f63e9d746517fe6f32f03` |

Only8 bytes differ, ar mtime fields at offsets30–33/3302–3305; both members'
effective contents are identical. This closes the archive-content comparison,
not byte-identical archive-file or clean-build reproducibility.
`.cache/ufs-component-guard/final-result.json` retains implementer file/patch
bindings; its pending-verifier label and older `selfcheck.json`/`review-frozen/`
are historical records, not modified to impersonate independent verification.
Component checkout (not a fourth enuma repository):
`C:/Users/Administrator/AppData/Local/Temp/opencode/ShengUfs-enuma-resource-guard-20261111`,
branch `enuma/resource-guard`, HEAD `e2b32cc429e8cf1501161c1d8c517f8994ceb9b2`.
Uncommitted patch: `.cache/ufs-component-guard/ShengUfs-resource-guard.patch`.
The active base, feeds, lock, submodule and device/SoC selections are unchanged.
The previously saved host identity/QR branch remains paused: unwired host core,
parser and QR shim/tests preserved, no DXE/menu/BootServices/GOP connection or
menu candidate. It is not a separate milestone or prerequisite for UFS work.
The patch is ready for offline handoff only: uncommitted, unpublished and not
integrated. Android was restored and is in user use; no device operation here.

Files: new component `UfsPlatformResources.h` pure bounded parser/immutable
selection; `UfsPlatformEntry.h` read-only ADT registry adapter;
`tests/platform_guard_test.py` real-entry extraction/host test; modified
`NativeUfs.cpp` probe/start admission and component `README.md` contract.
No changes to hardware initialization, STARTSTOP, transport, queues, SMMU policy,
DMA allocation/coherency, LUN, timeouts, write windows, publication or exports.

The adapter reads OSData and explicit lengths from `IODeviceTree:/`, not a
guessed address or board name. XNU source
`IOPlatformExpertDevice::init` in `iokit/Kernel/IOPlatformExpert.cpp` imports the
ADT before matching (`IOStartIOKit.cpp`: `gRootNub->init(dtTop)` precedes matching).
`IODeviceTreeSupport.cpp::MakeReferenceTable` imports properties as OSData.
No new ABI/vtable/callback/global registration or concurrent mutation mechanism.
Ordinary boot-time stable registry properties remain an assumption.

Full compatible list: 4096-byte/64-string bounds; final NUL required; empty
elements, duplicates and multiple defined SoC identities reject. Board/OS
compatibles are not SoC identities. Root SoC and HC node identity must agree;
one HC among at most128 arm-io children; exact ADT little-endian cells/reg/ranges
shape, range/overflow/length checks precede admission. Only HC0x1d84000/0x3000
is recognized. SM8250/AC recognized=true, execution=false, no GCC/PHY/SID/
context/LUN/DMA defaults. Raw DAL4e0/e0 do not enter execution; PHY e00 resource
is not conflated with1000 mapping alignment. Both real probe personalities
reject unsupported inputs; root start rechecks before even inspect MMIO.

**Intentional compatibility change approved by main:** SM8550 requires explicit
root `qcom,sm8550` plus consistent parseable HC resources. Missing/invalid SoC
identity now fails closed; no claim that all old SM8550 inputs still work.
Bounded public input check:
[official sheng DTS at fixed6bc0ce1](https://raw.githubusercontent.com/UniXNU/UniXNU-sheng/6bc0ce1e8c3a3733110a80dd80ddfb2a1ca46555/dts/sheng.dts)
line7 contains `xiaomi,sheng`, `qcom,sm8550`; local read-only base
`693f5d9cae8a408dd18b39f3f9fdc4228c934241/scripts/unixnu/devicetree.py:381–388`
preserves hardware compatible strings. Its253–255/375–376 encode ADT reg/ranges
as little-endian64-bit tuples. This supports that fixed source input only,
not historical binary contents/runtime success; no nuwa asset was read.

Actual commands (Windows cwd `D:/Code/PortingiOS/enuma`, Ubuntu22.04 **root**):

```powershell
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/c/Users/Administrator/AppData/Local/Temp/opencode/ShengUfs-enuma-resource-guard-20261111/tests/platform_guard_test.py --output /root/enuma-step10/UniXNU-enuma/.cache/sheng-ufs-resource-guard-20261111/host
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/c/Users/Administrator/AppData/Local/Temp/opencode/build-enuma-ufs-resource-guard-20261111.py --build --regression
```

Guard command exit0: strict ASan/UBSan halt-on-error,36 scenarios/442 rejected
root starts, rejected root/DT paths MMIO/DMA/queue/SMMU counters all0. Production
headers, full real probe and start prefix through guard execute; only permitted
hardware tail is replaced by counters. This does not execute real hardware bodies.
Truncation/empty/duplicate/conflicting/missing identities, unknown board, HC
mismatch/multiple/missing, cells/ranges/length/overflow, SM8250 and AC versus
SM8550 and multi-board-compatible cases are covered.

Final increment command (same Windows cwd/root WSL/Python, exit0):

```powershell
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/c/Users/Administrator/AppData/Local/Temp/opencode/ShengUfs-enuma-resource-guard-20261111/tests/platform_guard_test.py --output /root/enuma-step10/UniXNU-enuma/.cache/sheng-ufs-resource-guard-20261111/host-review-increment
```

Now54 scenarios/624 rejected root starts, production headers and the same real
entry prefixes. Fixtures separate DT root from IOPlatformExpertDevice, and
scanned HC from the non-root service provider. New negatives: independent
root/provider identities, provider-versus-HC reg address/length, wrong property
types, and root/provider/HC property changes after successful probe but before
start. Any malformed compatible OSData list on an unrelated bus child rejects;
finding a valid HC does not short-circuit the whole-bus scan.128 total children
can pass,129 reject. The zero MMIO/DMA/queue/SMMU counts are **extracted-model
evidence**, not proof that the complete archive contains no hardware calls.
The checker retains full ASan/UBSan with Linux-only non-PIE compile/link flags.

Build runner uses byte-identical base `build-arm-driver.py`/`kernel_target.py`,
catalog and official existing `linux_env`, a private source copy and isolated
output under ignored ext4 device cache; prepared kernel headers/recipe/ABI are
read-only links. It does not modify the prepared recipe or rebuild the kernel.
Actual inner cwd is cache `tree/`; `python3.11 scripts/build-arm-driver.py ShengUfs`
exit0, arm64-apple-ios17.0/-Werror object audit passed. Archive
`tree/build/sheng-ufs/libShengUfs.a`492600B; `xcrun ar t`, `nm -g -U`, `nm -u`
each exit0. Existing native_ufs globals exported, internal selector has no global
ABI exports. This is not a final prelink/import-resolution/ABI or runtime test.

**Initial regression failure resolved (self-checked):** the original PIE
`tests/SmmuTakeover.cpp` compiled0/run-11 with empty output; original runner1 is
preserved, not relabeled pass. In a separate baseline directory, extracting the
test and sole production header from fixed `e2b32cc...` and using identical flags
also gave-11. A bounded baseline strace then captured the cause, not merely an
inference from unchanged files: PIE load base0x61ab89cb5000 lies inside ASan14's
allocator reservation. Trace `baseline-trace-1.strace:436` successfully executes
`mmap(0x600000000000,4398046519296,PROT_NONE,MAP_FIXED|...)`, replacing that code;
line437 faults at0x61ab89d793c1, binary offset0xc43c1,
`__sanitizer::internal_mmap+0x21` (pop after syscall). The handler at
0x61ab89d63810 also faults. Symbolizer/disassembly bind those addresses; runtime
has no source-line debug information, and test `main` at SmmuTakeover.cpp:9 was
not reached. Host mmap_rnd_bits=32. This is a baseline host-ASan/PIE startup
collision, not a host-pointer/alignment failure inside takeover logic.

Minimal correction: **host only** `-fno-pie -no-pie`; no system ASLR changes,
dependency installation, test C++ fix or production SMMU/timeout-policy change.
Sanitizers/halt-on-error/default leak detection remain enabled. Baseline corrected
build/run0/0 (ELF EXEC), current SmmuTakeover0/0 and RootCommands0/0. Only trace
diagnostics disabled leak checking because LSan cannot run under ptrace; the
corrected tests did not. TransferPoll's existing pass is reused, not rerun.

Actual corrected invocation (cwd inherited from Windows enuma; inner cwd cache
`tree/`; exit0):

```powershell
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/c/Users/Administrator/AppData/Local/Temp/opencode/build-enuma-ufs-resource-guard-20261111.py --regression --regression-tests SmmuTakeover RootCommands
```

Exact baseline/trace/compile/link/test commands, cwd/exits and causal evidence
are saved in `.cache/ufs-component-guard/regression-investigation/`
`{commands.json,startup-commands.json,completion-commands.json,conclusion.json}`.
The new host invocation is not claimed as a pass of the old PIE invocation.

Exact logs: `/root/enuma-step10/UniXNU-enuma/.cache/sheng-ufs-resource-guard-20261111/`
`commands.json`, `build-result.json`, `host-review-increment/result.json`, `exports.txt`,
`undefined.txt`, regression investigation logs; copied to ignored device
`.cache/ufs-component-guard/` with the patch and reproduction runner.
The previously requested independent final guard/build/exports/non-PIE regression
and record/diff checks have now passed, as reported by main. Do not repeat them
for this documentation-only change; the command history above remains for
reproduction. No QEMU/EL1, full prelink/import-resolution or hardware tests ran.
Final integration/publication remains with main. There is **no device candidate**;
SM8250-AC execution remains rejected. Before any actual UFS takeover phase,
close the ownership/handoff contract (UTRL/UTMRL quiescence, exclusive SID/context,
DMA ownership, PA/IOVA/coherence, timeout-buffer lifetime and LUN identity) and
obtain the required deep review; later device work needs fresh explicit authority.
No device/claim/vendor execution/MMIO/QEMU/candidate/package/
kernel/firmware build/enable/push. Storage remains planned; runtime ownership,
quiescence, SID/context, PA/IOVA/coherence/timeout lifetime and LUN remain unproved.

## Reproduce

From `D:/Code/PortingiOS/enuma/UniXNU-enuma`:

```powershell
wsl -d Ubuntu-22.04 --cd /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma -- /home/wh1stl3/.local/bin/python3.11 scripts/check-enuma-ufs-evidence.py
wsl -d Ubuntu-22.04 --cd /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma -- /home/wh1stl3/.local/bin/python3.11 -m unittest discover -s scripts/tests -p test_enuma_ufs_evidence.py -v
```

Uses installed `dtc` and PyYAML (6.0.3), not DTS regex interpretation. Compiles
live DTS and shared DTSI to dtc YAML; resolves provider phandles using their
`#clock-cells`, `#reset-cells`, `#phy-cells` (and `#iommu-cells` if present).
Supply/pinctrl references have no specifier cells. Bus ranges must explicitly
describe covering identity windows. Unsupported translations are rejected.
The only report destination is ignored `.cache/ufs-evidence/report.json`;
source hashes/paths stay there. No identity/GPT GUID or full DT is exported.
This manually allowlisted summary is the committable evidence, not raw inputs.

## Observed local inputs

Live source `.cache/device-evidence/20261109-live-dt/live.dts`:

| Resource | Parsed evidence |
|---|---|
| HC / ICE (:12757–12798) | `0x01d84000/0x3000`, `0x01d90000/0x8000` |
| Interrupt | GIC tuple `(0,0x109,4)` = SPI265; architectural INTID297, not265 |
| PHY (:29428–29443) | `0x01d87000/0xe00`, ICE alias `0x01d90000/0x8000`, two lanes |
| GCC (:39614) | `0x100000/0x1f0000`; reset provider ID `0x21`, **not register offset** |
| HC clocks, in order | GCC IDs `a7,06,a6,b3,aa`; RPMh ID0; GCC `b2,b0,b1` |
| PHY clocks | RPMh ID0 and GCC ID`ad` |
| Supplies | HC vccq/ref-clk→PM8150 L6, vccq2→S4, vcc→L17, vdd-hba→GDSC; vccq-parent→PM8150A S8; PHY PLL→PM8150 L9, PHY→L5 |
| Reset pinctrl (:32131–32139,:36738–36746) | `ufs_reset`, assert output-low / deassert output-high, pull-down, drive8 |
| SMMU (:10927–10943) | base `0x15000000/0x100000`; separate tcu-base `0x15182000/0x20` |

Shared `../UniXNU-sm8250-common/dts/sm8250.dtsi` has disabled HC and PHY:
HC range `0x3000`, PHY range `0x1000`; no shared ICE resource. Live PHY length
`0xe00` is **not** `0x1000`: shared page-sized mapping does not enlarge the
live resource or prove ownership of padding. Both views are recorded separately.
The checker asserts the shared HC first reg equals the live HC first reg and
both shared nodes remain disabled. Targeted negatives require the exact semantic
errors for shared HC mismatch, nonidentity bus ranges and wrong IRQ (not parse
failures); an enabled shared HC is also rejected.

Firmware `../uefi-enuma/Platforms/Xiaomi/enumaPkg/Library/`:
`ConfigurationMapLib/ConfigurationMapLib.c:34–35` has EnableUfsIOC=0 and
UfsSmmuConfigForOtherBootDev=1; `MemoryMapLib/MemoryMapLib.c:101` maps SMMU
`0x15000000/0xd0000`. Firmware map length differs from DT resource length;
neither establishes post-firmware effective mappings or exclusive context use.
HC has no `iommus` or `dma-coherent`; absence proves neither bypass nor coherence.

## Original GPT, not porting prose

The selected existing capture is
`.cache/live-capture/20261107T141941555586Z/` with
`sda_first_32768.bin`, `sda_logical_block_size.txt`, `sda_sectors.txt`.
Protective MBR, primary header/array CRCs, metadata/usable bounds and all used
partition ranges/overlaps are checked. Linux sysfs size495042560 uses **512 B
sectors**, not4096 B logical blocks: total253461790720 B /61880320 blocks.
Userdata first2686976, last61880314 inclusive,59193339 blocks /242455916544 B.
The earlier existing `20261107T141806Z` capture independently parses to the same
userdata geometry; its extra trailing bytes are not GPT-directed data.
Backup GPT and current-device geometry are UNKNOWN (only historical primary
snapshot); Linux `sda` is **not proof of LUN0**. If originals are missing,
GPT stays UNKNOWN while DT/firmware checks can complete. Invalid present inputs
reject rather than fall back to prose. Tests include repaired-CRC invalid
geometries, so corruption alone cannot mask semantic validation failures.

Parent-relayed luna final read-only inspection of that same capture:
`by_name_links.txt:110` maps `userdata -> /dev/block/sda34`;
`proc_partitions.txt:70` is `259 18 236773356 sda34`. The latter capacity is
236773356 **1024-byte units**, not4096-byte logical blocks. Only the historical
partition mapping is established. Captured `dmesg_first_400` / `dmesg_last_400`
lack the **UFS host -> SCSI H:C:T:L -> [sda]** chain, and luna found no other local
capture completing it. Report field `historical_partition_identity` preserves
this attributed finding without adding a parser or treating it as a current
checker measurement. sda-to-LUN remains UNKNOWN, never assumed0.

## Still UNKNOWN / next real evidence

Actual SID/context exclusivity; firmware-exit UTRL/UTMRL state and DMA ownership;
coherence; PA/IOVA mapping; sda-to-LUN mapping; future native OS root UUID.
These require independently reviewed handoff/ownership and storage identity
evidence, not inferred defaults. Existing restore RAM-root UUID is unrelated.
No such device collection is authorized by this host-only task.
Next-stage evidence requires new read-only Android sysfs identity collection or
this board's firmware-exit contract evidence under appropriate authorization.
At that preparation checkpoint the last screen was23r, with no authorization to
return to Android; no transition or collection occurred then. The subsequent
limited authorization and stopped attempt are recorded below.

### First authorized return/identity attempt: historical false rejection

User subsequently authorized one return to Android plus read-only sysfs identity
collection only, not a new candidate boot, flash or UFS takeover. Initial
`adb devices -l` returned0/no transports; `fastboot devices -l` returned0/one
transport and targeted `getvar product` returned0/enuma. Before any reboot, the
single-use collection invocation rechecked discovery: **adb1 / fastboot1**, both
enumerations exit0. Its unique-transport precondition was not met, so entry
returned1 and **no reboot or sysfs command ran**. Current Android product and
boot_completed are unobserved; the last user screen observation remains23r, not
proof of the current boot mode. No repeated reboot/discovery attempt follows.

Ignored evidence: `.cache/device-evidence/20261110T1641451645541Z-ufs-identity/`
contains `collection.json` and `attempt-notes.json`; the directory uses the actual
host UTC clock rather than the conversation date. Serial/listings stayed in
memory; saved commands are redacted. Entry is ignored
`.cache/collect-ufs-identity-once.ps1`, parser self-check0 errors, invoked once.
The host-only checker report remains the prior historical-input result, **not**
a successful new sysfs capture. All LUN/context/ownership UNKNOWNs stay unchanged.
Blocker: parent must ask the user to return to Android manually and confirm
connection state before arranging another bounded discovery/collection. Next
host action is inspection of these saved stop records, not replaying the entry.

### Final authorized restore: Android ready, sysfs chain permission gap

The previous blocker was a **host gate error**, not evidence of conflicting
enuma identities: `.cache/collect-ufs-identity-once.ps1:65–84` used global
transport counts instead of target identity. The original failed evidence is
unchanged. Per the still-valid user authorization and updated Device access
rules, the ignored collector now queries each enumerated target using explicit
`-s` and permits one confirmed enuma plus the confirmed expected project
companion. Unknown/unexpected identities, multiple enuma, over-two devices or
duplicate serial across transports reject without state changes. The companion
receives identity queries only; no companion assets are accessed.

Offline stub checks (no device calls): before edit, the old false rejection was
reproduced; after edit seven cases passed, including the allowed mixed-device
case, multiple enuma, unknown/unexpected device, no enuma, already-Android and
cross-transport ambiguity. Allowed mock reboot calls were explicitly targeted
only to confirmed enuma; parser had0 errors. These are **self-checked**, not
independent mechanical verification.

Actual outcome, ignored
`.cache/device-evidence/20261110T1654315791913Z-ufs-identity/`:

- `collection.json`: enuma uniquely identified in fastboot with known companion
  on adb; selected serial/product reconfirmed immediately before the **sole**
  `fastboot -s <REDACTED> reboot`, exit0. Targeted adb wait/product query0/enuma;
  first boot_completed was empty immediately after adb appeared, entry1. This
  was an early readiness result, **not** a second reboot or Android failure.
- `collection-followup.json`: one bounded read-only pass, entry0. Identity again
  enuma, **sys.boot_completed=1**. No reboot in this followup. User informed that
  Android was ready and device actions stopped immediately after collection.
- `readlink -f /dev/block/by-name/userdata` exit0 → `/dev/block/sda34`.
  `/sys/class/block/{sda/device,sda,sda34}` realpath queries each exit1 without
  diagnostic. Geometry and vendor/model `cat` queries exit1 **Permission denied**;
  parent/driver traversal stops at failed initial realpath. Thus H:C:T:L,
  host/controller-driver association and current geometry were **not obtained**.
  No escalation/security-state change or additional device probe was attempted.
- `summary.json` links the command/exit records and offline gate checks. Serials
  and raw device listings remain memory-only. Linux size/start use512-byte
  sectors; logical block size is in bytes; unread values remain unknown, not
  backfilled from the older GPT snapshot.

The old request for manual return above is superseded by the successful restore.
The host-only `.cache/ufs-evidence/report.json` remains historical DT/GPT input
validation, not this new collection. **LUN/context/ownership remain UNKNOWN**;
even a future Android H:C:T:L L value would describe Android enumeration only,
not UEFI DMA/context handoff. Next host-only task: review existing enuma firmware
exit/ownership interfaces and define a separately reviewed, non-escalating plan
for the missing identity chain. No driver/config/root-window/UUID change, no
new candidate build or device test is authorized here. Android is left usable.

ShengUfs reference remains fixed at
`e2b32cc429e8cf1501161c1d8c517f8994ceb9b2`, **not integrated**. Its SM8550 probe,
GCC and SID0x60 assumptions cannot be transplanted. No storage/stage promotion.
23r PMGR conclusion remains publisher completion/return by control-flow inference;
stage23 text not directly observed, not full runtime/AMFI/liveness acceptance.

## UFSDxe bounded exit/config audit (self-checked, not queue-stop proof)

New `scripts/audit-enuma-ufsdxe-exit.py` audits only existing
`../uefi-enuma/Binaries/enuma/UFSDxe/UFSDxe.efi`,118784 B SHA256
`ffeaed467f8251b7e30a45075da84a1c563e2bac7dc4be0f79f0ed49a88b8dc9`.
PE AArch64/PE32+, entry RVA0x1000, image base0, Subsystem12. Section
RVA/raw-offset/length: text0x1000/0x1000/0x18000,
data0x19000/0x19000/0x3000, reloc0x1c000/0x1c000/0x1000. Mappings are parsed,
not assumed identity; runtime-driver attribute alone is not queue/runtime-I/O proof.

Existing Mu_Basecore `/home/wh1stl3/enuma-fw/mu_basecore` pin
`cfb93724a06ff86ff5ba971413368a7809ee42a5` supplies exact clean UEFI headers.
A compiler-only AArch64 layout/ABI probe (no firmware build/link/execution)
derives ST.BootServices offset0x60, BS.CreateEvent0x50/CreateEventEx0x170,
EVT_SIGNAL_EXIT_BOOT_SERVICES0x201 and GUID field byte order. The ignored
`header-abi.s` demonstrates Type/TPL/NotifyFunction/Context/Group/Event in
w0/x1/x2/x3/x4/x5. Constructor RVAs5d38/5d3c/5d40 bind the BS global at1a8e0;
entry argument forwarding instructions are listed separately for review.

| Registration RVA | Event/group | Callback RVA | Direct callback target |
|---|---|---|---|
| 0x5eec | CreateEventEx, Type0x200/TPL8, EBS GUID at0x190a8 | 0x5de8 | none in bounded body; global-byte store, not a proven queue stop |
| 0x6184 | CreateEventEx, Type0x200/TPL16, same EBS GUID | 0x60c0 | BL0x60c8→0x603c; BLR0x6088=BS.LocateProtocol(StatusCode), then exit flag |

Both NotifyContext arguments are NULL. EBS group GUID is
`27abf055-b1b8-4c26-8048-748f37baa2df`; **group match is not Type0x201**.
Three other bounded event sites5e88/6120/e6b0 are separately listed, not called
EBS. Entry paths are **syntactic direct CFG paths only** (conditions and call
return/termination unproven); all event success/callback invocation remain
UNKNOWN. Finite windows do not prove no other registrations exist.

Config/error strings at file offsets/RVAs14912/1492f (error string has newline)
resolve through instructions278c/27e4. Lookup2794→4cac→BR4cf4/x2 is now bound to
the Shim library interface below, **not a UEFI protocol method**. Actual enumaPkg
ConfigurationMapLib:34–35 remains EnableUfsIOC0/UfsSmmuConfigForOtherBootDev1.
No numeric store or match is promoted to MMIO/queue semantics or quiescence.

Reviewer-supplied generic exit baseline is separate: DarwinBoot.c779–783 closes
Root,812–825 calls EBS then directly DarwinEnter; MuCoreExitBootServices789–816
notifies events and836–865 clears BootServices/sets runtime state, without a
global BlockIo stop. DarwinEnter cache operations are not DMA shutdown.
FlushBlocks may write media and was **not invoked**. This tool does not establish
UTRL/UTMRL, SID/context, DMA ownership, PA/IOVA, cache coherence, timeout buffer
lifetime or LUN, nor BlockIo usability after EBS.

From device cwd, WSL Ubuntu-22.04 with `/home/wh1stl3/.local/bin/python3.11`:
`scripts/audit-enuma-ufsdxe-exit.py` exit0;
`-m unittest discover -s scripts/tests -p test_enuma_ufsdxe_exit.py -v`12 tests0.
Prior-revision actual CLI `--objdump /usr/bin/false`1/REJECTED is retained, not
repeated; current tests include failed/empty tools. Current real audit0.
Tests use real local bytes/tool plus invalid PE/RVA, nonidentity mapping, empty
or failed tool and altered real-xref negatives. No vendor binary/disassembly in
Git. Ignored `.cache/ufs-exit-audit/{report.json,disassembly.txt,header-layout.ll,header-abi.s,selfcheck.json}`
provides minimal reviewer evidence. Independent mechanical verification pending;
no device/build/firmware/base/driver/board/activation changes or storage promotion.

### Incremental interface closure and next bounded SMMU boundary

Header pin and UFSDxe SHA256 above unchanged. The compiler-only layout probe now
also uses the actual local Shim structs (an opaque, unused memory-descriptor
pointee only) to derive LoadLib+0x10/GetCfgInfoVal+0x18, and derives
BS.LocateProtocol+0x140 from the pinned UEFI header. The linear `trace` remains
**local fallthrough evidence, not a branch-merge proof**; these fixed parameter
windows were manually reviewed. New negatives corrupt the two real GUIDs and
BS-source/member/Shim-member instructions and require semantic rejection.

- **StatusCode closure:** callback60c0→603c, call6088 loads member+0x140 from
  BS global1a8e0. GUID192a8 is
  `d2b2b828-0826-48a7-b3df-983c006024f0`, checked against pinned
  `MdePkg/Include/Protocol/StatusCode.h:11–12`; output goes to global1a910.
  Callback then sets exit flag1a918; callback5de8 only sets byte1a8f1.
  These callback bodies do **not** invoke a StatusCode protocol method. This
  does not prove absence of other module exit paths, registration execution or
  queue shutdown.
- **Shim closure:** empty library global1a8c8 triggers4bfc→104a0, whose HOB GUID
  19098 matches `bedaeabc-5e70-4d66-9733-213d072b9d04` in QcomPkg.dec:13.
  Loader+0x10 loads `UEFI Config Lib` (string14f31), version argument0, into
  global1a8c8; library+0x18 is GetCfgInfoVal, output **UINT32***.
  Static binding sources: QcomPkg PlatformPeiLib/PlatformPei.c:25–30,80–97;
  ShimLoader.c:15–23,49–53,57–77; ShimLibraries/EFIShim.h:32–47 and
  EFIUefiConfig.h:33–38,94–101; ConfigurationMapHelperLib.c:7–35;
  enuma.dsc:95 and board ConfigurationMapLib.c:34–35. Source hashes/line
  references are in report `interfaces.source_inputs`; HOB creation, actual
  loading and successful runtime configuration remain UNKNOWN.
- **True next branch:** on the lookup path,2798 requires status x0=0,27c4
  requires UINT32[sp+0x64]!=0 before27c8→9548→14088. Alternate27d8 calls9548
  without that lookup gate; do not infer config0 globally prevents execution.
  Wrapper9550 forwards to14088 without explicit new arguments and maps nonzero
  result to-100. At14088, bit0 of global1b958 may return0 early; cached interface
  table global1b960 is tested (not the client context). If config slot19fa8==2, the code reads EnableUfsIOC
  via4cac (string18644); lookup failure resets that slot0. This is no ownership
  proof.
- **Provider boundary (now statically bound below):** when cached table is absent,14138 calls
  BS.LocateProtocol for GUID19248=
  `54b6d3b4-5d33-4f91-8600-6c41d5deb19a`;141ac invokes returned factory+0x8
  with x0=&global1b960 (shared interface-table output). First operation140fc
  invokes table+0x0, x0=&stack[sp+0x18] (separate software client-context output).
  The fixed HALIOMMU installation/table bytes below close this static binding,
  not module names alone. Runtime installation/configuration remain UNKNOWN.

The prior provider question is superseded by the focused increment below.
Tool report `interfaces` contains
exact anchor RVAs and bounded ranges; runtime interfaces/UTRL/UTMRL/SID/context/
PA-IOVA/coherence/timeout buffer lifetime/LUN all remain unproved. No device
commands or changes to Android user availability occurred in this increment.

### Final focused provider/resource increment (self-checked, no hardware access)

Only existing enuma HALIOMMU.efi SHA256
`36a5adbe91a796940f4c09eb53ae4ffb1632ef20d8c3085f7cceb2a706c1e306`
was added; AArch64 entry1000/image-base0/Subsystem11. Board binding is checked
against enuma EnumaInputs Vendor.dsc.inc:17/fdf.inc:16/apriori.inc:7.
Finite HAL decode windows are enumerated in `provider.disassembly_bounds`;
raw instructions stay in ignored `haliommu-bounded.txt`, not Git.

- Install chain1210→1488→1504; ST+0x60 at42f4–42fc sets BS global9168.
  InstallMultipleProtocolInterfaces+0x148 is derived from the pinned UEFI header;
  call1558 passes GUID9048/interface9098/NULL. GUID bytes match UFSDxe19248.
  Factory9098+8→14cc returns shared function table90b0 without allocation.
  Table+0/+0x10/+0x40 targets16b4/1920/2f10 respectively.
- UFSDxe140fc→HAL16b4 allocates/zeros **0x38 software bytes**, first word1.
  This is a software marker, not a hardware context bank. Mode method2f10
  clears that marker and sets ctx+0x20 to0xe0 (mode0) or0x009f00e0 (mode1),
  then calls2d98. UFSDxe14170/14214 supply the mode read via EnableUfsIOC;
  source value0 is not proof of the runtime read. Attach calls141d0/14244
  pass ctx/name`\_SB_.UFS0`/w2=0 or0x10/w3=0. Both groups must return success
  before completion-store1425c, but execution/completion is UNKNOWN. The27d8
  alternate path remains; not the entire chain is under the first config lookup.
- **New bounded selection:**1920→48a8→4934 searches external table type-byte1
  nodes, name at node+0x1d compared with the supplied UFS name via50dc.
  49a8 decodes wire records of0x14 bytes into0x20-byte software records;
  1af4–1afc compares each first UINT32 against caller w2 (0/0x10), and
  selected record+0x10 is used next. These are **observed selection values**,
  not proven SID, context-bank number or positional index. Actual UFS records
  are UNKNOWN: no runtime IORT property bytes were supplied.
- **Field limit:**2d98 walks ctx+0x28 list; when ctx first word0, ctx+0x20 is
  passed as32-bit w2 to34a4 at2e30 alongside resource-record fields. Its hardware
  bit meaning, destination register identity, completion and ownership are not
  closed. This task does not expand the register-write helpers to guess them.
- **Stop:**4e14 obtains `SMMU`/`IORT` properties via external function-table
  +0xc0/+0xf8 (6ac4/6ae4). That table is returned via protocol+8 following
  LocateProtocol6a48 for GUID9078=
  `ae37b942-457f-4c91-a196-d9669fd347a3`; protocol global94e8, returned table
  global94f0. That increment stopped there; the subsequent fixed DALSys property
  closure below supersedes the unknown static binding/contents, not runtime
  selection or ownership. No safety-call/register-write expansion follows.

Actual command `scripts/audit-enuma-ufsdxe-exit.py` exit0; affected-only
`-m unittest discover -s scripts/tests -p test_enuma_haliommu_provider.py -v`
4 tests exit0, including provider GUID, factory member and two selector mutation
subcases. Prior tests are retained, not rerun wholesale. Command/exit evidence
is ignored `provider-selfcheck.json`; report `provider` gives exact anchors.

Further external-property xref work needs parent scope, not automatic expansion.
The **actual deep-review question**, before any takeover design/test, is which
cross-EBS queue/bus-master/context ownership and timeout-buffer observations are
necessary to establish a safe handoff and fail-stop contract. Software ctx
allocation/shared tables/config flags do not answer it. UTRL/UTMRL, SID/context
exclusivity, PA/IOVA/coherence/timeout-buffer lifetime/LUN remain unproved. No
device command, vendor execution, MMIO read, build, enable, write window or push;
Android remains available to the user, storage grade and23r conclusion unchanged.

## Host identity snapshot contract (synthetic only at this checkpoint)

`scripts/parse-enuma-ufs-identity.py` and
`scripts/data/enuma-ufs-identity.schema.json` define a small **data-only** input.
There is no collector, hook, protocol method invocation or device entry. The
parser directly checks necessary fields/semantics; the schema is a JSON Schema
2020-12 contract, not a new generic validation engine. Current fixtures are
self-generated synthetic bytes, and every output retains that label. No real
UEFI snapshot exists here and tests do not identify the tablet.

- Public pinned Mu header layouts: BlockIo.h:127–204, DevicePath.h:345–356,
  890–901,1013–1063, ScsiPassThruExt.h:63–74,195–198. UFS/SCSI/HD node sizes
  are6/8/42 bytes; node lengths and integer fields are little-endian. End/truncated
  nodes are checked; unknown node types remain opaque, no LUN0 default.
- BlockIo revisions0x10000/0x20001/0x2001f gate optional cached fields. IoAlign
  is buffer alignment, LastBlock inclusive; MediaPresent is cached, MediaId
  nonpersistent. PassThru Mode AdapterId/Attributes/IoAlign do not supply a LUN.
- Partition association requires a unique **complete byte-exact parent path**,
  GPT signature bytes and geometry/number. Duplicates/ambiguous parents yield
  UNKNOWN reasons, never first-match selection. Capacity is only a consistency
  check, not unique identity. GPT4096-byte LBAs and Linux512-byte sectors stay
  distinct. The historical GPT report can supply geometry/reference only; the
  helper never invents its absent UEFI parent path/signature.
- Legal GetNextTargetLun positions do not prove presence; selector0/0x10 and
  public IORT routing do not prove SID/context or exclusivity. Cached/synthetic
  matches never promote current identity, ownership or activation readiness.

Actual parser command `scripts/parse-enuma-ufs-identity.py --synthetic-demo`0;
`-m unittest discover -s scripts/tests -p test_enuma_ufs_identity.py -v`19 tests0
(truncation, lengths, revisions, ambiguity, units, signature and unsafe inference
negatives). Ignored `.cache/ufs-identity-snapshot/` contains synthetic input,
report and selfcheck; raw paths/signatures/identity outputs do not enter Git.
Future capture implementation requires **separate deep review and an explicit
output channel**. No ReadBlocks/PassThru/INQUIRY/CAPACITY/Reset/Flush/Write/
ConnectController/GetNextTargetLun/BuildDevicePath implementation is authorized.

## Fixed DALSys private property closure (final scoped resource increment)

New `scripts/check-enuma-ufs-property-closure.py` reuses the existing PE mapper,
rejects changed input hashes and only decodes fixed installation/factory/consumer
windows plus bounded private data. DALSys SHA256
`e6b151c5506f52196e6ea687d15ffa074b7e3d518e8c52621ef62413000a8204`;
HALIOMMU SHA256 above unchanged. enuma Vendor.dsc.inc:10/fdf.inc:9/apriori.inc:3
select DALSys. BS global4d138 derives from ST+0x60 at19c8–19d0; install14f8 uses
BS+0x148 with GUID1d058/interface1d0a8. Factory+8→141c writes function table
1d0c0 via **x2** (not HAL factory's x0); +0xc0/+0xf8 targets2ca4/2eb4.

Static descriptor count1d210=1, descriptor1d218/db pointer1d220→7bc8 binds
property base1c208, typed table1bd98,20 name entries at1c618. SMMU entry1c820
(name8e38, property offset0x22c, collision0) gives property1c434 `IORT`, raw
type0x12/index0xf.16-byte typed item1be88 has +8 pointer2bf80. Header and PE
boundaries are checked; the physical typed-table span is only a bounds check,
not an invented semantic array count.

Private table2bf80 length0x1174/count25/first offset0x30; unique UFS name node
2c6e0 length0x65 has2 records beginning2c71d. These are **raw fields**:

| Record RVA | raw UINT32[0..4] | Static association |
|---|---|---|
| 0x2c71d | `[0,1,0x4e0,0x30,0]` | caller selector0 equals raw0 |
| 0x2c731 | `[0x10,1,0xe0,0x30,0]` | caller selector0x10 equals raw0 |

Both raw3 references resolve to table+0x30=2bfb0; referenced node's **raw UINT64
at+0x10** is0x15000000. No SID/context/bank, exclusivity or PA=IOVA names are
assigned. This is this board's **private property data**, not proof of installed
standard system ACPI IORT or that runtime selected this database.

Actual tool exit0 and affected-only
`-m unittest discover -s scripts/tests -p test_enuma_ufs_property_closure.py -v`
6 tests0: real-helper wrong names, typed-index/node/record bounds and changed-hash
negatives. Raw data/window output stays ignored `.cache/ufs-property-closure/`.
Existing blob/register/provider suites are not replayed. Git contains only
self-authored code/schema/tests and sanitized semantic summaries.

**Offline resources have reached the prescribed boundary.** Next is deep review
of a future capture/ownership-observation plan, with a defined output channel,
not direct device testing, candidate generation or a firmware hook. Runtime
SID/context exclusivity, UTRL/UTMRL quiescence, PA/IOVA/coherence and timeout
buffer lifetime remain UNKNOWN. No storage-grade or23r runtime promotion; no
device/vendor execution/MMIO/build/enable/push, and Android user use is untouched.

## Optional identity host core saved and paused; UFS component is the main line

Per the subsequent narrowed direction, no further menu/QR expansion is planned.
Existing code under firmware `enumaPkg/Drivers/EnumaUfsIdentityDxe/` is **unwired**:
IdentityCore.h/.c, HostTest.c and QrHost.c only; no entry/INF/DSC/FDF change.
Core allocation precedes an ordinary map (not final EBS MapKey); individual
Revision-gated fields are copied without provider padding. Complete ranges must
be known firmware RAM, not MMIO/unknown;64 handles/16KiB/128 nodes are bounded,
critical descriptions/pointers/fields/path bytes are checked before/after.
Map inclusion is not object size/lifetime proof; normal installed provider with
no concurrent unload remains an assumption. No sandbox/TPL/IRQ claim.

Snapshot v2 now requires candidate ID, completeness, reported handle count/64
limit, truncation/reason and per-item status. Any unread/failed/changed item,
count mismatch or>64 prevents global uniqueness. Mode was omitted. Independent
historical GPT extraction reads the old original snapshot only and saves raw
unique partition GUID/number/name/geometry/input hash to ignored
`.cache/ufs-identity-snapshot/historical-gpt-reference.json`. No UEFI parent path
is inserted into that independent reference; same-capture full-parent matching
comes afterwards. SCSI-only can give SCSI LUN but never UFS LUN; MediaId remains
nonpersistent. All UEFI test instances are synthetic, current identity UNKNOWN.

Necessary checks actually completed (self-checked): host clang core build0,
ASan/UBSan halt-on-error13 mock scenarios0 (alloc/count/missing/MMIO/overflow/
cross-page/short-object/pointer-change/path/revision and one-shot); parser23
tests0, page model5 tests0, old-GPT extraction0, C synthetic fixture parse0.
The initial mock pointer-arithmetic UBSan error was fixed and the final strict
run is clean. Public QrEncoderLib host shim build/guard test0 covers region/
initial alloc/mocked Blt error and cleanup. **No pixel QR decoding, actual font/
GOP rendering or menu adapter was tested**; no further display framework is added.
Page framing has snapshot ID/index/count/length/checksum and rejects missing,
duplicate or mixed pages. Host events UP/DOWN/SCAN_SUSPEND/Enter/Esc are explicit,
manual only. Raw outputs/executables/commands are ignored `.cache/ufs-identity-core/`.

Historical input/Tools/Advanced Logger QR was device-verified: README43/45,
porting35/108, firmware-log-capture.md69–70, source1070b371e95bf59cfc6f955a37fec3c26ad2e804.
The old logger's failure to exit with power is its CR/LF/ESC versus SCAN_SUSPEND
software limitation, not evidence that input is broken. Reviewer candidate
comparison: stage12/stage3 FD A matches,23r FD B corresponds to existing testedB,
DTB42d36a…f698 matches; enuma DSC A→B adds DebugLevel4 without input/display
option changes, **not** a claim of identical module bytes. No new FV hash gate.
23r FAT config stays default xnu/timeout3; do not alter it here. Menu timeout<0
still falls back with no input; first ConnectAll runs before config and is not
disabled by connect_all=false. Passive plugin does not imply zero boot I/O.

Next is the separately briefed **ShengUfs component** resource/entry guard in an
authorized temporary component checkout. No active pin/submodule/feeds change,
kernel/firmware build, candidate, menu entry, device/claim access or push. The
optional identity tool is not a prerequisite milestone.23r limited control-flow
conclusion and all unproved UFS ownership/execution boundaries remain unchanged.
