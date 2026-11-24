# 21H461 launchd routine 0x320: partial static analysis

Status: self-checked, static analysis only; no build or device operation.

The donor `out/userdata-clean-20261112/OS.raw` was mounted with apfs-fuse
`66b86bd525e8cb90f9012543be89b1f092b75cf3`, `-o ro`; the APFS container
exposes the system volume under `root/`, so the file is `root/sbin/launchd`
in that mount, i.e. `/sbin/launchd` in the OS. The mount was unmounted.
Local copy: `out/launchd-21h461-analysis/launchd`, 561856 bytes,
SHA-256 `8cec9a3c44a443b08e977ccc5d577850316ad428c575dc01f09b018dbd5b6a25`;
`file`: Mach-O 64-bit arm64 executable. Its embedded bundle version is
`2748.140.10.703.1`, SDK build 21H420. The image's 21H461 identity is inherited
from the donor provenance, not independently established from this binary.

All addresses below are file offsets; in `__TEXT`, VM address is
`0x100000000 + offset`. The saved disassembly is
`out/launchd-21h461-analysis/disassembly.txt`.

## Dispatch and handler

The dispatch function at `0x2cd24` subtracts 800 from its routine argument,
checks index <= 47, and reads byte table `0x553b9`. Byte zero is 8, so the
indirect branch base `0x2cd94` plus `8*4` selects `0x2cdb4`, which calls
handler `0x302f4`. This is a routine argument, not evidence that Mach
`msgh_id` itself equals 800.

```text
2cd68  sub  w8, w22, #800
2cd6c  cmp  w8, #47
2cd70  b.hi 0x10002ce7c
2cd7c  adr  x9, #165437       ; table 0x553b9
2cd84  adr  x10, #16          ; branch base 0x2cd94
2cd88  ldrb w11, [x9, x8]
2cd8c  add  x10, x10, x11, lsl #2
2cd90  br   x10
2cdb4  mov  x0, x21
2cdc0  bl   0x1000302f4
```

At `0x30330–0x3037c` the handler fetches `paths`: missing paths creates an
empty reply object at `0x30454` and returns zero; otherwise the value must be
an array or dictionary and the request must expect a reply, else return 22
at `0x30448`. A domain flag check returns 124 at `0x30318`. Flags `enable`,
`force`, `legacy-load`, `angel`, `managed-lwcr` and `by-cli` are read. The
dictionary case is normalized by `_xpc_dictionary_apply` at `0x304b8`.

The valid nonempty path calls `0x15f20` at `0x304f4` and returns zero. There
an array is enumerated (`_xpc_array_get_count`/`_xpc_array_get_string`,
`0x16118–0x161bc`), each string becomes a work item via `0x15904` and is
added through `0x16d00`. The dictionary case uses `_xpc_dictionary_apply`
at `0x16110`. Work is handed off via `0x3861c`: depending on state it calls
`_xpc_dictionary_handoff_reply` (`0x386a0`) or `_dispatch_async`
(`0x386bc`). The scheduled block `0x164ec` asserts its queue and initiates
each item through `0x15a50`. Thus the request processing is not simply a
synchronous in-place directory scan: completion can be deferred. This does
not establish whether the client waits indefinitely or the precise filesystem
operations used for every path.

Completion block `0x1630c` sets `bootstrap-error` and `errors` at
`0x163a8` and `0x163bc`; when the retained reply exists and no group is
present, it sends via `_xpc_pipe_routine_reply` at `0x1646c`. There is also
a group-notify branch at `0x16420`; its eventual send and the caller's
generic reply/error machinery have not been fully traced. Missing `paths`
creates a reply but its eventual sending site is not established here.
An unfinished work item, unserviced queue, or stalled underlying operation
could defer completion, but no unconditional infinite/no-reply branch was
proven. No timeout guarantee was established.

The binary contains `/private/var/db/com.apple.xpc.launchd`, but mere string
presence does not establish a write on this handler's call path. Likewise,
the path-specific open/stat/directory traversal and calls to other services
remain untraced; unrelated open/fstat sites cannot establish those claims.
Do not attribute a hang to a particular operation without that trace.

Apple's public [launchd tags](https://api.github.com/repos/apple-oss-distributions/launchd/tags?per_page=10)
include `launchd-842.92.1` at `49a9c79b2949192dfca697b1054245cdfb645788`,
not this binary's 2748.140.10.703.1. No corresponding public version was
identified; implementation differences cannot be reliably inferred by
comparing those versions.
