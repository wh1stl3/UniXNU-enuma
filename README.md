# UniXNU-enuma

小米平板5 Pro 5G / SM8250-AC的iPadOS17.7.11移植。当前主线按用户D-170要求：准备尽可能完整的启动链，采集实际报错并逐轮修复；单点早停仅作必要备用。

当前D-215：原生ramoops兼容核心、只读收集器与51,210项ASan/UBSan环形测试、5项收集器测试及AArch64对象已完成，未接线到生产固件。新增console B0000000/2MiB映射和一次44字节留存标记属于R-017最小待审范围；内存表和Null后端未改，尚无新FD或实机日志资格。最近Android/root/原槽/分区备份核验通过。完整ADT/FAT、预链接系统和运输链仍待运行时闭合，真实GOP/XNU/iPadOS未实机成功，原始影音仅本地。详见[原生ramoops审计](docs/operations/2026-10-25-ramoops-compatibility-audit.md)和[当前审查](docs/NEED-REVIEW.md)。

接手读[AGENTS](AGENTS.md)、[STATUS](docs/STATUS.md)、[HANDOFF](docs/HANDOFF.md)、[完整链路线](docs/operations/2026-10-25-full-boot-mainline.md)、[ADT/FAT进展](docs/operations/2026-10-25-full-adt-fat.md)、[boot v3运输](docs/operations/2026-10-25-boot-v3-payload-transport.md)、[S-001试启动](docs/operations/2026-10-25-system-transport-trial.md)、[S-002隔离方案](docs/operations/2026-10-25-display-thread-off.md)、[返回边界候选](docs/operations/2026-10-25-full-input-return-boundary.md)及[交接词](docs/2026-10-25-handoff-prompt.md)。所有内存/verified/设备恢复和破坏性分区门禁保持，源码pin不自动更新，参考仓只读，原始产物仅out/。

远端：[设备仓](https://github.com/wh1stl3/UniXNU-enuma)、[固件仓](https://github.com/wh1stl3/uefi-enuma)。
