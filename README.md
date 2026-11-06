# UniXNU-enuma

小米平板 5 Pro 5G（enuma / SM8250-AC）的 UniXNU 设备仓。目标：iPadOS 17.7.11（donor iPad7,1 / 21H461，xnu-10063，4K）。

## 当前进度（2026-11-06）
- 阶段：**仓库重建完成，未开始开发**（官方 steps 第 3 步（建设备仓）刚落地，需按 examples/device 模板补 dts/porting.toml 等新结构）。
- 已有：board.toml（IPSW pin 沿用 sheng 官方同 donor 值）、configs、scripts（ADT/审计工具）、AGENTS.md。
- 下一步：按官方 steps 核对 board.toml 与最新上游 schema 的键值差异。

## 约定
规则见 `../docs/governance-2026-11-06.md` 与 AGENTS.md。Apple 派生产物不上传本仓。
