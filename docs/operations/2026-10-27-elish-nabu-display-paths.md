# elish 与 nabu 两条显示参考路径

2026-10-27。用户报告实机 ADB 已恢复；本轮未用 ADB 独立查询，不将此更新扩大为启动授权。R027 冻结，未启动、未消费，无设备部署或推送。共享工作区未修改固件源码。

## elish：同屏证据提高优先级

Linux enuma 补丁系列明确指出 enuma 与 elish CSOT 使用相同面板，并复用 sm8250-xiaomi-elish-common.dtsi、兼容 xiaomi,elish-csot-nt36523；作者报告在 enuma 上测试显示正常。这是外部 Linux 测试陈述，不是本机 UEFI 资格。

来源：https://lore-kernel.gnuweeb.org/lkml/20260804-glossy-mastodon-from-sirius-db9aac@quoll/T/

本轮读取 MiCode/kernel_devicetree elish-r-oss 的 enuma-sm8250.dtsi（blob ad6ccfc3d4d1d54d3b1c9fd8bd28a3685dd65325），默认面板为 dsi_k81_42_02_0a_dual_cphy_video；触控配置仅有 display-maker 0x42。公开 dsi-panel-k81-42-02-0a-video.dtsi（blob 5d6cd8f2b3addf2d5819bc76d3e3109850c327ee）与本地 XBL K81 XML 对应：24bpp、三 lane CPHY、双控制器，水平前肩100/后肩26/同步20，垂直26/168/4。Android DT 的800宽是单链路半宽，不能与XML全屏1600当作矛盾。公开板级配置还有 KTZ8866、enp/enn及电源顺序；本轮仅记录，不实施 GPIO/寄存器操作。

因此撤销“只因机型名不同便降低 elish 面板复用价值”的判断。应优先将 elish CSOT 初始化与本机 K81命令、复位/背光顺序作语义对照。elish edk2-msm 使用 SimpleFb 的事实仍成立；同屏不会使 SimpleFb 自动变成原厂初始化实现。Linux面板源码本轮抓取遇到429，尚未完整取得，未宣称完成 Linux 命令级差分。

## nabu：已完成实际 PE 字节差分

固定仓库 Project-Aloha/mu_aloha_platforms aed1f7934ee4e0921b10c0b0a8dd7116a90a2f4b，设备目录 Platforms/SurfaceDuo1Pkg/Device/xiaomi-nabu。原版来自 Binaries/QcomPkg/Drivers/DisplayDxe/DisplayDxe.efi，补丁版来自 PatchedBinaries/DisplayDxe.efi。两者同仓同版本，尚未绑定原版的原始ROM版本。

两者均294912字节；原版SHA256 978a2ff9a7094927839c611701c13e451eaa431ca26ba40fd0497841c3d3830e；补丁版023042a3b066151593da455d4145293382e16f5c70072e75d278eed2e30e8ed2。全文件比较仅36字节变化，均在.text。PE节表确认这些位置文件偏移等于RVA，ImageBase显示地址为0。

- 0x18e0：调用0x15888前，将w1的2改为0。附近字符串是MDP init failed；参数语义尚未证明。
- 0x165a8..0x165b8：移除调用0x175ec及返回值保存，改为x0=0和cbz x0，走过错误分支。失败字符串MDPSetupPipe Failed支持该调用归因；无调试符号，不把字符串归因冒充符号恢复。
- 0x165d0..0x165dc：移除调用0x17460及返回值保存，改为x2=0和cbz x2。失败字符串MDPPanelInit Failed支持该调用归因。
- 后续0x18b74调用仍保留。不能将局部绕过称为整个驱动伪造返回，但这确实跳过了部分初始化/失败检查，不能照抄后宣称enuma原厂初始化成功。

这组实际差分比Surface Duo通用README更适合作为nabu依据：当前工作假设是补丁保留前级设置并绕过部分重复初始化。要证明它与enuma不返回关联，还须映射enuma精确PE的对应语义并证明执行到达；偏移不跨PE迁移。

另查到提交 f7e48abf08fa71311286da7dc69d352903f5775e，标题为“8150: Patch every 8150 DALSYSDxe for UFS CCA”。故不把DALSys补丁目录当作显示修复证据。其实际二进制差分尚未完成。

nabu配置EnableDisplayThread=0且EnableMultiThreading=0保持为已读事实。这些配置不能消除所有构造器依赖，也不证明enuma改同值就能返回。

## 同屏与配置差异

nabu K82 42 02 0a XML（blob 640029b654881348cf27b0bb7b6d3db1c8761840）与enuma K81均为1600×2560、双DSI、CPHY三lane、DSIRefreshRate 0x780000；DisplayResetInfo均为0 5000 10000 10000 0。但nabu水平前肩44、后肩20；enuma100、26；背光默认值65与25。共同DDIC/屏幕家族与不同固件时序配置可以同时成立，不能由这些差异断言物理屏一定不同。

本地两个K81资源文件的PanelDescription均写42 02 0a，因此文件名35本身不能用于证明另一供应商的实际选用。应以真实DT选择及面板身份为依据。

## 证据与下一判别

独立目录 out/public-display-references-20261027-c999/phase2 保存原版/补丁版PE（不入库）、display-diff.json、两个llvm-objdump调用点结果、nabu-panel.xml，以及两份MiCode原文JSON。此前sources.json/additional-sources.json保留固定来源。

elish路线下一重点是同K81/CSOT命令与供电复位语义，而非从头猜面板；nabu路线下一重点是把三个补丁区域的被调函数语义映射到精确enuma PE，并结合预调用证据判断是否到达该阶段。可靠出口仍优先于设备重试。没有运行OEM、未完成板级出口资格、未作正式GOP/ConOut成功声明。

## 同日继续：命令数据与精确PE调用对照

可复现脚本保存在独立out目录phase2/compare_paths.py；使用WSL python3和/usr/bin/llvm-objdump，无设备操作、无生产补丁。输出semantic-comparison.json和两个完整反汇编文本。执行成功，检查精确PE SHA256、PE节内字符串映射、三组错误引用唯一性；这些是静态解析检查，不是固件运行测试。

elish线：解析本机K81 XML的DSIInitSequence和MiCode同名K81的on-command，保留顺序，按DT七字节包头长度取payload；DCS短写0x05的末尾零填充经检查后去除。XML有189条DCS数据，DT有188条；唯一payload差分是XML多一个0x11（零基187）。其余188条按顺序相同。XML尾部为FD02/11、FD01/11、FD03、FF64、29、FF10；DT在11后记录70ms等待。FD/FF是独立的传输控制记录，脚本未验证原厂解释器如何实现广播/选链和延迟，不能将payload一致提升为执行等价。重复11可能对应分链发送，不能直接删掉。该结果明显降低“缺少本机面板初始化命令”作为首要解释的合理性。

nabu线：错误字符串地址由PE节表转换到RVA，再找相邻ADRP/ADD引用及之前的真实BL/错误分支；不是对两个文件硬套固定偏移。对应关系如下（名称是错误字符串支持的静态归因，不是恢复出的调试符号）：

| 功能归因 | nabu原版调用RVA → 目标 | enuma调用RVA → 目标 | nabu补丁行为 |
| --- | --- | --- | --- |
| MDP init | 0x18e4 → 0x15888 | 0x1998 → 0x167d8 | 前一条w1参数2改0 |
| MDPSetupPipe | 0x165b0 → 0x175ec | 0x176c4 → 0x18884 | 删除调用，走过错误分支 |
| MDPPanelInit | 0x165d4 → 0x17460 | 0x176e8 → 0x18700 | 删除调用，走过错误分支 |

两个MDP init实现开头存在实际结构差异：enuma先分配若干全局缓冲，nabu按表循环处理；因此即使调用角色对应，也不能宣称函数完全相同。参数2的完整语义尚未恢复，不命名为skip-reset等未经证明的标志。

后续最小判别：先证明enuma构造链完成及进入主函数，再观察0x1998对应初始化是否返回；若进入后续模式设置，进一步区分0x176c4和0x176e8。当前三项Boot Services包装器只能观察这些函数内经过的被包装服务，不能直接声称已覆盖三个函数边界。若必须新增边界观测，需独立默认关闭的精确PE绑定方案，不能改冻结R027或将跳过硬件初始化当作成功。

## 同日继续：控制器命令展开与MMU分支归因

公开源码Rivko/android-firmware-qti-sdm670固定20bb8ae36c93fc16bbadda0e0a83f930c0c8a271的boot_images/QcomPkg/Library/HALDSILib/dsiDriver.c定义FD为广播掩码、FF为毫秒延迟，并按mask的bit逐控制器发送。它是旧平台公开实现，不等同于已证明enuma闭源解释器实现。

在此明确限定的模型下，将本机K81命令展开到每条链路：FD02后的11仅发给控制器1，FD01后的11仅发给控制器0，FD03恢复双发；两条链路各188条payload且完全一致。因此此前“XML多一条11”的数据差分不是重复睡眠退出错误的证据。XML等待100ms、显示开启后16ms；Android DT的11之后70ms，等待仍不等价。check_transport_flags.py完成该展开，并验证将FD02改FD03、删除分链11两项负例均破坏两链一致性；这是模型检查，不是实际DSI发送测试。原始JSON保存在phase2/dsiDriver-source.json。

nabu参数2→0已不再只是未知参数：同一公开源码MDPLib.h定义bit1为MDP_INIT_FLAG_MMU_INIT，bit0为MINIMAL_INIT。精确nabu PE保存w1到w21，再转w26，于0x15d10测试bit1，控制0x15d14→0x1a3c8调用；精确enuma保存w1到w20，于0x16b88测试bit1，控制SID表查找和0x16bc0→0x1bca4调用。enuma该分支的字符串明确为Failed to setup MMU SIDs/Failed to find MMU SID mask。两份PE的被调函数查找相同GUID 54b6d3b4-5d33-4f91-8600-6c41d5deb19a，再通过接口多次间接调用。nabu最后参数固定1056；enuma从平台表得到参数，不能照搬常量。

现有追踪可利用的具体点：enuma 0x1bcdc经Boot Services偏移320调用LocateProtocol，返回RVA为0x1bce0，GUID如上；随后协议方法调用0x1bd04、0x1bd18、0x1bd2c、0x1bd4c不受现有三个Boot Services包装器覆盖。若查找失败，该函数有返回5的错误路径，不能直接称缺协议导致卡死；若查找成功后不返回，需区分后续协议方法，不能把最后LocateProtocol记录当卡死点。预调用窗口只能证明即将转发，不能证明原服务进入。

check_transport_flags.py复核两份PE摘要、关键指令原字节、节内GUID位置与GUID相等；输出transport-flags-result.json。现在可将MMU/SID协议交接列为具体候选，但仍须证明实际到达；不将2→0作为已批准或已验证的修复。本轮未修改PE、生产源码、内存或R027，无设备动作。
