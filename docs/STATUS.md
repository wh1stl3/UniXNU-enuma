# STATUS

更新：2026-10-23 22:40（Asia/Shanghai）。尚未写屏或进入XNU。

## 当前状态

R-004已获用户明确批准并执行最小映射：固件9f50890，staging新增且仅新增MDP 0x0ae00000/0x85000设备区，原迁移表字节保持。58项输入锁，无RAM/heap/owned/example/verified变化。原已测Mode/Info/跨度结论见历史报告。

新映射step3对照22:37:26 ADB15.878秒/核验29.626秒；step8只读探针22:39:15 ADB21.187秒/核验37.050秒。两次Android/root/原摘要通过，用户确认无按键自行返回。step8长时序提示未命中成功门，尚无描述匹配或数值GOP/scanout快照。互补selector2构建中，用同读取代码分类结果，不把单次时序当唯一证明。

首轮fastboot GetVar身份门中止，未发boot；正常reboot后完整恢复核验通过，另存identity-abort，不计为镜像失败或通过。新一轮身份门通过才执行对照，无校验放宽。

## 验证与下一步

25 scanout用例O1/Oz+ASan/UBSan、AArch64对象、既有240 GOP回归通过；两份全链接FD/30OEM/BootShim/v3、生成依赖、bundle四负例、workspace与staging唯一映射差异均通过。证据operations/2026-10-23-r004-scanout-device.md、reports/enuma-r004-{device,staged-map,scanout-bundle,identity-abort}.json、enuma-scanout-host.json。

step8仅检查源描述，最多72次32位读取，无像素访问或寄存器写入。谓词匹配不证明管线活动或颜色顺序；互补分类后进一步离线隔离描述字段。R-004不包含写屏。无返回立即停追加并恢复，之后按用户要求继续离线分析和新软件。未flash/erase/改槽。

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
