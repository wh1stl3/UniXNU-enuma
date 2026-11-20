# Old reuse gate A: offline evidence boundary

2026-11-21, self-checked source and existing-record review; no device access.
Gate A is not released. This is not authority for UFS access or DMA ownership.

## Version

The locally retained Linux reference `830b3c68c1fb1e9176028d02ef86f3cf76aa2476`
is not proven to be the exact Android kernel running on enuma, nor is it the
UEFI UFSDxe binary. Paths below are under `.cache/ufs-hci30-compat-20261111/ref/`.
`drivers_ufs_host_ufs-qcom.h:20-25,43,133-141` reads the controller's vendor
register at HC+0xe4 and extracts major bits 31:28, minor bits 27:16 and step
bits 15:0. Offset, masks and shifts are compiled constants; the register word
and extracted fields are runtime values. `drivers_ufs_host_ufs-qcom.c:1005-1006`
stores the extracted values; `:822-841` sets the broken-HCI-version quirk
exactly for major 2. Major 1 has separate quirks, with an extra interrupt
aggregation quirk at minor 1, step 1. The quirk selects a callback in
`drivers_ufs_core_ufshcd.c:705-723`: the callback returns the compiled
UFSHCI 1.1 encoding for major 1, otherwise 2.0 (`ufs-qcom.c:799-806`).
In this source the quirk is set for major 2, so its effective override is
HCI 2.0, not a claim that a raw register measured 2.0.

The recorded 24r read was HC+0x08 = 0x300, HCI version register, not HC+0xe4
hardware revision. It is parent-transcribed, not independently visually read:
`docs/ufs-24r-diagnostic.md:11-35`. It cannot determine the major-2 branch.
`docs/ufs-hci30-compat.md:47-73` reports no revision property in the existing
ADT, no revision in checked firmware configuration or Android dmesg excerpts,
and no direct `#0xe4` access in the existing UFSDxe disassembly. The latter
search is not a proof that indirect/derived addressing cannot read it.
The Qualcomm Linux rule is therefore established for that reference source,
not the actual enuma vendor binary or its runtime hw_ver.

## Six HC read-side-effect gaps

These six are the six additional HC reads specifically identified in
`docs/ufs-hci30-compat.md:85-118`, distinct from the later six-read SMMU
Observed result referenced in README. HC base is 0x1d84000 per the cited live
ADT; physical addresses below are base plus offset. Meaning is the Linux/EDK2
register-map name, not a hardware-side-effect guarantee.

| Offset | Address | Register / returned content |
|---|---|---|
| 0x50 | 0x1d84050 | UTRLBA, transfer request list base low |
| 0x54 | 0x1d84054 | UTRLBAU, transfer request list base high |
| 0x60 | 0x1d84060 | UTRLRSR, transfer list run/stop |
| 0x70 | 0x1d84070 | UTMRLBA, task request list base low |
| 0x74 | 0x1d84074 | UTMRLBAU, task request list base high |
| 0x80 | 0x1d84080 | UTMRLRSR, task list run/stop |

The checked Linux reference has writes but no read adoption at those six
offsets (`docs/ufs-hci30-compat.md:96-118`); the locally available EDK2
header names them but does not state read semantics. Thus no evidence here
establishes that reading them clears an interrupt, changes a state machine or
advances a queue, **or that it cannot do so**. The adjacent instructions for
six reads cannot be supplied from the 24r execution: it stopped on VER before
any of these six reads, and no matching six-read vendor execution has been
established. Other code's writes to these offsets do not prove a read effect.
In particular, IS at 0x20 has a separate write-one-to-clear write path; it is
not one of these six.

## Board conclusions and further offline work

Established at the stated evidence levels: reference-source branch and
register layout above; 24r parent transcription of raw VER=0x300 and
early refusal; the six register names and address arithmetic. The 24r result
did not sample HC+0xe4 or the six registers. The later SMMU ID/route/context
observations describe the SMMU, not the controller revision, and cannot infer
hw_ver or read semantics. The 2026-11-14 warm-route decision accepts a
specified DMA-retirement residual risk; it is not an old-gate-A release.

Offline next step: inventory existing timestamped vendor logs and snapshots
for an explicitly labeled HC+0xe4 raw word or a source-bound decoded
major/minor/step, recording provenance, controller identity and capture
context; decode the word with the masks above and verify whether the exact
running driver shares this implementation. A compiled `2.0` constant,
HC+0x08=0x300, SMMU IDs, and route contexts do not meet that criterion.
Separately, inspect existing vendor register access traces/disassembly with
dataflow tracking, not only immediate-offset string searches, for each of
the six reads and subsequent writes/branches. Such instruction evidence can
show software actions but alone cannot prove absence of hardware read side
effects. A controller-specific register specification or equivalent hardware
evidence remains necessary for that claim. No such new finding is asserted by
this review; whether further existing material resolves it is unknown.

## Follow-up: vendor Android image dataflow (partial, self-checked)

**Established in the static image:** the existing
`.cache/ufs-boot-offline-20261111/ufs-functions.txt:2984-3011,3177-3197`
identifies `ufs_qcom_init`: entry 0x820cf4 saves its argument in x19;
0x820fcc loads x8 from [x19], 0x820fd0 adds 0xe4, and 0x820fd4 loads
the word. 0x820fe0/0x820fe4 extract major/minor; 0x820ff4–0x820ffc
store major/minor/low 16 bits in the private object. At 0x820ff0–0x821018
major < 2 branches to 0x82103c, otherwise it sets a separate private field
and a base+0xdc pointer. These are static image offsets, not runtime PCs.
The host/controller-base interpretation is supported by the previously
recorded symbol/relocation analysis in
`.cache/ufs-boot-offline-20261111/checkpoint.md:3-9`.

At 0x8216d0–0x821744 (`ufs-functions.txt:3627-3656`) a separate comparison
branches on major == 2: 0x821720 `cmp w9,#2`, 0x821724 `b.ne 0x821748`,
0x821728–0x821730 OR 0x20 into hba+0x108; an additional conditional path
may OR 0x1a. The fixed reference names bit 0x20
`BROKEN_UFS_HCI_VERSION`, but exact source-revision identity and actual
device invocation are not established. The existing checkpoint traces the
conditional callback and 0x200 result, without observing either at runtime.
The input Image-current SHA-256 is
`2b6f267ab0c3e3b262871cb44d2b0a621c10efcddf4454e427b53cbc8292d07d`;
its boot/kernel binding is in `.cache/ufs-boot-analysis-20261111/current.json`.
This is Android kernel evidence, not a UFSDxe result.

**Strong inference:** the established reference naming and image dataflow
support identifying this word as the Qualcomm hardware revision in this
image; runtime controller identity and execution remain unobserved.

**UNKNOWN:** this follow-up did not finish an exhaustive search of `out/`
and `.cache/`, nor trace the six requested controller-offset reads in vendor
code. No board HC+0xe4 raw word was found in the subset checked; this is not
an exhaustive negative. The six reads' adjacent software writes/branches and
hardware read side effects remain unresolved. The old gate A is not released.

## Follow-up: six offset candidates (partial, self-checked)

The Android image disassembly `ufs-functions.txt:23106-23146` has stores,
not the requested reads: `0x834284`, `0x834298`, `0x8342ac`, `0x8342c0`,
`0x834304`, `0x834314` store respectively to `[x20->base]+0x50`, `+0x54`,
`+0x70`, `+0x74`, `+0x80`, `+0x60`. This does not establish that all vendor
reads were found or that reading any register has no hardware side effect.
The bounded candidate search was for add-immediates in the existing Android
disassembly followed by manual inspection; derived offsets and other binaries
remain unexamined. The exhaustive search and all six read-following instruction
sequences remain UNKNOWN.

Windows `rg` was unavailable (command not found); the requested full `out/`
and `.cache/` scan and Mach-O/EFI immediate inspection were not completed.
Consumed claim files must not be opened. No exhaustive negative is claimed.
