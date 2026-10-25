# UniXNU-enuma

小米平板5 Pro 5G / SM8250-AC的iPadOS17.7.11移植。当前主线按用户D-170要求：准备尽可能完整的启动链，采集实际报错并逐轮修复；单点早停仅作必要备用。

已实际生成29组件的实验系统预链接，并固定同SoC [UniXNU-umi](https://github.com/reAAAq/UniXNU-umi/tree/3eb72578597d2ca16471b172d45eddc096a34a04)作为ADT、RAM载荷、PMGR/UFS和CPU显示复用源。已生成完整结构ADT和96MiB真实FAT，实际loader解析主机检查通过；v3只读RAM运输和13项同次报告已实现并完成构建/打包资格，运行时发现、root及可见错误通道仍待闭合，尚无进入XNU或iPadOS的实机证据。当前D-214：S-013/S-014互补时序支持首样本Enable门禁Reason5，后续稳定性按该路径未执行；两笔Android/root/A槽/解锁/原分区与备份独立核验通过，均consumed。下一步独立验证原生双路计数推进，不放宽GOP准入。 原始影音仅本地，仍无真实GOP/XNU/iPadOS实机成功。 新只读发现原生ramoops与umi布局相合，优先审日志链；未修改映射或写入。已对账其他显示/日志路线，详见[路线账本](docs/operations/2026-10-25-display-log-route-ledger.md)。

接手读[AGENTS](AGENTS.md)、[STATUS](docs/STATUS.md)、[HANDOFF](docs/HANDOFF.md)、[完整链路线](docs/operations/2026-10-25-full-boot-mainline.md)、[ADT/FAT进展](docs/operations/2026-10-25-full-adt-fat.md)、[boot v3运输](docs/operations/2026-10-25-boot-v3-payload-transport.md)、[S-001试启动](docs/operations/2026-10-25-system-transport-trial.md)、[S-002隔离方案](docs/operations/2026-10-25-display-thread-off.md)、[返回边界候选](docs/operations/2026-10-25-full-input-return-boundary.md)及[交接词](docs/2026-10-25-handoff-prompt.md)。所有内存/verified/设备恢复和破坏性分区门禁保持，源码pin不自动更新，参考仓只读，原始产物仅out/。

远端：[设备仓](https://github.com/wh1stl3/UniXNU-enuma)、[固件仓](https://github.com/wh1stl3/uefi-enuma)。
