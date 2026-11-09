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

## RamBlock 探针 (host only)

Status: **self-checked**, no device run, push or merge. Branch
`feat/step10-ramblock-probe` starts at
`8ff7f821348637b97f5b7184c889ddb0dc33da11`. No kernel rebuild: source kernel
is the `c660a997...` candidate above. Packed restore disk, converted trust,
FD and DTB are the same pinned inputs above. No memory, UUID, ABI or
`-v serial=3 rd=md0-ramblock` argument changes were made.

`llvm-objdump --disassemble --disassemble-symbols=_bsd_init kernel.macho`
confirms `_bsd_init` at `fffffff0076f2854`, with direct calls:

```text
fffffff0076f2f34: 22 5c 0a 94  bl 0xfffffff007989fbc <_IOFindBSDRoot>  (+0x6e0)
fffffff0076f2f78: a8 c4 f6 97  bl 0xfffffff0074a4218 <_vfs_mountroot>  (+0x724)
```

Both builds set `[payload] entry_probe_reset_in = "_bsd_init"`,
`entry_probe_reset_before = true`, `entry_probe_reset_delay = 6` and
`entry_probe_reset_after` to the respective symbol (occurrence defaults to 1).
The delay is required to install the probe; **before=true resets immediately
at the call site without executing the call or waiting 6 seconds**. Panic screen
remains disabled. Temporary settings are confined to the ext4 build copy and
restored afterward; tracked `board.toml` remains the probe-free RamBlock candidate.

Build cwd `/root/enuma-step10/UniXNU`, Python 3.11 via
`PATH=/home/wh1stl3/.local/bin:/usr/local/bin:/usr/bin:/bin`:

```sh
python3.11 ./unixnu build payload -D ../UniXNU-enuma \
  --config ../UniXNU-enuma/.cache/stage3-build.toml \
  --data-ramdisk out/ipsw/21H461/044-75545-038.restore.dbr \
  --trust-cache out/ipsw/21H461/restore-trust.bundle
# Immediately preserve payload.img, payload.json and logs/payload-patch.log per tag.
python3.11 ./unixnu bootimg -D ../UniXNU-enuma \
  --uefi /mnt/d/Code/PortingiOS/enuma/uefi-enuma \
  --fd /mnt/d/Code/PortingiOS/enuma/uefi-enuma/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd \
  --dtb ../inputs/enuma.dtb -o out/enuma/stage6-ramblock-probe/<tag>/boot.img
```

### 判读表（待上机，不是当前观察结果）

Outputs are preserved in both
`/root/enuma-step10/UniXNU/out/enuma/stage6-ramblock-probe/` and
`D:/Code/PortingiOS/UniXNU/out/enuma/stage6-ramblock-probe/` (no overwrite).
Each tag contains boot.img, payload.img, payload.json, payload-patch.log,
boot.json, build logs and validation.json. Both payload and bootimg commands
exited 0. Each boot.img is **203505664 bytes**; each payload.img is 201326592 bytes.

| Tag / boot.img | boot.img SHA256 | payload.img SHA256 |
|---|---|---|
| `16r-before-vfs_mountroot/boot.img` | `b5d90f6f2649bc2f43335899fbccd4f7d7876ba83fc9f2f93f107c8ebe2ac4cd` | `401b72e1d16ec055a543eb5ca51fb698d1602338abe7e99f99b724bc285a8d3d` |
| `15r-before-IOFindBSDRoot/boot.img` | `d51917289c807dd9a9bea7253f4c0160917d5aed796d94a4e71c5daa9530393c` | `f30d061a956184a89923cd4bcc2ac547848f295e6424c068bcaadd67135e6a30` |

Probe logs (one line per image):

```text
patched kernel.macho: stage 1 blue bar, stage 2 magenta bar, stage 4 reset before call #1 to _vfs_mountroot in _bsd_init (at 0xfffffff0076f2f78)
patched kernel.macho: stage 1 blue bar, stage 2 magenta bar, stage 4 reset before call #1 to _IOFindBSDRoot in _bsd_init (at 0xfffffff0076f2f34)
```

Read-back checks: header v1, ramdisk byte-identical to the respective payload,
decompressed kernel after 192-byte BootShim equals the FD, appended DTB equals
the input; FD `e524988b8a05f15847ffc991170de8a5e0ead607400421e0835084497a71bf1e`,
DTB `42d36a005024e1a7c55cb5da077a13bb17e9fb9a79dc9dfac8a61cf1e182f698`.
All five FAT files were read back; content remains **188576511 bytes,
93.666966% of size_mib=192**, below 95%. Contained patched kernel hashes are
`dcdac86314cad793af81af0dafe90b453a58d8a67ea6d8676c66990d3c031769` (16r) and
`54a8e16d0394d9f37493d438ac000b53286b57dafdbdd68cf9935e78c56b0efa` (15r), both
different from the unchanged `c660a997...` source. Copied files were hash-compared.

Final record self-check: `python3.11 scripts/porting-record.py check --device
/mnt/d/Code/PortingiOS/enuma/UniXNU-enuma`, cwd
`/mnt/d/Code/PortingiOS/UniXNU`, PATH includes `/root/.local/bin` and
`/home/wh1stl3/.local/bin`, exit 0: `enuma: 14 structured areas checked`.
`git diff --check` in the host device repository exited 0. Parsed TOML comparison
confirms only one packaging host evidence entry was added; historical evidence
and all other areas are unchanged. Source kernel hash and restored board match
their original inputs. No host build blocker remains; the runtime result is pending.

先 16r；不复位再测 15r。复位只证明到达调用点，不证明挂载成功。

| Observation | Interpretation / next action |
|---|---|
| 16r resets | IOFindBSDRoot returned and reached mountroot call site; RamBlock published a root or root selection completed → investigate mounting. This alone does not identify which service supplied the root. |
| 16r does not reset, 15r resets | Consistent with stopping inside IOFindBSDRoot / root matching not finding the volume → inspect RamBlock start, UUID and ABI. Other intervening calls are not individually tested, so this is an inference. |
| Neither resets | RamBlock changed earlier progress → inspect NativeRamBlock registration/matching; absence of reset alone does not establish the exact failure site. |

No independent verifier was run in this task. Parent verifier should rerun the
two final payload/bootimg commands only if needed, in fresh tag directories with
the recorded temporary settings (no kernel rebuild), header/FAT/hash checks,
`python3.11 scripts/porting-record.py check --device <host device repo>` from
the base with the PATH above, and `git diff --check`. Integration and runtime
acceptance remain with the parent and a separately authorized device test.

## 2026-11-10: 16r observation and sole 17r after-call candidate

This section supersedes the pending 16r/15r decision table above. User reports
16r (`b5d90f6f2649bc2f43335899fbccd4f7d7876ba83fc9f2f93f107c8ebe2ac4cd`)
showed green/blue/magenta bars then immediately auto-returned to fastboot.
After continue, Android was normal and pstore empty. Media reference:
`.cache/media/stage6-ramblock-cp16r-20261110T000622406`. This is **user observation**;
whether the recording covers reset is unknown; no video verification is claimed.
It proves reaching `_bsd_init`'s `_vfs_mountroot` call site, **before executing
that call**, not a successful mount or launchd. 15r was not tested and need not be.

### Original kernel return-value paths (read-only source/disassembly)

Source kernel remains `c660a997e8d1af4093c21f405ef9aa2382f0a371556d3a2ecf0d9645f7fe7a05`.
Using `/usr/bin/llvm-objdump --disassemble --disassemble-symbols=_bsd_init`
against `out/enuma/ipados-17.7.11-21H461/enuma/kernel/kernel.macho` in the ext4
base shows these paths (full disassembly saved with the candidate):

```text
fffffff0076f2f78: bl   0xfffffff0074a4218 <_vfs_mountroot>
fffffff0076f2f7c: cbz  w0, 0xfffffff0076f2f9c <_bsd_init+0x748>
fffffff0076f2f80: strb wzr, [x24, #528]       ; rootdevice[0] = 0
fffffff0076f2f84: cmp  x27, x25
fffffff0076f2f88: b.eq 0xfffffff0076f3018     ; netboot failure path
fffffff0076f2f8c: str  x0, [sp]              ; errno printf argument
fffffff0076f2f90: mov  x0, x21
fffffff0076f2f94: bl   0xfffffff0072ac834 <_printf>
fffffff0076f2f98: b    0xfffffff0076f2f20     ; retry setconf/root selection
fffffff0076f2f9c: adrp x0, 0xfffffff007ab5000 ; success branch
fffffff0076f2fa0: add  x0, x0, #528
fffffff0076f2fa4: bl   0xfffffff00798adb4 <_IOSecureBSDRoot>
fffffff0076f2fa8: adrp x8, 0xfffffff007aa1000
fffffff0076f2fac: nop
fffffff0076f2fb0: ldr  x20, [x8, #1672]
fffffff0076f2fb4: ldr  w8, [x20, #112]
fffffff0076f2fb8: orr  w8, w8, #0x4000        ; MNT_ROOTFS
fffffff0076f2fbc: str  w8, [x20, #112]
fffffff0076f2fc0: bl   0xfffffff0074cc79c <_vfs_context_kernel>
fffffff0076f2fc4: mov  x19, x0
fffffff0076f2fc8: sub  x1, x29, #104
```

Corresponding applied source:
`out/enuma/ipados-17.7.11-21H461/enuma/tree/.cache/xnu-work/bsd/kern/bsd_init.c`
lines 998–1028 implement `while (TRUE)`, `setconf()`,
`if (0 == (err = vfs_mountroot())) break;`, clear rootdevice on error, hang with
increasing `IOSleep` on netboot failure, otherwise print errno and retry.
Lines 1030–1038 call `IOSecureBSDRoot`, set MNT_ROOTFS and call VFS_ROOT.
Thus **returning** from mountroot is distinct from **returning zero**. The old
stage-5 assertion that vfs_mountroot never returns is not a source-level contract.

The unmodified `scripts/patch-xnu-entry-probe.py:97–118,389–406` redirects the
call to the existing stage-4 cave: `bl callee`, wait 6 s, overwrite w0 for PSCI,
then reset. It neither records the result nor executes the original cbz.
17r reset would prove only that `_vfs_mountroot` returned (possibly an error),
not that the success branch, IOSecureBSDRoot, VFS_ROOT or launchd ran. No reset
alone would not distinguish a hang, panic, or other failure inside the call/reset path.
No script/cave changes were made.

### 17r build and necessary self-check

Starting host device HEAD `43115d7e77bd358f796acd748edaaf9d127467b2`, clean worktree.
One candidate, no kernel rebuild. Same ext4 cwd and payload/bootimg commands as
above, tag `17r-after-vfs_mountroot`. Temporary ext4 `[payload]` settings:
`entry_probe_reset_in="_bsd_init"`, `entry_probe_reset_after="_vfs_mountroot"`,
`entry_probe_reset_occurrence=1`, `entry_probe_reset_delay=6`,
`entry_probe_reset_before=false`, `panic_screen=false`. Board restored byte-for-byte
to the host probe-free board after build. No UUID/ABI/memory/boot-argument changes.
An initial bare python3.11 invocation failed before running the build (PATH);
using the previously documented `/home/wh1stl3/.local/bin/python3.11` resolved it.
Final payload exit **0**, then bootimg exit **0**; no device commands, push or merge.

Full output directory:
`D:/Code/PortingiOS/UniXNU/out/enuma/stage6-ramblock-probe/17r-after-vfs_mountroot/`
(also retained under `/root/enuma-step10/UniXNU/out/enuma/stage6-ramblock-probe/`).

| Output | Bytes | SHA256 |
|---|---:|---|
| boot.img | 203505664 | `c29ab3e713b31f450879c1b14796e049172b93dece1b40d35e93502d1220578c` |
| payload.img | 201326592 | `10aaebbe2763a9ee5569f088b0b6f289f7df15715e9aba59bc9bc556cb07ea1b` |
| contained patched kernel | 51109888 | `3cb2f73ec0a0d97301936ce7e711540c9ac8c0a4667c3db16f4f6192cacdb54d` |

`payload-patch.log`:
```text
patched kernel.macho: stage 1 blue bar, stage 2 magenta bar, stage 4 reset after call #1 to _vfs_mountroot in _bsd_init (at 0xfffffff0076f2f78)
```

One necessary read-back self-check exited **0**: header v1, embedded ramdisk
equals payload; gzip-decoded FD after 192-byte shim and appended DTB match the
full pins above; five FAT files total **188576511 bytes = 93.666966%**, below 95%.
Packed disk/trust hashes and kernel arguments match prior inputs; original kernel
hash unchanged. `payload.json`, `boot.json`, patch/build logs, `validation.json`
and `bsd_init.disasm.txt` accompany the images. Copies hash-match; destination
was new, so 16r, 15r and probe-free candidate were not overwritten.

No independent verifier or 17r device run occurred: **self-checked only**.
Final `porting-record.py check` with the command below exited **0**:
`enuma: 14 structured areas checked`; device-repo `git diff --check` exited **0**.
Parent verifier should rerun the final payload/bootimg commands above only in a
fresh tag directory with the stated temporary settings (no kernel rebuild),
then header/FAT/hash checks, `python3.11 scripts/porting-record.py check --device
/mnt/d/Code/PortingiOS/enuma/UniXNU-enuma` from the base with the documented PATH,
and `git diff --check` in the device repo. Final integration/acceptance belongs
to the parent. Next device test requires fresh user authorisation and recording.
