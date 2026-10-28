# v12 VBIF故障：公开源码与本机映射交叉核对

2026-10-28，用户要求继续公开资料搜索。本轮只读分析，没有修改固件、编出新候选或追加设备动作。v12原尝试传输超时后，明确授权retry1已成功启动、自行回Android且恢复检查通过，详见v12操作记录。

## 本机直接证据

三页独立转录得到DisplayDxe+0x2b140、PC=0x9a6ff140、ESR=0x96000047、FAR=0x0aeb0004、LR=0x9a6ff120。精确PE实际指令是`stur w8,[x9,#-172]`，为32位写，同EL三级翻译故障。GUID/镜像大小/会话与本FD唯一匹配。原MDP映射止于0x0ae85000，本机FDT单独描述vbif_phys=0x0aeb0000/0x2008，构建表无覆盖。

本地证据：`out/oem-dispcc-live-20261028/independent-read.json`、`decoded.json`、`fault-analysis.json`及`display-resource-coverage.json`。这是本机证据，公开其他设备配置只作交叉参考。

## 公开来源核对

1. [OnePlus官方SM8250 Kona DTS，固定cad09e0](https://github.com/OnePlusOSS/android_kernel_oneplus_sm8250/blob/cad09e061ef6cf689a4a1e54d27562e0f042236a/arch/arm64/boot/dts/vendor/qcom/kona-sde.dtsi)：MDP、VBIF、regdma、sid、swfuse分别是独立reg资源，范围与本机FDT吻合。不能把mdp_phys的0x84208长度当成整个显示子系统范围。
2. [OnePlus官方SM8250显示调试实现](https://github.com/OnePlusOSS/android_kernel_oneplus_sm8250/blob/cad09e061ef6cf689a4a1e54d27562e0f042236a/techpack/display/msm/sde_dbg.c)：相对显示VBIF基址，MMSS_VBIF_CLKON为+0x4。因此本次FAR落在VBIF时钟控制寄存器，而不是DSI像素写入。
3. [公开Qualcomm HALMDSS源码镜像，固定20bb8ae](https://github.com/Rivko/android-firmware-qti-sdm670/blob/20bb8ae36c93fc16bbadda0e0a83f930c0c8a271/boot_images/QcomPkg/Library/HALMDSSLib/hal_mdp_vbif.c)：Vbif_Init先配置clock gating，再配置burst/OT限制；ClockGating根据布尔参数生成AXI/testbus force-on字段并写CLKON。本机指令序列取参数低位、复制到bit1、与3异或后写+4，行为与此一致。该仓是公开源码镜像且SoC不同，不是本机符号文件；只能作函数行为匹配，不能直接给本机PE全部函数命名或判定上层调用阶段。
4. [Mu-Silicium j706f内存表，固定4cba43c](https://github.com/Project-Silicium/Mu-Silicium/blob/4cba43c90e02cdbefbcd9fcdbda33d2328deaec0/Platforms/Lenovo/j706fPkg/Library/MemoryMapLib/MemoryMapLib.c)、[同仓nabu](https://github.com/Project-Silicium/Mu-Silicium/blob/4cba43c90e02cdbefbcd9fcdbda33d2328deaec0/Platforms/Xiaomi/nabuPkg/Library/MemoryMapLib/MemoryMapLib.c)、[edk2-msm SM8150固定e195262](https://github.com/edk2-porting/edk2-msm/blob/e1952621f419f8db60ed28271264e1b5184c571d/Silicon/Qualcomm/sm8150/Library/PlatformMemoryMapLib/PlatformMemoryMapLib.c)：MDSS使用0x0ae00000/0x00134000、NS_DEVICE一类设备映射，覆盖本次VBIF及DSI资源；DISP_CC另列。此范围会覆盖DISP_CC一部分，不能不经重叠和属性审查直接复制到enuma，也不表示这些设备本机实测成功。

主线Linux的[dpu_hw_vbif.c](https://raw.githubusercontent.com/torvalds/linux/master/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_vbif.c)把CLK_FORCE_CTRL0列在+0x8。不能将本次+0x4误称为该寄存器，也不能拿GPU VBIF同名寄存器直接代替显示VBIF定义。

## 本机资源覆盖结果

按v12实际构建MemoryMap和本机live FDT逐项比较；此表是静态映射覆盖，不是实时页表dump，也不证明原厂PE必定使用全部资源。

| 资源 | 本机范围（base/bytes） | v12描述符覆盖 | 4KiB页对齐候选 |
|---|---|---|---|
| MDP | 0x0ae00000/0x84208 | 已覆盖 | 已有0x85000 |
| VBIF | 0x0aeb0000/0x2008 | 缺失，已有实测故障 | 0x0aeb0000/0x3000 |
| REGDMA | 0x0aeac000/0x214 | 缺失 | 0x0aeac000/0x1000 |
| SID | 0x0ae8f000/0x2c | 缺失 | 0x0ae8f000/0x1000 |
| DSI0控制器/PHY/PLL/动态刷新 | 0x0ae94000起，最高到0x0ae94c00 | 缺失 | 合并0x0ae94000/0x1000 |
| DSI1控制器/PHY/PLL/动态刷新 | 0x0ae96000起，最高到0x0ae96c00 | 缺失 | 合并0x0ae96000/0x1000 |
| SWFUSE | 0x0af50000/0x38 | 缺失 | 0x0af50000/0x1000，是否需要先查PE |
| DISP_CC内DSI/GDSC | 0x0af08000与0x0af03000 | v12已覆盖 | 保留 |

## 下一版建议

优先处理已被实测命中的VBIF完整页对齐窗口，同时完成其余显示资源的实际PE引用审查。对已确认原厂路径会访问的独立资源，在同一候选中逐项补齐、分别审计；对仅DTS存在但尚无使用证据的资源保留为待核对项。这样比每次只补一个故障字节更有机会把链推进得远，又不把外设大区无差别映射。

最小方案只加VBIF，归因最清楚，但可能马上暴露DSI/REGDMA/SID缺口；完整已知资源方案信息量更高，但需要额外PE和重叠/权限/属性验证。暂不推荐照搬其他板的0x134000大窗口，不改RAM字段/保留区/verified，不改原厂寄存器值或跳过原厂调用。

映射修复后可能转为时钟/电源未开导致的外部异常、VBIF/总线握手等待，或HAL IOMMU/DMA及DSI面板阶段失败；这些目前只是后续风险。当前ESR是CPU地址翻译故障，不能归因为IOMMU翻译失败或面板初始化失败。继续保留原异常现场采集，分别验收OEM真实返回、DXE完成和原厂GOP。
