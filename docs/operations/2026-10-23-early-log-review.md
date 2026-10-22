# R-002：早期日志的保留内存与回读路线

状态：approved，2026-10-23。用户已批准 R-002；以下保留原审查方案与当时事实。随后完成限定配置及临时 FDT 保留，实测与用户要求停止的当前状态见 [实测交接](2026-10-23-log-reservation-validation.md)。未读写物理日志或加载模块。

## 为什么到了审查点

完整GUID与延时对照支持走到UFSDxe、UFS隔离模式下DisplayDxe的CoreStartImage调用前，返回后未观察到命中。它仍可能停在公共启动包装器、库构造器或驱动主体，不能靠定时门得出具体寄存器/协议/异常位置。Metronome早调度未解决UFS边界，排除UFS后显示链仍有未闭合点。下一阶段需要可回读的早期日志。

已有实际证据：

- 本机OEM表的`Log Buffer`为`0x9fff7000`、`0x8000`（32KiB），UEFI类型RtData。这是来源事实，尚无运行中GetMap证明。
- 当前Android FDT的`/memory`覆盖它；reserved-memory没有覆盖节点，FDT头部reserve map也为空。
- 已采集`/proc/iomem`将它归入System RAM。只读查询8页`/proc/kpageflags`，目标内核头定义的KPF_RESERVED=32，在8页上均为false，部分页已是普通LRU/映射页，另有buddy页。因此不能直接把这里当跨重启保留日志来写或读取内容。
- Android没有/dev/mem、/dev/kmem、/proc/kcore；实际4.19.157-perf-gf8cf95f4dc15内核开启MODULES/MODVERSIONS/IKHEADERS，未开启MODULE_SIG，已只读取回3433340-byte匹配头文件（SHA256 e2482393e1d7ae0d2ec9c8155f940ae70317c907f54ef4f04f186f3c3db63c5c）。回读模块、符号CRC匹配和临时FDT引导封装尚未实施，不把这些条件当作模块可加载证明。

审查来源为[AGENTS.md](../../AGENTS.md)的明确规则：`修改任何 bringup-plan.json / board.toml 中内存大小或基址字段`须先记录再确认。A-002继续覆盖镜像生成和可恢复临时启动，R-001的512MiB预算不包含新增日志地址/大小配置。

## 两条路线

| 路线 | 工作与代价 | 限制 |
| --- | --- | --- |
| 软件保留日志，推荐 | 在临时Android启动时保护已有OEM日志候选32KiB；匹配实际内核ABI构建只读回读模块；先验证标记跨复位存活，再接入固件日志/异常打印。无需先拆机 | 需要新增保留内存配置及临时FDT封装；Bootloader可能清空此区，必须先做存活试验，不能保证可用 |
| 外接UART | 先核对enuma接点、电平、真实串口实现，再由人工连接串口采集启动/异常输出 | 需要硬件和人在场；接点与电平尚未确认，不提供猜测接线，也不宣称现有NullSerial会输出 |

## 推荐路线的最小批准范围

1. 只允许在board增加独立诊断配置，地址/大小严格限定为已有OEM候选范围`[0x9fff7000, 0x9ffff000)`，32KiB。精确拟议字段见[提案补丁](../proposals/R-002-board-config.patch)，仅为提案，尚未应用，也尚未接入功能。默认enabled=false，诊断须显式选择。
2. 只在临时Android诊断启动的FDT中对同一范围建立保留；不改变DRAM银行范围、UEFI FD/栈/heap、既有MemoryMapLib或512MiB owned请求。实现须保留stock vendor_boot及原分区，无法在临时镜像契约内安全实现时另停审查，不转为flash/erase。
3. 先验证临时Android实际FDT和页状态已保护该范围，再验证完整内核版本/符号版本的正常模块加载。首次仅用最小标记和只读回读，不对仍是普通RAM的页面操作；不强载ABI不匹配的模块。
4. 只有标记跨复位存活且回读可用，才在同一范围接入有界固件日志/异常记录。若Bootloader清空候选区、映射或ABI不满足，停止该路线并报告，不自行换地址、扩大范围或借用显示/SMEM等已有所有者区域。
5. 保持example=true、owned_memory_size=0x20000000、所有 *_verified 标记不变；只沿A-002进行带身份/备份/恢复检查的fastboot boot。没有flash/erase/改槽授权扩张。

本次批准针对新增诊断内存配置和以上有界验证；不是“地址已实机验证”或“持久日志已经可用”的批准。

## 已备好供审阅的工作

- 原UFS与Display入口边界、所有时序样本、FD/镜像摘要已归档；42项Python、真实头20组sanitizer、32/33OEM审计与负向缺项检查通过。
- 默认固件保留原生UFS，隔离变体显式声明唯一缺项，未用空实现替代。
- `scripts/audit_log_reservation.py`可从固定FDT、OEM表、实际页标志和实际内核头复算当前“不安全直接使用”的结论；它只读输入、写报告，未改变配置或设备。
- `reports/enuma-log-reservation-audit.json`、`enuma-log-readback-capabilities.json`、`enuma-reset-reason-comparison.json`与拟议board补丁已备好。内核头、配置、标识和原始日志仅在out/。

等待R-002选择期间不启用内存日志、不改任何真实内存字段。设备保持已恢复的Android，无待按键事项。
