# UniXNU-enuma

小米平板5 Pro 5G（enuma / SM8250）的 iPadOS17.7.11/21H461 移植工作仓；XNU10063.141.1、4KiB。当前example配置，未进入XNU或iPadOS用户态，未证实可见GOP输出。


当前路线：[公开资料复审：先审显示交接契约和原厂运行时ABI](docs/operations/2026-10-25-public-source-route-review.md)；[DisplayDxe执行边界定位](docs/operations/2026-10-25-display-entry-isolation-plan.md)保留为有界支线；接手读[AGENTS](AGENTS.md)、[STATUS](docs/STATUS.md)、[HANDOFF](docs/HANDOFF.md)、[D-164/D-163](docs/DECISIONS.md)、[审核状态](docs/NEED-REVIEW.md)和[交接提示词](docs/2026-10-25-handoff-prompt.md)。

原厂模块支持优先复用，但尚无运行闭包和可见显示证明。R-014两笔无返回尚未定位；APRIORI只保证入队，R-015不按原动机执行。新detail15/detail13候选仅为方案，未构建/上机；本轮文档未提交，实机前须完整资格与发布/恢复门禁。历史0/3/0计划冻结，不解码或原样重试失败镜像。

设备仓负责板级契约、打包、实机恢复和审计；firmware/为固定固件子模块，构建实现不复制回来。所有产物放out/，参考仓只读；原厂PE、备份与设备身份不提交。当前源码锁与gitlink为aa9ec66，实时状态以Git和来源锁核对。

继续复用UniXNU的DarwinBoot、ArmCpu/ArmDTPlatform、NativePrelink/NativeRamBlock及载荷工具；LineageOS/MiCode作为SM8250/enuma硬件依据。未验证GOP可见输出、PE_Video交接或XNU入口；sheng参数和实机结论不继承。

远端：[设备仓](https://github.com/wh1stl3/UniXNU-enuma)、[固件仓](https://github.com/wh1stl3/uefi-enuma)。
