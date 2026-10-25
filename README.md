# UniXNU-enuma

小米平板5 Pro 5G / SM8250-AC的iPadOS17.7.11移植。当前主线按用户D-170要求：准备尽可能完整的启动链，采集实际报错并逐轮修复；单点早停仅作必要备用。

当前D-217：S-015原生ramoops留存探针75秒未自动返回，已停止追加；用户恢复Android且root/原槽/双分区备份摘要独立核验通过，相机补拍桌面。没有有效nonce读回，65字节缺文件错误不算日志。R-017 writer单笔及S-015 consumed；继续离线map-only/cold对照隔离，原始影音仅本地。真实GOP/XNU/iPadOS未闭合。详见[当前状态](docs/STATUS.md)和[S-015记录](docs/operations/2026-10-25-ramoops-S-015.md)。

接手读[AGENTS](AGENTS.md)、[STATUS](docs/STATUS.md)、[HANDOFF](docs/HANDOFF.md)、[完整链路线](docs/operations/2026-10-25-full-boot-mainline.md)、[ADT/FAT进展](docs/operations/2026-10-25-full-adt-fat.md)、[boot v3运输](docs/operations/2026-10-25-boot-v3-payload-transport.md)、[S-001试启动](docs/operations/2026-10-25-system-transport-trial.md)、[S-002隔离方案](docs/operations/2026-10-25-display-thread-off.md)、[返回边界候选](docs/operations/2026-10-25-full-input-return-boundary.md)及[交接词](docs/2026-10-25-handoff-prompt.md)。所有内存/verified/设备恢复和破坏性分区门禁保持，源码pin不自动更新，参考仓只读，原始产物仅out/。

远端：[设备仓](https://github.com/wh1stl3/UniXNU-enuma)、[固件仓](https://github.com/wh1stl3/uefi-enuma)。
