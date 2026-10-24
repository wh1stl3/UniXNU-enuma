> D-171后续：完整结构ADT与96MiB FAT已实际生成并经真实loader函数主机检查；本文的“缺ADT/FAT”是D-170历史状态。当前以STATUS和[新专项](2026-10-25-full-adt-fat.md)为准，v3运输/root/报错仍未闭合。

# 完整启动链优先：按实际iPadOS报错迭代（D-170）

## 用户澄清与执行方式

用户原文：“我本来的想法是一次性做到iPadOS 然后分析启动的报错 每次启动解决一些”。含义已澄清：不是密集绘制或增加录像频率，而是尽量在一笔启动中沿完整链推进，读取真实报错、每轮修复一批问题，减少人为早停的往返。

据此将完整链作为主线，B/detail13仅保留离线备用。优先补齐真实缺失输入；不拿“只有UEFI且空ramdisk”的镜像当iPadOS试启动，不为了收集已知必缺输入的报错消耗实机。准备可观测、可恢复的尽可能完整候选后，允许沿链跑到真实失败点；单点探针只用于缺乏直接报错时的必要隔离。不是承诺下笔必进桌面，也不要求把所有离线不确定性证明完才允许试运行。

原设备/内存/verified/破坏性分区门禁不变。无日志且无法保证可控返回仍按AGENTS停，R-002失败的跨Bootloader保留区不重新使用；不盲目借用umi保留RAM/Recovery布局。

## 本轮已产生的真实系统输入

- 复用已审计macOS平台内核b940f550…c6052d，含ArmDTPlatform/ArmCpu/pthread，普通ARM64和4KiB；无需重复编译已有归档。
- 用固定NativePrelink 2b6ffb5的真实emit函数，结合相同iPad7,1/21H461 donor f18b4df8…9de7，**实际发出**out/full-boot/system-components.experimental.macho：54231040字节，SHA256 be83a7ec0c11132c13b9581d8784a1775584bb97ff5c66484bcbb2e7bef0879e。
- APFS、AMFI、CoreTrust、AppleImage4、sandbox、HID/IOSurface/IOMobileGraphics等根的完整依赖闭包包含29个原始组件；原始组件可执行字节由上游发出器逐段核对保持不变。类/依赖存在不代表相应Apple硬件驱动可用于Qualcomm。
- AMFI early initializer来自**完全相同donor**的固定参考，原地址0xfffffff005ab4ae0；发出器检查原模块可执行范围和原始initializer ABI标记。这里复用的是原始Apple二进制函数，不是复制另一SoC的物理地址。
- 虚拟slide由本机两份Mach-O的重叠检查选择0、-2MiB…第一个通过值-0xe00000，不是直接采用sheng的-16MiB。虚拟跨度68382720字节，只描述内核映射，不证明512MiB入口预算足以运行完整iPadOS。
- 输出复查普通ARM64、4KiB TCR、可执行入口及平台导出通过。工具prepare_system_prelink.py，报告enuma-system-prelink.json / enuma-system-prelink-format.json。

上游仍明确runtime_qualified/loadable=false，instruction_relocation_complete/register_dataflow_qualified未证明。此文件是离线实验性系统输入，**不是可直接boot的完整镜像**；没有改board的内存数值、源码pin或verified。

## 新的首选复用来源：同SM8250的umi完整系统实现

已实际下载并固定[UniXNU-umi](https://github.com/reAAAq/UniXNU-umi/tree/3eb72578597d2ca16471b172d45eddc096a34a04)，提交3eb72578597d2ca16471b172d45eddc096a34a04。维护者及[UniXNU设备文档](https://unixnu.com/devices/umi)报告到Hello/Setup Assistant，并有UFS/OS/SystemOS/持久Data/CPU显示。属于维护者报告，不是enuma独立实测；未把它写为完成Setup或进入主屏。

源码锁显示其测试框架为7b52e7968c76453cdc18b5aa174fc368d5293b91、测试uefi-umi为48bc41218c480519bfd299c22205f44e418df9d0。最新firmware检出727f6c2只作对照；测试版本文件通过git show固定取数。当前enuma仍用5fdbd5d/aa9ec66，未替换底座。文件摘要及许可在config/system-reuse-sources.lock.json，适用性报告reports/enuma-umi-system-reuse.json。

| 实现 | 优先复用内容 | 必须保留的本机边界 |
| --- | --- | --- |
| scripts/umi_adt.py及make-umi-adt.py | 完整loader/chosen/product、安全身份和硬件描述的组织方式 | CPU/GIC/timer可对照；DRAM、GOP、种子、根卷UUID用本机/同donor事实，不能拷其12GiB配置 |
| UmiRamPayloadDxe | FDT、保留窗口、FAT/BPB、只读BlockIo边界检查和挂接 | umi用boot v1，本机v3会组合vendor/generic ramdisk；不猜偏移/向上取整，不凭同名窗口证明适用 |
| UmiPlatformPower.cpp | 原始PMGR服务ABI与原始nub构建；未实现操作明确失败 | 需要自己的ABI/对象布局证据；不复制SM8550实现或造成功stub，不能把提供服务扩大成时钟/休眠成功 |
| UmiUfsProbe / UmiNativeUfsHost / UmiSmmuTakeover | 已有SM8250时钟、DMA接管、UFS队列与根卷发布路径 | 本机FDT亦有0x1d84000/0x3000；流归属、电源、LUN/GPT与实际接管仍逐项核对，先只读 |
| legacy-display、boot-progress、Data | CPU framebuffer显示、阶段/错误记录和Data组织 | enuma面板/stride/scanout、Data来源、内存/日志区域和持久布局不能继承 |

许可证保留BSD-2-Clause-Patent、MIT及文件级原始说明。其BUILD明确部分真实Hello配方依赖本地存储ABI、trust/Data seed、原始固件导入和参考Mach-O记录，公共默认board仅是最小基线；因此不能直接运行其builder或宣称一键移植。触控FTS/PMIC GPIO5与enuma NT36523无关，不搬用。

此前“固定通用NativeUfs只含SM8550路径”的判断只描述我们的旧通用pin，不能扩大成“没有可复用的SM8250完整存储实现”。现已找到umi板级真实实现，后续以复用和接口迁移为先，不从零重写。

## 当前完整链缺口与下一批实现

| 环节 | 本机当前事实 | 下一步 |
| --- | --- | --- |
| UEFI/loader | A返回核验通过，不代表完整DXE/BDS/DarwinBoot走通；B离线备用 | 集成完整载荷后去掉人为早停；保留可控退出/异常证据，必要时才用B隔离 |
| 系统内核 | 平台内核和本轮预链接已存在 | 对照umi原始ABI/安全/PMGR集成，保留真实失败，不造服务 |
| ADT | 只有2956字节硬件片段，缺完整chosen/product/NVRAM/loader输入 | 优先迁移umi的完整ADT组织方式并接enuma已审计硬件事实；需新物理数值时再审查 |
| FAT载荷 | 尚无kernel+完整ADT+trust+config的正式FAT包；旧发现盘不是系统包 | 复用上游payload.py构建，不复制另一套FAT builder；明确真实输入及自动启动项 |
| 运输与发现 | 当前诊断镜像generic ramdisk为空；v3候选实际入口FDT/组合边界未验证 | 优先适配UmiRamPayloadDxe的真实边界机制，验证完整范围与SFS发现，不改成v1碰运气 |
| root与Data | 无本机原生块驱动闭环、系统卷/seed/UUID/几何配置；NativeUfs/显示在当前内核配置中关闭 | 从umi移植SM8250 UFS/PMGR和CPU显示的必要集，先只读源/块摘要；覆盖userdata另审，不继承其GPT |
| 错误观察 | 当前有相机/时序，没有已建立的UEFI→XNU完整文本通道 | 复用可见控制台/boot-progress/同次日志机制；跨复位RAM失败限制保持，不把复位耗时当文本错误 |

下一批实现重点是**完整ADT + FAT载荷 + v3运输 + 报错输出**，同时核对umi的PMGR/UFS接口。准备具有完整输入且可观察/可恢复的最大范围候选，再按真实失败修复一批。不能把本轮54MiB预链接发出，或B构建通过，当作XNU/用户态已实机通过。

本轮用户澄清后无新增设备动作；A仍只有前一轮一笔、R-016 consumed。B保持备用，未申请或扩张新的分区/像素/内存/verified权限。
