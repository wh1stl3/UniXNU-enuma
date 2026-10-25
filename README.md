# UniXNU-enuma

小米平板5 Pro 5G / SM8250-AC的iPadOS17.7.11移植。当前主线按用户D-170要求：准备尽可能完整的启动链，采集实际报错并逐轮修复；单点早停仅作必要备用。

D-225，S-019受控返回，准备互补S-020。S-019 query1已单次发出并受控回Android、独立恢复通过；S-019 consumed。单笔时序不分类，当前文档推送与即时门禁后继续S-020 query2；S-020尚未发出。时序：{"issued_at": "2026-10-25 21:53:31", "issued_at_utc": "2026-10-25T13:53:31.737879+00:00", "boot_command_return_seconds": 2.625, "fastboot_disconnect_observed_seconds": 5.093, "fastboot_return_seconds": null, "adb_return_seconds": 25.422, "boot_complete_seconds": 39.531}。文档、资格及下一步见[当前状态](docs/STATUS.md)，原始影音仅本地，真实可见GOP/XNU/iPadOS未闭合。

接手读[AGENTS](AGENTS.md)、[STATUS](docs/STATUS.md)、[HANDOFF](docs/HANDOFF.md)、[完整链路线](docs/operations/2026-10-25-full-boot-mainline.md)、[ADT/FAT进展](docs/operations/2026-10-25-full-adt-fat.md)、[boot v3运输](docs/operations/2026-10-25-boot-v3-payload-transport.md)、[S-001试启动](docs/operations/2026-10-25-system-transport-trial.md)、[S-002隔离方案](docs/operations/2026-10-25-display-thread-off.md)、[返回边界候选](docs/operations/2026-10-25-full-input-return-boundary.md)及[交接词](docs/2026-10-25-handoff-prompt.md)。所有内存/verified/设备恢复和破坏性分区门禁保持，源码pin不自动更新，参考仓只读，原始产物仅out/。

远端：[设备仓](https://github.com/wh1stl3/UniXNU-enuma)、[固件仓](https://github.com/wh1stl3/uefi-enuma)。
