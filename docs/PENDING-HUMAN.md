# PENDING-HUMAN

当前无待按键或在场操作。用户最新要求为 alioth/elish SimpleFb GOP 离线审计并暂不操作实机；审计已完成，没有设备查询、启动或模块加载，不自动续测。

最后实机记录为 R-002 第二次临时 Android 启动：FDT 保留32KiB、8页均reserved，启动完成/root/原分区摘要正常。本轮未重新查询，普通重启不保证继续保留，不能沿用旧样本做新回读。

SimpleFb所缺scanout参数、实现差异与未来实机G0–G6验收条件已写入 docs/operations/2026-10-23-simplefb-gop-offline-audit.md；这些是后续工作条件，不是已安排的人工按键待办。

2026-10-23 续进：离线marker模块及实际源码主机保护检查已通过，尚未推送/加载。保存scanout证据审计仍缺六项入口事实；需后续恢复设备工作范围后再观测，不是当前待按键事项，不自动续测。新交接见2026-10-23-log-reader-offline-followup.md。
