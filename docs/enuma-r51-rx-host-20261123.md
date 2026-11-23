# enuma r51 mach_msg2 trap counters — host build

Status: **self-checked**, no device run or independent verification; deep
review of the concurrency-sensitive hot path remains required.

## Instrumentation

The generated `out/ufs-sm8250-rx-20261123-r51/source/osfmk/ipc/mach_msg.c`
calls `enuma_rx_enter()` at line 944, and `enuma_rx_exit(slot)` at line 1067,
immediately before its sole `return mr` at line 1068. The build generator
asserts the original function has exactly one `return ` and it is `return mr;`;
all original error gotos converge on that return. The exit uses the saved
entry slot even if process state changes. The existing send/receive logic,
return value, timeout and wakeup paths are not edited. The native disassembly
has calls at `0xfffffff00b860064` and `0xfffffff00b8601a0`.

`package/EnumaRx.inc` uses two fixed PID slots (5 and 34) for each of the
relaxed 64-bit atomic entry and exit counters. Other PIDs are ignored. There
is no new lock, allocation, hot-path print or deliberate panic. PID reuse
aggregates different processes; counters wrap modulo 2^64. Counters run even
when reporting is off. No send/receive option filtering is attempted: a
combined call's flags do not say which phase is currently executing.

`package/EnumaBootProgress51.inc:20` adds the dump to the existing bp report,
which is reached only when `enuma-bp=1`; otherwise no new lines are printed.
The exact format strings are:

```
enuma-rx: sb5 in=%llu out=%llu\n
enuma-rx: bb34 in=%llu out=%llu\n
```

Each string occurs once in each final Mach-O. The print reads are separate
relaxed atomic loads, not a coherent snapshot.

| Difference | Interpretation |
| --- | --- |
| `in - out > 0` | A coherent snapshot would indicate that many in-flight counted invocations; it cannot distinguish send from receive or identify the peer. |
| `in - out = 0` | A coherent snapshot would indicate no counted invocation is in progress. The printed values are **not** coherent, so equality is not a hard instantaneous exclusion. |

Entry and exit increments bracket most, but not literally every machine
instruction of the trap: preemption can occur just before entry increment or
just after exit increment. Neither value proves a thread is sleeping. Legacy
Mach trap paths are not covered. Observed long-term stable values strengthen
an inference but do not make the individual samples transactional.

## Build evidence

`/home/wh1stl3/.local/bin/python3 scripts/build-enuma-r51-rx.py --r51`
completed exit 0. The base UniXNU HEAD before and after was
`693f5d9cae8a408dd18b39f3f9fdc4228c934241`. No new third-party code.

| Item | r49 SHA-256 | r51 SHA-256 |
| --- | --- | --- |
| `kern_exec.o` | `0aeba58e498ee3d3ea918114658e19c79f6faed30f6f3ceb1a19180fc91f4336` | `caf21bbcc9d421b7f703fc57d5b5393c55a8a78cbbd2201a40292de65fdf5755` |
| `mach_msg.o` | `2352cd45263853bacf75680ea236397b0dd54b8c3369518362e94053cb42b7fe` | `8e1109655f8dfcad46ef4485795aabeff97507886c897871378ee06af4794ab0` |
| `boot.img` | `1180a2c7b2c7f903cf412791a704a3051dbf6335f696f0183896a4c3b1f9d3f5` | `3cc69f25413bc961a57fcc41a821b57a40889f0a8eb310fd8da4cc3571edb177` |

Boot size is 169,951,232 bytes, delta 0; native Mach-O delta +320 bytes;
prelink, payload and ADT sizes delta 0. The r49 five primary artifacts were
hash-snapshotted unchanged; ADT is byte-identical. Of the direct link inputs,
1,004 other filelist entries and 15 archives are unchanged. Only
`Payloads/kernel.macho` changed in the FAT payload; boot arguments are
unchanged. Both Mach-O files have zero undefined symbols including weak;
format uniqueness and named disassembly symbols were checked. Full hashes,
commands and disassembly are in the local candidate directory.

Not established: actual device behavior, timing effects, absence of panic,
thread wait state, peer identity, persistence, or GUI. The generated
candidate has not been reviewed by deep reviewer or independently verified.
