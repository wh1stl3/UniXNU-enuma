# AGENTS.md — UniXNU-enuma

长期规则见 `D:/Code/PortingiOS/docs/context-brief.md`；路由见 `docs/routing.md`，决策见 `docs/decisions.md`。本文件只写 enuma 专属约定。

## 目标
小米平板 5 Pro 5G（enuma / **SM8250-AC**，骁龙 870）通过 UniXNU 运行 iPadOS 17.7.11（donor: iPad7,1 / 21H461，xnu-10063，4K）——D-002 既定路线。
官方设备索引把 enuma 归档为 `SM8250`（系列名）；本仓与 board.toml 一律写 `SM8250-AC`。

## 基线
- 活动基座：`D:/Code/PortingiOS/UniXNU`，固定 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`；只读，不随上游HEAD自动换pin。
- **已是官方 format 2**：`schema_version = 2`、`feeds.toml`（钉 `FFT-infra/UniXNU-sm8250-common@166235ec…`）、`dts/enuma.dts`、`configs/enuma_defconfig`、`patches/xnu/series`、`porting.toml`、`scripts/package.sh`、`.github/workflows/*`。
- SoC 共享仓 `../UniXNU-sm8250-common` 是社区 `FFT-infra/UniXNU-sm8250-common`（kona：DTSI + 两条 SMP/拓扑补丁 + A650 GMU kit）的检出；origin 指本仓 fork，upstream 指 FFT-infra。同 SoC 的 alioth 已用它跑到桌面；**AC 特有的 CPU/GPU 频率档、电源票与热区仍须本板提供**。
- 当前状态和阻塞见 `../AGENTS.md`、`README.md` 顶部进度块；21r–24r claim 已消耗，禁止访问/删除/重放。23r 单次观察及其静态门禁见 `docs/pmgr-23r-diagnostic.md`、`docs/pmgr-23r-package.md`；24r 历史过程见 `docs/ufs-24r-diagnostic.md`。这些历史门禁不是当前运行时或阶段验收。
- 2026-11-16 GOP 生产整包 r5 主机侧封存完成：`seal.py` + manifest 重建 + `audit.py --verify` 均 exit 0（429 项，五件产物哈希未变），`self-checked`、`release_allowed=false`，未部署未实机验证；证据 `out/enuma-gop-production-20261114-r5/`（`HANDOFF.md` 2026-11-16 更新块）与 `out/enuma-gop-r5-preseal-manifest-20261116/`，细节见 `README.md` 顶部。

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
- AI 分工与路由：`../../docs/routing.md`。
- 双机通用治理：`../../docs/context-brief.md`。
