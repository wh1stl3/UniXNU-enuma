# UniXNU-enuma

以 UniXNU 为底座，适配小米平板 5 Pro 5G（enuma / SM8250 系列）运行 **iPadOS 17.7.11 / 21H461**，采用 XNU 10063.141.1、4 KiB 路线。

先读 [AGENTS.md](AGENTS.md)、[当前状态](docs/STATUS.md)、[决策](docs/DECISIONS.md)、[待审查事项](docs/NEED-REVIEW.md)。仓库和交接纪律继承 UniXNU-nuwa，板级参数与 iPhone donor 不继承。

设备仓通过 UniXNU 的 `-D` 接口接入。所有输出须显式指向本仓 `out/`；参考树只读。当前为 example 配置，不代表 iPadOS 已可启动。实机已覆盖SimpleFb安装返回、分层GOP元数据和只读MDP地址/格式探针；固定几何假设被受控拒绝，实际描述解码候选已完成离线资格、尚未实测。尚未写屏或进入XNU，精确步骤及限制以STATUS为准。

目录：`config/` 路线和来源锁；`configs/` 内核候选配置；`drivers/EnumaPlatform/` 板级支持代码；`firmware/` 固定提交的独立 UEFI 仓子模块；`scripts/` 审计和主机检查；`reports/` 可复现证据；`docs/` 五件套与操作记录。

复现命令与驱动差异见 [首轮报告](docs/operations/2026-10-22-offline-bringup.md)。audit_inputs.py 全量核对缓存 donor，plan_adt.py 只生成 JSON 计划，check_workspace.py 验证固定输入及上游配置接口，均不生成启动镜像。

Kona/GENI/UFS 接入来源见 [固件与驱动报告](docs/operations/2026-10-22-kona-platform.md)；最新固件与实机范围见 [当前状态](docs/STATUS.md) 和 [入口定位报告](docs/operations/2026-10-22-entry-checkpoints.md)。主机模型/AArch64 对象、固件执行和完整 IOKit/内核运行的结论分别记录。

R-001 已批准并配置 512 MiB；[内存交接报告](docs/operations/2026-10-22-owned-memory.md) 记录真实 DarwinBoot ADT 解析和窗口选择函数的主机检查。物理分配未观察；后续生成/可恢复启动已由 A-002 授权，新内存字段及验证标记仍需审查。

本机内存/GOP 来源与 33 个厂商驱动见[本机平台固件报告](docs/operations/2026-10-22-native-platform-firmware.md)。最新已测诊断镜像、重建差异和限制以 STATUS 为准；诊断门镜像会主动复位，只包含固件阶段。

公开远端：[wh1stl3/UniXNU-enuma](https://github.com/wh1stl3/UniXNU-enuma)。[macOS Actions](https://github.com/wh1stl3/UniXNU-enuma/actions/workflows/macos-xnu.yml) 手动选择 preflight 或 bootstrap；bootstrap 是关闭本板功能的通用 XNU 4 KiB 基线，不是 enuma 完整内核，不能刷机。构建日志、SDK/来源记录及基线产物保存为 Actions artifact；镜像、设备备份和凭据不进 Git。

已完成[官网144页路线核对](docs/operations/2026-10-22-official-docs-route-review.md)及[完整页面清单](docs/operations/2026-10-22-official-site-inventory.md)。首次通用bootstrap的历史缺符号失败已被后续成功链接取代；源平台内核CI39927966148已链接，仍不是enuma运行证据。官网新工具与本仓固定源码有版本差异，后续按独立审查接入真实静态库/预链接流程。

已[接入 UniXNU 主分支固定版本及21个模块](docs/operations/2026-10-22-upstream-integration.md)，保留 enuma 补丁与 boot v3，新增关闭 legacy 功能时的编译期引用修复。本地完整固件与主机回归通过；[macOS新版通用最终链接已通过](https://github.com/wh1stl3/UniXNU-enuma/actions/runs/39790786938)，[DXE队列定位](docs/operations/2026-10-22-dispatch-checkpoints.md)为历史阶段；当前实机范围见STATUS，元数据返回不等于可写屏。

固件已独立至 [wh1stl3/uefi-enuma](https://github.com/wh1stl3/uefi-enuma)，设备仓通过 `firmware/` 固定其提交；克隆后初始化子模块。`board.toml [firmware]` 与预检已接通，固件包装器实际调用官方 backend，完整构建/OEM/v3回归通过。复现、私有输入要求和 example 保护范围见[双仓接入说明](docs/operations/2026-10-22-uefi-repository.md)。

固件编译实现位于uefi-enuma/Resources/Scripts/build_enuma_firmware.py；本仓同名脚本为校验固定源锁的适配入口。文档职责与历史记录索引见[docs/README.md](docs/README.md)。
