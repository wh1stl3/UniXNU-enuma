# r39 Data mount, seed vm directory and swap prefix

Status: self-checked offline source/artifact investigation; no device access,
volume modification or build. r39 error 30 is the parent-transcribed
`vnode_open` EROFS, not a mount-table observation.

## Mount flags

The pinned base `UniXNU@693f5d9cae8a408dd18b39f3f9fdc4228c934241`,
`patches/xnu/offline-owner-systemos-mount.patch:236-245` constructs:

```c
struct mount_args request = {.type = scratch + 0x100, .path = scratch + 0x120,
    .flags = 0, .data = scratch + 0x200};
copyout("apfs", request.type, 5);
copyout("/private/var", request.path, 13);
error = mount(p, &request, &result);
```

The `copyout` calls above are shown individually; the actual patch combines
them in a short-circuit error check. Flags are **0**, neither `MNT_RDONLY` nor
`MNT_UNION`. This is the Data mount, not the separate read-only SystemOS union
mount at patch lines 80-118. At lines 247-257 the code looks up `/private/var`,
checks its device and APFS type, and rejects `vfs_flags(data_mount) &
MNT_RDONLY`; lines 288-290 panic on failure when the Data macro is enabled.
The local built-source tree `/root/enuma-step10/UniXNU/out/enuma/ipados-17.7.11-21H461/enuma/tree/.cache/xnu-work/bsd/kern/kern_exec.c:7982-8040,8188-8190`
contains the corresponding code. r39 `link.filelist:585` instead identifies
the inherited r34 `objects/kern_exec.o`; source-to-object identity and actual
runtime mount flags have not been independently established here.

Thus the intended Data mount is **read-write, non-union**; its requested flags
do not directly explain EROFS. The rejection check applies at mount time only.
Missing facts are the effective r39 prefix, mount table and path resolution at
the failing open, and APFS/runtime read-only state. A later remount, another
mount or prefix, path resolution into a read-only layer, or filesystem-level
refusal are hypotheses, not established causes. The previous r4 absence of a
panic was only indirect evidence, not a positive r39 mount observation.

## Seed directory

r39 host record `docs/enuma-r39-aksid-host-20261123.md:44-46` says its FAT
members except kernel match r35; seed provenance and hash are recorded in
`docs/data-seed-20261119-generation.md:40-52,57-67`. The local equivalent
`out/data-seed-macos-20261119/data.dbr` was read-only SHA-256 checked:
`c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470`.
It is a DBRDISK1 packed sparse APFS disk, not a directly mountable directory.

Read-only byte scan with Python 3.11 for `b"vm\x00"` found offsets 955348 and
977600 in the packed file. At 955348 the preceding 12 bytes are
`020000000000009003208690`: consistent with an APFS directory-record key,
parent object 2, hashed-name length 3, name `vm`. This is evidence for a
root-level `vm` record, but scanning bytes does **not** establish that the key
belongs to the current live volume tree rather than stale metadata, nor that
the entry is a directory. Therefore `/private/var/vm` existence remains
**unconfirmed**; an APFS-aware read-only traversal of the current root tree
is needed. `UniXNU/scripts/make-data-seed.py:59-74` copies the donor's
`private/var` tree, but does not explicitly create `vm`, so the generator
alone cannot settle it. If the parent is missing, ordinary lookup is ENOENT,
not this observed EROFS; absence alone would not explain error 30.

## Swap defaults

In the same local XNU work tree, `osfmk/vm/vm_compressor_backing_store.h:55-61`
sets the non-macOS prefix to `/private/var/vm/swapfile`; the macOS branch is
`/System/Volumes/VM/swapfile`. `osfmk/vm/vm_compressor_backing_store.c:78`
initializes `swapfilename` to `SWAP_FILE_NAME`; `bsd/kern/kern_sysctl.c:4516`
exposes it as writable `vm.swapfileprefix`. Consequently runtime may differ.
`kern_sysctl.c:3978-3979` exposes read-only `vm.swap_enabled`; backing-store
source lines 462,519 initialize it to 0 and set it to 1 upon initialization.
Neither default nor initialization proves the prefix or mount at r39 failure.

No source change is justified by these observations alone. Inspect the effective
prefix, current mount/path and APFS state, and traverse the seed tree before
choosing a fix.
