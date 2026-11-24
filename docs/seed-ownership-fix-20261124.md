# Data seed ownership correction — stopped (2026-11-24)

Status: **blocked; no ownership correction performed** (`self-checked`).

WSL `sshpass` was installed and used to log in to the macOS VM; `sw_vers`
reported macOS 15.8.3 and `whoami` reported `wh1stl3`. The intended remote
destination did not exist at the time of the check. No image was transferred
or mounted.

The local source `out/data-seed-macos-20261119/data.dbr` has SHA-256
`c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470`
and is 1,142,976 bytes, not 2,146,996,224 bytes. Its header is `DBRDISK1`:
the latter size is the packed image's logical expanded size, as also documented
in `data-seed-20261119-generation.md`. It is not a raw disk image suitable for
the specified raw-image attach. Unpacking and repacking were not included in
the requested procedure, so work stopped before the transfer.

No `chown` or `chmod` was run, no fixed image or new hash was produced, and
no APFS ownership or directory verification was performed. The original seed
and its contents were not modified. Whether ownership can be enabled and
changed on the expanded volume remains unverified.

## Follow-up: expanded image and path blocker

The above is the earlier attempt. This follow-up used the official
`UniXNU/drivers/DarwinBoot/Test/packed_ramdisk.py` `regions()` parser and
the sparse-write expansion pattern in `UniXNU/scripts/seed-data-skip-setup.py`
lines 53–61. From WSL, the effective expansion was:

```python
logical, extents = packed_ramdisk.regions(source.read_bytes())
with destination.open('xb') as f:
    f.truncate(logical)
    for offset, data in extents:
        f.seek(offset)
        f.write(data)
```

The official repack command, **not run**, is
`python3 /mnt/d/Code/PortingiOS/UniXNU/drivers/DarwinBoot/Test/packed_ramdisk.py out/data-seed-macos-20261119/data.raw.fixed out/data-seed-macos-20261119/data.fixed.dbr`.
This raw size is below the tool's 2 GiB sparse-seek threshold.

- Original `data.dbr`: 1,142,976 bytes,
  SHA-256 `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470`.
- Expanded `data.raw`: 2,146,996,224 bytes,
  SHA-256 `1342537e745ba6efeebea6df74d6d53eb70a94c842fb92b32aa72f3ac161b20a`.
  The VM transfer hash matched before attachment.
- VM attachment yielded `/dev/disk6`, APFS volume `/dev/disk7s1`,
  mounted at `/Volumes/Data`; `diskutil info` reported `Owners: Disabled`.
- `/Volumes/Data/private/var` does not exist: the volume root contains `db`,
  `mobile`, `vm` and other directories directly. `ls` reported the missing
  path. The ownership values displayed while ownership was disabled are not
  reliable on-disk ownership evidence.
- The requested recursive chown of `<mnt>/private/var` therefore cannot be
  applied as written. Treating the whole volume root as that path and doing
  `chown -R` would change other subtrees too, conflicting with “other paths
  untouched”. No ownership enabling or chown was performed. The image was
  detached using `sudo hdiutil detach /dev/disk6`.
- Fixed raw/packed image and APFS ownership verification are absent. The
  original packed file was not overwritten. Attach may modify the VM copy;
  the expanded local source remains available.

Status: blocked pending clarification of whether recursive ownership changes
to all volume-root descendants are authorized, or only the volume root itself
and the specified `db` and `mobile` subtrees. `self-checked`

## Authorized ownership correction

The user subsequently authorized correcting ownership of the volume root as
iOS `/private/var` and its descendants. Connection self-check returned macOS
`15.8.3`, user `wh1stl3`, and a home listing containing Desktop, Documents,
Downloads, Library, Movies, Music, Pictures, Public and nuwa-fix. The initial
home glob failed under zsh; a subsequent search found `~/seed-work/data.raw`
with SHA-256 `e8251d12ee03efd3ad8740f7c6bbf8e29e81fcd406b5df6781f975987cf9c3fd`,
so it was replaced by a fresh transfer of the local raw image. Both source and
transferred copy matched
`1342537e745ba6efeebea6df74d6d53eb70a94c842fb92b32aa72f3ac161b20a`.

Raw attach produced `/dev/disk6`, `/dev/disk7`, and `/dev/disk7s1` mounted
at `/Volumes/Data`. `diskutil info` reported `Owners: Disabled` before
`sudo diskutil enableOwnership /Volumes/Data` and `Owners: Enabled` after it.
The requested commands then ran:

```sh
sudo chown -R 0:0 /Volumes/Data
sudo chown -R 501:501 /Volumes/Data/mobile
```

`ls -ldn /Volumes/Data /Volumes/Data/db /Volumes/Data/mobile /Volumes/Data/vm`:

```text
drwxr-xr-x  33 0    0    1056 Nov 19 21:28 /Volumes/Data
drwxr-xr-x  36 0    0    1152 Nov 19 21:28 /Volumes/Data/db
drwx--x--x   7 501  501   224 Nov 19 21:28 /Volumes/Data/mobile
drwxr-xr-x   2 0    0      64 Nov 19 21:28 /Volumes/Data/vm
```

`find /Volumes/Data -maxdepth 2 -uid 501 ! -path '/Volumes/Data/mobile*'`
returned no entries. After `sudo hdiutil detach /Volumes/Data` ejected disk6,
the VM image and the pulled local `out/data-seed-macos-20261119/data.raw.fixed`
both had SHA-256
`9a4f85a1a1e88b4ef7a1b4728725d86d0e25ff12160a2ddb9412ba2e732c836b`.
The original local raw and packed seed were not overwritten; no repack,
kernel build, or phone operation was performed. Runtime use of the corrected
seed is not verified. `self-checked`
