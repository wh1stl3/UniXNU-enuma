# v11：ClockDxe 显示时钟读取异常

2026-10-28。依据本次三页实机记录、最终人工纠正、本次 FD 清单及精确 PE 反汇编。原始媒体和初次错误转录均保留；最终 E13 第二行是 `G04DB5DEA653024D1A`。

## 已证实的现场

| 项目 | 值 |
| --- | --- |
| PC / RVA | 0x9a88ad58 / 0x11d58 |
| ESR / FAR | 0x96000007 / 0x0af022c0 |
| LR / 同镜像 RVA | 0x9a88aa40 / 0x11a40 |
| SPSR / Type | 0x60000005 / 0 |
| 唯一镜像 | ClockDxe，4db5dea6-5302-4d1a-8a82-677a683b0d29 |
| Base / Size | 0x9a879000 / 0x35000 |
| 精确 PE SHA256 | 834428700f5e034e52285e1d516b98e86e71ce4b6d7211a9b40fa87d92137cab |

PC 指令字 `0xb862490a`，反汇编 `ldr w10, [x8, w2, uxtw]`，即32位读取。ESR EC=0x25、WnR=0、FnV=0、DFSC=7：同EL数据异常、三级地址翻译故障、FAR有效。ISV=0，所以访问宽度及寄存器来自精确指令，不能从综合症自行补全。

LR前的0x11a3c是 `bl 0x11d34`；调用前0x11a2c设置W2=4，进入callee后到故障前未再调用函数或改W2。因此该静态调用路径与现场相符，推算X8=0x0af022bc。没有拍到X8/W2，明确保留推算属性。LR仍在ClockDxe内，不能据此重建上层DisplayDxe/GOP调用栈。

## 映射缺口及寄存器归属

本次build3实际生成的 `work/uefi/Platforms/Xiaomi/enumaPkg/Library/MemoryMapLib/MemoryMapLib.c` SHA256为 `5fee8940c4cee08fb3cac33f75ffe706a624fce5e7f435447141bd133ab5fba8`。全部描述符解析后，没有一条覆盖0x0af022c0：Display MDP是[0x0ae00000,0x0ae85000)，AOSS是[0x0b000000,0x0f000000)。两者之间的DISP_CC未映射。

本机既存live-fdt.bin（SHA256 `643aa3ec450139d38f8cde9a94bca6d9e8e75e752cb7aa992685d34267434c62`）中的 `/soc/qcom,dispcc@af00000` 为 `qcom,kona-dispcc`，reg=0x0af00000/0x20000。只读使用共享主线中的既存证据，未写共享树。

Linux官方[SM8250显示时钟驱动](https://raw.githubusercontent.com/torvalds/linux/master/drivers/clk/qcom/dispcc-sm8250.c)将 `disp_cc_mdss_ahb_clk_src` 的cmd_rcgr定义为0x22bc；[RCG2实现](https://github.com/torvalds/linux/blob/master/drivers/clk/qcom/clk-rcg2.c)定义CFG_REG=4。因此0x0af00000+0x22bc+4恰为本次FAR，支持显示AHB时钟源配置读取的解释。公开源码用于命名和交叉核对，本机PE/FAR/FDT为主要证据；不据上游DTS的0x10000替换本机0x20000窗口。

当前最强根因候选是平台缺少DISP_CC映射。已证实故障类型和构建描述符缺口；未采集实时页表，仍不能完全排除运行中页表变更。此证据不支持先修改Clock协议ABI、跳过原厂调用或伪造EFI_SUCCESS，也不能直接回填为v10的已证根因。

## 下一版方向与可能的下一卡点

1. v12优先做DISP_CC设备映射修复；范围以本机FDT和OEM实际访问交叉审查，核对页对齐、无重叠、NS_DEVICE属性及最终链接描述符。内存base/size变更仍按既有review规则执行；本轮只分析，未改映射或生成v12。
2. 保留v11异常现场及真实OEM/Core/GOP调用，重新完整构建、新资格、新trial。验证故障页覆盖，并以删除映射的负例证明检查能发现本次缺口。旧镜像、资格和trial不改写、不重试。
3. 映射修复后若变成外部异常/访问拒绝，转查时钟电源域或访问权限；若新FAR落其他未覆盖MMIO，按新现场逐段审查，不全地址空间兜底映射。
4. 若进入时钟更新后停滞，核对实际CMD_UPDATE/CLK_OFF轮询及电源依赖。本次PE在0x119fc调用后含0x11a0c的bit0轮询回边；这是静态后续风险，不是已到达或已挂住的证据。
5. 只有时钟路径实际通过后，继续按HAL IOMMU→真实OEM返回→整轮DXE→原厂GOP逐项验收。当前三页没有证明上述阶段完成，也没有证明失败阶段必在构造器。

先前最小nonce+cold留存实验仍有价值，但本次已经得到可操作异常现场，其优先级低于修复明确映射缺口，不需要作为该修复的前置条件。

## 证据与边界

结构化报告 `reports/enuma-oem-exception-v11-live-20261028.json`；本地完整证据 `out/oem-exception-live-20261028/` 中human-confirmed-pages.json、decoded-confirmed.json、fault-analysis.json和clock-fault-disassembly.txt。媒体只在Media-enuma。v11单次已消费、未按键自动回Android，独立原分区与备份核验通过。本次继续分析未发设备命令、未修改固件，R027/旧候选冻结；源码与文档发布结果另记本地receipt及最终答复。
