# UniXNU-enuma

小米平板5 Pro 5G（enuma / SM8250）的 iPadOS17.7.11/21H461 移植工作仓；XNU10063.141.1、4KiB。当前example配置，未进入XNU或iPadOS用户态，未证实可见GOP输出。

先读 [AGENTS](AGENTS.md)、[STATUS](docs/STATUS.md)、[HANDOFF](docs/HANDOFF.md)、[DECISIONS](docs/DECISIONS.md)、[NEED-REVIEW](docs/NEED-REVIEW.md)。当前路线见[取数通道校准与显示访问隔离](docs/operations/2026-10-24-takeover-calibration.md)。历史自动返回不等于显示事实，旧delay20/固定基线取数结论已降级；不可直接运行旧vprobe队列。

源码：设备仓维护设备契约、打包、实机恢复与审计；firmware/是独立uefi-enuma固定提交子模块，构建实现仅在固件仓维护。所有中间产物进out/，上游和nuwa参考只读。来源固定在config/sources.lock.json及config/uefi-source.lock.json。

当前Android/root/原A槽/解锁及boot/vendor_boot与备份匹配；恢复证据见reports/enuma-recovery-reconciliation.json。新实机动作前落实文档并提交推送；失败停止追加，恢复核验后继续离线分析，不原样重试失败镜像。

新工具 scripts/run_value_probes.py --plan <qualification.json> --trial <id> 默认只做离线校验；--execute只允许单笔，不自动打包，不覆盖产物，不继续失败计划。先用无显示MMIO的0/3/0常量校准，之后才允许解码独立index/shift寄存器样本。精确参数与资格以当前状态和计划为准。

复用UniXNU的DarwinBoot、ArmCpu/ArmDTPlatform、NativePrelink/NativeRamBlock及载荷工具；LineageOS/MiCode提供SM8250/enuma的显示、SMMU、UFS与触控事实。sheng的SM8550参数与实机结果不继承；Android HAL不能直接加载进iPadOS。

远端：[设备仓](https://github.com/wh1stl3/UniXNU-enuma)、[固件仓](https://github.com/wh1stl3/uefi-enuma)。构建产物、原厂PE、备份和设备身份数据不提交。
