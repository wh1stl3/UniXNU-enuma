# AGENTS.md — UniXNU-enuma

长期规则见共享治理文档：`D:/Code/PortingiOS/docs/governance-2026-11-06.md`（12 条，v2 对齐官方 format 2）。本文件只写 enuma 专属约定。

## 目标
小米平板 5 Pro 5G（enuma / **SM8250-AC**，骁龙 870）通过 UniXNU 运行 iPadOS 17.7.11（donor: iPad7,1 / 21H461，xnu-10063，4K）——D-002 既定路线。
官方设备索引把 enuma 归档为 `SM8250`（系列名）；本仓与 board.toml 一律写 `SM8250-AC`。

## 基线
- 活动基座：`D:/Code/PortingiOS/UniXNU`，固定 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`；只读，不随上游HEAD自动换pin。
- **已是官方 format 2**：`schema_version = 2`、`feeds.toml`（钉 `FFT-infra/UniXNU-sm8250-common@166235ec…`）、`dts/enuma.dts`、`configs/enuma_defconfig`、`patches/xnu/series`、`porting.toml`、`scripts/package.sh`、`.github/workflows/*`。
- SoC 共享仓 `../UniXNU-sm8250-common` 是社区 `FFT-infra/UniXNU-sm8250-common`（kona：DTSI + 两条 SMP/拓扑补丁 + A650 GMU kit）的检出；origin 指本仓 fork，upstream 指 FFT-infra。同 SoC 的 alioth 已用它跑到桌面；**AC 特有的 CPU/GPU 频率档、电源票与热区仍须本板提供**。
- 当前进度：固件已可构建，22r已实机报告AMFI No PMGR panic；旧21r/22r claim已消耗，禁止访问/删除/重放。冻结23r prelink `bf9f7e12bb05dc3a09f1a732fbcdb83d7729f6378f65ea7fbe77646514edc072` 的PMGR静态deep、observer人工及完整包装门禁PASS，主机QEMU工具PASS不代表PMGR runtime。原mode1在hook前AppleImage4异常，fixture两次平台拒绝无执行结果，不继续或绕过该任务。主控转述deep必要性裁定允许首次有限受控诊断准备，不要求mode1/3/fault动态先通过；这些项目仍未验证，mode2 stage23及AMFI越过原失败是首次诊断目标。新ignored `.cache/run-cp23r-once.ps1` 仅离线准备（self-checked），当前无23r授权；主控最终确认及用户新的当轮授权后才可执行，提前录屏，失败停止不自动重试/换参/continue，不刷userdata。见 `docs/pmgr-23r-diagnostic.md`。`dram_size=8 GiB` 及既有EL0证据不证明所有权、完整exec/syscall或稳定用户态；各区等级和阶段7验收不提升。24r observation-only（默认0 `NATIVE_UFS_OBSERVATION_ONLY`，为1须 diagnostic 与 external-provider 均1；入口仅 `native-ufs-observe-reuse=1` 且 root/probe 缺席）已在临时 ShengUfs 工作树实现并 self-checked 官方矩阵（o=1 archive `82811fc3…`、215 undefined、旧7缺符号零引用；组件guard 54/624、host 633/639）；deep 判仅证据/措辞 CHANGES REQUIRED，源码 completion 正确、无须改源码。实现只在临时工作树与本地 `.cache`，未进本仓源码、未提交/推送远端；external=1 两格仅符号检查、o=1 无动态覆盖、native/prelink/final ABI 均未做，无24r设备授权。

## 目录约定（官方布局）
运行态摘要观察器补充（2026-11-10）：23r冻结hash上的五项人工静态门禁PASS WITH CONDITIONS，20函数native/prelink指令一致；observer补丁仍 `a3c12c0f1d210bb2481ba83fa28023c91fad27ac346f992d7613de7e8ed12109`。自动audit仍exit2/manual-review-required，不改JSON伪装PASS。完整23r包装独立PASS（包内唯一pmgr2/kernel及boot→payload绑定）；205 imports仅符号存在性，必要生命周期thunk另经deep回读。manifest历史release_allowed=false不改；有限诊断准备许可不等于runtime/显示/实机验收，也不等于当轮设备授权。资料见 `docs/pmgr-23r-package.md`、`docs/pmgr-23r-diagnostic.md`。

UFS 24r 补充（2026-11-11）：观察形态变体、矩阵与 patch 只在临时 ShengUfs 工作树及本地 `.cache/ufs-observation-only-20261111/`，本仓无源码改动，不得称已集成/已提交。external=1 与 observation 格只有符号检查，无函数体等价；o=1 无动态覆盖；native/prelink/link-map/payload/boot 及 final ABI、personality/PMGR-observer 重绑定均未做，无24r设备授权。

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
