# D-214：结合公开实现后的显示与日志优先级

本次为固定公开源码和选定enuma的只读核对。没有新boot、模块加载、物理内存内容读取、RAM写入或内存表修改。S-013/S-014的已消耗账本和最近独立Android恢复结论不变。

## 新增事实：原生ramoops后端已存在

此前只从活动FDT没有ramoops节点记录缺口，漏查了厂商内核可能通过命令行/硬编码建立的后端。本次实际root只读查询：

- `/sys/module/pstore/parameters/backend`为`ramoops`；命令行有`ramoops_memreserve=4M`。
- ramoops参数：`mem_address=2952790016`即`0xB0000000`，`mem_size=4194304`，console/pmsg各2097152，record/ftrace为0、ECC为0、mem_type为0。
- 仅读取`/proc/kpageflags`的1024页元数据，全部报告KPF_RESERVED；未读取这4MiB的物理内容。`/sys/fs/pstore`当时为空，不证明保留链失败或成功。
- 当前Linux后端存在、参数和页标志不是UEFI映射/缓存/写入资格，也不是跨复位保留证据。当前固件显式表没有专用Ramoops记录；后续还需核实际映射、分配排除与所有权，不能按别机地址直接写。

证据[enuma-ramoops-route-discovery.json](../../reports/enuma-ramoops-route-discovery.json)。这是与旧R-002的`0x9fff7000` Log Buffer不同的区域和Linux管理路径，旧标记失败不能直接否定它。它也尚未建立新的完整UEFI日志通道。

## 值得继续的排序

| 优先项 | 可复用的实际公开实现 | enuma下一步及边界 |
| --- | --- | --- |
| 日志首选：原生ramoops SerialPortLib | [umi固定3eb7257的RamoopsSerialPortLib](https://github.com/reAAAq/UniXNU-umi/blob/3eb72578597d2ca16471b172d45eddc096a34a04/overlay/Platforms/Xiaomi/umiPkg/Library/RamoopsSerialPortLib/RamoopsSerialPortLib.c)：12字节header、环形边界、签名、关中断与barrier；不依赖Boot Services/屏幕/存储 | 本机几何与其首2MiB console/后2MiB pmsg相合。先审本机内核格式、缓存、映射、保留与读出时机，再设计最小marker；不写pmsg、不抄内存表。warm存活仍需实测，源码本身也明确不能保证每笔保留。此路线可能避开旧方案所需的临时FDT/自定义reader问题，但当前不能保证无需任何内存表审查 |
| 点屏主线：继承scanout并恢复真实GOP/最小文字 | [cas固定893f502的DisplayHardware](https://github.com/ht94911/uefi-cas/blob/893f5025cea91a121f2566730779cb34955325fb/Platforms/Xiaomi/casPkg/Library/CasDisplayLib/DisplayHardware.c)，以及其纯Decode/Blt、阶段/错误十六进制标记；同SoC有菜单/EFI返回记录 | 本仓已复用这条路线，当前增量是独立原生活动/双窗计数资格，修正过强Enable前置后再审实际地址/布局。enuma双DSI video不同于cas命令刷新，禁止复制CTL_START、物理地址、尺寸或闲置银行读取。最小文字/阶段字比完整图形菜单更早有价值，但仍依赖真实可用帧缓冲 |
| 独立支线：I2C背光 | [小米52a2f18 KTZ8866驱动](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/drivers/video/backlight/ktz8866.c)给出器件行为；[fajita固定fb8c389的GENI FIFO核心](https://github.com/johnpanos/UniXNU-fajita/blob/fb8c389bd9877d4db0ef6e09170b83752dec7259/drivers/NativeGeniI2c/GeniI2c.c)提供轮询传输、超时/错误处理的BSD实现 | 优先核原厂I2C PE的真实协议ABI及应答，必要时评估可移植FIFO核心，不从零发明控制器。fajita为不同SoC，时钟、SE、GPIO、电源、FIFO能力和中断策略必须逐项核本机；LinuxGPL器件代码作为行为参考，直接移植须处理许可。旧R-012批准不当作任意控制器/时钟写范围扩张 |
| 有条件后备：原厂DisplayDxe运行环境 | edk2-msm提供Qualcomm模块组合/依赖组织，原XBL PE和本机XML已在本地 | 先有日志，再查真实构造器、HOB、锁/调度/电源服务和出错返回。不原样重复R-014、S-002或补空GUID。闭源PE存在、排队、进入和完成初始化分开记录 |
| 外接UART | 可绕过显示获取早期文字，但当前只有本机软件配置线索 | 测试点/TX-RX/电平和实际GENI后端成立时优先级可提升；现阶段不能由公开别机引脚常量补齐物理证据 |

## 后置项与取舍

USB CDC设备后端可以作为独立专项，但目前的上游主机终端和别机后端不能直接生成enuma早期日志。QR/AdvancedLogger导出器留待GOP、菜单和producer可用后接入；完整重写MDP/DSI/panel栈的范围远大于继承或窄背光，不作为下一步默认方案。

建议推进顺序：日志侧先完成原生ramoops的只读/离线兼容审计；显示侧继续已收敛的原生活动/计数与继承GOP；独立背光先做I2C协议资格。ramoops对当前问题有最大新增信息价值，但仍不能称已通过固件写入或跨复位读回。涉及新内存表项/地址字段或写入时，沿AGENTS给出具体审查和批准范围；本次没有提出审批问题，也未更改任何字段。

固定来源的git blob与本地文件一致性已重新检查，记录[enuma-public-route-priority-review.json](../../reports/enuma-public-route-priority-review.json)。官网/公开仓其他设备的成功仍不等于本机资格。原始影音只留本地。
