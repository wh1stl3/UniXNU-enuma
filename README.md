# UniXNU-enuma

小米平板5 Pro 5G / SM8250-AC的iPadOS17.7.11移植。当前主线按用户D-170要求：准备尽可能完整的启动链，采集实际报错并逐轮修复；单点早停仅作必要备用。

已实际生成29组件的实验系统预链接，并固定同SoC [UniXNU-umi](https://github.com/reAAAq/UniXNU-umi/tree/3eb72578597d2ca16471b172d45eddc096a34a04)作为ADT、RAM载荷、PMGR/UFS和CPU显示复用源。已生成完整结构ADT和96MiB真实FAT，实际loader解析主机检查通过；v3只读RAM运输和13项同次报告已实现并完成构建/打包资格，运行时发现、root及可见错误通道仍待闭合，尚无进入XNU或iPadOS的实机证据。当前D-205：D-205，互补首拒绝分类源码/主机通过，完整构建进行中。当前没有S-011/S-012设备动作，两候选完整产物资格尚未完成；当前无人工或新增审批待办。新资格完成并落实全部文档推送、即时身份/备份/相机/恢复后才逐笔执行。 原始影音仅本地，S-010与旧失败图不重试；仍无真实GOP/XNU/iPadOS实机成功。

接手读[AGENTS](AGENTS.md)、[STATUS](docs/STATUS.md)、[HANDOFF](docs/HANDOFF.md)、[完整链路线](docs/operations/2026-10-25-full-boot-mainline.md)、[ADT/FAT进展](docs/operations/2026-10-25-full-adt-fat.md)、[boot v3运输](docs/operations/2026-10-25-boot-v3-payload-transport.md)、[S-001试启动](docs/operations/2026-10-25-system-transport-trial.md)、[S-002隔离方案](docs/operations/2026-10-25-display-thread-off.md)、[返回边界候选](docs/operations/2026-10-25-full-input-return-boundary.md)及[交接词](docs/2026-10-25-handoff-prompt.md)。所有内存/verified/设备恢复和破坏性分区门禁保持，源码pin不自动更新，参考仓只读，原始产物仅out/。

远端：[设备仓](https://github.com/wh1stl3/UniXNU-enuma)、[固件仓](https://github.com/wh1stl3/uefi-enuma)。
