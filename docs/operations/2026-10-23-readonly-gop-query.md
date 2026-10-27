# SimpleFb 只读 GOP 运行时审计

## 范围与实现

前序17/16/17仅支持最终StartImage非错误；本次增加实际协议查询。
固件250849f223198f2b89c94f2eb49b6b0daf22d447，沿用SimpleFb提供者、
现有契约修复、完整GUID过滤、TimerLib/PSCI两秒复位和Dispatcher正常完成后七秒兜底。
参考复用仍限既有同SoC SimpleFb方案，不引入其他设备的地址、面板参数或实测结论。

`diagnostics/EnumaGopAudit.h`在SimpleFb成功安装协议之后只读检查：

- LocateHandleBuffer(ByProtocol, GOP)恰好一个句柄，并匹配安装时的ImageHandle。
- HandleProtocol返回实际SimpleFb GOP实例，Mode/Info/QueryMode存在。
- 单模式0、版本0、结构长度、非零宽高、stride、BGRX32及帧缓冲跨度算术一致。
- QueryMode当前模式成功，返回长度及所有定义的字段与当前Info相同。
- 查询信息和枚举列表临时分配均释放，FreePool错误也归为审计失败。

不访问物理帧缓冲、不调用Blt/SetMode、不读取MMIO，不新分配物理保留区。
Mode几何来自现有PCD构造，本次一致性通过仍不能证明1600×2560是真实scanout。

选择器1在上述合取通过后复位；选择器2在审计错误时复位。二者都要求
metadata-only、stage13/detail16/delay2、完整SimpleFb GUID、GUID-only和完成兜底。
Core原状态门在查询变体中禁用，避免Load/Install失败触发状态门、冒充审计结果。
未命中时保持原驱动返回值，继续到完成兜底。不能在安装后简单返回新错误：
Core可能卸载驱动，令已发布的函数指针悬空。同步兜底仍不能救驱动卡死。

## 主机验证和复现

`scripts/check_gop_audit.py`：固定Mu归档真实头，33元数据故障/正常用例、
3无效参数，ASan/UBSan；AArch64 COFF对象检查且仅导入GOP GUID。
组合实际contract/query补丁，提取实际安装后门代码，验证六组成功/warning/error选择。
另有六组不安全CLI组合在任何来源导出或设备操作之前被拒绝。
`scripts/check_dispatch_details.py`补充查询选择器下Core门禁用检查，并保留原有回归。
公共报告分别为`reports/enuma-gop-audit-host.json`和`reports/enuma-dispatch-details-host.json`。

固件构建命令使用本仓WSL虚拟环境Python，两个候选仅改变`--diagnostic-gop-query 1/2`：

```text
scripts/build_enuma_firmware.py --reference /mnt/d/Code/PortingiOSLegacy/common/sources/mu-nuwa-firmware --unixnu /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/sources/UniXNU --stop-stage 13 --stop-delay 2 --dispatch-ordinal 1 --detail-point 16 --dispatch-guid dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92 --dispatch-guid-only --dispatch-completion-fallback --diagnostic-simplefb --diagnostic-gop-query 1 --jobs 8
```

之后逐项运行FD审计、BootShim载荷准备、v3打包，完整报告与镜像留在out。
board正式默认显式关闭四个诊断选择，不修改example、内存或verified。

## 实机门禁与判读

仅临时fastboot boot；每笔相机先启动，再由既有runner重新核对enuma身份、
boot完成、root、解锁、槽、原备份及boot/vendor_boot摘要。通过/失败/相同通过镜像
的互补顺序用于区分谓词响应与正常完成兜底。无返回立即停追加，优先恢复。
恢复后继续核对Android完成、root、原摘要。录像原件和设备标识仅out。

短返回只能结合互补组支持审计谓词；长返回不单独证明失败分支或精确七秒命中。
没有传输数值GOP快照，不能称已读到屏幕上的模式数值，更不能称像素、菜单、BDS或XNU通过。

本文件后续追加实际构建和试验结果，未记录的步骤保持未验证。

第一次019191f目标构建在INF元数据解析阶段失败：固定Mu把`!if`行当成库名，
error4000。没有完成链接或启动设备；失败报告/完整日志留在out/gop-audit-first-failure。
250849f改为普通BaseLib/TimerLib/ResetSystemLib依赖声明，执行逻辑仍由默认0守卫。
此失败不计实机试验，也不隐去或称构建通过。

## 实际结果与恢复

两候选完整构建/源一致/30OEM/FD/BootShim/v3通过，155组诊断回归与串行workspace通过。
2026-10-23 19:45:38仅启动选择器1，75秒未见ADB或fastboot，runner退出2，立即停止追加。
用户反馈人工恢复Android；2026-10-23 19:48:15主机确认身份、完成1、root、解锁、原槽及原boot/vendor_boot摘要。
选择器2未启动，没有形成互补时序，不能断言GOP检查通过或失败。
录像cde4834a907a56f19fc03423e48b09e37e98e7ea67f9a63ae58601a779e0cc67，约94.955秒，抽查20/40/80秒黑屏；非逐帧无输出证明。
实机/镜像摘要及恢复字段见reports/enuma-gop-query-device.json。

AutoGen与静态库清单确认新增TimerLib为ArmArchTimerLib、ResetSystemLib为ArmPsciResetSystemLib，
PcdMonitorConduitHvc为0；存在ArmPsciResetSystemLibConstructor。源码构造器只返回成功，
这些离线事实仍不能排除依赖/构造器/复位路径的实际问题。
故障范围包括进入新增调用前、LocateHandleBuffer、HandleProtocol、QueryMode、FreePool、
本地Timer/PSCI门及更早执行路径，当前没有足够日志定位。

后续先离线拆分，优先考虑将结果门留在已验证Core位置，避免提供者新增复位依赖；
或先观察审计前/各服务调用边界。任何具体方案仍先完成完整构建和恢复条件审查，
本轮不再启动镜像。无新内存/verified变更，无需新增编号审批。

用户更新录像策略：无屏幕日志时必要截图+主机时序即可，实际画面变化或恢复操作再录像；
电源键位于屏幕右上角，用明确可见动作作证，不凭遮挡/窗口外断言。
