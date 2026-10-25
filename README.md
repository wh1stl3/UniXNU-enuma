# UniXNU-enuma

小米平板5 Pro 5G / SM8250-AC的iPadOS17.7.11移植。当前主线按用户D-170要求：准备尽可能完整的启动链，采集实际报错并逐轮修复；单点早停仅作必要备用。

D-228，S-021已受控返回，准备S-022七秒常量。S-021已单次发出、受控回Android并独立恢复核验，已consumed；S-022尚未发出。当前时钟界限：{"method": "host request interval minus quantized Linux uptime; 3-sample intersection", "boot_id_sha256": "9107737f47587883261dd4e628610a32b0ce06c886dd3804452cf7fc34b44505", "origin_monotonic_lower": 177088.955, "origin_monotonic_upper": 177089.025, "uncertainty_seconds": 0.07000000000698492, "calibrated_firmware_delay": false, "origin_after_issue_lower": 12.25199999997858, "origin_after_issue_upper": 12.321999999985565}。S-019/020仍ambiguous。详见[当前状态](docs/STATUS.md)；原始影音本地。

接手读[AGENTS](AGENTS.md)、[STATUS](docs/STATUS.md)、[HANDOFF](docs/HANDOFF.md)、[完整链路线](docs/operations/2026-10-25-full-boot-mainline.md)、[ADT/FAT进展](docs/operations/2026-10-25-full-adt-fat.md)、[boot v3运输](docs/operations/2026-10-25-boot-v3-payload-transport.md)、[S-001试启动](docs/operations/2026-10-25-system-transport-trial.md)、[S-002隔离方案](docs/operations/2026-10-25-display-thread-off.md)、[返回边界候选](docs/operations/2026-10-25-full-input-return-boundary.md)及[交接词](docs/2026-10-25-handoff-prompt.md)。所有内存/verified/设备恢复和破坏性分区门禁保持，源码pin不自动更新，参考仓只读，原始产物仅out/。

远端：[设备仓](https://github.com/wh1stl3/UniXNU-enuma)、[固件仓](https://github.com/wh1stl3/uefi-enuma)。
