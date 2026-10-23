# STATUS

更新：2026-10-23 21:58（Asia/Shanghai）。

## 当前结论

尚未写屏或进入XNU。Mode拆分step5（只检查指针存在）已自行回Android，用户确认无按键。旧step3超时原因仍未定，按新用户规则人工恢复后持续离线分析和新软件，不原样重试失败包。

26b1f99的step2/5 ADB17.024/16.943秒；迁移后00ddc01的step2 ADB15.865秒。三笔均完成Android/root/原摘要核验，用户逐笔确认无按键。迁移后step5已构建未测，其SimpleFb/Core与旧step5一致；迁移版step2已重验返回。

## 编译归属与验证

固件仓00ddc01已推送，实际编译实现和preflight桥在Resources/Scripts；设备仓只保留校验固定版本/全部摘要后的兼容调用。设备契约、依赖锁、打包、实机/恢复和out位置不变，56项固件输入锁。

迁移版step2/5实际全链接、30OEM/FD/BootShim/v3、bundle/四负例/workspace通过；三ownership测试及10兼容测试通过。迁移前后整包不一致，已解包定位SEC时间字符串/引用布局及PcdDxe调试标识差异，SimpleFb/Core等其余叶载荷一致；不声称可重现构建。

## 下一步与限制

step6（Mode头，不解引用Info）正在构建。审计后沿现有临时boot/身份备份/恢复门禁推进；超时停止追加并先恢复，之后继续离线迭代。step7/完整跨度/QueryMode尚未获得新实机结论。无数值GOP快照或真实scanout，禁绘制保持。

证据operations/2026-10-23-firmware-build-ownership.md、reports/enuma-firmware-build-ownership.json、reports/enuma-gop-mode-device.json。原内存/example/verified不变，未flash/erase/改槽。

## 系统与内核现状

目标enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB、UniXNU5fdbd5d。
macOS CI39927966148/head250cdf9已真实链接crypto plain/namespace、pthread、ArmDTPlatform、ArmCpu服务与源内核；21417672B内核SHAb940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d，本地NativePrelink解析通过。仅源平台链接，未预链接donor或启动，正式board归档/opt-in/ADT接回仍待做。

64MiB配置专用FAT已生成并双份一致，仅ENUMA FAT DISCOVERY 01/reset，无kernel/EFI/ADT/Data；未接publisher或打包启动。历史Android initrd非512对齐，不能冒充临时候选实际FAT范围。
OS/SystemOS只读根卷与Data分开；NativeUfs含SM8550参数且当前禁用，根卷PMGR依赖/GPT/UUID/Data仍未落实；未生成大系统卷或写userdata。
见[系统预研](operations/2026-10-23-system-kernel-userland-roadmap.md)、[平台链接与FAT](operations/2026-10-23-discovery-volume-platform-link.md)。

51MiB DXE heap、已批准512MiB owned、board example与所有verified不变。
R-002跨Bootloader持久日志失败边界保持，不换地址/扩区/借DFPS或SMEM；UART接点与TWRP未验证。NT36523未实测。
EnumaScreen文本后端仅host/AArch64对象通过，尚无INF/FDF/调用者集成，不在当前镜像中。

本轮新增donor离线审计：46,415,872字节普通ARM64 Mach-O，摘要与固定同donor pin一致，237模块及三组闭包/绑定计划通过；仅比较参考slide，未采用为板级配置、未emit预链接镜像。scripts/audit_enuma_donor.py可重放；完整ADT/载荷/内存/EBS/入口仍待闭合。
