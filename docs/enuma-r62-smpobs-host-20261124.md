# r62 SMP observation host build — 2026-11-24

Status: self-checked only; no device operation, independent verification, or runtime result. Deep review of inherited startup and concurrency remains pending.

## Arguments and observation

Relative to r61 remove `armcpu-spi-ipi=1 armcpu-self-ipi=1`, retain `sheng-smp=1 cpus=2 armcpu-diagnostics=1`, append `enuma-bp=1`. Read back from the payload embedded in `boot.img`:

```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1 dk=0 sheng-smp=1 cpus=2 armcpu-diagnostics=1 enuma-bp=1
```

Expected observation formats, not observed runtime output:

```text
enuma bp r49 i=%u t=%lu
enuma-cpu: online=%u seen1=0x%llx step1=%u fail1=%u
enuma-cpu: mpidr1=0x%llx
```

The inherited report emits other diagnostics, but the color-fill report is removed. Online count 2 supports a second online CPU, not proof of working interprocessor interrupts. No line, freeze or panic does not identify the cause.

The two IPI options are removed to avoid the SPI IPI configuration when board interrupt allocation is not established; the intended SGI alternative and delivery are not runtime verified. The unchanged ADT has only the two interrupt-controller properties found by the script; absence of device interrupt properties does not establish physical SPI occupancy or GIC capacity; see `docs/ipi-intid-conflict-20261124.md`.

## Character path and build evidence

The color-fill hook and its once-only disabled-path modification are withdrawn to restore the original character path; the `EnumaFbFill*.inc` files remain in the repository but are not linked into this candidate. The inherited color-fill statistics report and declarations are also removed because the original console object has no such globals. No timing or locking safety claim is made.

WSL root `/home/wh1stl3/.local/bin/python3 scripts/build-enuma-r61-smp2.py --r62` completed. Output `out/ufs-sm8250-smpobs-20261124-r62/boot.img`: 169951232 bytes, SHA-256 `e378b1055e26b7d9b743f1ea7f30d8d26bd3a89e48de54ee23428ae0f9c3d894`. The previous r62 output was moved to `out/_superseded/`. Upstream HEAD at start: `90c0893904859cf4bf8d486a08dc45ceb18bb50d`.

| Rebuilt unit | Input SHA-256 | Output SHA-256 |
|---|---|---|
| `video_console.o` | `66b79b41dd044fe3cdbe5fcf510bccc6bbdf8c8b2b5dfcb440df18939510b264` | `9394e2950c80eca52f359b41a8b6276e82caf3afbd604aff75e1abd241b6cf02` |
| `kern_exec.o` | `7f7b3104afcf7fd7040ee9107c334f83e3912273079d79f2341a48f1540d8560` | `2c9ecfb9c487252fbab5d34faa5550df8daffce1e474e1852fd3de1e84774db0` |

The selected `video_console.o` is the identical original object listed in the r49 link filelist, before the r52 fill insertion; it is reused directly rather than recompiled. Its exact path is in the candidate manifest. Thus the comparison is identity with that baseline, not a separately reproduced compile.

The r61 five artifact hashes were checked before and after; its boot SHA-256 remains `6f13c3b5ca3139309019ff966214a1f13acaa819bb8b928a42998452ffde015b`. ADT is byte-identical, SHA-256 `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457`. Both linked Mach-O files have zero undefined symbols including weak according to `llvm-nm` and symbol table checks. The payload changes only kernel and `unixnu.toml`; call sites and report formats were checked. The output manifest records full input/output hashes.

## Risk and rollback

Secondary startup, redistributor and IPI delivery, scheduling, and inherited diagnostic concurrency are unverified; the additional observation itself changes output and timing. The candidate has not been independently reviewed or tested. Rollback is the unchanged r58 `out/ufs-sm8250-rxpid-20261123-r58/boot.img`; any device operation requires separate authorization.
