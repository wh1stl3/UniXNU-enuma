# Data seed generated on a macOS 15 VM — 2026-11-19 (temporary, not a persistent Data volume)

## Latest: a 2,146,996,224 B APFS seed, `data.dbr` 1,142,976 B `c89592f8…0470`, built with the official tool at `--gib 3` and shrunk with `diskutil apfs resizeContainer … 2147m` (`self-checked`, host only)

2026-11-19. Host-only work in a macOS 15.x VM: no device, no flashing, no signing, no
deployment. The product is `out/data-seed-macos-20261119/data.dbr` (`/out/` is ignored;
the file is not in Git).

**This is a temporary seed.** It is attached from the payload's initrd as a RAM-backed
scratch volume and the ADT declares `/chosen:ephemeral-storage = 1`; nothing written into
it can survive a reboot. It is not the persistent Data volume the milestone requires.
Section "What this is not" lists the three mechanisms.

### Why the route looks like this

| Constraint | Source |
| --- | --- |
| The official generator only accepts whole GiB from **3 to 1024** and only grows | `UniXNU/scripts/make-data-seed.py:45-46`, `UniXNU/scripts/seed-data-grow.py:92-98` |
| The limit is in the scripts, not in `hdiutil` — `hdiutil` itself takes any size | observed this round: `hdiutil create`/`resizeContainer` accepted 2,147,000,000 B |
| A packed seed **> 2 GiB** (`0x80000000`) is `isBig` and its writes return `kIOReturnNotReady` unless a store backs it | `UniXNU/drivers/RamBlock/NativeRamBlock.cpp:219-293`; [`data-store-2gib-analysis.md`](data-store-2gib-analysis.md) |
| A seed **≤ 2 GiB** uses the sparse RAM path and is writable without a store (volatile) | `NativeRamBlock.cpp:227-231`; `SparseDisk.h:44-60` |
| Store mode 0 (no `sheng-data-persist`) means `direct == false`, so a `>2 GiB` seed would be read-only | `NativeRamBlock.cpp:88-90`, `:119` |

So: build the smallest seed the official tool allows (3 GiB), then shrink the APFS
container below 2 GiB. `2147m` is deliberately decimal — `2.147Gi` (≈2,305,323,696 B) and
`2147Mi` (2,251,292,672 B) both overshoot the 2 GiB limit.

### Procedure actually run

Scripts are the official ones from the pinned base `693f5d9cae8a408dd18b39f3f9fdc4228c934241`
(`scripts/make-data-seed.py`, `scripts/seed-data-grow.py`,
`drivers/DarwinBoot/Test/packed_ramdisk.py`), copied into the VM as
`~/unixnu/{scripts,drivers/DarwinBoot/Test}` with an existing empty `~/unixnu/build`
(`seed-data-grow.py:99` uses it as the temp parent and does not create it).
The source OS window is `044-76040-038.dmg` (5,157,406,069 B
`3f99b859c9728379110b66657c7b15285bcb1925ad8b5726542e2cdcf8b1028d`), converted to raw
6,077,580,800 B `e5634d04a8ac35f024845f583394e0a35deb26a04cb0c00286a8674e25a9a4f`
(both pinned in the 2026-11-12 `userdata-clean` round).

| Step | Action | Result this round |
| --- | --- | --- |
| 1 | `hdiutil convert <dmg> -format UDTO -o os-window` | raw `os-window.cdr` produced |
| 2 | attach the **whole** raw image read-only, `-owners off`, discover the mount point from the `/Volumes` difference | `ATTACH_MODE=whole`; `private/var` is a directory and `sbin/launchd` exists |
| 3 | `make-data-seed.py <OSX_MOUNT> ~/seed/data.dbr --gib 3 --build 21H461 --skip-setup` | 3 GiB seed, logical 3,221,225,472 B |
| 4 | restore the 3 GiB raw from `data.dbr` (`packed_ramdisk.regions`) | `data-3g.raw` = 3,221,225,472 B (the grow step's temp raw is deleted with its `TemporaryDirectory`) |
| 5 | read-only mount of the raw, `diskutil info -plist` | `UUID_BEFORE=62F1BC9E-4868-4CFF-BF7E-59AFCD474B4F`, `VolumeName=Data` |
| 6 | resolve the container from `diskutil apfs list -plist` by `PhysicalStores[].DeviceIdentifier`, then `resizeContainer <container> limits` | container resolved; the exact range printed by `limits` was not recorded |
| 7 | `diskutil apfs resizeContainer <container> 2147m` | `RESIZE_EXIT=0` |
| 8 | verify block 0 (`NXSB` magic, Fletcher64, block size 4096) and truncate the raw to `block_count × 4096` | `BLOCK_COUNT=524,169`, `CONTAINER_BYTES=2,146,996,224`, `CONTAINER_UUID=1BB8501A-9FA7-4616-B1B6-F64C245E8224` |
| 9 | archive the 3 GiB seed as `data-3g.dbr`, repack the shrunk raw with `packed_ramdisk.py` | `ENCODED_BYTES=1,142,976` |
| 10 | re-read the packed seed: header, `NXSB`, `APSB` pages | logical 2,146,996,224 B; volume UUID still `62F1BC9E-…4B4F` |
| 11 | copy back through the shared folder and hash on the Windows side | 1,142,976 B `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470` |

Repacking requires the output path not to exist (`packed_ramdisk.py:142` opens with
`'xb'`), hence the `mv` in step 9; the 3 GiB original is kept, not deleted.

### Identity of the result

| Field | Value |
| --- | --- |
| file | `out/data-seed-macos-20261119/data.dbr`, 1,142,976 B |
| SHA-256 | `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470` |
| packed format | `DBRDISK1`, version 1, page 4096, 10 extents |
| logical size | 2,146,996,224 B (524,169 × 4096), below the 2 GiB threshold |
| `NXSB` | block size 4096, block count 524,169, container UUID `1BB8501A-9FA7-4616-B1B6-F64C245E8224` |
| volume | UUID `62F1BC9E-4868-4CFF-BF7E-59AFCD474B4F` (three APSB pages agree), name `Data` |
| non-zero pages | 279 (build-round read-back) |
| volume UUID before shrink | identical to the final value — the shrink did not rebuild the volume |

The last row is the point of step 5: the volume UUID is unchanged across the shrink, so
the seed identity is a new seed (≤2 GiB means the identity is the whole-disk SHA-256, not
the `SHNGSEED2` index) but the same volume, and the kernel's
`XNU_OWNER_DATA_VOLUME_UUID` binding still points at `62F1BC9E-…`.

### Checks performed, and by whom

Host-side, this round (Windows, read-only on the artifact):

- file length and SHA-256 as tabulated;
- `DBRDISK1` magic/version/page/logical/extent count read from the file;
- block 0 `NXSB` block size and block count, container UUID;
- all three `APSB` pages present in the packed extents carry the same volume UUID.

From the r4 build round's read-back (`out/ufs-sm8250-launchd-data-20261119-r1/CHECKPOINT.md`
§3): 279 non-zero pages, and the same header/UUID values. Not re-derived here: the
`SHNGSEED2`/whole-disk identity computation and the Fletcher64 checks done inside the VM.

### Deviations from the original command sheet (recorded, not silently dropped)

1. **`hdiutil attach -offset` is not available on this macOS version.** The sheet's
   original slice-at-17408 command fails with `unknown option "-offset"`; the run attached
   the whole raw image instead (`ATTACH_MODE=whole`) and found the volume through the
   `/Volumes` difference. The `dd`-slice fallback exists in the sheet but was **not** used,
   so that branch is still unexecuted.
2. **`--gib 1` is impossible.** `make-data-seed.py` exits 2 with
   `--gib must be in 3..1024` and `seed-data-grow.py` exits 1 with
   `1 GiB is outside 3..1024`. The 3 GiB-then-shrink route replaces it; the size limit is
   script-level only.
3. **Shrinking changes the seed identity, not the volume.** `≤2 GiB` switches to the
   whole-disk SHA-256 identity, so this is a different installation seed from the 3 GiB
   one, even though the container and volume UUIDs are preserved. Anything that bound the
   3 GiB identity is stale.

### What this is not

1. **Not persistent.** The seed is delivered inside the payload as
   `initrd = "Payloads/scratch-data.img"`, so every boot reloads the same bytes; writes go
   into RAM. There is no store window (`sheng-data-persist` is absent, store mode 0) and no
   placement binding, so nothing survives a reboot.
2. **Declared ephemeral.** `unixnu/devicetree.py:328-329` adds
   `/chosen:ephemeral-storage = 1` when a seed is present and `persistent_data` is not
   declared; the r4 ADT carries that property. What the OS does with it beyond skipping
   first-boot migration has not been verified.
3. **Not a Data volume in the iOS sense.** `hdiutil -fs APFS` produces a plain APFS volume
   with `role = 0`, not `APFS_VOL_ROLE_DATA` (`0x40`); it is case-insensitive, and
   `shutil.copy2` does not preserve uid/gid, so the template's ownership is the VM user's,
   not `mobile`/`root`. Whether any of this matters was not tested.

Also not proven: that the device mounted the volume (the 2026-11-19 r4 boot leaves that a
strong inference, see
[`ufs-launchd-data-20261119-observation.md`](ufs-launchd-data-20261119-observation.md)),
that any write path works, or that a 2 GiB Data volume is large enough for a normal boot.

### Reproduction conditions

Requires macOS 15.x (the APFS formatter version fixes the expected bytes: `newfs_apfs`
2332.140.13.704.3) with the `044-76040-038.dmg` OS window available, ≥20 GB free, and the
three official scripts copied from the pinned base. The step-by-step command sheet used for
this run (`docs/data-seed-macos-vm-procedure.md`, `docs/data-seed-vm-run.sh`) exists only in
the working tree — it is **not** in this repository, so the steps above are the record
that ships. The macOS side of this round was executed by the user/parent in the VM; this
agent never touched the VM, and re-verified the identity bytes on the Windows host.

Status: `self-checked`, host only. No device action, no build, no persistence claim.
