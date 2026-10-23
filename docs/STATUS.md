# 当前进度：新固件step0无按键返回，继续只读管线分层

2026-10-23 Asia/Shanghai。当前设备Android启动完成，root与原boot/vendor_boot摘要通过。f15d520新step0于23:41:10临时启动，ADB15.856秒、启动完成31.445秒，用户确认全程未按键。只证明安装及Core返回路径，没有进入XNU或写屏。

此前838b38f step3于23:16:54超时，已当轮落实硬停文档，23:20:44人工恢复并核验通过。旧失败镜像SHAa8061b8510935bbe8991ec0d8723a1bcc3b1a9460422ecc9ac30ffe13813016a禁止原样重试。根因/故障PC未知；新step0通过不证明step3修复。

离线隔离：f15d520固定SEC source epoch横幅，双份相同输入全构建SEC TE完全一致，其他可执行叶模块只有Pcd RSDS八字节不同，整FD不一致。两份新step0均全链接/打包/审计通过；历史候选按固定Git源锁重放，五负例及workspace通过，实际构建仍严格使用当前pin。证据reports/enuma-sec-epoch-rebuild.json、enuma-sec-epoch-step0-device.json、operations/2026-10-23-sec-epoch-isolation.md。

下一步：新f15d520 step9，只读八个SRC0_ADDR作splash地址存在性对照，同源step10也已受控返回，下一软件是step11几何/跨度分层。step9/10从编译路径绕开GOP Mode审计，不使用失败step3作无关MDP对照；先step0已覆盖共有安装/返回路径，再step9覆盖MMIO最小读取。新版本step9已构建/审计并于23:46:56无按键返回：ADB16.964秒/完成30.109秒、root/原摘要通过。step10已于23:50:53无按键返回，ADB16.947秒/完成30.745秒，root/原摘要通过。短返回支持所检查的线性未压缩4字节格式；几何/stride/跨度/唯一活动性仍未知。正在离线新增step11几何/跨度探针，尚未构建或实测。step10不证明活动/唯一管线、几何、stride或写屏安全，完整描述仍未闭合。

R-004仅0x0ae00000/0x85000映射和有界只读；像素/寄存器写入、RAM/heap/verified及破坏性分区边界不变。超时立即停止追加、优先恢复，当轮更新交接；人工恢复后继续离线出新软件。当前无按键或批准待办。

源码发布：固件f15d520已推送；设备9bc1767已推送上一硬停/恢复，新基线里程碑367134b已推送，随后step9及新step10进度待下一里程碑提交。参考仓只读，全部产物/设备标识在out/。

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


23:40更新：SEC固定epoch的同输入双构建比较通过，SEC逐字节一致；整包仍有Pcd RSDS差异，不称根因修复。已审查新step0最小返回路径，准备在完整设备门禁下测试epoch-control-b，尚未执行。失败step3及step10禁止绕过，见operations/2026-10-23-sec-epoch-isolation.md。


2026-10-23 23:46:56 · f15d520 step9：ADB16.964秒/启动完成30.109秒，root/原摘要通过，用户确认无按键。image9a1cd385f7b7ecb77543db442acb71adf9167506346dbb24d12d8795c61d7864，FDe1f907465cd8d5b1908b4a3d9fb4e1515051fd975faa0773ff4b77fb40b44463。短返回支持splash地址存在性；step10已于23:50:53无按键返回，ADB16.947秒/完成30.745秒，root/原摘要通过。短返回支持所检查的线性未压缩4字节格式；几何/stride/跨度/唯一活动性仍未知。正在离线新增step11几何/跨度探针，尚未构建或实测。


2026-10-23 23:50:53 · f15d520 step10：ADB16.947秒/启动完成30.745秒，root/原摘要通过，用户确认无按键。image3364f1726954f246ef3f7f82f52f69fc3aa75e50c2eced8ec62566558b639473，FDea1fb90a73dfe0ecf1413e9d7dfdb2c989bafab0b40c9e1b693d6450ffe795bc。仅格式/压缩谓词时序证据；不能证明活动性、唯一性、几何、pitch或像素安全。
