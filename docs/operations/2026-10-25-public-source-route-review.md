# enuma 路线复审：公开源码与本机证据（2026-10-25）

范围：离线源码、公开资料及既有实测记录复核；本轮没有构建、访问设备、启动或刷分区。设备仓HEAD为3eb3ded589d744447c954f43e2ffc1410e4a30a4，firmware检出aa9ec666abadfeacda608870ecfb4e7179c7ecc3；当前文档未提交。D-164调整下一步优先级，不推翻D-163的证据更正，不扩大任何硬件授权。

## 主判断与路线选择

当前优先缺口是**引导交接契约和原厂运行环境尚未闭合**，而不是已经证明需要重写显示驱动。此为中等置信度的工程判断，不是已定位根因。DSI接口计数推进、原厂PE/XML存在、GOP句柄存在分别只覆盖局部条件，不能互相替代。

将上一轮“原厂栈优先”的单一路线调整为：

1. 主线：审清ABL→BootShim→SEC/DXE→ExitBootServices→XNU的continuous-splash继承条件；若真实扫描输出可保留，复用现有SimpleFb/GOP适配，只补已证实的契约缺口。
2. 有界支线：保留原厂DisplayDxe的入口/返回隔离，并优先逆向其真实运行依赖；不能无限增加模块、GUID stub和低带宽计时试验。
3. 条件后备：只有证明继承路径不能满足、原厂环境修复代价过高，才依据本机面板和公开驱动实现最小真实初始化。窄背光适配和完整MDP/DSI重写的成本不同，应按缺口决定。

如果BootShim入口前面板已经关闭，或扫描源不是可安全映射的线性缓冲，SimpleFb主线必须转入契约修复/真实初始化，不能继续只改GOP元数据。如果原厂PE的实际调用均有兼容实现且可稳定完成模式设置，则提升原厂支线。两者都允许被新证据推翻。

## 公开资料：已核对行为和复用边界

### 1. 同SoC UEFI说明继承帧缓冲是一条已有路线

固定edk2-msm：e1952621f419f8db60ed28271264e1b5184c571d。

- [SM8250配置](https://github.com/edk2-porting/edk2-msm/blob/e1952621f419f8db60ed28271264e1b5184c571d/Platform/Qualcomm/sm8250/sm8250.dsc)：PcdMipiFrameBufferAddress=0x9c000000。
- [elish内存表](https://github.com/edk2-porting/edk2-msm/blob/e1952621f419f8db60ed28271264e1b5184c571d/Platform/Xiaomi/sm8250/Library/elish/PlatformMemoryMapLib/PlatformMemoryMapLib.c)：Display Reserved=0x9c000000/0x02400000。
- [SimpleFbDxe](https://github.com/edk2-porting/edk2-msm/blob/e1952621f419f8db60ed28271264e1b5184c571d/Silicon/Qualcomm/QcomPkg/Drivers/SimpleFbDxe/SimpleFbDxe.c)：106–109行SetMode直接返回；151–157行明确从前级bootloader的PCD描述继承；193–203行自行构造模式；219–225行清屏并维护cache。它不初始化面板，也不从硬件自动发现真实pitch/格式。

意义：不必把“搬原厂DisplayDxe”和“从零写整套显示栈”当成仅有的两条路。限制：elish不是enuma；上述常量重合并不证明本机当前scanout，32bpp线性/stride=width和cache hack不可直接移植，原驱动的清屏行为也不属于当前像素授权。

### 2. UniXNU已有针对ABL的显示交接处理

[UniXNU sheng设备文档](https://unixnu.com/devices/sheng)明确记录：stock ABL在没有splash region时关闭面板，boot image补/reserved-memory/splash_region。该网页为2026-10-25查阅的浮动资料，落地实现须再固定对应仓库提交。

意义：第一优先应审查**ABL实际收到和修改的FDT**，不能仅以Android启动后的/sys/firmware/fdt含保留区断言当前临时镜像交接正确。限制：sheng为SM8550，不能复制其地址、大小、节点策略或同镜像重试结论。此资料不是enuma ABL必然相同行为的证据。

当前enuma采用Boot v3、保留vendor_boot中的DTB，不能因为另一参考仓用v1就换打包格式。先追踪实际输入/选择/交接，再评估必要的DTB适配；遵守既有内存字段和映射审批。

### 3. 小米和Qualcomm作者源码表明continuous splash涉及SMMU生命周期

固定MiCode内核52a2f180865f8368828985d6384130acd093fa93：

- [sde_kms.c](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/sde_kms.c)的_sde_kms_splash_mem_get（719–755行）通过one_to_one_map映射splash物理区；释放路径解映射并归还保留内存。源码含The Linux Foundation版权与GPL-2.0许可。
- 对照[LineageOS sde_kms.c](https://github.com/LineageOS/android_kernel_xiaomi_sm8250/blob/6b34d24765327d746074c8e53b5ad0d24a51acc7/techpack/display/msm/sde/sde_kms.c)和[dsi_display.c](https://github.com/LineageOS/android_kernel_xiaomi_sm8250/blob/6b34d24765327d746074c8e53b5ad0d24a51acc7/techpack/display/msm/dsi/dsi_display.c)，固定6b34d24765327d746074c8e53b5ad0d24a51acc7。后者包含split-DSI各控制器的时钟门控处理，不能把一个接口的活动当成双链路成功。

意义：核对CPU物理地址、显示IOVA/映射及保留期，不能仅用SSPP地址数值推导CPU可安全访问。项目已有kona-preserve-display.patch抑制MDP SMMU detach和sec-preserve-display.patch抑制清屏，应验证其覆盖的真实构建路径，不重复实现同样的开关。Linux里的恒等映射代码只说明该路径的设计，不证明本机此时映射已经成立。

### 4. 小米设备树给出板级差异，背光并非通用PMIC WLED

固定MiCode/kernel_devicetree：43b11af42a275b9415634f4d196579938820896d。

- [enuma-sm8250.dtsi](https://github.com/MiCode/kernel_devicetree/blob/43b11af42a275b9415634f4d196579938820896d/qcom/enuma-sm8250.dtsi)：301–311行KTZ8866在QUP SE11 I2C、地址0x11、HWEN139/ENP130/ENN131；318–323行PMIC LCDB/WLED禁用；354–357行默认面板引用。
- [k81 42 02 0a面板](https://github.com/MiCode/kernel_devicetree/blob/43b11af42a275b9415634f4d196579938820896d/qcom/dsi-panel-k81-42-02-0a-video.dtsi)：dual DSI C-PHY，宽度800为1600的一半，高2560，有复位序列、广播和首帧后更新背光策略。须以本机panel-id/实际DTBO确认型号，不能认为所有K81资源都同时适用。
- [小米KTZ8866驱动](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/drivers/video/backlight/ktz8866.c)：35–52行真实I2C访问，54–92行亮度/使能，115–131行配置回读，146–219行probe；其配套include/linux/platform_data/ktz8866.h也是配置来源。

意义：如后续证实只有背光未恢复，可复用已存在的真实I2C协议和这些时序/寄存器含义做窄适配；不应先写GENI控制器或套其他设备WLED值。本轮没有证明背光是唯一缺口，不执行I2C/MMIO写入。公开GPL源码作为行为依据；如直接移植代码，先落实文件许可和模块边界。

### 5. 第三方ROM是硬件依据，不是Darwin二进制兼容层

固定xiaomi-enuma-dev/android_device_xiaomi_elish_enuma：0d41d4d29ae7329a454c6bb4e4b8c66331177249。

[BoardConfig](https://github.com/xiaomi-enuma-dev/android_device_xiaomi_elish_enuma/blob/0d41d4d29ae7329a454c6bb4e4b8c66331177249/BoardConfig.mk)仍使用elish路径、elish.config和elish OTA assert；[依赖](https://github.com/xiaomi-enuma-dev/android_device_xiaomi_elish_enuma/blob/0d41d4d29ae7329a454c6bb4e4b8c66331177249/lineage.dependencies)指向sm8250-common；[专有文件清单](https://github.com/xiaomi-enuma-dev/android_device_xiaomi_elish_enuma/blob/0d41d4d29ae7329a454c6bb4e4b8c66331177249/proprietary-files.txt)是Android HAL/固件等清单。不能把仓名包含enuma当成板级配置均已适配；不能直接将Android .so链接进Darwin。固件数据、协议和时序可逐项复用，执行环境与许可需分别确认。

UniXNU公开enuma页面目前列出多个社区仓，但页面“缺UEFI/可构建镜像”的摘要落后于本仓既有构建证据：[设备页](https://unixnu.com/devices/enuma)。因此网页支持表只能作为线索，不能覆盖本机审计，也不能据此宣布别的仓已经实机解决显示。Tlrenhb参考仓既有固定审查见2026-10-24-tlrenhb-reference-evaluation.md，本轮不改变其只读/来源边界。

## 新发现：原厂线程/HOB运行环境的静态缺口

当前firmware源码可复现：

```powershell
rg -n 'EnableMultiThreading|EnableDisplayThread' firmware/Platforms/Xiaomi/enumaPkg/Library/ConfigurationMapLib/ConfigurationMapLib.c
rg -n 'FD Reserved|FD_Reserved|Scheduler|DtbExtension' firmware/Silicon/Qualcomm/QcomPkg/Library/PlatformPeiLib/XblProtocols.c
rg -n 'FD Reserved|FD_Reserved|Sched Heap|Display Reserved' firmware/Platforms/Xiaomi/enumaPkg/Library/MemoryMapLib/MemoryMapLib.c
```

1. ConfigurationMapLib.c第29/34行两个线程开关均为1。
2. XblProtocols.c第112–120行只按FD Reserved/FD_Reserved查区；未找到时初始化为0的描述符保持0，直接return。MemoryMapHelper.c按名称不区分大小写的完整匹配，失败返回EFI_NOT_FOUND，不会回退到UEFI FD。
3. 当前enuma内存表没有上述两个名称，虽有Sched Heap和UEFI FD，不能视为同名替代。因此**以这份表调用当前GetXblHobAddresses路径时，不会通过该路径恢复scheduler或DTB扩展地址**。
4. PlatformPei.c第129行将地址初始化为0，第136/139行查找/建HOB；只有scheduler非0才建对应HOB，并通过EFI_KERNEL_PROTOCOL调用Lock->InitLock创建FV表。QcomPkg.dsc.inc声明使用这份PlatformPeiLib；具体R-014 SEC二进制仍需另行与构建记录/反汇编绑定。
5. EFIKernelInterface.h包含ThreadCreate/Resume、锁等真实ABI。不能用一个成功返回的stub替代。

结论强度：这是当前源码的确定路径缺口，不是“实机必定在线程里挂死”。还未证明本机DisplayDxe实际消费哪个接口、线程配置分支是否走到，以及是否有其他提供者。不要仅因这个发现就把EnableDisplayThread改0：同步模式也可能依赖锁、事件、TPL或其他XBL服务。

也不要给UEFI FD改名或添加任意FD Reserved区域：当前扫描器按机器码模式寻找函数，解析循环直到RET，无明确函数长度上限；地址、代码驻留、重定位、页权限、堆/锁/中断状态都需核实。原XBL指针在ABL退出/BootShim重定位之后可能不再有效。修复内存表仍遵守AGENTS审批。

## 下一步顺序与交付判据

### 第一步：先完成离线契约与PE调用审计

输出两份结构化证据：

- handoff-contract：逐段记录Boot v3选择的DTB/DTBO、ABL显示相关属性的消费者、BootShim入口FDT寄存器保存、SEC是否继续传递；明确每段“已知/从源码推导/待实测”。Android后期FDT只作对照。逐项列出splash base/size、实际stride/format/线性或压缩、SMMU、双DSI、供电/背光及ExitBootServices生命周期。现有补丁已覆盖的行为标复用，不重写。
- native-display-abi：固定本机DisplayDxe SHA256及PE入口，用LLVM/Ghidra等对EnableDisplayThread字符串交叉引用、协议查找、HOB查找、Thread/Lock/SetMode调用建立真实调用图；记录调用地址、表偏移、返回值处理和提供者。对比原XBL APRIORI与当前FD差集，但只有真实调用/状态依赖才进入修复集合。

尽可能先用已有Android日志、DTB、备份与原厂PE完成，不为取资料刷第三方ROM，不越过当前设备停点。新的硬件取证必须单独通过原有门禁。

### 第二步：再选择最有区分力的一次实机候选

上一轮detail15/detail13方案仍有效，但降为原厂支线的有界定位工具；先完成离线审计，避免带着已知环境缺口继续盲试。若尚需判断是否到达目标入口，先A；A有效后按证据决定B及状态/GOP检查。已有失败镜像不原样重试，不将fallback称watchdog。

如果首要缺口是ABL实际FDT/显示关闭，则候选应检验该契约，而不是继续加DXE。如果PE真实消费缺失运行时，则先确定真实兼容实现或有来源的同步路径；若必须重建大片XBL线程内核，降低原厂方案优先级。任何新增内存/映射或硬件写入不从本分析获得授权。

### 第三步：以可见控制台闭合到XNU

显示验收分别记录：真实模式有效→受控可见变化→退出Boot Services后仍可用→PE_Video交接→XNU入口/异常输出。像素试验需新批准，旧R-005/R-007不复活。GOP安装和QueryMode成功不替代可见输出。

通用内核/载荷继续复用UniXNU固定底座，先核对CPU/中断/定时器/4KiB/内存契约及最小日志入口，再按上游可用能力选择ramdisk或存储。显示、XNU、用户态、UFS和Adreno分别验收；不把SM8550/A740实现当SM8250/A650已支持，不在首屏前扩展到完整GPU、相机、蜂窝适配。

## 门禁和文档状态

本轮只落地路线研究，无设备动作、源码实现、内存字段修改或verified变化。原恢复证据仍仅表示当时已恢复，实时模式未知。下一次实机前仍需不可变候选资格、适用文档提交推送、即时enuma身份/备份和现场恢复核验；超时停止追加、先恢复并当轮同步文档。此评估不新批R-008/R-012/R-013/R-014，不重新执行R-015。
