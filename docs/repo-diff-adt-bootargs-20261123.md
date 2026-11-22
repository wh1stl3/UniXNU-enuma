# 五仓 ADT、启动参数与用户态策略（2026-11-23）

状态：self-checked，未构建、未访问设备。A 为生成映像实物；C 为配置声明，非运行事实；U 为不可得，绝不等于不存在。仅 A 支持实际结论。五仓并非同一 OS 或同一运行机次。

## B — ADT / 设备树

enuma r40 独立 `out/ufs-sm8250-storegeom-20261123-r40/kernel.macho.adt` SHA-256 `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457`；`mtype -i <r40>/payload.img ::/EFI/UniXNU/Payloads/kernel.macho.adt` 提取后逐字节等于独立文件。复用 `scripts/compare-display-config-20261123.py:parse` 解析节点和属性。nuwa 取 `nuwa/worktree-display-dsp/out/nuwa-resume-display-scale-audit-20261122/actual-vendor-ramdisk.img` 同一成员，SHA-256 `ae717c64726d95b0edddf6a3316edc897f2e8a61ca9d3c9c29db2e72f649ec2d`。这不是当前 nuwa 默认构建。sheng `c8f92b20`、sirius `ac0c9004`、OPi5 `729ba25f` 无实际 ADT；配置无法证明最终无属性或值。敏感 ID、随机种子与根匹配原文不入库，记录长度与 hash。

### /chosen 逐键

列两个实际 ADT 的键与三个参考仓 board.toml 的显式 chosen 键的并集；其他层可能还有未列属性，因此不是五仓完整并集。`[U]` 是无最终 ADT，并非缺该键。

| 键 | enuma | sheng | nuwa | sirius | OPi5 |
|---|---|---|---|---|---|
| `amfi-only-platform-code` | [A] 有，LE32=1 | [U] 无最终 ADT，配置未查全 | [A] 有，LE32=1 | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `boot-manifest-hash` | [A] 无 | [U] 无最终 ADT，配置未查全 | [A] 有，48B，SHA256=ca3d19816979a0864aa6c0b312745255d9568303e5f88d3a11c89769d6d10c3c（值不公开） | [C] bytes `5fd2fc139b688ddf071aa815c1ea75d26bcd994a528cf02e365661eab5139ec7b580d63ca9319e218962a2236f23faca` | [U] 无最终 ADT，配置未查全 |
| `certificate-production-status` | [A] 有，LE32=0 | [U] 无最终 ADT，配置未查全 | [A] 有，LE32=0 | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `certificate-security-mode` | [A] 有，LE32=1 | [U] 无最终 ADT，配置未查全 | [A] 有，LE32=1 | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `chip-id` | [A] 有，LE32=2508971023 | [U] 无最终 ADT，配置未查全 | [A] 有，LE32=1254799579 | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `crypto-hash-method` | [A] 有，`sha2-384\x00` | [U] 无最终 ADT，配置未查全 | [A] 有，`sha2-384\x00` | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `darwinboot-efi-map` | [A] 无 | [U] 无最终 ADT，配置未查全 | [A] 无 | [C] bytes `0000000000000000000000000000000000000000… (len=1536)` | [U] 无最终 ADT，配置未查全 |
| `darwinboot-memory-size` | [A] 有，LE64=2852126720 | [U] 无最终 ADT，配置未查全 | [A] 有，LE64=5100273664 | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `display-scale` | [A] 有，LE32=2 | [U] 无最终 ADT，配置未查全 | [A] 有，LE32=3 | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `dram-base` | [A] 有，LE64=2147483648 | [U] 无最终 ADT，配置未查全 | [A] 有，LE64=37580963840 | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `dram-size` | [A] 有，LE64=8589934592 | [U] 无最终 ADT，配置未查全 | [A] 有，LE64=9663676416 | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `effective-production-status-ap` | [A] 有，LE32=0 | [U] 无最终 ADT，配置未查全 | [A] 有，LE32=0 | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `effective-security-mode-sep` | [A] 有，LE32=1 | [U] 无最终 ADT，配置未查全 | [A] 有，LE32=1 | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `ephemeral-storage` | [A] 有，LE32=1 | [U] 无最终 ADT，配置未查全 | [A] 无 | [C] u32 `1` | [U] 无最终 ADT，配置未查全 |
| `kernel-ctrr-to-be-enabled` | [A] 无 | [C] u32 `0` | [A] 无 | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `mix-n-match-prevention-status` | [A] 无 | [U] 无最终 ADT，配置未查全 | [A] 有，LE32=0 | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `name` | [A] 有，`chosen\x00` | [U] 无最终 ADT，配置未查全 | [A] 有，`chosen\x00` | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `nvram-bank-count` | [A] 有，LE32=1 | [U] 无最终 ADT，配置未查全 | [A] 有，LE32=1 | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `nvram-bank-size` | [A] 有，LE32=8192 | [U] 无最终 ADT，配置未查全 | [A] 有，LE32=8192 | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `nvram-current-bank` | [A] 有，LE32=0 | [U] 无最终 ADT，配置未查全 | [A] 有，LE32=0 | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `nvram-proxy-data` | [A] 有，8192B，SHA256=3c6e675b2f28d917c292a325131c6c868d6ddb82ed8a74fd90c607cdb7fb3525（值不公开） | [U] 无最终 ADT，配置未查全 | [A] 有，8192B，SHA256=3c6e675b2f28d917c292a325131c6c868d6ddb82ed8a74fd90c607cdb7fb3525（值不公开） | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `osenvironment` | [A] 有，`main\x00` | [U] 无最终 ADT，配置未查全 | [A] 有，`main\x00` | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `random-seed` | [A] 有，256B，SHA256=2dca9b315767f9259f11a0a55e9207fea2210f2751311beabf782d2d31444dac（值不公开） | [U] 无最终 ADT，配置未查全 | [A] 有，256B，SHA256=1c7e573e88e23dfa83ef8becdd8f897bfd922a8121ba9ccddc4df0d16ee1d559（值不公开） | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `root-matching` | [A] 有，171B，SHA256=175cfb81016b001f209fb8b35d6ef710c751af4f7b43e3d14fa8534698674963（值不公开） | [U] 无最终 ADT，配置未查全 | [A] 有，171B，SHA256=573b453c2217f68c5fdd692111b047141a1cb982f0700d5d93374e349306bc68（值不公开） | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `text-fixups` | [A] 有，232B，SHA256=7bc511880615f355787a3814bc5745d75f8294c2734c33460742d22f885c7c2f（值不公开） | [U] 无最终 ADT，配置未查全 | [A] 无 | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |
| `unique-chip-id` | [A] 有，8B，SHA256=c4599bdd67154a39432aec6a371e48c9976691cd02b9e48f54a81909591f6315（值不公开） | [U] 无最终 ADT，配置未查全 | [A] 有，8B，SHA256=70db26d0e599674e27974ae4c43c2fa7526335757e5a2fc9819387135fd56810（值不公开） | [U] 无最终 ADT，配置未查全 | [U] 无最终 ADT，配置未查全 |

本组差异 12 项（A 12 项：enuma/nuwa 两映像；C 4 项为显式配置线索而非最终差异；五仓总数未知）。

### 节点逐项

按路径名大小写不敏感搜索实际 ADT 属性所属节点；运行时创建的 IORegistry 节点不在此统计。

| 节点族 | enuma | sheng | nuwa | sirius | OPi5 |
|---|---|---|---|---|---|
| `arm-io` | [A] `/arm-io`, `/arm-io/intc`, `/arm-io/ufshc` | [U] 无实际 ADT | [A] `/arm-io`, `/arm-io/intc` | [U] 无实际 ADT | [U] 无实际 ADT |
| `display-subsystem` | [A] 无 | [U] 无实际 ADT | [A] 无 | [U] 无实际 ADT | [U] 无实际 ADT |
| `dart` | [A] 无 | [U] 无实际 ADT | [A] 无 | [U] 无实际 ADT | [U] 无实际 ADT |
| `iommu` | [A] 无 | [U] 无实际 ADT | [A] 无 | [U] 无实际 ADT | [U] 无实际 ADT |
| `aon` | [A] 无 | [U] 无实际 ADT | [A] 无 | [U] 无实际 ADT | [U] 无实际 ADT |
| `disp0` | [A] 无 | [U] 无实际 ADT | [A] 无 | [U] 无实际 ADT | [U] 无实际 ADT |
| `dsi0` | [A] 无 | [U] 无实际 ADT | [A] 无 | [U] 无实际 ADT | [U] 无实际 ADT |
| `gpio` | [A] 无 | [U] 无实际 ADT | [A] 无 | [U] 无实际 ADT | [U] 无实际 ADT |
| `i2c` | [A] 无 | [U] 无实际 ADT | [A] 无 | [U] 无实际 ADT | [U] 无实际 ADT |
| `spi` | [A] 无 | [U] 无实际 ADT | [A] 无 | [U] 无实际 ADT | [U] 无实际 ADT |
| `hid` | [A] 无 | [U] 无实际 ADT | [A] 无 | [U] 无实际 ADT | [U] 无实际 ADT |
| `digitizer` | [A] 无 | [U] 无实际 ADT | [A] 无 | [U] 无实际 ADT | [U] 无实际 ADT |
| `pmgr` | [A] 无 | [U] 无实际 ADT | [A] 无 | [U] 无实际 ADT | [U] 无实际 ADT |
| `clk` | [A] 无 | [U] 无实际 ADT | [A] 无 | [U] 无实际 ADT | [U] 无实际 ADT |
| `interrupt-controller` | [A] `/arm-io/intc` | [U] 无实际 ADT | [A] `/arm-io/intc` | [U] 无实际 ADT | [U] 无实际 ADT |

本组差异 1 项（A 1 项：两映像；C 0 项；五仓总数未知）。

## C — boot-args

A 表示映像 `unixnu.toml` 的 xnu entry 字符串（打包参数，不证明运行时覆盖）；C 表示 `board.toml` 指定数组，sheng 选明确的 iPadOS 17 override，sirius、OPi5 是默认配置。以下按完整 token 比较，不把不同值视为相同；无法断定参数实际生效。

### 各仓完整集合

- enuma [A]：`-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1`

- sheng [C]：`-v serial=3 debug=0x14e kt_fixed_zones=120 offline-legacy-register=1 offline-legacy-gop=1 offline-legacy-unit-scale=2 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 offline-hid-home=1 offline-hid-input=1 offline-legacy-phase=4 offline-mobile-graphics-client=1 offline-mobile-graphics-load=1 offline-apfs-load=1 boot-progress=2 -apfs_shared_datavolume offline-key-events=1 native-ufs-root=1 pmgr=2 disable-watchdogd=1 lite=1 boot-ui-focus4=SpringBoard smp=1 cpufreq=4 touch=4 aks=1 gpu-power=9 gpu-metal=1 fb-gpu=1 banner=0 gpu-dcvs=1 gpu-addon=1 armcpu-spi-ipi=1 -no_slto_panic ml-timeout-lock-panic-scale=40 touch-hid=1 data-persist=2 staged-apps=1 buttons=1 backlight=1 wifi=5 vsync=120`

- nuwa [A]：`-v serial=3 native-ufs-root=1 native-ufs-lun=0 nuwa-pmgr=2 rd=uuid boot-uuid=DADD93F8-DBBF-4B17-A1DF-0F11E64172F7 boot-progress=2 aks=1 disable-watchdogd=1 build-tag=nuwa-r35 boot-progress-scale=3 sheng-data-persist=2 sheng-log-reserve=1024 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-phase=4 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 nuwa-lite=1 nuwa-mg-reset=1`

- sirius [C]：`debug=0x14e kt_fixed_zones=120 ml-timeout-lock-panic-scale=40 -no_slto_panic boot-progress=2 sheng-smp=1 cpus=8 armcpu-self-ipi=1 armcpu-timer-intid=19 sheng-pmgr=2 sirius_usb=2 sirius_emmc_hs=3 sirius_emmc_win=1 launchdsuffix=release amfi_get_out_of_my_way=1 sirius-allow-unverified=1 sirius-data-write=1 sheng-disable-watchdogd=1 sheng-lite=1 sirius-skip-rootauth=1 offline-legacy-register=1 offline-legacy-gop=1 offline-legacy-unit-scale=2 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sirius-fb-wc=1 sirius-fb-cached=1 offline-legacy-phase=4 offline-mobile-graphics-client=1 offline-mobile-graphics-load=1 offline-apfs-load=1 sheng-vsync=60 sirius-cpufreq=1 offline-key-events=1 sheng-aks=1 sirius-spawn-log=1 sirius-touch=1 sirius-touch-hid=1 sheng-touch-hid=1 dk=0 sirius-skip-setup=1 sirius-gpu=2 validation_disables=0x10`

- OPi5 [C]：`-v serial=3 debug=0x10014e -enable_kprintf_spam nvme=4 offline-apfs-load=1 nvme-root-trust=1 emmc-systemos-union=1 emmc-data-mount=1 nvme-data-size=2048 nvme-data-persist=1 sheng-smp=1 armcpu-self-ipi=1 armcpu-mmio-sgi=0 cpumask=31 sched-slowcpus=240 wdt-kick=1800 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 rk3588-vop-direct=1 rk3588-vop-esmart=2 rk3588-vop-vp=2 rk3588-vop-fence=1 offline-legacy-unit-scale=2 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 offline-key-events=1 sheng-aks=1 sheng-vsync=60 opi5-hid=1 opi5-hid-input=1 sheng-touch-hid=1 opi5-usb=5 rk3588-dvfs=6 rk3588-gpu=0 evb10-ps=10 evb10-bt=SpringBoard mali=8 mali-metal=1 evb10-gpu-addon=1 mali-wallpaper-fit=1 mali-sched-wait=2`

### 五组独有与共有（按完整 token）

**仅 enuma [A]**：`rd=md0-ramblock`

**仅 sheng [C]**：`-apfs_shared_datavolume`, `armcpu-spi-ipi=1`, `backlight=1`, `banner=0`, `boot-ui-focus4=SpringBoard`, `buttons=1`, `cpufreq=4`, `data-persist=2`, `fb-gpu=1`, `gpu-addon=1`, `gpu-dcvs=1`, `gpu-metal=1`, `gpu-power=9`, `lite=1`, `offline-hid-home=1`, `offline-hid-input=1`, `smp=1`, `staged-apps=1`, `touch-hid=1`, `touch=4`, `vsync=120`, `wifi=5`

**仅 nuwa [A]**：`boot-progress-scale=3`, `boot-uuid=DADD93F8-DBBF-4B17-A1DF-0F11E64172F7`, `build-tag=nuwa-r35`, `native-ufs-lun=0`, `nuwa-lite=1`, `nuwa-mg-reset=1`, `nuwa-pmgr=2`, `rd=uuid`, `sheng-data-persist=2`, `sheng-log-reserve=1024`

**仅 sirius [C]**：`armcpu-timer-intid=19`, `cpus=8`, `dk=0`, `launchdsuffix=release`, `sirius-allow-unverified=1`, `sirius-cpufreq=1`, `sirius-data-write=1`, `sirius-fb-cached=1`, `sirius-fb-wc=1`, `sirius-gpu=2`, `sirius-skip-rootauth=1`, `sirius-skip-setup=1`, `sirius-spawn-log=1`, `sirius-touch-hid=1`, `sirius-touch=1`, `sirius_emmc_hs=3`, `sirius_emmc_win=1`, `sirius_usb=2`, `validation_disables=0x10`

**仅 OPi5 [C]**：`-enable_kprintf_spam`, `armcpu-mmio-sgi=0`, `cpumask=31`, `debug=0x10014e`, `emmc-data-mount=1`, `emmc-systemos-union=1`, `evb10-bt=SpringBoard`, `evb10-gpu-addon=1`, `evb10-ps=10`, `mali-metal=1`, `mali-sched-wait=2`, `mali-wallpaper-fit=1`, `mali=8`, `nvme-data-persist=1`, `nvme-data-size=2048`, `nvme-root-trust=1`, `nvme=4`, `opi5-hid-input=1`, `opi5-hid=1`, `opi5-usb=5`, `rk3588-dvfs=6`, `rk3588-gpu=0`, `rk3588-vop-direct=1`, `rk3588-vop-esmart=2`, `rk3588-vop-fence=1`, `rk3588-vop-vp=2`, `sched-slowcpus=240`, `wdt-kick=1800`

**五仓共有 [A/C]**：`offline-legacy-cpu-present=1`, `offline-legacy-gop=1`, `offline-legacy-phase=4`, `offline-legacy-pm=1`, `offline-legacy-register=1`, `offline-legacy-transfer=1`, `offline-legacy-validate=1`, `offline-mobile-graphics-load=1`

### 所有非共有 token（含部分共有，不遗漏）
- `-apfs_shared_datavolume` — sheng[C]；作用未查证。
- `-enable_kprintf_spam` — OPi5[C]；作用未查证。
- `-no_slto_panic` — sheng[C], sirius[C]；作用未查证。
- `-v` — enuma[A], sheng[C], nuwa[A], OPi5[C]；作用未查证。
- `aks=1` — sheng[C], nuwa[A]；作用未查证。
- `amfi_get_out_of_my_way=1` — enuma[A], sirius[C]；sirius board.toml: bring-up: let init exec from an unverified root。
- `armcpu-mmio-sgi=0` — OPi5[C]；作用未查证。
- `armcpu-self-ipi=1` — sirius[C], OPi5[C]；作用未查证。
- `armcpu-spi-ipi=1` — sheng[C]；作用未查证。
- `armcpu-timer-intid=19` — sirius[C]；sirius board.toml: SDM670/710 virtual timer is GIC PPI 3 (INTID 19), not the architectural PPI 27。
- `backlight=1` — sheng[C]；作用未查证。
- `banner=0` — sheng[C]；作用未查证。
- `boot-progress-scale=3` — nuwa[A]；作用未查证。
- `boot-progress=2` — sheng[C], nuwa[A], sirius[C]；sirius board.toml: draw the kernel console lines on the screen (the readable log)。
- `boot-ui-focus4=SpringBoard` — sheng[C]；作用未查证。
- `boot-uuid=DADD93F8-DBBF-4B17-A1DF-0F11E64172F7` — nuwa[A]；作用未查证。
- `build-tag=nuwa-r35` — nuwa[A]；作用未查证。
- `buttons=1` — sheng[C]；作用未查证。
- `cpufreq=4` — sheng[C]；作用未查证。
- `cpumask=31` — OPi5[C]；作用未查证。
- `cpus=8` — sirius[C]；作用未查证。
- `data-persist=2` — sheng[C]；作用未查证。
- `debug=0x10014e` — OPi5[C]；作用未查证。
- `debug=0x14e` — sheng[C], sirius[C]；作用未查证。
- `disable-watchdogd=1` — sheng[C], nuwa[A]；作用未查证。
- `dk=0` — sirius[C]；sirius board.toml: DriverKit off (gIODKDebug without kIODKEnable): dext personalities never match. With it on,。
- `emmc-data-mount=1` — OPi5[C]；作用未查证。
- `emmc-systemos-union=1` — OPi5[C]；作用未查证。
- `evb10-bt=SpringBoard` — OPi5[C]；作用未查证。
- `evb10-gpu-addon=1` — OPi5[C]；作用未查证。
- `evb10-ps=10` — OPi5[C]；作用未查证。
- `fb-gpu=1` — sheng[C]；作用未查证。
- `gpu-addon=1` — sheng[C]；作用未查证。
- `gpu-dcvs=1` — sheng[C]；作用未查证。
- `gpu-metal=1` — sheng[C]；作用未查证。
- `gpu-power=9` — sheng[C]；作用未查证。
- `kt_fixed_zones=120` — sheng[C], sirius[C]；作用未查证。
- `launchdsuffix=release` — sirius[C]；sirius board.toml: DEVELOPMENT: load /sbin/launchd directly and report its errno。
- `lite=1` — sheng[C]；作用未查证。
- `mali-metal=1` — OPi5[C]；作用未查证。
- `mali-sched-wait=2` — OPi5[C]；作用未查证。
- `mali-wallpaper-fit=1` — OPi5[C]；作用未查证。
- `mali=8` — OPi5[C]；作用未查证。
- `ml-timeout-lock-panic-scale=40` — sheng[C], sirius[C]；作用未查证。
- `native-ufs-lun=0` — nuwa[A]；作用未查证。
- `native-ufs-root=1` — enuma[A], sheng[C], nuwa[A]；作用未查证。
- `nuwa-lite=1` — nuwa[A]；作用未查证。
- `nuwa-mg-reset=1` — nuwa[A]；作用未查证。
- `nuwa-pmgr=2` — nuwa[A]；作用未查证。
- `nvme-data-persist=1` — OPi5[C]；作用未查证。
- `nvme-data-size=2048` — OPi5[C]；作用未查证。
- `nvme-root-trust=1` — OPi5[C]；作用未查证。
- `nvme=4` — OPi5[C]；作用未查证。
- `offline-apfs-load=1` — sheng[C], sirius[C], OPi5[C]；sirius board.toml: load APFS。
- `offline-hid-home=1` — sheng[C]；作用未查证。
- `offline-hid-input=1` — sheng[C]；作用未查证。
- `offline-key-events=1` — sheng[C], sirius[C], OPi5[C]；sirius board.toml: kits/sirius/KeyStoreProbe.cpp publishes the AppleKeyStoreState service。
- `offline-legacy-unit-scale=2` — sheng[C], sirius[C], OPi5[C]；sirius board.toml: 2x display unit scale for high DPI。
- `offline-mobile-graphics-client=1` — sheng[C], sirius[C]；sirius board.toml: support MobileGraphics client。
- `opi5-hid-input=1` — OPi5[C]；作用未查证。
- `opi5-hid=1` — OPi5[C]；作用未查证。
- `opi5-usb=5` — OPi5[C]；作用未查证。
- `pmgr=2` — enuma[A], sheng[C]；作用未查证。
- `rd=md0-ramblock` — enuma[A]；作用未查证。
- `rd=uuid` — nuwa[A]；作用未查证。
- `rk3588-dvfs=6` — OPi5[C]；作用未查证。
- `rk3588-gpu=0` — OPi5[C]；作用未查证。
- `rk3588-vop-direct=1` — OPi5[C]；作用未查证。
- `rk3588-vop-esmart=2` — OPi5[C]；作用未查证。
- `rk3588-vop-fence=1` — OPi5[C]；作用未查证。
- `rk3588-vop-vp=2` — OPi5[C]；作用未查证。
- `sched-slowcpus=240` — OPi5[C]；作用未查证。
- `serial=3` — enuma[A], sheng[C], nuwa[A], OPi5[C]；作用未查证。
- `sheng-aks=1` — enuma[A], sirius[C], OPi5[C]；sirius board.toml: its user client answers the state queries (no passcode, unlocked): with。
- `sheng-data-persist=2` — nuwa[A]；作用未查证。
- `sheng-disable-watchdogd=1` — enuma[A], sirius[C]；sirius board.toml: package/BootWatchdogPolicy.c disables com.apple.watchdogd before launchd: it traps。
- `sheng-lite=1` — enuma[A], sirius[C]；sirius board.toml: the same policy also disables the network/iCloud/photo daemons this phone has no use。
- `sheng-log-reserve=1024` — nuwa[A]；作用未查证。
- `sheng-pmgr=2` — enuma[A], sirius[C]；sirius board.toml: publish an ApplePMGRNub for the unchanged AMFI (kits/sirius/SiriusPmgr.cpp)。
- `sheng-smp=1` — sirius[C], OPi5[C]；sirius board.toml: ArmCpu claims every /cpus nub: without it AppleARMCPU (kernelcache) takes the secondary nubs and panics on the non-Apple tree。
- `sheng-touch-hid=1` — enuma[A], sirius[C], OPi5[C]；sirius board.toml: NativeHidInput: add the touch screen collection to that combined device。
- `sheng-vsync=60` — enuma[A], sirius[C], OPi5[C]；sirius board.toml: 60 Hz software vsync heartbeat。
- `sirius-allow-unverified=1` — sirius[C]；sirius board.toml: bring-up: NativeEmmc authorizes the SystemOS union mount (no owner policy)。
- `sirius-cpufreq=1` — sirius[C]；sirius board.toml: kits/sirius/sirius_cpufreq.c: both clusters to their highest non-boost level;。
- `sirius-data-write=1` — sirius[C]；sirius board.toml: NativeEmmc publishes the persistent Data container behind the root image in。
- `sirius-fb-cached=1` — sirius[C]；sirius board.toml: and read the write-combined source surface through a cacheable mapping,。
- `sirius-fb-wc=1` — sirius[C]；sirius board.toml: drivers/GopFramebuffer (board fork): map the scanout write-combined; uncached,。
- `sirius-gpu=2` — sirius[C]；sirius board.toml: package/sirius_gpu.c: Adreno 616 phases 1-2 (CX power, GMU SMMU context, GMU boot, HFI)。
- `sirius-skip-rootauth=1` — sirius[C]；sirius board.toml: the sealed-root answer needs the owner-root chain; see。
- `sirius-skip-setup=1` — sirius[C]；sirius board.toml: package/BootWatchdogPolicy.c: write Setup's done flags (purplebuddy) and SpringBoard's。
- `sirius-spawn-log=1` — sirius[C]；sirius board.toml: package/BootProgress.c: a SPAWN console line per exec and exit, with the second。
- `sirius-touch-hid=1` — sirius[C]；sirius board.toml: package/SiriusHidProbe.cpp: publish the touch screen (ShengHidInput) to iOS, as sheng's。
- `sirius-touch=1` — sirius[C]；sirius board.toml: package/sirius_touch.c: QUP1 SE1 I2C, FTS521 chip id, then the event FIFO。
- `sirius_emmc_hs=3` — sirius[C]；sirius board.toml: card clock up to 100 MHz (1 = 25, 2 = 50, 3 = 100), each step proven。
- `sirius_emmc_win=1` — sirius[C]；sirius board.toml: publish the SHNGROOT windows of [userdata] as block devices。
- `sirius_usb=2` — sirius[C]；sirius board.toml: CDC-ACM log console over DWC3 (patches/xnu/sirius-usb-console.patch)。
- `smp=1` — sheng[C]；作用未查证。
- `staged-apps=1` — sheng[C]；作用未查证。
- `touch-hid=1` — sheng[C]；作用未查证。
- `touch=4` — sheng[C]；作用未查证。
- `validation_disables=0x10` — sirius[C]；sirius board.toml: KF_STACKSHOT_OVRD: user stackshots return KERN_NOT_SUPPORTED. Watchdogs ask。
- `vsync=120` — sheng[C]；作用未查证。
- `wdt-kick=1800` — OPi5[C]；作用未查证。
- `wifi=5` — sheng[C]；作用未查证。

本组差异 104 项（A/C 混合：按五仓参数声明的 token 并集扣五仓共有；A-only 差异 22 项；C-only 不能独立定为运行时差异）。

## D — 用户态与策略

[C] 仅列源码声明与已识别配置；未观察完整链接闭包或运行态。缺少正向证据写 U，不将未搜索到等同无。

| 项目 | enuma | sheng | nuwa | sirius | OPi5 |
|---|---|---|---|---|---|
| entitlements 注入 | [U] 未完成闭包审计 | [U] 未完成闭包审计 | [U] 未完成闭包审计 | [U] 未完成闭包审计 | [U] 未完成闭包审计 |
| trust cache | [A] ADT memory-map TrustCache | [C] board payload.runtime trust_components | [A] ADT memory-map TrustCache | [C] board.toml:96-99 原始模块 bundle | [C] board.toml:82 两项 pin |
| dyld shared cache | [A] text-fixups 声明三个 dyld shared cache 修补；执行结果未知 | [C] macOS 27 override 有 fixup；17 不可据此外推 | [U] 未完成闭包审计 | [C] board.toml:113-118 多项 fixup | [U] 未完成闭包审计 |
| amfi_get_out_of_my_way | [A] r40 参数 =1 | [C] 17 参数数组未列 | [A] 候选参数未列 | [C] board.toml:136 =1 | [C] 默认参数数组未列 |
| developer mode 强制 | [U] 未完成闭包审计 | [U] 未完成闭包审计 | [U] 未完成闭包审计 | [U] 未完成闭包审计 | [U] 未完成闭包审计 |
| NoAccessPolicy / NoContract | [C] UFS 准入默认拒绝，见 enuma AGENTS.md；非 IOKit open 策略 | [U] 未完成闭包审计 | [U] 未完成闭包审计 | [U] 未完成闭包审计 | [U] 未完成闭包审计 |
| offline-mobile-graphics-client | [A] r40 参数未列，默认值未知 | [C] 17 参数 =1 | [A] 候选参数未列，默认值未知 | [C] board.toml:158 =1 | [C] 默认数组未列，默认值未知 |
| 用户态二进制替换或 patch | [A] ADT 声明三个 dyld cache fixup 与一个 BTAudioHALPlugin fixup；应用结果未知 | [C] macOS override 有 QuartzCore fixup，17 未确认 | [U] 未完成闭包审计 | [C] board.toml:113-118 dyld cache fixups | [U] 未完成闭包审计 |
| 专为 bb/SpringBoard 打开 IOKit 放宽 MAC/sandbox/AMFI | [U] 未完成闭包审计 | [U] 未完成闭包审计 | [U] 未完成闭包审计 | [U] 未完成闭包审计 | [U] 未完成闭包审计 |


sirius `board.toml:136` 原文：`"amfi_get_out_of_my_way=1", # bring-up: let init exec from an unverified root`。这是未验证根的 init exec 声明，不是为 backboardd/SpringBoard 打开 IOKit 而放宽检查的证据。enuma r40 参数同样有此项；不能将其出现解释成观察到的 sandbox 行为。`NoAccessPolicy`/`NoContract` 是 UFS 资源准入，不能混同 IOKit 用户客户端策略。

enuma r40 [A] `/chosen:text-fixups` 四项目标分别是 `dyld_shared_cache_arm64.15`、`dyld_shared_cache_arm64.13` 两处及 `BTAudioHALPlugin` 一处；没有显示针对 libSystem、launchd 或 backboardd 本身的条目，不代表这些二进制从未被其他途径修改。nuwa [A] `/chosen:text-fixups` 缺失，不代表没有其他注入路径。

本组差异未知（A 已确认的实际参数差异 1 项：`amfi_get_out_of_my_way=1` 在 enuma 存在而 nuwa 候选未列；C 可见线索 2 项：sirius fixup、graphics-client 显式配置；不代表完整差异数）。

## 材料边界

sheng、sirius、OPi5 需提供对应确切构建的最终 ADT 和启动包，才能升级 [A]；需补齐五仓用户态二进制替换、entitlement、MAC/sandbox/AMFI 全部输入与实际运行日志才能回答 D 的否定项。配置 [C] 只能作线索，不能作运行结论。当前两份实际 ADT 的差异不证明因果。
