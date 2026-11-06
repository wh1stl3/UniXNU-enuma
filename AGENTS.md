# AGENTS.md — UniXNU-enuma

长期规则见共享治理文档：`D:/Code/PortingiOS/docs/governance-2026-11-06.md`。本文件只写 enuma 专属约定。

## 目标
小米平板 5 Pro 5G（enuma / SM8250-AC）通过 UniXNU 运行 iPadOS 17.7.11（donor: iPad7,1 / 21H461，xnu-10063，4K）——D-002 既定路线。

## 基线
- UniXNU 基座：`D:/Code/PortingiOS/UniXNU`（最新上游 main，HEAD e2fdae4）。
- 本仓由旧 UniXNU-enuma 重建（2026-11-06），board.toml/configs/scripts 自备份恢复。

## 硬边界
- 设备写入动作须用户当轮明确授权；ECID/序列号不入库；Apple 派生产物不上传 GitHub。

## 关联文档
- AI 分工与调度：`../../docs/ai-orchestration-2026-11-06.md`。
- 双机通用治理（本仓 AGENTS 引用同一份）：`../../docs/governance-2026-11-06.md`。
