# r63 SMP self-IPI host candidate — 2026-11-24

Status: self-checked, no device operation or independent verification. Baseline is clean r62 at device commit `f7836aa`, boot SHA-256 `e378b1055e26b7d9b743f1ea7f30d8d26bd3a89e48de54ee23428ae0f9c3d894`; not the superseded color-hook candidate. r63 changes only the boot argument: restore `armcpu-self-ipi=1`, do not enable `armcpu-spi-ipi=1`. Per the supplied deep reviewer conclusion, secondary `initCPU` sends its first self-IPI to let XNU clear `SIGPdisabled`. This is an intended mechanism, not a delivery observation.

The SGI path uses a software-generated interrupt for the self-IPI; SPI is a shared peripheral interrupt path and the separate SPI option is not enabled. Neither interrupt delivery nor hardware resource safety is established by this host build.

## Embedded boot argument readback

```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1 dk=0 sheng-smp=1 cpus=2 armcpu-diagnostics=1 enuma-bp=1 armcpu-self-ipi=1
```

The script compares the complete string with r62 plus exactly ` armcpu-self-ipi=1`, reads it from the payload extracted from `boot.img`, and compares every payload member: only `unixnu.toml` changes. Its SHA-256 is `447e4a06146d0250a93fa78e0792706bec4112607e8228ee457b7f0d7431ac93` → `c1c89624ed35670f5e5d112d1a01d4e07530799720ef4d448c735fca5286f2b8`. No compilation unit was modified or rebuilt.

## Observations and interpretation

Inherited report formats are `enuma-cpu: online=%u seen1=0x%llx step1=%u fail1=%u` and `enuma-cpu: mpidr1=0x%llx`. They report processor availability and secondary diagnostic state, not an IPI delivery receipt. `step1=7` alone does **not** prove IPI delivery. `online=2` alone does not prove interprocessor signalling.

| Observation | Interpretation |
|---|---|
| `online=2`, `step1=7`, `fail1=0` | Secondary startup markers reached; IPI delivery and subsequent cross-core work remain unproven. |
| `fail1` nonzero or earlier `step1` | Secondary startup did not follow the expected diagnostic path; use the actual recorded values, not an assumed cause. |
| Missing lines, freeze or panic | Inconclusive about delivery and cause; capture the actual last output. |

No `ipi1` is emitted: `tree/drivers/ArmCpu/ArmCpu.cpp:26,619,627,633` has `armcpu_ipi_interrupts`, one global volatile counter updated on interrupt paths, not a per-CPU receive counter. It cannot establish CPU1 reception and no counter or concurrency code is changed.

## Mechanical evidence

- Output `out/ufs-sm8250-smp3-20261124-r63/boot.img`: 169951232 bytes, SHA-256 `f94c738c9b04b8edaec46775c00bd99d239b4a72a1f2fcf2c46a709b096eaa64`.
- r62's five artifact hashes checked before and after; boot remains `e378b1055e26b7d9b743f1ea7f30d8d26bd3a89e48de54ee23428ae0f9c3d894`.
- Original r49 `video_console.o` selected in inherited link filelist: `9394e2950c80eca52f359b41a8b6276e82caf3afbd604aff75e1abd241b6cf02`, checked before and after. `kern_exec.o` remains `2c9ecfb9c487252fbab5d34faa5550df8daffce1e474e1852fd3de1e84774db0` per r62 manifest; no object is rebuilt.
- ADT byte-identical including embedded copy, SHA-256 `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457`. Native and prelinked Mach-O are unchanged; `llvm-nm -u` and symbol-table checks find zero undefined symbols including weak.
- Build: WSL root, `PATH=/home/wh1stl3/.local/bin:/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 /home/wh1stl3/.local/bin/python3 scripts/build-enuma-r63-smp3.py`. Base pinned at `693f5d9cae8a408dd18b39f3f9fdc4228c934241`; upstream HEAD checked at start, `8542980d02b4d2cc5c32ee3542de1760b2562aac`.

Secondary startup, SGI delivery, inherited diagnostic concurrency, and scheduling remain unverified; inherited diagnostics perturb timing. Rollback is the unchanged r58 `out/ufs-sm8250-rxpid-20261123-r58/boot.img`. No device operation is authorized by this host candidate.
