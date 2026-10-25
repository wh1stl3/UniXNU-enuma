# UniXNU-enuma

小米平板5 Pro 5G / SM8250-AC的iPadOS17.7.11移植。当前主线按用户D-170要求：准备尽可能完整的启动链，采集实际报错并逐轮修复；单点早停仅作必要备用。

D-229，启动时钟常量校准通过，继续显示隔离。S-021/S-022均受控返回且consumed；仅校准通过：{"scope": "indirect calibration of known2/7 second same-Core constants, not display/GOP evidence", "calibration_passed": true, "negative_minus_positive_origin_interval_seconds": [4.956999999994878, 5.096000000019558], "predeclared_acceptance_interval_seconds": [4, 6], "individual_uncertainty_seconds": [0.07000000000698492, 0.06900000001769513], "adb_delta": 5.343999999999998, "android_complete_delta": 4.3289999999999935, "both_new_boot_ids": true, "both_independent_recoveries": true, "old_S019_S020_reclassified": false, "limitation": "Controlled known-delay difference calibrates this host/boot-clock path only; no unique instruction-path or display proof. Hardware state can still change across boots."}。后续仍用全新资格/精确图和当前文档/即时设备相机门禁，不重试旧图。S-019/020仍ambiguous。详见[当前状态](docs/STATUS.md)；原始影音本地。

接手读[AGENTS](AGENTS.md)、[STATUS](docs/STATUS.md)、[HANDOFF](docs/HANDOFF.md)、[完整链路线](docs/operations/2026-10-25-full-boot-mainline.md)、[ADT/FAT进展](docs/operations/2026-10-25-full-adt-fat.md)、[boot v3运输](docs/operations/2026-10-25-boot-v3-payload-transport.md)、[S-001试启动](docs/operations/2026-10-25-system-transport-trial.md)、[S-002隔离方案](docs/operations/2026-10-25-display-thread-off.md)、[返回边界候选](docs/operations/2026-10-25-full-input-return-boundary.md)及[交接词](docs/2026-10-25-handoff-prompt.md)。所有内存/verified/设备恢复和破坏性分区门禁保持，源码pin不自动更新，参考仓只读，原始产物仅out/。

远端：[设备仓](https://github.com/wh1stl3/UniXNU-enuma)、[固件仓](https://github.com/wh1stl3/uefi-enuma)。
