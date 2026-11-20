# r4 persona and decmpfs: offline source reading

Status: self-checked, source analysis only; r4 screen text is the unverified
parent transcription in `ufs-launchd-data-20261119-observation.md:95-112`.
XNU source references below are to
`out/root-match-assertion-20261118/source-xnu/`; this source copy's exact
correspondence to every r4 object was not independently established here.

## Persona type 6

`bsd/sys/persona.h:45` defines type 6 as `PERSONA_SYSTEM_PROXY`.
`libsyscall/wrappers/persona.c:106-123` implements the userspace
`kpersona_find_by_type`, passing type and `PERSONA_OP_FIND_BY_TYPE` to
`__persona`; kernel `bsd/kern/sys_persona.c:499-501,400-461` dispatches to
`persona_find_all`. In `bsd/kern/kern_persona.c:444-502`, the list is searched
for all requested attributes and `ESRCH` is returned when `found == 0`.
For this wrapper it searches type alone. The similarly named kernel
`persona_find_by_type` at `:430-434` is not the syscall's direct callee.

The log associates the messages with launchd domains, but no launchd binary
was extracted from the donor APFS images in this investigation, so the exact
userspace call site and its error branch are not established. The wrapper is
userspace; that alone does not identify which process issued this call.
The transcript reports subsequent service attachments and bootstrap exit
(`observation:99-105,110-111`), not proof that the affected service or
launchd itself handled this particular return without aborting. Fatal versus
recoverable for the individual request, and noise versus mainline defect,
remain undetermined. On-device attribution would require a captured caller
PID, return/exit behavior and the affected service's sustained state; no new
device run is authorized by this record.

## decmpfs err 14

`bsd/kern/decmpfs.c:1647-1653` identifies `decmpfs_read_compressed`, a VFS
read handler. At `:1825-1829` it fetches uncompressed data; `:1890-1895`
copies it from the UPL to the requested UIO and logs a copy failure.
`:1901-1904,1913-1923` commits the UPL, exits, logs and returns the error.
Thus `:1922` is a general error exit, not a second copy call. Error 14 is
`EFAULT` (`bsd/sys/errno.h:104`). The copy helper propagates `uiomove64`
(`bsd/vfs/vfs_cluster.c:6689-6760`); this identifies the failing copy path,
not the specific invalid address or its cause.

The filesystem read implementation supplies the `vnop_read_args`; the
open XNU copy contains no filesystem caller of `decmpfs_read_compressed`,
so the APFS call/return handling cannot be established from this source.
The generic `VNOP_READ` dispatch returns its filesystem result
(`bsd/vfs/kpi_vfs.c:3848-3870`), and the generic vnode read path returns it
(`bsd/vfs/vfs_vnops.c:1133-1145`). This is a read path, not proof of a
page-in or mapping failure: `decmpfs_pagein_compressed` is a distinct handler
(`bsd/kern/decmpfs.c:1278`). Whether this particular read affected exec,
mapping, or an important service is unknown without the process, file, call
stack and outcome. An on-device capture matching those fields and the
subsequent exec/service result would resolve that question; no new device run
is authorized here. Noise versus defect remains undetermined.

The two phenomena are not causally linked by the available evidence.
