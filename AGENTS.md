# AGENTS.md — UniXNU-enuma

长期规则见共享治理文档：`D:/Code/PortingiOS/docs/governance-2026-11-06.md`（12 条，v2 对齐官方 format 2）。本文件只写 enuma 专属约定。

## 目标
小米平板 5 Pro 5G（enuma / **SM8250-AC**，骁龙 870）通过 UniXNU 运行 iPadOS 17.7.11（donor: iPad7,1 / 21H461，xnu-10063，4K）——D-002 既定路线。
官方设备索引把 enuma 归档为 `SM8250`（系列名）；本仓与 board.toml 一律写 `SM8250-AC`。

## 基线
- 基座：`D:/Code/PortingiOS/UniXNU`（上游 main `e2fdae4` + 1 个本地 submodule pin 提交 `af9d099`：ArmCpu/XnuPrelink）。
- **已是官方 format 2**：`schema_version = 2`、`feeds.toml`（钉 `FFT-infra/UniXNU-sm8250-common@166235ec…`）、`dts/enuma.dts`、`configs/enuma_defconfig`、`patches/xnu/series`、`porting.toml`、`scripts/package.sh`、`.github/workflows/*`。
- SoC 共享仓 `../UniXNU-sm8250-common` 是社区 `FFT-infra/UniXNU-sm8250-common`（kona：DTSI + 两条 SMP/拓扑补丁 + A650 GMU kit）的检出；origin 指本仓 fork，upstream 指 FFT-infra。同 SoC 的 alioth 已用它跑到桌面；**AC 特有的 CPU/GPU 频率档、电源票与热区仍须本板提供**。
- 未完成：`[payload]` 的 `dram_size` 与 `[userdata]` LBA 缺实测；`uefi-enuma` 的 `enumaPkg`/`Resources/Configs/enuma.toml` 只有骨架（缺 `Binaries/enuma`、板级 DTB、真实 FD base/size）。

## 目录约定（官方布局）
- 板级文件：`board.toml`、`porting.toml`、`feeds.toml`、`configs/`、`dts/`、`patches/xnu/series`、`package/`、`scripts/package.sh`、`proprietary-files.txt`、`local.toml.example`。
- `drivers/`、`kits/` 不是设备仓目录——驱动与库来自组件仓，共享资源来自 `UniXNU-sm8250-common`；设备 `package/` 在构建树内成为 `kits/enuma`。
- 历史脚本（`scripts/audit_*.py` 等）产生于 format 1 布局，部分引用不存在的 `firmware/`、`diagnostics/`、`out/boot-journal-tests`，复用前先核对，不要当作官方接口。
- 旧的 `[diagnostics.persistent_log]`（R-002）已不在官方 schema 内，数值保留在 `board.toml` 注释与 `porting.toml` 诊断区域。

## 硬边界
- 设备写入动作须用户当轮明确授权；ECID/序列号不入库；Apple 派生产物不上传 GitHub。
- 不照抄 sheng/nuwa 板值（MMIO/IRQ/面板/电源/chip_id 均须 enuma 证据）；组件一律用规范 ID。

## 记录纪律
`porting.toml` 是唯一权威记录：改代码同步对应区域的 findings/evidence，并跑 `python3 scripts/porting-record.py check --device .`。

## 关联文档
- AI 分工与路由：`../../docs/ai-orchestration-2026-11-06.md`。
- 双机通用治理：`../../docs/governance-2026-11-06.md`。
