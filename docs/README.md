# 文档入口

STATUS.md是当前唯一状态；HANDOFF.md是可直接接手的快照；AGENTS.md记录持久规则。DECISIONS.md/WORKLOG.md按时序保留决策和历史，NEED-REVIEW.md顶部汇总当前审核状态并保留批准边界。PENDING-HUMAN.md/NEED-HUMAN.md仅记录当前人的待办或现场需求。

2026-10-24当前对账：最近实测7dc3bf1 step12已无按键受控返回Android/root/原摘要通过，实测里程碑6f07283已推送；当前源码为固件c73eb6e，62项源锁匹配，新源码step12/step13均待重建和审计。4db旧对照仅离线构建资格通过，未上机，不是新源码构建证明。R-005 preparing/pending，尚未请求像素批准、未写屏、未进入XNU。

下一实机前须将全部当前文档对齐、提交并推送，再执行身份/备份/恢复/候选门禁。operations/保存各阶段当时的事实，历史“未执行/待恢复”不等于当前状态。reports/区分静态、主机和实机证据；现有enuma-firmware-build.json/enuma-fd-audit.json/enuma-boot-payload.json对应4db历史离线对照，源锁对账以config/uefi-source.lock.json为准。out/保留不发布的镜像、备份、原始日志和标识。

固件仓README/docs/pixel-preview.md描述当前实现及限制；冻结导入docs/enuma-overlay.md保留原迁移摘要，不作当前进度。详见operations/2026-10-24-pixel-preview-proposal.md。
