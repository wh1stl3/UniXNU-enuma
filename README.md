# UniXNU-enuma

Xiaomi Pad 5 Pro 5G（enuma，SM8250-AC / 骁龙 870）的 UniXNU 设备仓。目标：iPadOS 17.7.11 / 21H461，donor 身份 iPad7,1（J120AP）。

**当前阶段**：官方 `porting/steps` 第 5 步**已完成**（固件可构建 + 设备仓 preflight）；第 7 步 bring-up 阶段 1–2 已实机到达 UniXNU 内置菜单。**里程碑（2026-11-08，用户当轮授权并录像）**：`fastboot boot` `stage12-simplefb/boot.img`（sha256 `ef782289…6dca`，固件源码 `1070b371`）走完 SEC→DXE→BDS→UniXNU 菜单（音量键移动、电源键确认、Tools→Advanced Logger 二维码轮播可用）；ramoops 日志通道（`0xB0000000`/4 MiB）读回固件日志，判读见 `docs/firmware-log-capture.md`；日志与视频留本地 `.cache/media`（不入库）。原厂 `vendor_boot_a.img` 的 4 个 DTB 候选与 pre-root 实机 FDT 已按字节取证并记录哈希（`scripts/enuma_firmware_inputs.py`，来源见 `proprietary-files.txt`）：vendor_boot 只有 SoC 基座 DTB（board-id `0x00`），enuma 板级 DTB 由 dtbo_a entry 07（board-id `0x2e`）叠加得 `.cache/firmware/dtb/sm8250-xiaomi-enuma.dtb`（候选 DTB 已被 ABL 接受，但内容未核）。`uefi-enuma` 已按 enuma 实机 XBL 的扁平厂商模块路径接入，`[uefi_fd]` 0x9FC00000/0x300000；厂商 `Binaries/enuma` 与板级 DTB 仍走 `.cache/firmware/`（不入库）。2026-11-08 修复并已做 reviewer 审查（Sol，INSUFFICIENT EVIDENCE→修复→待复核）：复位槽位改回通用 ResetSystemRuntimeDxe、`EnableUfsIOC` 与 enuma cfg 一致；「写入分级」规则已修订（允许厂商固件正常启动的附带写入，不偏离 stock）。

**里程碑（2026-11-09，用户当轮授权并录像）**：bring-up 阶段 3 首次上机通过——`fastboot boot` `out/enuma/stage3/boot.img`（sha256 `141eaa7e…b7bb`，203505664 B，header v1，ramdisk=192 MiB FAT payload，固件源码 `1070b371`）返回 OKAY（推送 4.5 s，未刷任何分区）；ramoops 读回 `UNIXNURAMDISK: device tree at 0xA3DFE000`（980302 B）与 `UNIXNURAMDISK: initrd block device 0xA3FFF000 size 0xC000000 Success`，随后 `[Bds]Booting UniXNU` → UniXNU.efi 加载 → FAT 挂载，无 `no initrd in /chosen`、无 ASSERT、无 NO WINDOW（SPSS/SMBIOS 的 start failed 为已知无害项）。屏幕：菜单出现，**默认项 UniXNU 倒计时 3 s 走完后调用 DarwinBoot，占位内核（32 B）预期 Load Error**（无内核交接）；Tools 项因显示尺寸不可见但可选中，Advanced Logger 导出可用。ABL 已确认把 initrd 写入 `/chosen`（此前未证实项）；ramdisk 实际范围 0xA3FFF000–0xAFFFF000 整块在 Kernel 预留区 0xA0000000/0x10000000 内，与固件 FD(0x9FC00000+0x300000)、DXE Heap2(0x93200000) 无重叠、距 ramoops(0xB0000000) 4 KiB；这 192 MiB 占去 256 MiB Kernel 预留区大部分，阶段 4 DarwinBoot 窗口/`owned_memory_size` 须据此重估（待阶段 4 实机）。证据细节见 `porting.toml`（packaging/firmware/memory/configuration 四区 device 证据）。

**下一步**：第 7 步 bring-up 阶段 4（DarwinBoot：Kernel 预留与 `owned_memory_size` 窗口重估）；阶段 5 起才需要真内核/prelink。

2026-11-08 恢复厂商模块：此前误判为「enuma XBL 无」的 19 个模块（SdccDxe/FeatureEnablerDxe/PILProxyDxe/PILDxe/SPSSDxe/AdcDxe/UsbPwrCtrlDxe/QcomChargerDxeLA/ChargerExDxe/UsbfnDwc3Dxe/XhciPciEmulation/XhciDxe/UsbMsdDxe/UsbDeviceDxe/UsbConfigDxe/UsbInitDxe/ButtonsDxe/TsensDxe/LimitsDxe）实为 enuma 自己 xbl_a 内原件（xbl_a sha256 `7ac67cbf…565057`），只是 `extract_enuma_xbl.py` 的 SELECT 白名单遗漏；已按原件导入恢复，厂商模块总数 52（含 ButtonsDxe 音量/电源键与完整 USB/SDCC/充电栈）。构建通过（FD=3145728 B，self-checked，仅 compiles，无设备证据）；ButtonsDxe 的 DEPEX 能否满足须实机观察。

## 三仓关系

| 仓 | 作用 | 位置 |
| --- | --- | --- |
| `UniXNU-enuma`（本仓） | 板级连接、组件选择、镜像与分区策略、记录 | 本目录 |
| `UniXNU-sm8250-common` | kona（SM8250/SM8250-AC）共享资源、DTSI、SoC 配置与补丁 | `../UniXNU-sm8250-common`（`FFT-infra/UniXNU-sm8250-common` 的检出：origin 为本仓 fork，upstream 指 FFT-infra；`feeds.toml` 钉 `166235ec…`，alioth 实机用的是 `a6e7e36c…`） |
| `uefi-enuma` | Mu-Silicium 固件（`enumaPkg` + `Resources/Configs/enuma.toml`，已可构建；厂商 `Binaries/enuma` 与板级 DTB 走 `.cache/firmware/` 不入库） | `../uefi-enuma` |
| `UniXNU`（基座） | 解析器、package、DarwinBoot、组件 | `../../UniXNU` |

注意：官方设备索引把 enuma 归档为 `SM8250`（系列名），本仓一律写 `SM8250-AC`。alioth（Redmi K40）同为 SM8250-AC（骁龙 870，非 865），其板级 CPU/GPU 频率票不移植到 enuma。

## 前置条件

- 基座检出：`D:/Code/PortingiOS/UniXNU`（`[package] unixnu` 指向它）。
- Python 3.11+、git、`dtc`、`mtools`；内核与 payload 在 Linux/WSL 构建（`scripts/linux/setup-toolchain.py`）。
- `uefi-enuma` 的 `Platforms/Xiaomi/enumaPkg` 与 `Resources/Configs/enuma.toml`（派生自同 SoC 的 pipaPkg）已按 enuma 实机 XBL 接入并可构建；厂商 `Binaries/enuma` 与板级 DTB 走 `.cache/firmware/`（不入库），`[uefi_fd]` 0x9FC00000/0x300000；`scripts/enuma_firmware_preflight.py` 在构建前检查这些输入。
- `scripts/enuma_firmware_inputs.py`（WSL Python 3.11 + `dtc`）用于从只读备份按需单文件取用、校验哈希并把 `vendor_boot` v3 的 DTB 候选做结构化边界解析；原始镜像只留在 Git 忽略的 `.cache/firmware/`，不入库。

## 固件输入取证与第 6 步候选（预备，未选择任何组件）

`scripts/enuma_firmware_inputs.py` 已从备份（`backup-manifest-2026-11-06.md` §E）单文件取用并校验：

- `vendor_boot_a.img`：header v3，page 4096、ramdisk 2230、dtb 1613832 @ offset 8192；结构化边界解析得 **4 个 DTB**（kona v1/v2/v2.1 SoC 基座，msm-id `0x164` 子类型 `0x10000/0x20000/0x20001`，board-id 全 `0x00`；外加 1 个 173 字节 MP_DATA），全部通过 `dtc` 校验。
- `fdt.stdout`（pre-root 实机 FDT）：model `xiaomi enuma`、msm-id `0x164/0x20001`、board-id `0x2e`，与 kona v2.1 基座 msm-id 一致。**board-id `0x2e` 不在任何 vendor_boot 候选内**，故板级 DTB 须来自运行时 overlay（实机 FDT）或板级 DTS，不能直接选用 vendor_boot 内任一 DTB。

按官方 step 6 依赖序的候选矩阵（`board.toml [components] include` 仍只有基线 5 项，未选择任何驱动）：

| 依赖序 | 区域 | 候选方向 | 阻塞输入 |
| --- | --- | --- | --- |
| 1 | 平台与内存 | SoC 共享层 + 板级内存/保留区 | 实测 UEFI 内存图 / `[payload] dram_size` |
| 2 | 存储 | ShengUfs | UFS 寄存器/时钟/SMMU、GPT 几何 |
| 3 | 显示与亮度 | GopFramebuffer | 面板/背光/DSI 证据 |
| 4 | 输入 | ShengHidInput / ShengNovatekTouch | 触控/按键证据 |
| 5 | GPU | Adreno A650（SoC 共享 A650 GMU kit） | enuma GPU OPP/电源票 |
| 6 | Wi-Fi | 待定（enuma 为 QCA6390） | Wi-Fi 寄存器/固件 |
| 7 | DSP/音频/电源 | 待定 | 电源票/热区 |

以上仅记录候选，未改 `[components]`、未选择任何新组件。

## 阶段 3 就绪度分析（kernel/package/payload）

第 7 步 bring-up 阶段 3 首次需要的输入（逐项，缺一不可）：

| 位置 | 内容 | 现状 |
| --- | --- | --- |
| OS profile 补丁 | `ipados-17.7.11-21H461` 的 `patches/xnu/series` 补丁与 TODO（`early_security_init`、`text_fixups`、`product-id`、`artwork-device-subtype`）清点 | 待读 `UniXNU/docs/zh/building` 与 `concepts/payload` 后清点 |
| `[payload] dram_size` | 实机 `/memory` 或 SMEM 取证（RamManagerDxe 映射 `0x80000000-0x280000000` = 8 GiB；已写入 `0x200000000`，2026-11-09 阶段 3 上机通过 ABL 启动，但该单段 span 非连续可分配内存证明） | 已写入，阶段 3 上机通过 |
| `[payload] kernel_args` | `native-ufs-root=1`（路线 B，见 `../../docs/launch-route-2026-11-06.md` §4） | 未加 |
| `[userdata]` 几何 | `first_lba`/`last_lba`/`lba_bytes`（本机 GPT 的 userdata 条目；已有只读取证值，未写入 board.toml） | 未写入 |
| `[payload.adt] root_match_volume_uuid` | 构建 userdata 后取到的 APFS 卷 UUID | 占位 |
| 存储 ABI | 所选 kernelcache + `storage-abi/interface-audit.json` | 未准备 |

以上为第 7 步起的第一批输入清单；`[userdata]` 刷写与持久化验证仍在 bring-up 前五阶段之后（路线 B，须用户当轮授权）。

## 构建

在基座检出目录执行：

```sh
./unixnu defconfig enuma_defconfig -D ../enuma/UniXNU-enuma
./unixnu fetch -D ../enuma/UniXNU-enuma
./unixnu status --json -D ../enuma/UniXNU-enuma
./unixnu tree -D ../enuma/UniXNU-enuma
```

仅在开发共享层的本地改动时，在本仓 `local.toml` 写入（常规构建使用 feeds/lock 的远端 pin）：

```toml
[[source]]
kind = "soc"
name = "sm8250"
local = "../UniXNU-sm8250-common"
```

或使用设备打包脚本：

```sh
scripts/package.sh --check --os ipados-17.7.11-21H461
scripts/package.sh --os ipados-17.7.11-21H461 --uefi ../uefi-enuma
```

## 记录

`porting.toml` 是唯一权威记录（14 个区域）。改动代码后同步对应区域的 findings/evidence，并运行：

```sh
cd ../../UniXNU
python3 scripts/porting-record.py check --device ../enuma/UniXNU-enuma --base origin/feat/step3-format2
```

## 文档

- 固件日志抓取（ramoops）：[`docs/firmware-log-capture.md`](docs/firmware-log-capture.md)
- 移植流程：<https://unixnu.com/zh/porting/steps>
- SoC 支持：<https://unixnu.com/zh/porting/soc-support>
- 设备仓规范：<https://unixnu.com/zh/porting/device-repository>
- 设备树：<https://unixnu.com/zh/porting/device-tree>
- 启动验证：<https://unixnu.com/zh/porting/bring-up>

## 约定

治理规则见 `../../docs/governance-2026-11-06.md`（12 条）。Apple 派生产物只留本地 `out/`，不上传 GitHub；ECID 等设备种子只经命令行或 Git 忽略的配置传入。`scripts/` 下的历史审计工具产生于 format 1 布局，其中部分引用已不存在的 `firmware/`、`diagnostics/` 目录，接入前先核对。
