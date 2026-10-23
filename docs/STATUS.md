# STATUS

更新：2026-10-23（Asia/Shanghai）。当前唯一真相，历史见WORKLOG。

## 当前状态

**继续离线主线，本轮零设备查询、启动或写入。** 最近实机证据仍为12:11:03人工按键恢复后核验enuma/完成1/root/槽_a/解锁/原boot与vendor_boot摘要；不是本轮实时连接状态。233a9d8首测未自动返回仍为历史失败，GOP/BDS/XNU均未通过。

## 本轮完成

固件gitlink82ce8a5、50项源锁。复现并修复SimpleFb静态配置大小导致失败清理后真实Mu库重试失败；新增拟暴露帧缓冲跨度≤原描述符Length、乘法/区域端点溢出检查。没有修改内存表或引入地址，不据范围约束宣称像素归属正确。默认原生33与无UFS32不变，SimpleFb独立诊断保留30 OEM，Blt禁像素和Probe早退保持。

新增真实Mu配置前缀+完整SimpleFb+固定DarwinBoot视频helper的host联测，基线两问题可复现，修复后三种配置ASan/UBSan通过；合成BGRX视频元组及拒绝格式/跨度通过，真实scanout仍未知。完整驱动/组合patch、50项Python、50源锁和串行workspace检查通过。资格校验会临时apply/reverse同一out上游补丁，build与workspace检查须串行。

实际AArch64/backend还原、30 OEM/FD/BootShim/v3通过，FD 75c34141a785d4dc38f1475e6ce1a60b894f30db98c18b58926958c6e2bd203f；补丁后实际编译SimpleFb与host源相同。源码CI39912601757回读PASS，仅源码验证。实际AutoGen两构造器和Null串口绑定已审计，不等于实机执行。所有新镜像仅归档未启动。

详见[真实库与loader交接](operations/2026-10-23-simplefb-loader-handoff.md)、[机器证据](../reports/enuma-simplefb-loader-bringup.json)。这两个缺陷不等于首测黑屏根因已找到，尤其重试问题不必在首次调用触发。

## 仍有效的主线与边界

6bc5b81的完整GUID-only选择保留实际句柄/detail/status守卫；可选正常Dispatcher结束7秒复位在架构协议检查/BDS之前，默认关闭，不能处理卡死。旧序号32未校准，仍不能解释为新SimpleFb执行事实。7479da1早期队列对照及后续GUID候选都未实测；上轮147组头测试对应头文件本轮未变。

Native Display历史仅调用前/canary前缀门支持；同Mu pool成功门有延时响应，失败门未观察，不构成扩堆依据。51MiB DXE Heap、512MiB owned、内存/example/verified均不变。R-002跨Bootloader不保留，日志路线仍停，不换址/扩大/借DFPS或SMEM。TWRP/UART未验证。

目标enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB、UniXNU5fdbd5d/21模块。实际scanout六项、UEFI map/窗口分配、EBS、GOP可见、BDS、XNU及NT36523仍待实机。

## 下一步

保持既定离线范围。恢复实机工作后重新核对身份/备份与恢复条件，先早期队列对照，再完整GUID point20的2/7/2；确认后推进驱动返回/唯一GOP字段、真实显示、GetMemoryMap与512MiB窗口/EBS，最后XNU入口。单次7秒返回不能区分目标与正常完成兜底；卡死立即恢复并停追加。没有新的内存/verified/破坏性操作审批项。

设备上一里程碑00505f8与固件82ce8a5已推送，本轮设备发布见Git/WORKLOG；参考仓只读。
