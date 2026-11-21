# r9 post-mount path and space probe

Host-only **self-checked** diagnostic; no device run, independent verifier or
deep review. Not approved for deployment. Default patch series is unchanged.

## Design and interpretation

`patches/xnu/enuma-r9-vnode-space-probe.patch` modifies
`bsd/kern/kern_exec.c` in an isolated copy. In `load_init_program`, the call
is immediately after successful `native_owner_cache_prepare` and
`native_owner_data_prepare`, before memorystatus and launchd exec. An atomic
relaxed sequence allows only seq=0 to probe. The pre-existing r8 timebase
probe remains in `bsd_init.c`; it is not duplicated or changed.

The six lookups use `vnode_lookup(path, 0, &vp, vfs_context_current())`,
the context already used after Data mount in `native_owner_data_prepare`.
`bsd_init.c` uses `vfs_context_kernel()` instead, so permissions/context are
not identical. Each successful lookup releases the vnode. Type is REG, DIR,
OTHER, or `-` on error. The following paths are printed untruncated:

| Path | Expected successful type; failure interpretation |
| --- | --- |
| `/System/Library/LaunchDaemons` | DIR; otherwise record errno/type |
| `/System/Library/LaunchDaemons/com.apple.CommCenter.plist` | REG; otherwise record errno/type |
| `/System/Library/LaunchDaemons/com.apple.SpringBoard.plist` | REG; otherwise record errno/type |
| `/usr/libexec/xpcproxy` | REG; otherwise record errno/type |
| `/System/Library/dyld` | DIR; otherwise record errno/type |
| `/System/Library/Caches/com.apple.dyld` | DIR; otherwise record errno/type |

Expected types are diagnostic hypotheses, not verified file existence.
ENOENT alone does not distinguish a genuinely absent file from an unexpected
mount view. Credentials and permission errors must be interpreted separately.

| Line | Meaning |
| --- | --- |
| `enuma-fs: / <total_kib> <available_kib>` | Root filesystem capacity and `f_bavail` |
| `enuma-fs: /private/var <total_kib> <available_kib>` | Mounted Data capacity and `f_bavail` |
| `enuma-fs: maxvnodes <value>` | `desiredvnodes`, the value returned by `kern.maxvnodes` sysctl, not `kern_maxvnodes` |

`vfs_getattr` requests `f_bsize`, `f_blocks`, and `f_bavail`; values use
1024-byte KiB. An additional `enuma-fs: var-critical` means available
space is below 1024 KiB. Lookup/getattr failure prints an error line; if
getattr succeeds without supplying a requested attribute, the error line can
say `error 0` and does not mean capacity was measured. Calls request no
filesystem mutations, but runtime latency and filesystem side effects are
not independently established. The commpage timebase hypothesis was not
tested; use an independent method if later needed.

The packed scratch seed is 1,142,976 B but its logical APFS container is
2,146,996,224 B (about 2047.5 MiB). Available space cannot be calculated from
packed size: APFS overhead and runtime writes are unknown. Official evb10
reports 256 MiB ENOSPC and a 512 MiB volume reaching lock screen; the larger
logical container lowers the priority of the space-shortage hypothesis but
does not exclude it. Compare future measured available space, not packed
size, while noting those evb10 numbers describe volume capacity.

## Host evidence

Package script exit 0, using Python 3.11.18. Boot image 169951232 B
`fd5da6e4084d9b85e9f3921b15f1d4b9c8ce0e6dbb6c89681dfa603d14563669`;
payload 167772160 B
`e387d04b36a70914bb48c610e297ae5ed28161ad4d28f7bf804129a7d502f7c8`;
prelink `a2a85ff792749623f7c16a7e7ef773c422e238de7c9039ed40f82c8964605ed5`.
The six vnode `_printf` call sites are in `_load_init_program`; there are
two `_enuma_fs_probe` calls, three `_printf` sites in that helper, and one
maxvnodes `_printf` site. Each exact `enuma-vn` format and the four distinct
`enuma-fs` formats occurs once in prelink.

The r9 `kern_exec.o` was recompiled:
`9667d5ee37165a293ba520cc16f4fc31f3d60b2d83f50d9d1b3c0b682d012cea`,
versus r8 `dd0612ccc27fedcdca4f70bc3436f986cad936606e432e43726611b81146371f`.
`bsd_init.o` is reused from r8
`f6e6f5ad7fa0c141ef4cd87ddb73ca0a2c7999ad6ae999cb499b4800dfe3b3ac`;
reuse does not claim byte-identical recompilation. The rebuilt
`IOKitBSDInit.cpo`, `IOUserClient.cpo` and `EnumaUfsOwnerQuery.o` match r8.
Actual cc1 `-I` lists for r8 bsd_init and r9 kern_exec match, 14 entries.
The inherited build-result JSON erroneously labels kern_exec equal to r4 and
not replaced; actual hashes and link filelist supersede those r6-era labels.

The wrapper replaces `devicetree.generate` output with the complete r6 ADT
before official `payload.py:194` writes it into staging. Official
`payload.py:250-256` constructs the FAT then hashes the final image and ADT.
Packaging reads back with `mtype`, compares ADT byte-for-byte with r6, and
checks both against the official report; there is no post-report replacement.
ADT SHA-256
`099dda97e8c01592cf9542b806b868ce098415ef9bab8ed7a01c8d03edd95059`.
Normal official `mcopy` during FAT construction is not a post-report change.
The prior claim that any `mcopy` violated the brief was incorrect. An earlier
packaging run failed at `unchanged` because its definition was accidentally
removed; restored assertion covers IOKitBSDInit and EnumaUfsOwnerQuery,
with changed kern_exec checked separately against r8.

Relative to r8, the probe changes kern_exec/prelink and therefore payload
and boot bytes. Boot arguments, mode 0, r6 ADT, initrd, trust inputs and
160 MiB payload size remain the same. Current r8 rehashes:
boot `0797330553b8cd1e5c2833dadb70a29ae816a490ae63c172b6fd8cde00339779`,
payload `32acf717f122db943122d66e8067c027368ff4295597432d3c76a9da2c0c896a`,
manifest `e8c32e7d5dc928eadc7744d151983e85d50cc276a9cb6658a65f01dea6b32500`.
Boot and payload match prior recorded pins; no prior whole-directory snapshot
or independent manifest pin was established.
