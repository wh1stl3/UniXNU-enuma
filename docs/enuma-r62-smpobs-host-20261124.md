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

The inherited report also emits an `enuma-fbfill` line and other inherited diagnostics. Online count 2 supports a second online CPU, not proof of working interprocessor interrupts. No line, freeze or panic does not identify the cause.

The two IPI options are removed to avoid the SPI IPI configuration when board interrupt allocation is not established; the intended SGI alternative and delivery are not runtime verified. The unchanged ADT has only the two interrupt-controller properties found by the script; absence of device interrupt properties does not establish physical SPI occupancy or GIC capacity; see `docs/ipi-intid-conflict-20261124.md`.

## Character path and build evidence

Previously the disabled framebuffer fill parsed its boot argument on each call; now the first disabled parse marks it done and later calls return after the flag check. This is a source-level path comparison, not a measured timing or a claim that the inherited console locking is safe. When enabled, its existing behavior is retained.

WSL root `/home/wh1stl3/.local/bin/python3 scripts/build-enuma-r61-smp2.py --r62` completed. Output `out/ufs-sm8250-smpobs-20261124-r62/boot.img`: 169951232 bytes, SHA-256 `32a877a8b1bad892c3519fde29eb5c60514561d0a6030deb6b02c751c445925c`.

| Rebuilt unit | Input SHA-256 | Output SHA-256 |
|---|---|---|
| `video_console.o` | `66b79b41dd044fe3cdbe5fcf510bccc6bbdf8c8b2b5dfcb440df18939510b264` | `77a2bfc4f1f3946d0c009972d591d72186d8c3c5b5459c520818a5c6087baad6` |
| `kern_exec.o` | `7f7b3104afcf7fd7040ee9107c334f83e3912273079d79f2341a48f1540d8560` | `aa68bf35ebcd7c188c0aad08af9fed576c0a72db47f53c2faf1d64a564cf7a28` |

The r61 five artifact hashes were checked before and after; its boot SHA-256 remains `6f13c3b5ca3139309019ff966214a1f13acaa819bb8b928a42998452ffde015b`. ADT is byte-identical, SHA-256 `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457`. Both linked Mach-O files have zero undefined symbols including weak according to `llvm-nm` and symbol table checks. The payload changes only kernel and `unixnu.toml`; call sites and report formats were checked. The output manifest records full input/output hashes.

## Risk and rollback

Secondary startup, redistributor and IPI delivery, scheduling, and inherited diagnostic concurrency are unverified; the additional observation itself changes output and timing. The candidate has not been independently reviewed or tested. Rollback is the unchanged r58 `out/ufs-sm8250-rxpid-20261123-r58/boot.img`; any device operation requires separate authorization.
