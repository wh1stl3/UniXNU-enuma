# 当前进度：格式对照受控返回，几何/跨度候选构建中

2026-10-24 Asia/Shanghai。设备当前Android启动完成，root/原槽/解锁及boot/vendor_boot原摘要通过。ab0cb79同源step10于2026-10-23 23:59:30临时启动，ADB16.919秒、启动完成31.082秒，用户确认全程未按键。step11正在完整构建，尚未实测。

固件ab0cb79已推送并固定到当前gitlink/59项源锁；新增step11仅只读SRC0_ADDR/SIZE/YSTRIDE，最多24读，检验1600x2560/pitch6400/四字节对齐/完整跨度在0x9c000000..0x9e300000范围内的假设。84主机用例O1/Oz+ASan/UBSan、AArch64对象无外部依赖通过；旧GOP240用例/7对象/48标记/实际Mu传递6用例及7CLI拒绝通过。当前step10已全链接/候选审计并实测，step11待构建后做同源bundle和独立设备门禁。

f15d520的step0/9/10此前均无按键返回，设备里程碑367134b、a50d0fb已推送。SEC固定source epoch双构建载荷一致，其他可执行模块仅Pcd RSDS八字节不同；整包不一致，不称根因修复。

历史硬停：838b38f step3于23:16:54超时，已当轮更新五件套与HANDOFF，23:20:44人工恢复及身份/root/原摘要核验通过。旧失败image a8061b8510935bbe8991ec0d8723a1bcc3b1a9460422ecc9ac30ffe13813016a不原样重试，根因/故障PC未知。新只读路径不执行GOP Mode审计，不把其结果当step3修复。

没有写屏、进入XNU或新分区写入。候选活动性、唯一性、裁剪/额外平面仍未知；几何/stride/跨度待step11。R-004仅0x0ae00000/0x85000映射与有界只读，RAM/heap/verified/破坏性分区边界不变。实际超时立即停止追加并优先恢复，当轮落实交接；恢复后继续离线出新软件。当前无按键/批准待办。

证据：reports/enuma-geometry-device.json、enuma-scanout-host.json、enuma-sec-epoch-rebuild.json，operations/2026-10-23-geometry-layer.md。当前ab0cb79设备集成/源码锁与新进度待里程碑提交，参考仓只读。

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


固件ab0cb79已推送并更新当前gitlink/源锁：新增step11几何/跨度只读谓词，84主机用例O1/Oz+ASan/UBSan及AArch64对象通过，无新映射/像素/寄存器写入。当前正在完整构建同源step10对照，随后构建step11；ab0cb79尚未实测。f15d520 step9/10实测里程碑a50d0fb已推送。


2026-10-23 23:59:30 · ab0cb79 step10：ADB16.919秒/完成31.082秒，用户无按键确认，root/原摘要通过。image5f303d1d2d4586597a34adc0a98b512a5454f0786d5bcbb5eab7eb47a176822b，FDb026f96806723c9a28e540034f3139fb5492892a704ae035985927209cfc3367。格式层对照受控返回，step11仍待单独资格/实测。


2026-10-24 00:02:48 · ab0cb79 step11：ADB21.196秒/完成36.695秒，用户无按键确认，root/原摘要通过。image2cf0b95911aa7d6b0b066382656304163482f54e133f8c556e9a0fbfd9e1ea4c，FD1ebfd9e7808df6bfba8a70c9349e76927d342f668a048081b2540612505f5c1c。几何/stride/完整跨度仅有谓词时序证据；唯一性、裁剪、额外平面、活动性和写屏仍未证明。


2026-10-24 00:08:19 · step11 selector2互补探针ADB15.866秒/完成30.310秒，用户无按键确认，root/原摘要通过；与selector1约21.196秒共同支持固定几何/stride/跨度条件拒绝，具体字段未知，不是硬停。YSTRIDE0按固定SDE源码610..634行包含两个16位pitch字段。下一软件step12解码实际源矩形/裁剪/stride低半字和较小保留区边界，只读，不认定唯一/活动或物理-IOVA一致。
