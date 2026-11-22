# enuma r34 Mach message observation — host build

Host-only `self-checked` build; no device observation.
Independent review, verification, and device observation have not occurred.
This iteration did not complete an upstream HEAD check because the network was
unreachable; the local UniXNU HEAD was `693f5d9cae8a408dd18b39f3f9fdc4228c934241`.

The intended hooks are xnu-10063 `osfmk/ipc/mach_msg.c:659`
`mach_msg_trap_send` and `:752` `mach_msg_trap_receive`. They count user
trap paths, not message success; receive entry precedes port validation and
waiting. Counters are relaxed atomics, independently sampled; names match
exact `comm`, not PID, and multiple processes with a name are aggregated.
The intended dump reuses r32's 30-second/20-report timer and retains its
`enuma-att` and `enuma-ctl`:

```
enuma-ipc: begin send=<n> recv=<n>
enuma-ipc: bb send=<n> recv=<n>
enuma-ipc: sb send=<n> recv=<n>
enuma-ipc: end
```

| Observation | Interpretation |
| --- | --- |
| bb send and recv both grow | Both instrumented user-message paths are active; neither count establishes a successful message. |
| both bb counters stay zero while global counters grow | No matching backboardd activity observed on these paths; computation or blocking elsewhere remains possible. |
| only bb recv grows | Receive entry is active; this alone cannot establish waiting, since the hook precedes port validation and actual waiting. |

The global counter adds one atomic operation on each path entry; the helper
checks the first character before full comm comparison. Actual performance and
safe concurrent comm access remain unverified; own current process avoids
referencing another task but does not itself prove comm synchronization.

## Compile and link

The earlier attempt failed at `ipc_kmsg.h:230:2` (`ipc_kmsg_t` unknown)
because it reused the BSD `kern_exec.o` recipe instead of the osfmk recipe.
The original full command (argument array and cwd) is at
`/root/enuma-step10/UniXNU/out/enuma-ufs-version-diagnostic-20261112-python311/out/enuma/ipados-17.7.11-21H461/enuma/tree/build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/osfmk/DEVELOPMENT/mach_msg.o.json:1`.
Its `arguments` is the complete exact command, not an inferred flags list.
The r34 recipe reads this compiler-generated JSON fragment and changes only
argument 2 (patched source) and argument 4 (new object output); it preserves
all other arguments and cwd. Both hooks are in this one compilation unit.

Build command: `PATH=/home/wh1stl3/.local/bin:/opt/unixnu-linux/bin:/usr/bin:/bin /home/wh1stl3/.local/bin/python3 -B scripts/build-enuma-r34-ipc.py --dtb /root/enuma-step10/inputs/enuma.dtb`, exit 0.
Link occurred before prelink; native and prelink undefined-symbol checks
including weak symbols were empty. Both binaries contain exactly four
`enuma-ipc:` formats and retain three each of `enuma-att:` and `enuma-ctl:`.
The object disassembly has one `_enuma_ipc_record` relocation each in
`_mach_msg_trap_send` (argument 0) and `_mach_msg_trap_receive` (argument 1).
Patched source locations are `source/osfmk/ipc/mach_msg.c:668,767`;
dump insertion is `source/bsd/kern/EnumaBbScan.inc:162`.

| Artifact | r32 SHA-256 | r34 SHA-256 | size delta |
| --- | --- | --- | ---: |
| kern_exec.o | b34d3a4d9d4e512c6274f8a15ac01c3f6716ce87bfec452c2be7e121246d5fe4 | ca1370c29397c93f86ad1399a62dbe1020d419b7a3b485b429896ca0fd61c79d | +2240 |
| IOUserClient.cpo | a916b55a8c43ea076d447e27330013277a9b9d3b2abca51c44265338dce7431b | 455ebd7abc178922efeb1faed7020b828fa56a300cef023c3639de58dd397568 | -8 |
| native.macho | a95b41811931830683da764d88b6e50106f940b970495bea19f5c1de987357fa | 0352644a06f030608a0889f70f7453eb5fc302fb66a676ae134dc2eb8c2845f0 | +232 |
| prelink.macho | 9c3413aad135e2e43b07855f45d021cecd3bf38b96c77c4990e321be020ff18e | d974059707e07b77504e38d984c4c3bf5a41b6a39fc4931ecfbcb42ed97cb26a | 0 |
| payload.img | 877ee476c72af5e497d34f5a9ababd0f72b3736a01eef70e1457d3d3909cfe14 | 69feca6c43aea783a0adb4b0959c23168fbb78fbfaba1f01389e1df8889b0343 | 0 |
| boot.img | 9fe165606f0300dd83e53e6377a58ff9a3791f08845701d95ff6fa1e9dd40011 | 345741e4b48153ca2635905c7b9da47d376b62fd3b23784ac7fd0bac5e9a0e80 | 0 |

r34 `mach_msg.o` SHA-256 `2352cd45263853bacf75680ea236397b0dd54b8c3369518362e94053cb42b7fe`;
boot size 169951232. Filelists contain 1006 entries; only paths for
`mach_msg.o`, `kern_exec.o`, `IOUserClient.cpo` differ. `IOUserClient.cpo`
was recompiled by the r32 replay and its bytes differ; no machine-code
equivalence is claimed. The six r32 hashes above match the existing r32
record, but no before-build full-directory snapshot was taken. The failed
compile and JSON-parser intermediates are retained separately.
Runtime, counter performance, comm synchronization, deep review and
independent verifier remain unverified.
