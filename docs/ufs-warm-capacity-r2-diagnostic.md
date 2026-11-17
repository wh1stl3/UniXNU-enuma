# Warm capacity r2 UFS observation — device result

## Latest: one warmcap-r2-NEW boot; every judged criterion hit (self-checked record)

2026-11-16. The user authorized one boot of the warm capacity r2 candidate. Exactly
one `fastboot boot` was issued and it returned 0. The facts in this document are
parent-relayed (execution, timeline, claim state) plus an independent `vision`
read of a cropped photo, as described under "Evidence sources". They are **not**
an independent device re-run by this repository, and no host tooling here re-read
the image.

### Execution and timeline

Serial is deliberately withheld; the device was identified by model, not by
connection order.

1. `adb -s <enuma> reboot bootloader`.
2. `fastboot getvar product` → `enuma` (matched before booting).
3. Single boot of the already-built candidate, no flash, no `continue`:

```
pwsh -NoProfile -File out/ufs-native-warm-capacity-20261114-r2/run-once.template.ps1 `
  -AuthorizeDeviceThisRound -AuthorizeHcWritesAndDmaNopLu0Rc10ThisRound `
  -AuthorizationRound "warmcap-r2-NEW"
```

| Time | Event |
| --- | --- |
| 21:49:57 | run-once entry; authorization flags and round accepted |
| 21:49:58 | claim marker atomically created (len 0) |
| 21:50:03 | single `fastboot boot` returned, script exit 0 |

No `STOP:` line, no client timeout, no retry, no second boot, no partition
write, no `fastboot continue`.

### Candidate identity

| Item | Value |
| --- | --- |
| boot image | `out/ufs-native-warm-capacity-20261114-r2/package-lu0-r1/boot.img`, 203505664 B, SHA-256 `3b094db25cf727fda0ab34372fe5eaf28f85f4ff3fc24b29efadadfa6a9b6c80` |
| candidate manifest | `out/ufs-native-warm-capacity-20261114-r2/final-audit-r2/candidate-manifest.json`, 75636 B, SHA-256 `735e8588d47d1cacd9c010470083f4c7ffd6265ad87888c34e09174418fd65c1` |
| vendor FD | `e524988b8a05f15847ffc991170de8a5e0ead607400421e0835084497a71bf1e` |
| session | `0x454e554d41435032` |
| candidate | `0x5741524d43415032` |
| policy | `0x261114c2` |
| scope | `enuma-warm-capacity-r2-HC-write-DMA-NOP-LU0-RC10-terminal` |

The two hashes above were re-read on this host (size and SHA-256 match); the
remaining identifiers are parent-relayed from the frozen candidate.

### Claim state

`.cache/ufs-warm-capacity-r2-enumacp2-device-attempt.claimed` was atomically
created at 21:49:58 with length 0 and is **consumed**. It is retained and must
not be opened, deleted or replayed. Any further device observation needs a new
round name and a new per-round authorization.

### Final screen (ten lines, verbatim)

```
WARM-CAP2 COMPLETE
WHY NOP/capacity complete; no block read or hardware admission
CMD n=2 op=25 LU=0 OCS=00 SCSI=0000
PROTO=0 res=0 sense=000000 err=00000000
POLL=2 IS=00000400 DB=00000001
PREIS=00000400 published=1 poison=0
RC10 observed=1 last=03b037ff bytes=4096
GEO MATCH expected=4096x61880320
TERMINAL no retry; retained
NO ROOT / NO BLOCK READ / NO STORE
```

### Field interpretation

Decoded against the reviewed candidate source and the reviewer's reading of the
recorded lines:

- `WARM-CAP2 COMPLETE` / `WHY NOP/capacity complete; no block read or hardware
  admission`: the terminal summary path was reached on the success branch; the
  candidate performed no block read and no admission step.
- `CMD n=2 op=25 LU=0 OCS=00 SCSI=0000`: two commands were issued — the NOP and
  the READ(10) capacity query — both to LUN 0. `op=25` is READ(10), `OCS=00`
  means no controller error, `SCSI=0000` means GOOD status.
- `PROTO=0 res=0 sense=000000 err=00000000`: no protocol-level failure, zero
  residual length, empty sense data, no driver error latch.
- `POLL=2 IS=00000400 DB=00000001`: two polling rounds, one doorbell write.
  `IS` bit 10 is the UFS HC `UCCS` (primary command completion) bit, left set by
  the predecessor; it is a normal completion bit and is not inside the
  candidate's `0x71880` fatal mask.
- `PREIS=00000400 published=1 poison=0`: the pre-submit snapshot of `IS` equals
  the post-submit value, so the bit was already set before this candidate ran;
  the snapshot was published in the record; the poison latch never tripped.
- `RC10 observed=1 last=03b037ff bytes=4096`: the READ(10) response was observed
  once, and the last returned LBA is `0x03b037ff` = 61880319. `bytes=4096` is
  the **logical block size the device reported** (RC10 response bytes 4–7), not
  a transfer length: this RC10 carried only an **8-byte** data segment
  (`hostScsi (..., true, 8, ...)` at `RootWarmAdopt.h:143`, whose
  `gWarmCapacity.blockBytes` comes from
  `loadBe32 (gHost.virt + kDataOffset + 4)` at `RootWarmAdopt.h:147`). No
  4096-byte transfer happened.
- `GEO MATCH expected=4096x61880320`: the reported block size and block count
  match the expected geometry; 61880319 is the 0-based maximum LBA of 61880320
  blocks, so the one-count difference is the standard max-LBA/count relation,
  not a mismatch.
- `TERMINAL no retry; retained`: the terminal path holds state and issues no
  retry.
- `NO ROOT / NO BLOCK READ / NO STORE`: no root mount, no block read, no store.

The later stop at `Waiting on <dict … IOMedia>` is the expected rootwait after
the candidate's `return false` when no RAM root is present; it is not a panic.
`magazine write failed: 30`, `No _nvramController` and
`IOCPUInterruptController` appear on screen but are unrelated to the judged
criteria.

### Criteria (DELIVERY.md:135-137) and verdict

| Criterion | Observed | Verdict |
| --- | --- | --- |
| terminal `WARM-CAP2 COMPLETE` | `WARM-CAP2 COMPLETE` | hit |
| geometry match | `GEO MATCH expected=4096x61880320` | hit |
| capacity read observed | `RC10 observed=1 last=03b037ff bytes=4096` | hit |
| commands: NOP + RC10, LUN 0 | `CMD n=2 op=25 LU=0 OCS=00 SCSI=0000` | hit |
| protocol / residual / sense / err zero | `PROTO=0 res=0 sense=000000 err=00000000` | hit |
| publication and no poison | `published=1 poison=0` | hit |
| no retry | `TERMINAL no retry; retained` | hit |
| no root / no block read / no store | `NO ROOT / NO BLOCK READ / NO STORE` | hit |

### Evidence sources

Three sources agree character for character on the ten lines: two separate
manual transcriptions by the parent session and one independent `vision`
sub-session read of the cropped screenshot. Agreement between a parent
transcription and its own re-transcription is weaker than a second independent
reading, so only the third source is independent; nothing in this repository
re-read the image itself.

- No video was recorded for this run.
- Photo original: 531611 B SHA-256
  `d2d0251b271b15636f5768995b526e3253d97d8ddc4b7be443931d3985c92566`,
  2000×1500.
- Crop sent to `vision`: 146320 B SHA-256
  `c7ee84a6cf3d0a0bf9acaacedaeed6dc58bedf1d53194c5c2220c1ed7a91692b`,
  2000×534, 1:1 crop, JPEG quality 85.
- Both images exist only in a host temporary directory; they are not in Git and
  are not uploaded anywhere. This document carries hashes and conclusions only.

### Not established

- Persistent root volume, Data volume or any persistent store.
- LU0 partition identity: only the whole-disk geometry matches; the partition's
  own identity was not read.
- SMMU ownership, vendor DMA retirement completion, or a DMA safety proof.
- Any formal bring-up stage promotion; the stage record is unchanged.
- Correct behaviour of any command other than NOP and the READ(10) capacity
  query, and any block-data read. This CAP2 run exercised only the
  prepare/NOP/8-byte RC10 path; it does **not** validate a 4 KiB (or any
  multi-block) data-block DMA transfer, and `bytes=4096` must not be read as one.
- That a repeat boot would behave the same; no retry was made.
- Default NoAccessPolicy / NoContract: unchanged.

### Reproduction conditions

- Host side: the frozen candidate directory can be rebuilt and re-audited with
  WSL root plus Python 3.11 (`check.py`, then `package.py --lun 0`, then
  `audit.py`, each into a new output directory) exactly as recorded in
  `out/ufs-native-warm-capacity-20261114-r2/DELIVERY.md`; the base pin stays
  `693f5d9cae8a408dd18b39f3f9fdc4228c934241`.
- Device side: one enuma, identified by `fastboot getvar product` before booting,
  a new per-round user authorization for the single `fastboot boot`, and a new
  authorization round name. The current claim is consumed, so the existing round
  cannot be replayed.
- Without a new authorization there is no reproduction path; this document does
  not grant one.
