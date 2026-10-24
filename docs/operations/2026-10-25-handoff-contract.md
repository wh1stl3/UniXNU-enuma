# ABL→BootShim→UEFI显示交接契约（D-166）

本轮只使用已有备份、R-014镜像、固定固件源码和公开实现，未访问设备。完整摘要和反汇编摘录见reports/enuma-display-handoff-audit.json；可运行scripts/audit_display_handoff.py复现，不提交OEM二进制或原始FDT。

## 已取得的本机二进制证据

本机ABL分区备份SHA256 ff00cd26595d81f97673a7dacaf12e025d25053747bd3819c73dbefd02cc802a。ELF32外壳内含ARM64 LinuxLoader PE，946176字节，SHA256 0460da8ebfc6c77012be96ecf075c4364466b498eb8f87a6f1b8b4bcd6cee612。以下为该PE的RVA。

- 0x1cad8–0x1cae4把字符串0xbb128 `/reserved-memory/splash_region`传给节点查找调用0x2e1f8；0x1caf4检查返回值符号位，失败转0x1cbd0。
- 失败路径引用0xbb147的`ERROR: Could not get splash memory region node`。成功路径继续找reg，0x1cb58要求属性长度16字节；错误日志也区分缺reg与长度错误。
- 这已经是本机实际消费者线索，不再仅以sheng文档类推。但尚未证明该分支直接关闭面板；也未完成整个ABL显示退出/事件回调的反向调用图。

## 保存的DTB与消费者名称不匹配

stock vendor_boot_a备份SHA256 3da202d0c9a5b618b61cd1923e87810536c5f70c9da7875de80075290641daba，头版本3、页4096、头长度2112。独立按头计算DTB区偏移后解码出三份完整DTB及一份173字节的小树，不把小树称第四份完整设备配置。

三份完整DTB的SHA256分别为324049d746aaa16ada3b425ea5eed30f6d49a90c9d63d5e57ea5a632c27becb8、0bd93f077080a6e3bedff5cf384ff97fc863667c59e3379cbbe5bbc165c4168e、afc3540645e5a11351532ce2b5384f27acfb412ee0780ff5a57d72301d5ddb52。三者均有：

| 节点 | 原始reg解释 | 对照意义 |
| --- | --- | --- |
| /reserved-memory/cont_splash_region@9c000000 | base=0x9c000000,size=0x02300000 | 连续splash保留区，名字与ABL查找目标不同 |
| /reserved-memory/dfps_data_region@9e300000 | base=0x9e300000,size=0x00100000 | 与splash合计0x02400000，不能整段视为像素缓冲 |

历史Android FDT 643aa3ec450139d38f8cde9a94bca6d9e8e75e752cb7aa992685d34267434c62有相同两个节点，亦无splash_region节点。当前证据只能建立**保存输入/历史输出与一个真实ABL消费者的名称缺口**；尚无这次临时boot所选DTB、应用DTBO之后及ABL跳转前的FDT内容。不得把历史Android树当本次入口树。

不直接添加第二个相同reg的保留区，不扩大splash到DFPS，不改vendor_boot或切Boot v1。若后续确实需要节点适配，先确定消费者、选树及重复内存描述的处理，再提交最小变更方案。

## 逐阶段证据矩阵

| 阶段 | 当前证据等级与结果 | 未闭合条件 |
| --- | --- | --- |
| boot包 | 实际R-014镜像：Boot v3、空generic ramdisk、192字节shim+3MiB FD、无追加DTB；保留stock vendor_boot策略 | ABL实际DTB/DTBO选择及动态改写 |
| BootShim | 当前固定源码复制FD到0x9fc00000，cache维护后跳转，未覆盖x0 | 实机x0值/内容、FDT驻留范围是否被后续分配覆盖 |
| SEC入口 | 当前源码ModuleEntryPoint保存x0到gSecEntryArg0，Sec.c建立gSiliciumEntryArgHobGuid | 这条链为源码证据，未冒充R-014 SEC机器码资格 |
| DXE消费FDT | enuma板级文件未发现该EntryArg HOB消费者；上游ShengBootMemoryDxe有真实消费者实现，可参考解析/保留方式 | 不能整搬其AddMemory/PublishInitrd；内存增补需要原审批 |
| XBL运行时 | 当前内存表缺FD Reserved/FD_Reserved，现查找路径不恢复scheduler和DTB扩展地址 | 其他协议提供者、原XBL代码/堆/锁/中断状态是否仍有效 |
| scanout | 既有DSI双窗计数支持局部接口活动；已有preserve-display补丁 | 完整双DSI路由、fetch、CPU物理/IOVA、stride、像素格式、线性/压缩与cache |
| 电源/背光 | MiCode提供面板双链路和KTZ8866接线/时序；原厂PE确有相关实现 | 当前面板/背光状态及是否有退出事件关闭，未证明背光为唯一缺口 |
| ExitBootServices→XNU | 有上游路径可复用，但本机未验收 | 显示资源生命周期、GOP→PE_Video、XNU入口与异常日志 |

结论：优先查交接契约得到本机证据支持；还不能把它简化成“补一个DT节点就能亮屏”。A/detail15可先隔离是否到达原厂启动边界；若成立，再取得入口FDT和运行时闭包证据，决定继承帧缓冲或修复原厂模式设置。现有低带宽返回通道未达到任意寄存器可靠解码资格，不继续解码历史时序。

## 再次纠正超时判读

D-165的“75秒无返回表示派发挂死/异常循环/死锁”仍略强。completion fallback不是watchdog；无返回还可能涉及其前置路径未到达、ResetCold没有生效或主机观测失败。只有后续阶段证据才能收窄，不能从源码注释把若干可能原因升级为穷尽结论。本轮没有新实机超时，也没有触发新的设备硬停。
