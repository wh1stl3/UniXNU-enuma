# enuma SMP 就绪度（2026-11-23）

**评级：需先补证据，不直接试。** 本次只读静态检查，无构建、设备访问或运行时 processor count；r54 单核仅是静态推断。需先核对 r54 实际 ADT 的 PSCI/GIC 值与 CPU affinity，证明本板跨核 IPI 路径，并专项审查启用后的 UFS/显示及其他共享状态并发。不能将其他设备的 IRQ 或参数作为 enuma 硬件证据。

## 已链接与补丁边界

`out/ufs-sm8250-fbfill3-20261123-r54/native-link.map:1023,31983,31996,71136-71138` 显示 ArmCpu.o、`sheng-smp`、`sheng-smp-gic` 字符串及 `finishSecondary`、`startSecondary`、`startThread` 符号已链接。`:48817` 有 `_thread_group_set_default_preferred_clusters`，与 `../UniXNU-sm8250-common/patches/xnu/native-smp-type-clusters.patch:94-109` 新增符号对应，是类型集群补丁相关代码进入链接的直接证据，但不证明所有 hunk 生效或运行时使用。

`../UniXNU-sm8250-common/patches/xnu/native-smp-secondary.patch:1-23` 将 MAX_CPUS 4 改 8、BCM2837 reset MPIDR mask 改 `0xffff`；本次没有得到 r54 reset 入口的反汇编或编译期 MAX_CPUS 直接证据，因此**不能判定该补丁在 r54 完整生效**。`native-smp-type-clusters.patch:9-18` 编译期设两个 cluster 和 AMP；符号证据同样不能代替全部宏和拓扑行为核验。共享仓 `patches/xnu/series:2-3` 列出补丁不等于该候选必然应用。

## 消费路径和失败模式

以下是活动基座 `D:/Code/PortingiOS/UniXNU/drivers/ArmCpu/ArmCpu.cpp` 源码，链接图证明有 ArmCpu，但本次未逐字节比对 r54 归档与该源码，具体源码对应关系仍需确认。

* `:209-227` 的 `probe`：`PE_parse_boot_argn ("sheng-smp", &smp, sizeof (smp));`，secondary 在 `smp == 0` 或逻辑 ID 无效时返回 nullptr。
* `:393-466` 的 `start`：secondary 排队；boot 先准备 GIC、读取 `sheng-smp`/`sheng-smp-gic`，建 IOCPU interrupt controller、注册 boot CPU 并 drain。控制器分配、IRQ 注册或 boot CPU 注册失败会 panic。
* `:469-497,530-553` 的 `finishSecondary` 注册 CPU 与 topology 的 physical/logical/cluster 信息，创建 helper；`processor_start (self->machProcessor);` 的源码注释明确称未抵达 scheduler 时仅该 helper 卡住，但其他子系统是否因此等待，未验证。失败有 `armcpu_smp_fail`/PSCI rc 记录，不保证屏幕可见。
* `:500-513,812-827` 从 ADT `/psci:method` 接受 `smc` 或 `hvc`，`startCPU` 调 PSCI CPU_ON（`0xc4000003`），传 reset vector 物理地址。缺 method 返回 `KERN_NOT_SUPPORTED` 和 -1001；PSCI 非零返回失败。此实现走 PSCI，未见 spin-table 路径；不证明固件实际支持。
* `:556-579` secondary 核对 MPIDR，唤醒本核 redistributor、使能 GIC、安装中断、启用 timer、标 running；MPIDR 不符或 redistributor 失败则 park。`:662-674` 默认发 SGI；SPI IPI 是显式开关。`:577-579` 注释说明首次 IPI 清 `SIGPdisabled`，`armcpu-self-ipi=1` 才主动发送；可用 IPI 和芯片路径必须本板验证，不能凭参考配置选值。`:603-659` 意外 architectural IRQ 会 panic。
* `:530-542` 的 `armcpu-edge` 另控所有 secondary 完成后的 `ml_cpu_init_completed`；缺省不调用，不能把 cluster-type 填入等同于调度迁移已工作。`pmgr` 并未出现在上述 CPU_ON 直接调用链，不能据此断言整个系统不依赖电源初始化。

## ADT 与依赖

共享源 `../UniXNU-sm8250-common/dts/sm8250.dtsi:15-33` 有 `cpu@0,100,200,300,400,500,600,700` 和 `psci { method = \"smc\"; }`；板级 `dts/enuma.dts:8,32-35` 引入它但仍标 CPU 启用待办。历史 ADT 对照 `docs/adt-full-diff-20261123.md:139-145,188-235` 列 `/arm-io/intc` 和 `/cpus/cpu0` 至 `/cpus/cpu7`；`docs/SESSION-HANDOFF-20261120.md:46` 记录一 running、七 waiting，无 cluster-type。**这些不是 r54 ADT 的直接解码**，r54 `/psci` 是否存在及其值、各节点 affinity、GIC 资源和节点值均未核，不能说 r54 全齐。缺 CPU nub 会少核；缺 cluster-type 时补丁注释 `native-smp-type-clusters.patch:11-13` 描述单 cluster 回退，而非必然启动失败。核对本板 E/P 划分后再决定是否补属性，不把它写成仅运行 secondary 的已证硬前置。

## 并发风险及回退

secondary 成功上线后原先仅以单核运行过的 UFS、显示、驱动轮询和共享缓冲会并发；尚未逐一审查，不能认定有具体死锁，也不能认定安全。具体已有示例：`ArmCpu.cpp:576,621,627,671` 对跨核运行的全局诊断计数使用非原子读改写，可能丢计数，因此不能单靠这些计数断言精确 IPI 数；`:605-619` 中断 drain 循环持续等待 spurious ID，异常持续中断可卡住，诊断参数开启时才有百万次 panic。IPI 丢失可导致跨核信号/等待不推进；早期 reset、GIC、锁或并发故障可导致卡死或 panic，具体触发须另证。

`sheng-smp` 不传或设 0 时 ArmCpu probe 拒绝 secondary，故**逻辑上可通过参数回退**；若参数嵌在不可编辑的既有载荷，则须重新打包或换回已有单核镜像，不一定须重编内核；其他 CPU 驱动是否抢占 secondary 也须核实，不能保证仅改参数必然安全。

## 对照与下一步

`docs/missing-bootargs-and-fdrloader-20261123.md:7` 记录 sheng、sirius、pipa 配置 `sheng-smp=1`，不是三者实测均成功的证据；`docs/repo-diff-adt-bootargs-20261123.md:80,178` 的 sirius 另用 `cpus=8`、`armcpu-self-ipi=1` 和本机 timer 值；pipa `docs/pipa-cs-dyld-diff-20261123.md:9` 指出其补丁文件存在不证明实际应用。`docs/SESSION-HANDOFF-20261120.md:46` 的历史方案提 `armcpu-spi-ipi=1`，只作待核假设，不是本板已验证配置。

先完成 r54 ADT/两补丁机器码核验、IPI 路径及并发 deep review；再设计可观察每核 PSCI 返回值、进入阶段、running 和往返 IPI 的独立单次临时实验，保留原单核镜像；设备 boot 须另获当轮授权。无运行验证，self-checked。
