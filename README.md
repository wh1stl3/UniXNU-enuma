# UniXNU-enuma

小米平板5 Pro 5G / SM8250-AC的iPadOS17.7.11移植。当前主线按用户D-170要求：准备尽可能完整的启动链，采集实际报错并逐轮修复；单点早停仅作必要备用。

D-226，独立双路显示观测配对完成，按结果隔离。S-019/S-020均consumed，均受控返回并独立恢复。配对结果：{"scope": "indirect same-source paired timing, not direct native register log", "conclusion": "ambiguous", "negative_minus_positive_seconds": {"adb_return_seconds": -4.281, "boot_complete_seconds": -1.359}, "predeclared_absolute_delta_window_seconds": [3, 7], "predicate": "collection success AND both active throughout AND both nonzero stable Timing AND both stable Enable AND both two-window Frame increments1..64", "exact_enable3_not_required": true, "complement_includes": ["metadata/PCD rejection", "read/wait/revision rejection", "one or both inactive", "Timing/Enable instability", "one or both nonmoving/wrapped/over64 frames"], "exact_values_observed": false, "gop_verified": false, "pixel_access": false, "limitation": "Android boot noise and inherited state changes across boots remain confounders; complement does not uniquely identify which mask failed"}。后续按实际结果选新候选，不重复本对镜像。文档、资格及下一步见[当前状态](docs/STATUS.md)，原始影音仅本地，真实可见GOP/XNU/iPadOS未闭合。

接手读[AGENTS](AGENTS.md)、[STATUS](docs/STATUS.md)、[HANDOFF](docs/HANDOFF.md)、[完整链路线](docs/operations/2026-10-25-full-boot-mainline.md)、[ADT/FAT进展](docs/operations/2026-10-25-full-adt-fat.md)、[boot v3运输](docs/operations/2026-10-25-boot-v3-payload-transport.md)、[S-001试启动](docs/operations/2026-10-25-system-transport-trial.md)、[S-002隔离方案](docs/operations/2026-10-25-display-thread-off.md)、[返回边界候选](docs/operations/2026-10-25-full-input-return-boundary.md)及[交接词](docs/2026-10-25-handoff-prompt.md)。所有内存/verified/设备恢复和破坏性分区门禁保持，源码pin不自动更新，参考仓只读，原始产物仅out/。

远端：[设备仓](https://github.com/wh1stl3/UniXNU-enuma)、[固件仓](https://github.com/wh1stl3/uefi-enuma)。
