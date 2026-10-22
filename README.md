# UniXNU-enuma

以 UniXNU 为底座，适配小米平板 5 Pro 5G（enuma / SM8250 系列）运行 **iPadOS 17.7.11 / 21H461**，采用 XNU 10063.141.1、4 KiB 路线。

先读 [AGENTS.md](AGENTS.md)、[当前状态](docs/STATUS.md)、[决策](docs/DECISIONS.md)、[待审查事项](docs/NEED-REVIEW.md)。仓库和交接纪律继承 UniXNU-nuwa，板级参数与 iPhone donor 不继承。

设备仓通过 UniXNU 的 `-D` 接口接入。所有输出须显式指向本仓 `out/`；参考树只读。当前为 example 配置，不代表已有可启动镜像。固件需要单独的 uefi-enuma 适配，禁止把 sheng 固件直接用于 enuma。

目录：`config/` 路线和来源锁；`configs/` 内核候选配置；`scripts/` 只读审计；`reports/` 可复现证据；`docs/` 五件套与操作记录。

复现命令与驱动差异见 [首轮报告](docs/operations/2026-10-22-offline-bringup.md)。audit_inputs.py 全量核对缓存 donor，plan_adt.py 只生成 JSON 计划，check_workspace.py 验证固定输入及上游配置接口，均不生成启动镜像。
