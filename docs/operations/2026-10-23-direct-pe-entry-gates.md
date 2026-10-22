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
