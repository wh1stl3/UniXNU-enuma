# STATUS

更新：2026-10-22（Asia/Shanghai）。当前唯一真相，历史见WORKLOG。

## 当前结论

**双仓结构已落地：wh1stl3/uefi-enuma承接固件源码，设备firmware/固定引用3376c4411e08442f45f4120ed6d96f2e302c51e8。board.toml已接入官方[firmware]配置，真实unixnu.firmware.build完成固件构建与Mu core补丁恢复；33OEM字节审计、boot v3回读和33项测试通过。新候选未启动。**

固件迁移25个原文件逐字节保持，六个补丁/诊断/DSC-FDF/板级内存配置保留；source gitlink与33项摘要互锁。旧LICENSE/README仅改路径，设备仓不再维护另一份板级源码。厂商二进制、cfg/XML原文与备份不入Git，仅发布输入摘要。两个工作树与nuwa/PortingiOS只读边界已写入AGENTS。

目标仍为enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB。board.toml仅新增firmware表，所有旧表与1ab7ee8一致；example=true、512MiB请求、物理内存字段和 *_verified 标记不变。官方顶层CLI的example保护已实测仍拒绝完整build；现阶段只通过已授权的固件包装器调用backend。

## 当前构建证据

- 官方preflight核对102个私有输入、三Mu依赖、DarwinBoot接口和规范化基线。Mu core补丁由官方backend应用并在finally恢复，恢复后再核对DxeMain/Dispatcher原始LF摘要。源码树保持干净，输出只在设备out/。
- 当前完整FD **bc3e16ffd0ab46ceff6bee689c2ba18c496e31e43be553163755fd0922c1f917**，81文件/33原厂PE-DEPEX字节一致，当前overlay检查通过。
- 新候选out/boot-candidate/enuma-official-backend-stage12-boot-v3.img，3153920 bytes，SHA **25d6947b0eeb2112baeab69d301d97984747b17082d279808e72bcd3d09525d7**，boot v3回读通过，**未实机启动**。快照out/uefi-migration/official-backend-stage12/。raw BootShim/空ramdisk/原厂vendor_boot契约保留。
- 33项Python通过，包括新预检拒绝不安全暂存和缺OEM输入。ADT计划只因新增firmware表刷新board摘要，512MiB与原硬件数据不变；真实DarwinBoot主机契约回归通过。
- 固件仓源码Actions run39796073610通过（a1215b7）；run39796926508对应当前3376c44，记录时排队。它仅检查源码，不构建OEM镜像。本地当前源码契约已通过。
- UniXNU底座仍固定5fdbd5d及21模块；macOS通用4KiB XNU最终链接/审计run39790786938通过，产物de5ccd24…已回读。这关闭板级功能，仍不是enuma最终内核或donor prelink。本轮未重跑macOS内核构建。

## 最新实机边界

本轮没有USB/启动/刷写/改槽操作。最后实测仍是迁移前stage12首个队列项加载前探针：ADB15.870秒、Android完成31.623秒，root与boot/vendor_boot摘要不变。镜像SHA d974069340e6fc69d5e8eb898bd3cdab4eff202a226fb449cbdfdc0dfd40850e，FD33d8dcc5d62ab61064dbb760672d989155f3968467c42b538250eedbeb641af9。

stage11的2/7秒ADB差仅0.005秒，不认定CoreDispatcher完成；stage12支持到达首项加载前，尚无该门独立2/7对照。一次fastboot身份查询在推送前中止并恢复后重试的记录保留。

仍在官网阶段1UEFI；没有GOP base/stride/format、UEFI map、菜单/FAT卷、DarwinBoot/XNU或NT36523运行证明。Android分辨率与35MiB cont_splash不替代GOP或根因证据。

## 下一步

1. 继续使用新固件仓的stage13/ordinal1区分首项加载和入口返回，再按实际队列/必要GUID门定位调度内问题；不盲重试黑屏镜像。
2. 取得真实GOP、UEFI map、BDS/Probe与菜单协议闭包。新内存值或验证标记仍需审查。
3. 再补完整ADT/NVRAM/种子/占位符、真实板级archives/最终内核/donor prelink，推进基础平台与NT36523 IRQ/HID；SM8550专用参数不继承，A650后置。

远端：https://github.com/wh1stl3/UniXNU-enuma 与 https://github.com/wh1stl3/uefi-enuma。固件a1215b7/3376c44已推送，设备迁移提交号及推送见Git/后续记录。无新增待批准硬停或待按键事项。

详情：[双仓接入](operations/2026-10-22-uefi-repository.md)、[DXE实测](operations/2026-10-22-dispatch-checkpoints.md)、[主分支接入](operations/2026-10-22-upstream-integration.md)。
