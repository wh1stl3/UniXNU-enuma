# v13持续VBIF翻译异常：公开源码核对

2026-10-28。仅公开资料和本地精确构建只读核对，未改固件、未制作新候选、未追加实机。v13已消费，原镜像和资格冻结。

## 1. 地址契约获得独立支持

[Linux主线SM8250 DTS](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/qcom/sm8250.dtsi) 的 mdss_mdp 配置包含 VBIF `0x0aeb0000/0x3000`，与v13新增窗口一致。该来源支持范围选择，不证明本机活动页表或硬件初始化。

[Mu-Silicium j706f映射](https://github.com/Project-Silicium/Mu-Silicium/blob/main/Platforms/Lenovo/j706fPkg/Library/MemoryMapLib/MemoryMapLib.c) 使用MDSS `0x0ae00000/0x134000`，并独立列DISP_CC `0x0af00000/0x20000`，二者存在重叠；因此不能将其表形状直接当作本机修复，更不能由一个表文件推导维护者实测进度。

## 2. 同2MiB多段映射不是已知必败条件

[TianoCore提交ab644cf](https://github.com/tianocore/edk2/commit/ab644cfac595608f5c8a65531e410d25f0e94c61) 在2022-10-19删除了将已有table替换为block并释放下层页表的优化，为后续break-before-make/TLB维护做准备。不能将该提交直接描述成本机复现bug的修复。

[当前ArmMmuLibCore.c](https://github.com/tianocore/edk2/blob/master/UefiCpuPkg/Library/ArmMmuLib/AArch64/ArmMmuLibCore.c) 的UpdateRegionMappingRecursive在已有IsTableEntry时继续递归，复用下级表。实际v13快照 `build1/work/Mu_Basecore/UefiCpuPkg/Library/ArmMmuLib/AArch64/ArmMmuLibCore.c` 同样有这段逻辑。因此将MDP/VBIF/DSI/DISP_CC分段描述不是足以认定的根因；仍可用实际版本与实际顺序做离线回归，但不可只因共用2MiB块就宣称后写覆盖前写。

## 3. 区分翻译失败与普通权限问题

[Arm官方Memory management](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/Learn%20the%20Architecture/LearnTheArchitecture-MemoryManagement-101811_0100_00_en.pdf) 解释了表描述符、页描述符和无效描述符。v13的DFSC=7属于三级translation fault，优先调查活动翻译路径；不能直接归结为显示电源未开或GOP ABI。

上述当前EDK2及本地版本的GcdAttributeToPageAttribute对EFI_MEMORY_RP采用不设置TT_AF的实现。直接套用“RP使PTE无效”不适用于这里；AF清除通常对应access-flag fault，与本次translation fault分类不同。仍须审计实际调用及其他修改，不能由此排除所有DXE页表问题。

## 4. 下一步优先级（推论，不是已证根因）

1. 用精确Mu_Basecore版本和v13映射顺序复现页表建立，验证VBIF三页与DSI/MDP/DISP_CC在全部描述符处理后仍可翻译；同时检查实际链接入口与返回状态，而不只看常量表。
2. 对比MMU建立后、OEM入口前及异常现场的TTBR/TCR/目标地址翻译结果和叶项，区分从未建立、切换了另一张表、后续清除/破坏；避免把静态映射清单当作当前页表。
3. 若早期翻译成立而异常前失效，再追DXE内存属性修改、页表生命周期和覆盖写；若始终有效，再核对实际异常上下文/翻译制度与采样时点。
4. 当前不把扩大MDSS、改寄存器、跳过VBIF调用或升级整个EDK2作为已证修复。

公开branch文件为本次读取状态，不等于本地依赖版本；关键行为已与v13构建快照核对。没有发现能直接套用并证明修复本轮故障的公开补丁。
