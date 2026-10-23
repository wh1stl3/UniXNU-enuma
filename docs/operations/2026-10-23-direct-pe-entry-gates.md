# 真实PE入口细分门

2026-10-23（Asia/Shanghai）。用户选择R-003推荐方案，授权沿可控返回探针继续。R-002跨复位RAM日志仍停止，不换址或再次写标记。本轮不修改板级内存字段/验证标记，旧原生/无UFS模式仍分开。

## 插桩契约

- detail20：固定Mu Image.c的Image->Started=TRUE之后、调用Image->EntryPoint之前。
- detail21：Image->EntryPoint直接C返回之后、CoreExit之前。
- detail22：Exit/LongJump回到CoreStartImage之后、TPL核对/恢复与cleanup之前。

Dispatcher立即围绕CoreStartImage设置当前调度handle/FileName，调用返回后清空；Image.c只调用DxeCore内bridge，bridge用同一个Dispatcher计数与完整GUID过滤。不是每个translation unit各数一份。CoreDispatcher本身拒绝重入；其他handle的嵌套StartImage被排除。选择为空或被清空时不命中。

原detail13/14/15及状态筛选16–19保持。新增20–22不把EFI_STATUS当设备状态；point21遇到驱动直接调用Exit时可能不执行，point22仍可执行。PE入口里可能运行厂商构造器，不能从point20证明进入了厂商主体或某个寄存器访问。

测试优先使用无UFS的Display完整GUID4138022f-06c7-4f79-9c94-7e33b511a4e7、实际预计队列32，并保留全部样本。用同source的2/7/2延时对照支持门命中，不用一次自动复位当成功。point20若支持，再分别定位21/22；若不支持，需同source旧point15对照，不能跨插桩布局直接认定包装器故障。

## 固定来源与构建

固件0924fbd新增共享桥与Image.c细分补丁；原25迁移文件/六patch字节不变。第一次官方backend因新增Image.c未做LF规范化而拒绝patch，没有生成/推送该候选。后续a927ca1将Image.c纳入out暂存LF规范化和固定Mu基线哈希，extensions锁住reset元数据；没有改源码语义或运行配置。两提交已推送，设备gitlink/43项源锁随之更新。

原Mu计时、PSCI reset、完整GUID/ordinal筛选被复用，没有新MMIO/持久RAM/异常处理空实现。参考同SoC仓用于先前显示/依赖比较，本轮真正插桩对象是已固定Mu CoreStartImage，不照搬他板地址或输出通道。

35组实际header/bridge主机ASan/UBSan通过，覆盖13–22、status、完整GUID两半/NULL、ordinal、不同handle嵌套/清空context以及stage0/12；45项Python通过，重放patch两次及Image三个callsite精确计数通过。仅主机验证，不是硬件结论。

源码CI：0924fbd run39830524553、a927ca1 run39830711644均成功且回读PASS日志。完整固件build/32OEM PE-DEPEX审计/BootShim/v3回读、具体FD/镜像hash与设备实测以reports和后续本文件补充为准，不能继承旧布局实测。

## 实测记录

本轮当前实测结果按reports/enuma-entry-device-tests.json的peentry变体归档；每个变体快照保存在out/entry-probe/，完整FD/构建/预检/审计/payload和日志私有。恢复必须核对Android启动完成/root/原boot与vendor_boot摘要。无flash/erase/改槽。


第一组实测（a927ca1、无UFS、Display实际PE调用前point20）已完成2/7/2秒：ADB16.977/22.272/16.367秒，启动完成29.512/34.926/29.445秒。两个差值5.295/5.905秒支持到达point20，保留全部噪声样本，不声称精确计时。2秒镜像4d050369b823cbdbbe4ed9b6e9a90cdedd067ab21659be9bc6e9fcdd13cecdcb，7秒镜像fdb981bd2d2694fca159e8e1a36aa5a2d1c7d856d16d08b699a62cc751277165。三次均恢复Android/root/原摘要。

补充语义：point22位于SetJump/entry/CoreExit整个代码块之后；它不能单独证明一定发生LongJump（也涵盖CoreExit意外返回后的fallthrough）。本轮不能把PE入口前门当成入口内构造器/主体执行证明。原厂Display PE在RVA0x1000有系统表/配置表包装，静态线索见reports/enuma-display-pe-entry-static.json，未修改原厂二进制。

point21（直接PE返回后）2秒样本于02:34:30启动，ADB33.063秒/Android45.293秒，镜像c84033ab4bd2202e3bf338b8de16142eb6c7b2d05e16db22499c42030ccc61e2；未观察到短延时门，不能单凭它排除驱动调用Exit。point22继续构建验证。


point22于02:39:14启动，ADB32.894秒/Android45.706秒，镜像fa472e6d3b5e1fd92da40c9a9c4c9fdc1a6ea4f58d89ba916edfb43c65412be2；同样未观察短门，恢复核对正常。因此目前支持调用前，未观察直接返回或Exit代码块后门；仍不把负向时序当成“绝无返回”的绝对证明。

## 独立全局异常门

后续固件903ffed将point23设在固定AArch64 DumpCpuContext入口、格式化/ConOut前，复用EnumaStageCheckpoint的真实Timer/Reset；明确补齐AArch64 TimerLib/ResetSystemLib依赖。只写out暂存补丁及头，不改OEM字节/内存表/持久RAM。新C/INF的LF基线和header进入来源锁，设备总44项。

此门没有driver GUID/ordinal归因，builder禁止--dispatch-guid或非占位ordinal1。点23不由Dispatcher/Image门合成；字段ordinal1只是兼容CLI占位。例外入口可能早于/晚于目标驱动，故不能把全局异常门命中直接当Display异常。若未命中，可能未到默认DumpCpuContext、已注册handler接管、栈/handler/timer/reset失败或其他世界复位，不能排除全部异常。

新增6组实际header sanitizer检查2/7秒和stage0/12/默认detail不触发；分发/桥头37组检查与45项Python/源码patch重放通过。新源完整固件/设备与CI结果另行记录，不能继承a927ca1的实机布局证据。

## 包装器依赖线索（静态，未确认根因）

只读检查锁定的33个enuma OEM PE，全部包含b898d8dc-080a-40f7-99e3-31627b806a5a GUID字节，逐模块PE摘要/entry RVA/文件偏移见reports/enuma-oem-canary-static.json。仅有字节不能证明相同控制流，更不能证明当前配置表存在。

Display的RVA0x1000包装器实际只比较配置GUID的前64位，找到后将VendorTable字段作为全局值；缺失分支经0x10f4/0x1238进入0x6c3c，在0x6c7c有SMC与返回值重试。独立研究也将同GUID/包装器识别为Qualcomm stack canary初始化：[Binarly原研究](https://www.binarly.io/blog/dark-side-of-uefi-cross-silicon-exploitation)。这是研究作者的一手分析，仅作为识别线索，不继承其设备运行结果；本机仍需实际表状态/分支观测。

不能因此直接认定RNG/SMC导致黑屏，也不能安装常量canary、跳过安全初始化或修改OEM PE。许多更早调度的OEM也含同GUID，因此“Display独有的缺失canary问题”尚不成立。若继续细分，优先在真实PE调用前做只读配置表存在/缺失门，与同source point20正对照；先确认实际分支，再评估同SoC真实实现。仍不新增固定内存或改验证标记。

## 异常门实测结果

903ffed、无UFS的全局point23分别于02:47:40/02:52:16启动2/7秒候选：ADB30.766/30.772秒，Android完成47.328/43.804秒。ADB差0.006秒，没有选择延时应产生的5秒响应，未观察默认DumpCpuContext门；不排除其他异常/复位源。两次均自动恢复Android/root/原boot与vendor_boot摘要；没有分区写入。镜像摘要分别88e53621dab0391348e30dd9c3ee81c5ccc2522f8fd22a4d4f029f9acdbf8573、f6ae9661713fda552c03a4dfb169a158b835940a6645b8d36ad1df418dbf10d7，FD分别28ac8f84f9d7f8a693a024c463d87429fdcd03abbc19c6fb2d610cf9a94fb3b9、7108200f8e26ac572052812b823e1095512d8d40d8c61492e4bae000aeccd399。

两候选均实际完成官方backend/补丁还原、32原厂PE-DEPEX逐字节、192字节BootShim+3MiB FD及AOSP v3回读审计。源码CI run39834543624成功且回读PASS；仅源码契约，不代替固件/硬件验证。当前source的point20正对照另记，不继承旧布局运行结果。

## d3a0972只读配置表门

903ffed同source point20正对照于02:56:46启动：ADB15.951秒、Android30.408秒，镜像0e50753557ac05ad0c1a61341bf968cc41c587ca8b238e9aab63bab5232b936e；全部恢复核对正常，支持新异常插桩布局仍可到达PE调用前。

d3a0972新增point24存在/point25缺失，位于Image->EntryPoint前，沿用同一handle/完整文件GUID/ordinal筛选。配置表内容匹配仅用包装器实际比较的GUID前64位；不声称完整GUID或VendorTable有效，不读取canary值，不安装配置表、不调用RNG/SMC。空system table、非零数量配空指针、数量超过4096均不产生缺失结论；4096只是遍历上限，不是UEFI规范限制。其他stage/detail不遍历表。

47组真实header sanitizer验证存在/缺失、第一项不匹配/第二项前缀匹配而后64位不同、上下文/GUID/ordinal及坏表守卫；45项Python/实际patch重复重放通过。原迁移字节/内存/标记保持。固定edk2-msm e1952621递归源码树1890项未截断，未找到canary/stackcheck/RNG/random命名源文件；这不是证明它绝无相关实现，但目前没有可直接替换的已审计源码。本轮不改用别机RNG二进制。d3a0972源码CI39882096705已触发，实机结果另记。

## 配置表存在门实测结论

d3a0972、Display完整文件GUID、实际队列32、无UFS的point24于09:10:20/09:15:04/09:16:21完成2/7/2秒，第三次复用第一份完全相同镜像。ADB17.298/21.464/16.058秒，Android完成32.397/36.925/30.174秒。初差4.166秒、复测差5.406秒，保留全部噪声样本，支持达到匹配前缀存在门。2秒镜像1409f10d5694184a49f12e5a07300d4524ba74d752bc03ffdc0842066315108b、7秒502700233670321e624fd960cb6b72268219e92672ea3ba8b253b8090f474f1c；FD分别2c4604d7a20b747fccdb4c04721e57dd05689f30827a5ed868633dfa2cb623ea、6e029dc1307f8b7d677d92d33f2f48a2c260c0bca86a7bca45c1ce8ef3d4eedb。

两候选官方backend/core还原、32原厂PE-DEPEX、BootShim/v3审计通过，三次Android/root/原分区摘要正常，无flash/erase/改槽。源码CI39882096705成功并回读PASS。point25缺失门仅47组主机检查覆盖，未生成/启动它的独立变体，不声称硬件负对照。

此结果是PE调用前的只读表状态，降低“缺表触发canary RNG初始化”的嫌疑；不是完整GUID/值有效性或实际执行包装器的证明，也不能排除后续其他SMC。静态RVA0x114c之后先调用0x123c一串库构造器，之后才到0x1508附近的入口包装；未把RVA标签当公开符号或运行证明。下一步优先评估在固定Mu的真实UEFI服务边界观察构造器/驱动调用，需区分目标PE直接调用、嵌套镜像及事件回调，不能仅凭Dispatcher全局上下文归因。这一层尚未实现，也尚无GOP/map/BDS/XNU/触控证明。
