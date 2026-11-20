# Enuma r8 timebase diagnostic

Status: host-only self-checked; no device run or independent verification.

The parent reports that deep review rejected r7 because its DEVELOPMENT kernel
did not enable kprintf spam: its `kprintf` path sends output to os_log, whose
fallback does not set TOCONS. r8 substitutes `printf` at the existing three
probe source sites; atomic sequence gating, sampling, the single 5000 ms
sleep and position before `load_init_program` remain unchanged.

The r4 screen transcript in `docs/ufs-launchd-data-20261119-observation.md`
reports the kernel `decmpfs.c:1894` cluster-copy error. XNU
`bsd/kern/decmpfs.c:98-112,1894` expands its `ErrorLogWithPath` into
`printf`. The same transcript's `Early boot complete` is launchd output, not
evidence of a kernel printf call.

In the XNU source, `osfmk/kern/printf.c:873-888,895-905` sends `printf`
through `vprintf_internal`, `__doprnt` and `console_printbuf_putc`.
`osfmk/console/serial_general.c:144-155,159-186` flushes a newline to
`console_write`; `serial_console.c:524-550,554-590` writes directly or
through a console ring and attempts a drain. The latter can be disabled or
otherwise refused and is not a proof that every line reaches the panel.
`serial_console.c:252-263,278-288` dispatches `_cnputs` through `_cnputc`
to the selected `cons_ops` implementation (`:122-128`).

## Host build and packaging

Build exit 0 and packaging exit 0. The first isolated build was interrupted
by the invoking tool's one-second timeout (exit 143); the completed build
used a separate fresh `self-check/attempt2` directory. No interrupted outputs
were reused. The copied r7 recipe was adapted only to select that directory.
The r7 wrapper injects the complete r6 ADT before the official payload is
assembled; no post-packaging mcopy. Reusing the random-seed is diagnostic
only, not a production entropy strategy.

| Item | SHA-256 |
| --- | --- |
| r8 bsd_init.o | `f6e6f5ad7fa0c141ef4cd87ddb73ca0a2c7999ad6ae999cb499b4800dfe3b3ac` |
| r7 bsd_init.o | `2aa4d4caa3c0cbebc96a3bc1cb1c4fd2713016924be2ee3ae4fcc8f8c6bccea2` |
| r6 bsd_init.o | `6c54e226afccc480e1101335edee289c9bcdf46d6200342561f7d689f81b8c1c` |
| r8 native.macho | `ffea81061ec17ab23b6c06657d5fffb075cce7d5253529b301a2bbf8ffb6f25d` |
| r8 prelink.macho | `ff502bebd813e333f0f082adf0cf5424f9ed16017671f01fa937e050e754cc6b` |
| r8 payload.img, 167772160 B | `32acf717f122db943122d66e8067c027368ff4295597432d3c76a9da2c0c896a` |
| r8 boot.img, 169951232 B | `0797330553b8cd1e5c2833dadb70a29ae816a490ae63c172b6fd8cde00339779` |
| readback ADT, 14048 B | `099dda97e8c01592cf9542b806b868ce098415ef9bab8ed7a01c8d03edd95059` |

The payload and boot measured hashes match the candidate manifest; the
readback ADT is byte-identical to r6. The 15-token boot arguments, mode 0,
seed initrd, trust cache and payload size match r6. The four other recompiled
objects (`IOKitBSDInit.cpo`, `kern_exec.o`, `IOUserClient.cpo`,
`EnumaUfsOwnerQuery.o`) are byte-identical to r6 and r7.

The build's native-image reachability audit records two calls to
`_native_legacy_display_probe` and two to `_native_legacy_display_late_probe`.
`llvm-objdump --disassemble-symbols=_bsdinit_task` shows two `_printf`
instructions (exit and skip share one) and one `_IOSleep`. Enter, exit and
skip strings each occur once in prelink. Both linked images have zero strong
and weak undefined symbols.

R6 boot, payload and manifest were rehashed and match the three previously
recorded pins. R7 boot and payload match its recorded hashes. The build and
packaging used r6/r7 as inputs and wrote into r8 only; no whole-directory
before snapshot was available, so whole-directory byte identity is not
independently established. The official base HEAD remains
`693f5d9cae8a408dd18b39f3f9fdc4228c934241`.

No device run, display output, timebase behaviour or successful delay is
established. The changed startup probe requires final deep review; independent
verifier rerun remains pending.
