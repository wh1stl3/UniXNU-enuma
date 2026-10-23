# STATUS

更新：2026-10-23 21:29后（Asia/Shanghai）。当前唯一真相；历史见WORKLOG。

## 当前状态

**step2自行返回；step3在75秒内未返回，已停止追加测试。用户人工恢复后21:27:29主机核验Android完成/root/原槽/解锁/原分区摘要通过。尚未进入XNU。**

用户本轮授权继续直到进入XNU，现场可恢复条件沿用；不是跳过既有无返回停点。step2于21:20:06临时启动，ADB16.923秒、完成与摘要核验31.178秒，用户确认全程未按键。step3于21:24:57启动，75秒无ADB/fastboot，截图黑屏；没有启动step4或互补候选。恢复录像601帧完整解码。下次不能用本次恢复状态替代新门禁。

故障范围缩至step2→step3新增Mode/Info访问与跨度检查及相关路径，不能确定根因或异常PC，也不能排除布局/更早路径/清理/Core返回。旧250849f故障同样未定因。step0/1此前均无按键返回，当前step2与其短时序相近；单次时序不唯一证明选中门命中。

证据：[本轮实测与离线边界](operations/2026-10-23-gop-step23-device.md)、[实测报告](../reports/enuma-gop-step23-device.json)、[反汇编边界](../reports/enuma-gop-step3-offline-boundary.json)。没有数值GOP快照、真实scanout、像素/菜单或XNU通过证据。

## 已有实现与验证

固件e286834/54输入锁、core-warning-v2不变。step0–3已分别全链接/打包审计，step4仅既有host/对象覆盖，未全链接打包/实测。本轮step2/3实际30OEM/FD/BootShim/v3与归档AutoGen/库清单核对通过，禁绘制/Probe早退、两秒目标门及七秒同步完成兜底保持。

实际step3链接DLL表明新增审计依次读取Mode/Info字段和计算跨度，不调用QueryMode，不解引用FrameBufferBase。静态反汇编不是执行轨迹，不称已定位坏指针。

## 下一步与约束

因step3无返回，当前停止追加实机候选，先离线细分Mode指针、Mode头/Info指针、Info字段、跨度和清理/Core返回。不要重试完整step3、step4或旧250849f。继续实机前重新评估隔离方案、现场恢复和身份/备份/原摘要；无返回停追加并恢复。

无绘制不持续录像，恢复/显示变化时录像。当前已恢复、无人工按键待办。未flash/erase/改槽，未改内存/example/verified。UART接点与TWRP未验证。

## 系统与内核现状

目标enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB、UniXNU5fdbd5d。
macOS CI39927966148/head250cdf9已真实链接crypto plain/namespace、pthread、ArmDTPlatform、ArmCpu服务与源内核；21417672B内核SHAb940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d，本地NativePrelink解析通过。仅源平台链接，未预链接donor或启动，正式board归档/opt-in/ADT接回仍待做。

64MiB配置专用FAT已生成并双份一致，仅ENUMA FAT DISCOVERY 01/reset，无kernel/EFI/ADT/Data；未接publisher或打包启动。历史Android initrd非512对齐，不能冒充临时候选实际FAT范围。
OS/SystemOS只读根卷与Data分开；NativeUfs含SM8550参数且当前禁用，根卷PMGR依赖/GPT/UUID/Data仍未落实；未生成大系统卷或写userdata。
见[系统预研](operations/2026-10-23-system-kernel-userland-roadmap.md)、[平台链接与FAT](operations/2026-10-23-discovery-volume-platform-link.md)。

51MiB DXE heap、已批准512MiB owned、board example与所有verified不变。
R-002跨Bootloader持久日志失败边界保持，不换地址/扩区/借DFPS或SMEM；UART接点与TWRP未验证。NT36523未实测。
EnumaScreen文本后端仅host/AArch64对象通过，尚无INF/FDF/调用者集成，不在当前镜像中。

两仓源码可写，nuwa及其他参考只读；原始设备数据/视频/镜像仅out。固件e286834已推送，设备实现595d6a6已推送；后续文档提交发布状态以Git/WORKLOG为准。

本轮新增donor离线审计：46,415,872字节普通ARM64 Mach-O，摘要与固定同donor pin一致，237模块及三组闭包/绑定计划通过；仅比较参考slide，未采用为板级配置、未emit预链接镜像。scripts/audit_enuma_donor.py可重放；完整ADT/载荷/内存/EBS/入口仍待闭合。
