# Enuma r7 timebase diagnostic — host-only

Status: self-checked; no device access or independent verifier rerun.
The r7 image is a diagnostic candidate, not deployment authorization.

## Probe and interpretation

`patches/xnu/enuma-timebase-probe.patch` adds a default-off
`XNU_ENUMA_TIMEBASE_PROBE` in `bsd/kern/bsd_init.c`, before
`load_init_program()`. A relaxed atomic fetch-increment assigns a sequence.
Only sequence zero samples `mach_absolute_time()` converted to nanoseconds,
`microtime`, and `CNTVCT_EL0`, logs enter, calls `IOSleep(5000)`, then samples
and logs exit. A nonzero sequence prints only `enuma-tb: skip seq=N`, does not
read or write shared timestamps, and does not wait. A skip may precede enter
if sequence zero is preempted. Skip means the entry was reached more than once;
it does not distinguish overlapping from sequential invocations.

| Observation | Interpretation |
| --- | --- |
| Real elapsed about 5 s and counter delta about 96,000,000 | Consistent with a 19.2 MHz counter and nominal delay, not proof of a correct system clock. |
| Real elapsed much less than 5 s | Delay or its scheduling/time conversion is abnormal; counter and external timing are needed to narrow it. |
| Real elapsed much more than 5 s | Delay, scheduling or output latency may be abnormal; the lines alone do not identify which. |
| Enter without exit | No completed pair observed; blocked sleep, trap, output loss or later failure cannot be distinguished. |
| Skip | Ignore for the paired measurement; it is not a second delay. |

96,000,000 assumes 19.2 MHz and five real seconds; runtime counter frequency
and readability in this context remain unverified. External real-time
measurement is required and logging itself has latency.

## Packaging and evidence

The first r7 packaging attempt replaced ADT inside an already built FAT image
after the official `payload.json` was written. Its ADT and payload hashes
therefore described the earlier image; that intermediate is superseded and
must not be used. The official ADT generator includes a random-seed, so ADT
bytes differ between builds even with identical deterministic inputs.

The repack uses `r7-payload-wrapper.py` only in the r7 output directory: it
calls the official generator, then supplies the r6 ADT as the return value
before `UniXNU/scripts/unixnu/payload.py:191-196` writes the staged ADT.
Official volume creation and report generation at `:250-256` thus hash the
actual input and final image. No post-report ADT replacement or manually typed
hashes are used. Reusing the full ADT also reuses its random-seed; this is
strictly a diagnostic comparison, not a reproducible or production entropy
strategy.

The repack was host-only and did not recompile the kernel:

| Item | r7 SHA-256 or observation |
| --- | --- |
| `bsd_init.o` | `2aa4d4caa3c0cbebc96a3bc1cb1c4fd2713016924be2ee3ae4fcc8f8c6bccea2`; r6 `6c54e226afccc480e1101335edee289c9bcdf46d6200342561f7d689f81b8c1c` |
| `native.macho` | `24a7dad03ff15b169026e767f8db2b69ca75ea4e91e6a36ef395799b7e139dc6` |
| `prelink.macho` | `dcfc854d5c11979326e388d55cb16c0d18e67132fd47052df9a48ff8252c7477` |
| `payload.img`, 167,772,160 B | `a4e17eca3be7360a05a9afc2e24cd940e5baab3245a64dec017e6bfdf7bf48c6` |
| `boot.img`, 169,951,232 B | `439f3b36568268e559bfd6a2fb35a1ad9bb7769c1cfd0c4e402936e81c58468b` |
| ADT read from payload | 14,048 B `099dda97e8c01592cf9542b806b868ce098415ef9bab8ed7a01c8d03edd95059`; byte-identical to r6 |

Measured payload and boot hashes agree with final reports and manifest; the
ADT report agrees with readback. The 15-token boot line, mode 0, initrd,
160 MiB payload size, trust cache and ADT are retained from r6. Relative to
r6 the probe changes `bsd_init.o`, linked kernels, payload and boot image;
the four other explicitly recompiled objects were byte-identical. Other link
inputs were reused, not independently byte-compared against a pre-build
snapshot.

`/usr/bin/llvm-objdump` shows two display probe and two late-probe calls,
two `_kprintf` instructions in `_bsdinit_task` (exit and skip share one),
one `_IOSleep` call, the atomic `ldxr/stxr` and nonzero skip branch, and two
`CNTVCT_EL0` reads. Enter, exit and skip format strings each occur once in
prelink. Strong/weak undefined symbol counts are zero in both linked images.
The linker was `/opt/unixnu-linux/CommandLineTools/usr/bin/ld`, ld64-956.6.

r6 boot and payload hashes were remeasured as
`3161efc679c726ffc8f804f81a43f1f61cb49fcf4df8262c2e268c6e41f12b74` and
`4ca318cd39d297cfa654bcd7e3fec0a6529cfb8543469c24e974ce793889b9c8`.
Its manifest measured `1a4124ae8e5680b06b0db9fc98f0a00fa8ac2c84b3805cd00d575f63079711d6`;
the parent supplied this manifest baseline. r7 writes only in its own output
directory. No earlier per-file mtime snapshot exists.

No device test, display pixels, timebase behaviour, successful timer sleep,
counter access or clock accuracy is established. Final independent verifier
and deep review of the startup/concurrency change remain pending. Default
series and board configuration are unchanged.
