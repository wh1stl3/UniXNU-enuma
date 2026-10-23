# STATUS

更新：2026-10-23（Asia/Shanghai）。当前唯一真相，历史见WORKLOG。

## 当前状态

**enuma已人工恢复并核验Android；本轮依用户最新指令继续离线，不操作实机。** 12:11:03 +08:00核验enuma/槽_a/完成1/root/解锁及原boot_a、vendor_boot_a摘要，用户确认按键恢复。233a9d8首测未自动返回的历史结果保持，不能称其定时复位或GOP通过。见[恢复报告](../reports/enuma-simplefb-recovery.json)。未flash/erase/改槽，没有新设备试验。

## 本轮主线进展

固件gitlink6bc5b81、50项源锁。增加完整GUID-only选择，保留完整GUID/实际句柄/detail/status守卫，解除未知运行序号与GUID的AND依赖；默认仍旧序号模式。可选正常分派结束7秒复位，置于缺失架构协议检查和BDS之前；默认关闭。它不能处理驱动/构造器/Dispatcher卡死，不是异步看门狗，也不能追溯修复旧镜像。

7479da1早期stage12/ordinal1 SimpleFb对照已构建打包，未实测。6bc5b81 GUID-only point20/2秒加正常完成兜底实际AArch64构建/官方core patch还原通过，FD 8f2c6f8a00a311ee63b1c9ca16db7b1b4d5bd501819193aa6875edb7be051ff7；实际编译宏已核对。147组真实头ASan/UBSan、三种完成门配置/非法配置拒绝、50项Python/组合patch重复重放/50源锁检查通过。全部新镜像仅离线生成，不把构建当运行证明。

详见[完整GUID与兜底审计](operations/2026-10-23-guid-only-dispatch-offline.md)、[机器证据](../reports/enuma-dispatch-selection-offline.json)。新版本后续FD/30 OEM/BootShim/v3审计以当前reports为准。

## 仍有效的证据与边界

同SM8250 alioth/elish路线已形成30-OEM独立SimpleFb诊断，排除CPR/Display/UFS，其余本机PE/DEPEX保留。默认33、无UFS32模式分别保留；真实Mu驱动已有查找/模式/分配/错误/清理/溢出修补，metadata模式禁止Blt像素写入，Probe直接绘制入口早退。scanout实际地址偏移、pitch/格式/线性、DFPS子范围、缓存和生命周期仍未知。

nuwa同Mu pool成功门有5.370秒延时响应，失败门未观察预期响应；没有堆耗尽/扩堆依据。Native Display历史仅调用前/canary前缀存在门支持，不转移成新SimpleFb运行结论。51MiB DXE Heap、512MiB owned、原内存表/example/verified不变；R-002跨Bootloader不保留，持久日志路线仍停，不换地址/扩大/借DFPS或SMEM。

目标enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB、UniXNU5fdbd5d/21模块。尚未证明GOP安装/可见、实时UEFI map、BDS、XNU或NT36523。TWRP未测试。

## 下一步

保持离线。下次恢复实机时先重新核验设备并测早期队列对照，再做完整GUID point20的2/7/2延时对照（正常完成兜底固定7秒），有响应后才推进驱动返回/协议状态。单次7秒返回无法区分目标和兜底；卡死仍须按硬停规则停止并恢复。没有待批的新内存/verified/破坏性操作。

设备上一里程碑e197e02已推送；本轮发布见Git/WORKLOG。参考仓只读。

发布核验：固件6bc5b81已推送；源码CI39911281252成功并回读PASS（仅源码契约）。GUID-only候选FD审计30个原厂PE/DEPEX逐字节、192字节BootShim+3MiB FD及AOSP v3打包回读通过；全部新镜像未启动。编译宏取自实际DxeCore clang响应文件并随私有归档保存。
