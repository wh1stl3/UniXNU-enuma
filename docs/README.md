# 文档入口

STATUS为当前唯一状态，HANDOFF为接手快照，AGENTS为持久规则；WORKLOG/DECISIONS及operations保留历史。

当前固件c73eb6e/62项源锁；step12/step13完整离线构建资格通过，单次R-005实测已无按键返回Android/root/原摘要。视频未确认白条，用户明确白点是键盘反光；账本consumed阻止重复执行。当前设备结果见STATUS及reports/enuma-r005-device.json。顶层build/FD/payload报告对应step13，成对摘要见enuma-pixel-preview-bundle.json；旧7dc3bf1实测为历史。

每笔新实机前对齐并提交推送全部当前文档，再即时核验身份/备份/恢复。当前仍无XNU运行证明。固件冻结导入文档为历史；像素范围见NEED-REVIEW R-005和operations/2026-10-24-r005-takeover.md。

R-005后续离线审计：五份固定Qualcomm SDE与elish/SM8250及保存enuma FDT已核对，形成现有映射内两读DSI时序使能计划；未实现新固件探针。见scripts/audit_display_activity_plan.py及operations/2026-10-24-display-activity-plan.md。
