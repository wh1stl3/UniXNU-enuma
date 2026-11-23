# enuma r61 多核条件清单（2026-11-24）

状态：self-checked，纯静态调查，不构建、不访问设备。r61 是 r58 原内核和 ADT 的参数重打包；`docs/enuma-r61-smp2-host-20261124.md:7-20,29-39`。下文区分实际包证据、共享 DTS 的输入值、生成器逻辑和运行时事实；共享 DTS 不能替代对 r61 ADT 字节解码或真实寄存器的验证。`UniXNU` 指 `D:/Code/PortingiOS/UniXNU`，`ArmCpu.cpp` 指该树 `drivers/ArmCpu/ArmCpu.cpp`；共享仓指 `../UniXNU-sm8250-common`。r58 实际编译源码与活动树完全一致尚未以逐字节对照证明。

| 项目 | ADT/代码现状 | 判定 | 依据（文件:行） | 若出问题的症状 |
|---|---|---|---|---|
| CPU 数量及 affinity | r58 ADT 有 cpu0–cpu7，r61 复用；共享 DTS 八个 `cpu@0,100,200,300,400,500,600,700`，`reg` 分别 `0,100,200,300,400,500,600,700`（十六进制）；A55 四、A77 四。实机既有 FDT/频率记录 4+3+1，与数量及四小核/四大核一致；共享 DTS 未区分三个 Gold 与 prime。实际 r61 每个 reg 值尚未独立解码。 | 部分 | `docs/enuma-r61-smp2-host-20261124.md:7-9,34`; `../UniXNU-sm8250-common/dts/sm8250.dtsi:15-30`; `porting.toml:85` | 错 affinity 时 secondary 不启动、MPIDR 不匹配或少核 |
| enable-method / idle 描述 | 上述共享 DTS 八个节点均未声明 `enable-method`、`cpu-idle-states`；生成器只复制 reg/state/compatible/timebase 和可选 cluster-type，不输出这两项。代码使用独立 `/psci`，不根据 CPU 的 enable-method 选 spin-table；idle 状态不等于冷启动必要条件。实际 r61 属性逐项未解码。 | 部分 | `../UniXNU-sm8250-common/dts/sm8250.dtsi:20-33`; `UniXNU/scripts/unixnu/devicetree.py:341-369`; `ArmCpu.cpp:500-513,812-827` | CPU_ON 不成功或休眠/恢复不可用，具体原因未定 |
| 拓扑/调度 | DTS 未列 cluster 层级或 `unixnu,cluster-type`；r58 ADT 无 cluster-type。生成器仅在有 E/P 时写入；补丁注释指出无类型回退单 cluster，scheduler 在 E 或 P 任一缺失时直接 return，保持 boot cluster 偏好；不是缺属性就不能起第二核。 | 部分 | `../UniXNU-sm8250-common/dts/sm8250.dtsi:15-31`; `UniXNU/scripts/unixnu/devicetree.py:355-360`; `../UniXNU-sm8250-common/patches/xnu/native-smp-type-clusters.patch:9-18,67-90`; `docs/enuma-r61-smp2-host-20261124.md:9` | 异构调度/性能不理想；不能据此断言启动失败 |
| GIC redistributor | 共享 DTS distributor `0x17a00000+0x10000`，redistributor `0x17a60000+0x100000`，stride `0x20000`，数学上容纳八帧、包含第二帧；代码按 GICR_TYPER affinity 搜索，不按 CPU 序号保证命中。历史实际 ADT `reg` 32 字节；r61 具体范围、真实 affinity、MMIO 可访问性及中断投递均未实测。 | 部分 | `../UniXNU-sm8250-common/dts/sm8250.dtsi:41-50`; `docs/adt-full-diff-20261123.md:139-145`; `ArmCpu.cpp:240-273,310-343,556-567` | GIC 初始化失败、secondary park、无定时中断 |
| PSCI 和提供者 | 共享 DTS `/psci` method=smc；多核生成器要求有该节点，ArmCpu 不设默认 conduit，发 SMC64 CPU_ON `0xc4000003`。PSCI 实际由何固件层/安全监控实现及 r61 运行时 CPU_ON 支持、返回值未验证；不是由 ADT 声明推导 UEFI 或 iBoot 是实现者。 | 部分 | `../UniXNU-sm8250-common/dts/sm8250.dtsi:33`; `UniXNU/scripts/unixnu/devicetree.py:365-369`; `ArmCpu.cpp:500-527,812-827` | 缺节点 rc=-1001；固件拒绝 CPU_ON 或 secondary 未进 reset |
| SPI IPI 路由/冲突 | `armcpu-spi-ipi=1` 对逻辑 CPU0/1 选 INTID 1008/1009；设置 group 1、edge、priority、IROUTER affinity 和 enable，用 GICD ISPENDR 软件置 pending，handler 调 ipi_handler；`armcpu-self-ipi=1` 首次自身发 IPI。未证明 GICD_TYPER 支持到这些 INTID、本板已保留或与其他设备无冲突；不能据共享 DTS 没列出便断言无冲突。 | 未验证 | `ArmCpu.cpp:95-127,393-403,556-579,632-637,662-673` | 自 IPI 不达则 SIGPdisabled 未清，跨核信号不推进、挂起/中断风暴 |
| 电源/时钟及 idle | CPU_ON 直接路径无 pmgr/clk 配置；PSCI 后端是否负责 rails/clocks 未证。`sheng-pmgr=2` 不等于 CPU 电源实现：板级 bridge 的 CPU core/cluster/idle 方法调用 unavailable；`pmgr` 与 `sheng-pmgr` 是不同参数，不能混为一谈。缺硬件 PM domain 证据，不认定必需直接操作。 | 未验证 | `ArmCpu.cpp:812-827`; `package/ShengPlatformPower.cpp:52-59,82-85,127-135`; `docs/enuma-r61-smp2-host-20261124.md:20` | 不上电/不启动；idle 或 resume 调用触发失败 |
| 编译容量 | 补丁指定 `MAX_CPUS=8`、reset MPIDR mask `0xffff`；ArmCpu 的 `ARMCPU_SMP_SLOTS=8`。r58 构建树头文件和链接符号证据支持，但无该次目标编译命令/二进制 reset 指令的完整复核。 | 部分 | `../UniXNU-sm8250-common/patches/xnu/native-smp-secondary.patch:3-23`; `ArmCpu.cpp:51`; `docs/enuma-r61-smp2-host-20261124.md:9` | 核数量截断、reset 映射错误或卡启动 |
| coherency | secondary MMU/cache off 时，启动代码对 reset vector、ResetHandlerData、boot args `dc civac` 清理；不证明上线后的硬件跨核 cache coherency、内存属性与同步协议正确。 | 未验证 | `ArmCpu.cpp:799-825` | secondary 取旧入口/数据，或上线后数据竞争、死锁 |
| timebase / PMU | 共享 DTS timebase 19.2MHz；secondary `enableCPUTimeBase` 打开虚拟计时器，handler INTID 27 调 rtclock；每核计时器频率/同步和中断均未证，PMU 配置与可用性未证。 | 未验证 | `../UniXNU-sm8250-common/dts/sm8250.dtsi:15-18`; `ArmCpu.cpp:569-574,620-625,775-779`; `../UniXNU-sm8250-common/patches/xnu/native-smp-secondary.patch:11` | timer 不推进、调度卡住；PMU 统计不可用 |
| `ml_*` 初始化与参数选择 | `cpus=2` 留 boot CPU 并按拓扑选择最多两核；`cpumask` 与 `cpus` 同时出现会置配置错误、稍后 panic，r61 参数仅前者。secondary 经 processor_start 后仅 `armcpu-edge` 非零才在全部核启动后调用 `ml_cpu_init_completed`；r61 未列该参数。 | 部分 | r58 构建树 `.cache/xnu-work/osfmk/arm64/machine_routines.c:1002-1015,1029-1061`; `ArmCpu.cpp:530-543`; `docs/enuma-r61-smp2-host-20261124.md:15-20` | 参数冲突 panic；processor_start helper 卡住；多 cluster edge 未初始化 |
| 并发安全 | 两核运行使此前单核路径实际并发；本轮没有验证 UFS、显示、驱动及共享状态，已有 ArmCpu 某些诊断计数非原子，不能用其证明精确 IPI 次数。deep review 待完成。 | 未验证 | `docs/smp-readiness-20261123.md:26-28`; `ArmCpu.cpp:575-576,620-634,671` | 上线后卡死、数据竞争或计数丢失，不可凭现象直接归因 |

## 风险排序与首查

1. **PSCI CPU_ON → secondary reset/MPIDR → GICR**：有无到达 `armcpu_smp_step` 4/5/6/7、PSCI rc 和 fail；这些是源码内诊断状态，不保证屏幕可见，也不意味着允许额外设备操作。
2. **INTID 1008/1009 可实现、无冲突、可双向投递**：GICD_TYPER、路由及往返 IPI 的本板证据缺失。
3. **上线后的并发/coherency**：启动成功并不等于多核安全，尤其既有 UFS/显示共享状态；需 deep review。

若 r61 卡启动，先按末条可见日志定位是 CPU_ON 前、secondary reset、GICR 还是上线后，再优先查第 1 项的现有 step/rc/fail 记录；现有记录不可见时不能凭卡住直接归因。r61 已有 `armcpu-diagnostics=1` 也不提供正向 CPU 上线屏显保证（`docs/enuma-r61-smp2-host-20261124.md:43-51`）。

计数按表格 12 行：具备 0、部分 7、缺失或未验证 5。这里只表示证据完备度，不是硬件故障统计。
