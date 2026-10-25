# UniXNU-enuma

小米平板5 Pro 5G / SM8250-AC的iPadOS17.7.11移植。当前主线按用户D-170要求：准备尽可能完整的启动链，采集实际报错并逐轮修复；单点早停仅作必要备用。

已实际生成29组件的实验系统预链接，并固定同SoC [UniXNU-umi](https://github.com/reAAAq/UniXNU-umi/tree/3eb72578597d2ca16471b172d45eddc096a34a04)作为ADT、RAM载荷、PMGR/UFS和CPU显示复用源。已生成完整结构ADT和96MiB真实FAT，实际loader解析主机检查通过；v3只读RAM运输和13项同次报告已实现并完成构建/打包资格，运行时发现、root及可见错误通道仍待闭合，尚无进入XNU或iPadOS的实机证据。当前D-207：D-207，S-011受控返回并独立恢复，准备互补S-012。S-011(query1)于18:45:34发出，镜像4f413f286bba150e007e2333d9aa466fef98d046bc23ebb05256d01f213261a7已consumed。命令2.625秒、断开5.093秒，ADB26.484秒/完成40.547秒受控回Android，无主机恢复reboot。独立Android完成/root/A槽/解锁及boot_a/vendor_boot_a设备与备份摘要全部通过，278/278帧解码，原始影音仅本地无音频。证据reports/enuma-video-topology-S-011-result.json，原trial out/device-tests/20261025T184520-system-transport/result.json。

单笔时序接近长返回，仅初步支持首次状态非Topology，不据此确证。按预先计划，当前文档提交推送后执行S-012(query2)一次，仍保持即时Android/备份/fastboot/相机/恢复门禁及75秒期限，完成互补核对后才分类。S-011与S-010及旧图不重试；当前无人工/审批待办。 原始影音仅本地，S-010与旧失败图不重试；仍无真实GOP/XNU/iPadOS实机成功。

接手读[AGENTS](AGENTS.md)、[STATUS](docs/STATUS.md)、[HANDOFF](docs/HANDOFF.md)、[完整链路线](docs/operations/2026-10-25-full-boot-mainline.md)、[ADT/FAT进展](docs/operations/2026-10-25-full-adt-fat.md)、[boot v3运输](docs/operations/2026-10-25-boot-v3-payload-transport.md)、[S-001试启动](docs/operations/2026-10-25-system-transport-trial.md)、[S-002隔离方案](docs/operations/2026-10-25-display-thread-off.md)、[返回边界候选](docs/operations/2026-10-25-full-input-return-boundary.md)及[交接词](docs/2026-10-25-handoff-prompt.md)。所有内存/verified/设备恢复和破坏性分区门禁保持，源码pin不自动更新，参考仓只读，原始产物仅out/。

远端：[设备仓](https://github.com/wh1stl3/UniXNU-enuma)、[固件仓](https://github.com/wh1stl3/uefi-enuma)。
