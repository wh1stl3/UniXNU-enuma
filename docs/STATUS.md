# STATUS

更新：2026-10-22（Asia/Shanghai）。当前唯一真相；历史见 WORKLOG。

## 当前结论

**512 MiB 配置已按 R-001 落实，DarwinBoot 内存交接约定已通过主机检查；尚无可启动固件。** Kona 固件源码增量和 SM8250 板级支持代码已落地。 目标保持 iPadOS 17.7.11 / 21H461、iPad7,1 / j120ap、XNU 10063.141.1、4 KiB。只做离线工作，未访问设备。

## 已完成

- 512 MiB 请求进入 ADT 输入计划：/chosen/darwinboot-memory-size，LE uint64。固定 DarwinBoot 的真实 AdtNode、RunEnd、AllocateWindow 函数通过 ASan/UBSan 主机测试，覆盖144种截断、重复/错位属性、保留洞、相邻描述符、对齐和失败处理；没有生成 ADT 文件或实际 UEFI 分配。

- 固件继续使用 UniXNU/uefi-sheng 329b473d 中的 KonaPkg；Mu_Basecore cfb93724 与 UniXNU feeds 匹配，无需升级底座。选定 Kona/alioth 文件与 Mu-Silicium 42fe5637 相同。
- enuma DSC 和 FvMain 均接入真实 UniXNU app、UniXNUDxe、DarwinBoot；平台/厂商输入缺失时拒绝构建。没有借用 alioth 内存图或二进制。
- Kona PlatformSec 最小补丁保留显示 SMMU 映射；精确应用及三种预处理分支检查通过，watchdog 行为保留。尚不证明显示能保持到 XNU。
- EnumaGeniSpi 复用 NativeGeniSpi，增加本板 FIFO/PIO 入口、mode0/CS0 实际配置和错误后失效处理。EnumaUfsClock 提供九项 Kona GCC 只读快照；偏移逐项与固定厂商源码比对。
- 上游 GENI 寄存器模型、本板适配和 UFS 快照的 ASan/UBSan 检查通过；三个 freestanding AArch64 对象编译通过。不是 IOKit/固件链接或硬件结果。
- 固件增量七项检查测试通过；完整镜像前置检查按预期拒绝。选定来源可从锁文件重取，参考仓保持只读。
- 首轮 donor 六组件/两个 DMG 摘要、FDT 4613 节点、GIC/PSCI/timer/CPU 计划及 example 防护继续有效。

复现和证据：[内存交接检查](operations/2026-10-22-owned-memory.md)、[固件与驱动报告](operations/2026-10-22-kona-platform.md)、reports/。已按 R-001 配置 512 MiB owned-memory 请求，物理基址与总 DRAM 未设置；未生成镜像，未设置任何 *_verified=true。

## 下一步与待决项

1. **R-001 已批准并落实**：owned_memory_size="0x20000000"（512 MiB）；配置检查只接受此范围，example 防护继续有效。ADT 到固定 DarwinBoot 解析器及窗口选择函数的主机检查已完成，尚无实际 UEFI 分配结果。
2. 继续闭合 enuma 固件的 MemoryMapLib/ConfigurationMapLib、DDR/栈/GOP、厂商协议和 FD/boot header。当前没有完整 enuma 厂商依赖，R-001 的批准不会自动解决它们。
3. SPI 仍缺真实时钟/供电/pinmux/独占状态交接；NT36523 触点协议及固件名需核实。UFS 仍缺 QMPv4 PHY、电源、时钟写入、SMMU 和链路启动，不能启用 SM8550 NativeUfs。
4. 用户方便时接入 enuma 后只读复核 ROM/FDT/内存/驱动绑定；本轮不等待设备、不操作 nuwa。

## 限制

- 本板代码尚未接到 IOKit service；无完整 XNU/UEFI 构建、prelink、QEMU、实机或 iPadOS GUI 验收。
- board.toml 仍为 example=true；具体内存基址、UEFI 配置、镜像打包和任何设备启动仍须各自审查。
- 仅本地 main 提交，未建立或推送远端；提交记录见 Git 和 WORKLOG。
