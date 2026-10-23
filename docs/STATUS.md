# STATUS

更新：2026-10-23 22:13（Asia/Shanghai）。尚未写屏或进入XNU。

## 当前实测

固件00ddc01，Mode头step6、Info字段step7、完整跨度step3均受控回Android，用户逐笔确认全程未按键；ADB分别15.879/15.871/15.926秒，完整核验31.933/31.101/32.396秒，Android完成/root/原分区摘要通过。此前指针step5及同源/迁移对照亦自行返回。

当前完整跨度候选image SHA805bfabfa23b0f4e0db8a00bab94a143a61636cfa76292d6148185a8ebfab4fd。原e286834 step3失败镜像未重试，故障PC/根因仍未知，当前成功不证明旧故障已修复。短时序与源码支持检查路径，但缺数值GOP快照和真实scanout证据。

## 构建与下一步

实际编译实现已迁至uefi-enuma Resources/Scripts/build_enuma_firmware.py，设备同名脚本为版本/摘要校验薄封装；56项源锁。设备仓保留契约、打包、实机、恢复和out输出。两仓相关里程碑已推送。构建/打包/源锁和既有主机检查通过；详情reports/enuma-firmware-build-ownership.json。

下一步重点核对enuma现有framebuffer描述、映射与像素格式，评估复用FrameBufferSerialPortLib直接日志和最小色块路径；完整GOP QueryMode不是所有早期写屏方案的必经条件。不能照搬nuwa地址/驱动参数，原禁绘制在映射/边界闭合前保持。未运行step4，未输出实际像素。

无返回停止追加启动、先恢复，随后按用户要求持续离线分析和新软件。无新内存/example/verified或flash/erase/改槽。证据reports/enuma-gop-mode-device.json、operations/2026-10-23-gop-mode-split.md。

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
