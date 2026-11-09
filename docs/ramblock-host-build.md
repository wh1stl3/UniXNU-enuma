# Stage 6 RAM-root candidate (2026-11-09)

Status: **self-checked**, not independently verified or device-tested. No push,
merge, device command or partition write was performed. Apple-derived outputs
are local only, under `UniXNU/out/enuma/stage6-ramblock/` (also ext4 build out).

## Source and offline inputs

Device branch `feat/step10-ramblock`, based on main
`74dc21dd5c323a763a225f98a6eefc3815272046`; initial implementation
`e0ced004f2a29f9e40ddd7a3a200e7a3e3ad19c4`, with the follow-up source changes
in this commit. Base `693f5d9cae8a408dd18b39f3f9fdc4228c934241` copied to
`/root/enuma-step10/UniXNU`. No tracked base files were edited in either copy;
the two previously approved LF XnuPrelink patches were preserved.

`local.toml` in the ext4 device clone points each locked source to an offline
copy of the successful DrvFS feed cache (`offline-sources/`). All nine locked
HEADs and Git tree hashes matched the read-only originals. XNU:
`d8b80295118ef25ac3a784134bcf95cd8e88109f`, tree
`4a516c20160a996d0fc79a9d039c4c41450032b1`.
Cached omitted DriverKit/TrustCache headers and `.cache/linux` (LLVM/Libc)
were also reused. Interrupted preparation was completed after checking the
60 applied patch log entries, copying cached headers, running the unmodified
header preparation script, then writing its exact input signature. Initial
cache preparation missed those auxiliary caches and attempted network access;
those failed attempts are not successful build evidence.

Archives retain the full arch list (arrays replace, not append), then RamBlock,
the static audit installer, base bindings builder, and the device volatile-store
backend. The latter returns persistence mode 0 and performs no hardware I/O;
it resolves the optional store imports that the kernel linker does not tolerate
as unresolved weak imports. UFS remains disabled.

## Commands and elapsed times

Working directory `/root/enuma-step10/UniXNU`, PATH includes
`/home/wh1stl3/.local/bin`, Python 3.11, 16 jobs:

```sh
./unixnu defconfig enuma_defconfig -D ../UniXNU-enuma
./unixnu tree -D ../UniXNU-enuma
./unixnu build kernel -D ../UniXNU-enuma --out ./out -j 16
./unixnu build payload -D ../UniXNU-enuma --config ../UniXNU-enuma/.cache/stage3-build.toml \
  --data-ramdisk out/ipsw/21H461/044-75545-038.restore.dbr \
  --trust-cache out/ipsw/21H461/restore-trust.bundle
./unixnu bootimg -D ../UniXNU-enuma --uefi /mnt/d/Code/PortingiOS/enuma/uefi-enuma \
  --fd ../inputs/SILICIUM_UEFI.fd --dtb ../inputs/enuma.dtb \
  -o out/enuma/stage6-ramblock/boot.img
```

All final commands exit 0. Successful final **incremental** kernel/prelink:
23:03:40–23:04:10, 30 s; payload 1 s; bootimg 2 s. The offline-resumption
work interval 22:36:44–23:04:10 is 27 m 26 s, including interrupted bootstrap,
cache recovery, failed link and waits. It is **not** a clean ext4 build benchmark
and cannot establish a speedup versus the old approximately 3 h DrvFS build.

## Restore inputs and ABI limits

RestoreRamDisk and RestoreTrustCache were range-extracted from the same donor
IPSW. The DMG is IM4P-wrapped raw APFS (not a UDIF): unwrap, check `NXSB`,
then use DarwinBoot's `packed_ramdisk.pack`. The raw disk is 184549376 bytes;
the encoded disk is 137445888 bytes, SHA256
`fab7639b00c9683403c0e4a0a3641b04d04d4fcffadb38319d3e237c7d96c841`.
The reference UUID `9071148B-B025-402D-AD7A-48464D8B5FFF` is recorded by
the same-OS fuxi-oddlylabs port and its byte sequence occurs in the raw APFS
image; no independent APFS volume traversal was performed here.

Restore trust is version 1 (267 entries). DarwinBoot `ValidTrustCaches`
accepts only v2. `prepare-restore-trust.py` preserves all hashes/types/flags
and UUID, adds zero constraint-category/reserved bytes, and wraps one module.
Layouts follow public `TrustCache/RawTypes.h:58-99`. The zero-category semantic
is an **unqualified compatibility assumption**, not Apple personalization or
a hardware observation. Bundle: 6440 bytes, SHA256
`750b5d8ac5f5b52b8fd02d261caf96dd318db0904b3651ca05d9ae4939de488a`.

The 190-slot reference mapping was compiled from pinned public IOStorageFamily;
all 14 own-method target pointers were checked again against the final kernel.
Metaclass/constructor/D2 addresses match the old enuma measurement and same-OS
marble/fuxi records. Live class sizes 0x90/0x88 and native-4K metadata remain
borrowed, not measured on enuma. Static binding is not runtime ABI qualification.

## Image checks

| Output | Bytes | SHA256 |
|---|---:|---|
| kernel.macho | 51109888 | `c660a997e8d1af4093c21f405ef9aa2382f0a371556d3a2ecf0d9645f7fe7a05` |
| payload.img | 201326592 | `d5a98ce352bfdac616bb9e2e4bdab58b8d8029d1f611a3c58ae1a969f5b08f8e` |
| boot.img | 203505664 | `8f5835c02258cd3f14cbc477bb86622d53ef7fb6c797c23b9148429797bbccff` |

Header v1; ramdisk 201326592 bytes, byte-identical to payload. Decompressed
kernel region after the 192-byte BootShim equals FD SHA256
`e524988b8a05f15847ffc991170de8a5e0ead607400421e0835084497a71bf1e`;
appended DTB SHA256
`42d36a005024e1a7c55cb5da077a13bb17e9fb9a79dc9dfac8a61cf1e182f698`.
Payload source and contained kernel hashes match (no entry/panic probe).
`payload.json` data hash equals the encoded disk hash above.

FAT files under `EFI/UniXNU/`: `unixnu.toml` 455 bytes;
`Payloads/kernel.macho` 51109888; `kernel.macho.adt` 13840;
`kernel.macho.trustcache` 6440; `scratch-data.img` 137445888.
Total **188576511 bytes / 192 MiB = 93.666966%**, below 95%.
Arguments are exactly `-v serial=3 rd=md0-ramblock`.

Build logs show RamBlock `-Werror` success, bindings `PASS: 190 concrete slots`,
and volatile backend mode=0. Eighteen historical boot images (stage4-log,
stage5-probe, bisect 01–16) matched the original reports/tracked bisect hashes
before and after copying. All destination files were copied without overwrite
and hash-compared. Detailed validation and full historical hashes are in the
local `validation.json`, alongside `boot.json` and `payload.json`.

## Memory and acceptance boundary

The observed 512 MiB window has no overlap with fixed live-DT no-map ranges.
The ADT single span still includes the 69 MiB hole and low-address reservations;
dynamic reservations' ownership is unproven. Stage 3–5 success is not a safety
proof. All memory values are unchanged. Mounting APFS and starting launchd remain
**unverified on enuma**; no desktop or Android-preservation runtime claim is made.

Independent verifier should rerun the final kernel/payload/bootimg commands
(fresh output location; do not overwrite this candidate), `porting-record.py
check --device <device>`, `git diff --check`, and the header/FAT/hash checks above.
Runtime acceptance belongs to a separately authorized device test.
