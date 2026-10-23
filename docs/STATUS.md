# STATUS

更新：2026-10-23 21:47（Asia/Shanghai）。

## 当前结论

尚未写屏或进入XNU。旧step3超时已人工恢复；按用户最新规则，恢复后自动继续离线分析、修复和新候选，不作为整轮停止点。

固件26b1f99已推送，新增Mode拆分step5/6/7。step2对照与step5已完整构建打包、审计通过；240主机用例O1/Oz、七对象、48标记、六Mu传输、七CLI、四bundle负例及workspace通过。

新step2 21:45:28启动，ADB17.024秒、完整核验28.813秒，Android/root/原分区摘要通过；本次无按键确认待答，暂不启动step5。step5仅指针存在检查，6/7尚未全链接。旧step3失败原因仍未定位，不原样重试。

## 下一步

确认新对照是否自行返回后，按相同恢复门禁测试step5，再逐层推进Mode头、Info与跨度。无返回停止追加启动并恢复，随即继续离线隔离。用户提出构建归属调整，已准备将实际编译入口迁到uefi-enuma，设备仓保留校验调用、打包/实机/恢复；迁移后须实际构建验证。

证据见operations/2026-10-23-gop-mode-split.md及reports/enuma-gop-mode-split.json、reports/enuma-gop-mode-device.json。没有数值GOP快照或真实scanout证据；禁绘制保持。原内存/example/verified不变，未flash/erase/改槽。

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
